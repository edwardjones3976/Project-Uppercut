// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
#include "UppercutFightSession.h"

#include "Misc/Paths.h"

namespace
{
    FString BandKeyOf(const FUppercutRangeCanon& C, int32 Band)
    {
        return C.BandKey.IsValidIndex(Band) ? C.BandKey[Band] : FString(TEXT("mid"));
    }
}

bool FUppercutFightSession::Load(const FString& RepoDir,
                                 const FString& CardA,
                                 const FString& CardB,
                                 const FString& RulesetId,
                                 FString& OutError)
{
    bReady = false;
    Sources.Reset();
    if (!UppercutLoadRangeCanon(RepoDir, RangeCanon, Sources, OutError))
    {
        return false;
    }
    TArray<FUppercutCanonSource> EvadeSources;
    if (!UppercutLoadEvadeCanon(RepoDir, EvadeCanon, EvadeSources, OutError))
    {
        return false;
    }
    Sources.Append(EvadeSources);
    if (!UppercutLoadStaminaCanon(RepoDir, StaminaCanon, OutError))
    {
        return false;
    }
    if (!UppercutLoadAttrCanon(RepoDir, AttrCanon, OutError))
    {
        return false;
    }
    if (!UppercutLoadRoundCanon(RepoDir, RulesetId, RoundCanon, OutError))
    {
        return false;
    }
    if (!UppercutLoadFighterCard(RepoDir, CardA, Fighter[0].Card, OutError))
    {
        return false;
    }
    if (!UppercutLoadFighterCard(RepoDir, CardB, Fighter[1].Card, OutError))
    {
        return false;
    }
    Fighter[0].ParticipantId = TEXT("red_corner");
    Fighter[1].ParticipantId = TEXT("blue_corner");
    // Pressure power prefers inside; range timing prefers outside.
    Fighter[0].Policy.PreferredBand = TEXT("inside");
    Fighter[0].Policy.AggressionBiasQ = 6500;
    Fighter[1].Policy.PreferredBand = TEXT("outside");
    Fighter[1].Policy.AggressionBiasQ = 4000;
    bReady = true;
    return true;
}

void FUppercutFightSession::Reset(uint32 Seed, int32 TickBudget)
{
    RangeBridge.Reset(RangeCanon, Seed);
    for (int32 i = 0; i < 2; ++i)
    {
        Fighter[i].Range = RangeBridge.Fighter[i];
        Fighter[i].Wind = StaminaCanon.WindStart;
        Fighter[i].Reserve = StaminaCanon.ReserveStart;
        Fighter[i].WindMax = StaminaCanon.WindMax;
        // Decision 0022 / 0026: fighter-local substream from bout seed + identity.
        Fighter[i].PolicyStream = UppercutMixSeed(Seed, Fighter[i].ParticipantId);
        Fighter[i].DecisionBusy = 0;
    }
    Round.Reset(TickBudget);
    Tick = 0;
    Decisions = 0;
    Punches = 0;
    Landed = 0;
}

int64 FUppercutFightSession::Separation() const
{
    return Fighter[1].Range.Pos - Fighter[0].Range.Pos;
}

void FUppercutFightSession::DecideAndCommit(int32 Who, TArray<FString>* OutRows)
{
    FUppercutFightFighter& Me = Fighter[Who];
    if (Me.DecisionBusy > 0 || Me.Range.Busy > 0) { return; }

    FUppercutThinObservation Obs;
    Obs.Band = BandKeyOf(RangeCanon, Me.Range.Band);
    Obs.PreferredBand = Me.Policy.PreferredBand;
    Obs.WindFractionQ = (Me.WindMax > 0)
        ? (int32)((Me.Wind * 10000) / Me.WindMax) : 10000;
    Obs.bWindLow = Obs.WindFractionQ < 3500;
    Obs.bOnRopes = false;
    Obs.bOpponentRecovering = Fighter[1 - Who].Range.Busy > 0;
    Obs.bIncoming = Fighter[1 - Who].Range.bInFlight;

    // Throwable moves from the current band (Rule 12).
    for (const auto& Pair : RangeCanon.Moves)
    {
        if (!Pair.Value.bPunch) { continue; }
        if (RangeCanon.InBand(Pair.Key, Me.Range.Band))
        {
            Obs.ThrowableHere.Add(Pair.Key);
        }
    }

    const FUppercutThinDecision D = Me.Policy.Decide(Obs, Me.PolicyStream);
    ++Decisions;
    Me.DecisionBusy = DecisionInterval;
    if (OutRows)
    {
        OutRows->Add(FString::Printf(
            TEXT("D|%d|%s|%s|%s|%s\n"),
            Tick, *Me.ParticipantId, UppercutThinTacticName(D.Tactic),
            *D.Execution, *D.Reason));
    }
    AdvanceRangeFromTactic(Who, D, OutRows);
}

void FUppercutFightSession::AdvanceRangeFromTactic(
    int32 Who, const FUppercutThinDecision& D, TArray<FString>* OutRows)
{
    FUppercutFightFighter& Me = Fighter[Who];
    FUppercutRangeFighter& R = Me.Range;
    R.LastActionTick = Tick;

    if (D.Tactic == EUppercutThinTactic::Advance)
    {
        R.Pending = RangeCanon.DirAdvance * RangeCanon.Stride;
        R.LastAction = TEXT("step_in");
        R.Busy = 4;
        Me.Wind = FMath::Max((int64)0, Me.Wind - StaminaCanon.WindPerRu);
    }
    else if (D.Tactic == EUppercutThinTactic::Retreat)
    {
        R.Pending = RangeCanon.DirRetreat * RangeCanon.Stride;
        R.LastAction = TEXT("step_out");
        R.Busy = 4;
        Me.Wind = FMath::Max((int64)0, Me.Wind - StaminaCanon.WindPerRu);
    }
    else if (D.Tactic == EUppercutThinTactic::Attack && !D.Execution.IsEmpty())
    {
        const FUppercutRangeMove* Move = RangeCanon.Moves.Find(D.Execution);
        if (Move)
        {
            R.bInFlight = true;
            R.PunchMove = D.Execution;
            R.PunchT0 = Tick;
            R.PunchBand = R.Band;
            R.bPunchLegal = RangeCanon.InBand(D.Execution, R.Band);
            R.Busy = Move->Frames;
            R.LastAction = D.Execution;
            ++Punches;
            Me.Wind = FMath::Max((int64)0, Me.Wind - Move->Ext);
        }
    }
    else if (D.Tactic == EUppercutThinTactic::Rest)
    {
        R.LastAction = TEXT("rest");
        Me.Wind = FMath::Min(Me.WindMax,
            Me.Wind + StaminaCanon.Recover[(int32)EUppercutAction::Rest]);
    }
    else if (D.Tactic == EUppercutThinTactic::HoldPosition)
    {
        R.LastAction = TEXT("hold");
        Me.Wind = FMath::Min(Me.WindMax,
            Me.Wind + StaminaCanon.Recover[(int32)EUppercutAction::HoldPosition]);
    }
    else
    {
        R.LastAction = TEXT("observe");
        Me.Wind = FMath::Min(Me.WindMax,
            Me.Wind + StaminaCanon.Recover[(int32)EUppercutAction::Observe]);
    }

    if (OutRows)
    {
        OutRows->Add(FString::Printf(TEXT("A|%d|%d|%s\n"),
            Tick, Who, *R.LastAction));
    }
}

void FUppercutFightSession::ResolveContacts(TArray<FString>* OutRows)
{
    for (int32 Atk = 0; Atk < 2; ++Atk)
    {
        FUppercutRangeFighter& A = Fighter[Atk].Range;
        if (!A.bInFlight) { continue; }
        const FUppercutRangeMove* Move = RangeCanon.Moves.Find(A.PunchMove);
        if (!Move) { A.bInFlight = false; continue; }
        const int32 Age = Tick - A.PunchT0;
        if (Age < Move->Startup || Age >= Move->Startup + Move->Active)
        {
            if (Age >= Move->Frames) { A.bInFlight = false; }
            continue;
        }
        if (!A.bPunchLegal)
        {
            if (OutRows)
            {
                OutRows->Add(FString::Printf(
                    TEXT("P|%d|%d|%s|whiff_band\n"), Tick, Atk, *A.PunchMove));
            }
            A.bInFlight = false;
            continue;
        }

        // Evade check (Phase R rules, shared core).
        FUppercutFightFighter& Def = Fighter[1 - Atk];
        bool bEvaded = false;
        // Minimal: if defender last action was an evasion id, ask EvadeCanon.
        if (Def.Range.LastAction.StartsWith(TEXT("slip"))
            || Def.Range.LastAction.StartsWith(TEXT("roll")))
        {
            bEvaded = EvadeCanon.Evades(Def.Range.LastAction, A.PunchMove,
                                        TEXT("head"));
        }
        if (bEvaded)
        {
            if (OutRows)
            {
                OutRows->Add(FString::Printf(
                    TEXT("P|%d|%d|%s|evaded\n"), Tick, Atk, *A.PunchMove));
            }
            A.bInFlight = false;
            continue;
        }

        // Landed: witness + knockdown pressure from card-scaled threshold.
        ++Landed;
        Round.WitnessLanding(Atk);
        const int64 ForceQ = AttrCanon.Apply(5000, Fighter[Atk].Card,
                                             TEXT("delivered_impact"));
        const int64 PressureQ = ForceQ; // simplified product for live MVP
        const int64 ThresholdQ = AttrCanon.Apply(RoundCanon.PressureThresholdQ,
                                                 Def.Card,
                                                 TEXT("knockdown_pressure_threshold"));
        if (OutRows)
        {
            OutRows->Add(FString::Printf(
                TEXT("P|%d|%d|%s|landed|force=%lld\n"),
                Tick, Atk, *A.PunchMove, (long long)ForceQ));
        }
        Round.TryKnockdown(1 - Atk, PressureQ, ThresholdQ, OutRows);
        A.bInFlight = false;
    }
}

void FUppercutFightSession::Step(TArray<FString>* OutRows)
{
    if (!bReady || Round.IsFinished()) { return; }

    Round.Tick = Tick;

    if (Round.Phase == EUppercutRoundPhase::Counting)
    {
        Round.TickCount(OutRows);
        ++Tick;
        return;
    }

    // Drain pending movement (shared range rules).
    for (int32 i = 0; i < 2; ++i)
    {
        FUppercutRangeFighter& R = Fighter[i].Range;
        if (R.Busy > 0) { --R.Busy; }
        if (Fighter[i].DecisionBusy > 0) { --Fighter[i].DecisionBusy; }
        if (R.Pending != 0)
        {
            const int64 Applied = RangeCanon.Drain(R.Pending, R.Pending);
            const int32 Sign = (i == 0) ? 1 : -1;
            // Fighter 0 advances +pos toward fighter 1; fighter 1 advances -pos.
            if (R.LastAction == TEXT("step_in"))
            {
                R.Pos += (i == 0) ? Applied : -Applied;
            }
            else if (R.LastAction == TEXT("step_out"))
            {
                R.Pos += (i == 0) ? -Applied : Applied;
            }
            (void)Sign;
            R.Pos = FMath::Clamp(R.Pos, RangeCanon.Ropes,
                                 RangeCanon.Axis - RangeCanon.Ropes);
        }
        const int64 Sep = Separation();
        R.Band = RangeCanon.ResolveBand(R.Band, FMath::Abs(Sep));
    }

    DecideAndCommit(0, OutRows);
    DecideAndCommit(1, OutRows);
    ResolveContacts(OutRows);

    ++Tick;
    if (Tick >= Round.TickBudget && !Round.IsFinished())
    {
        Round.SealDecision(OutRows);
    }
}

FString UppercutFightStreamHeader(const FUppercutFightSession& Session,
                                  uint32 Seed, int32 Ticks,
                                  const FString& RepoDir)
{
    return FString::Printf(
        TEXT("H|phase=INTEGRATED_1R|contract=uppercut-integrated-v3|seed=%u|ticks=%d|repo=%s\n"
             "H|cards=%s,%s\n"),
        Seed, Ticks, *RepoDir,
        *Session.Fighter[0].Card.Id, *Session.Fighter[1].Card.Id);
}

FString UppercutFightStreamTrailer(const FUppercutFightSession& Session,
                                   int64 Rows, uint64 Fnv)
{
    return FString::Printf(
        TEXT("S|rows=%lld|fnv=%016llx|ticks=%d|punches=%lld|landed=%lld|"
             "result=%s|cards=%d-%d|kd=%d-%d\n"),
        (long long)Rows, (unsigned long long)Fnv, Session.Tick,
        (long long)Session.Punches, (long long)Session.Landed,
        *Session.Round.Method,
        Session.Round.Card[0], Session.Round.Card[1],
        Session.Round.KdRound[0], Session.Round.KdRound[1]);
}
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]
