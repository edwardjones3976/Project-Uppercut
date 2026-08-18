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
    TArray<FUppercutCanonSource> GuardSources;
    if (!UppercutLoadGuardCanon(RepoDir, GuardCanon, GuardSources, OutError))
    {
        return false;
    }
    Sources.Append(GuardSources);
    TArray<FUppercutCanonSource> PunchEconSources;
    if (!UppercutLoadPunchEconomyCanon(RepoDir, PunchEconomyCanon,
                                       PunchEconSources, OutError))
    {
        return false;
    }
    Sources.Append(PunchEconSources);
    TArray<FUppercutCanonSource> CondSources;
    if (!UppercutLoadConditionCanon(RepoDir, ConditionCanon, CondSources, OutError))
    {
        return false;
    }
    Sources.Append(CondSources);
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
        Fighter[i].Posture = TEXT("high_guard");
        Fighter[i].RecoveryTicks = 0;
        Fighter[i].bEvasion = false;
        Fighter[i].EvasionId.Reset();
        Fighter[i].EvasionOpenAt = 0;
        Fighter[i].EvasionCloseAt = 0;
        Fighter[i].bEvasionUsed = false;
        Fighter[i].ArmWorkLeadQ = 0;
        Fighter[i].ArmWorkRearQ = 0;
        Fighter[i].bSteppedSinceThrow = true;
        Fighter[i].Condition.Reset(ConditionCanon);
    }
    Round.Reset(TickBudget);
    Tick = 0;
    Decisions = 0;
    Punches = 0;
    Landed = 0;
    Blocked = 0;
}

int64 FUppercutFightSession::Separation() const
{
    return Fighter[1].Range.Pos - Fighter[0].Range.Pos;
}

void FUppercutFightSession::DecideAndCommit(int32 Who, TArray<FString>* OutRows)
{
    FUppercutFightFighter& Me = Fighter[Who];
    if (Me.DecisionBusy > 0 || Me.Range.Busy > 0 || Me.RecoveryTicks > 0)
    {
        return;
    }

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
    // Decision 0026: sort by move id — TMap iteration order must not choose
    // the punch. Python throwable_from already sorts; keep both sides aligned.
    for (const auto& Pair : RangeCanon.Moves)
    {
        if (!Pair.Value.bPunch) { continue; }
        if (RangeCanon.InBand(Pair.Key, Me.Range.Band))
        {
            Obs.ThrowableHere.Add(Pair.Key);
        }
    }
    Obs.ThrowableHere.Sort([](const FString& A, const FString& B)
    {
        return A < B;
    });

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
        Me.bSteppedSinceThrow = true;
        Me.Wind = FMath::Max((int64)0, Me.Wind - StaminaCanon.WindPerRu);
    }
    else if (D.Tactic == EUppercutThinTactic::Retreat)
    {
        R.Pending = RangeCanon.DirRetreat * RangeCanon.Stride;
        R.LastAction = TEXT("step_out");
        R.Busy = 4;
        Me.bSteppedSinceThrow = true;
        Me.Wind = FMath::Max((int64)0, Me.Wind - StaminaCanon.WindPerRu);
    }
    else if (D.Tactic == EUppercutThinTactic::Attack && !D.Execution.IsEmpty())
    {
        const FUppercutRangeMove* Move = RangeCanon.Moves.Find(D.Execution);
        if (Move)
        {
            const FString* Hand = PunchEconomyCanon.HandByMove.Find(D.Execution);
            if (Hand)
            {
                int64& Work = (*Hand == TEXT("lead")) ? Me.ArmWorkLeadQ : Me.ArmWorkRearQ;
                const int64 Ceiling = PunchEconomyCanon.MaxArmMultiplierQ - 10000;
                Work = FMath::Min(Ceiling, Work + PunchEconomyCanon.PerThrowSameArm);
            }
            if (!Me.bSteppedSinceThrow)
            {
                R.Pending += PunchEconomyCanon.RuCededPerThrowWithoutStep;
            }
            Me.bSteppedSinceThrow = false;
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
    else if (D.Tactic == EUppercutThinTactic::Guard)
    {
        if (!D.Execution.IsEmpty())
        {
            Me.Posture = D.Execution;
        }
        R.LastAction = TEXT("guard");
        const FUppercutGuardPosture* Ps = GuardCanon.Postures.Find(Me.Posture);
        if (Ps && Ps->HoldPerTick > 0)
        {
            Me.Wind = FMath::Max((int64)0, Me.Wind - Ps->HoldPerTick);
        }
    }
    else if (D.Tactic == EUppercutThinTactic::Evade)
    {
        const FString Ev = D.Execution.IsEmpty() ? TEXT("slip_lead") : D.Execution;
        if (CommitEvasion(Who, Ev))
        {
            R.LastAction = Ev;
        }
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

bool FUppercutFightSession::CommitEvasion(int32 Who, const FString& EvasionId)
{
    FUppercutFightFighter& Me = Fighter[Who];
    if (Me.bEvasion || Me.RecoveryTicks > 0) { return false; }
    const FUppercutEvasion* E = EvadeCanon.Evasions.Find(EvasionId);
    if (!E || E->Kind != TEXT("active_window")) { return false; }
    Me.bEvasion = true;
    Me.EvasionId = EvasionId;
    Me.EvasionOpenAt = Tick + E->Startup;
    Me.EvasionCloseAt = Me.EvasionOpenAt + E->Active;
    Me.bEvasionUsed = false;
    Me.RecoveryTicks = E->Startup + E->Active + E->Recovery;
    Me.DecisionBusy = Me.RecoveryTicks + EvadeCanon.MistimeTicks;
    return true;
}

bool FUppercutFightSession::EvasionActive(int32 Who) const
{
    const FUppercutFightFighter& F = Fighter[Who];
    return F.bEvasion && Tick >= F.EvasionOpenAt && Tick < F.EvasionCloseAt;
}

void FUppercutFightSession::TickEvasions(TArray<FString>* OutRows)
{
    for (int32 i = 0; i < 2; ++i)
    {
        FUppercutFightFighter& F = Fighter[i];
        if (!F.bEvasion) { continue; }
        if (Tick == F.EvasionOpenAt && OutRows)
        {
            OutRows->Add(FString::Printf(
                TEXT("W|%d|%s|%s|open|until=%d\n"),
                Tick, *F.ParticipantId, *F.EvasionId, F.EvasionCloseAt));
        }
        if (Tick >= F.EvasionCloseAt)
        {
            if (F.bEvasionUsed)
            {
                if (OutRows)
                {
                    OutRows->Add(FString::Printf(
                        TEXT("W|%d|%s|%s|close\n"),
                        Tick, *F.ParticipantId, *F.EvasionId));
                }
            }
            else
            {
                F.RecoveryTicks += EvadeCanon.MistimeTicks;
                if (OutRows)
                {
                    OutRows->Add(FString::Printf(
                        TEXT("W|%d|%s|%s|mistimed|penalty=%d\n"),
                        Tick, *F.ParticipantId, *F.EvasionId,
                        EvadeCanon.MistimeTicks));
                }
            }
            F.bEvasion = false;
            F.EvasionId.Reset();
            F.EvasionOpenAt = 0;
            F.EvasionCloseAt = 0;
            F.bEvasionUsed = false;
        }
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
            Fighter[Atk].RecoveryTicks += UppercutApplyOutcomeRecovery(
                PunchEconomyCanon, TEXT("whiffed"), Move->Frames);
            A.bInFlight = false;
            continue;
        }

        // Evasion stage (Phase R): active window must beat the punch's region.
        FUppercutFightFighter& Def = Fighter[1 - Atk];
        FString Region = EvadeCanon.Region.FindRef(A.PunchMove);
        if (Region.IsEmpty()) { Region = TEXT("head"); }
        const bool bWindow = EvasionActive(1 - Atk);
        const FString ActiveEv = bWindow ? Def.EvasionId : FString();
        bool bEvaded = false;
        if (bWindow)
        {
            bEvaded = EvadeCanon.Evades(ActiveEv, A.PunchMove, Region);
            Def.bEvasionUsed = true;
        }
        if (bEvaded)
        {
            Fighter[Atk].RecoveryTicks += UppercutApplyOutcomeRecovery(
                PunchEconomyCanon, TEXT("dodged"), Move->Frames);
            if (OutRows)
            {
                OutRows->Add(FString::Printf(
                    TEXT("P|%d|%d|%s|evaded|evasion=%s\n"),
                    Tick, Atk, *A.PunchMove, *ActiveEv));
            }
            A.bInFlight = false;
            continue;
        }

        // Guard stage (Phase L): only after evasion did not clear the lane.
        const bool bCommitted = Def.Range.bInFlight || Def.bEvasion;
        const bool bBlocked = GuardCanon.Intercepts(
            Def.Posture, bCommitted, A.PunchMove);
        if (bBlocked)
        {
            ++Blocked;
            Fighter[Atk].RecoveryTicks += UppercutApplyOutcomeRecovery(
                PunchEconomyCanon, TEXT("blocked"), Move->Frames);
            if (OutRows)
            {
                OutRows->Add(FString::Printf(
                    TEXT("P|%d|%d|%s|blocked|guard=%s\n"),
                    Tick, Atk, *A.PunchMove, *Def.Posture));
            }
            A.bInFlight = false;
            continue;
        }

        // Landed: regional condition + knockdown pressure.
        ++Landed;
        Round.WitnessLanding(Atk);
        const FString TargetRegion = ConditionCanon.PrimaryRegionByMove.FindRef(A.PunchMove);
        const int64 Effort = ConditionCanon.EffortByMove.FindRef(A.PunchMove);
        if (!TargetRegion.IsEmpty() && Effort > 0)
        {
            Def.Condition.Absorb(ConditionCanon, TargetRegion, (int32)Effort);
        }
        const int32 WindFracQ = Def.WindMax > 0
            ? (int32)((Def.Wind * 10000) / Def.WindMax) : 10000;
        const int64 PressureQ = UppercutKnockdownPressureQ(
            ConditionCanon, A.PunchMove, Def.Condition, WindFracQ,
            Def.Range.bInFlight || Def.bEvasion, Def.bEvasion,
            Def.Card, AttrCanon);
        const int64 ThresholdQ = AttrCanon.Apply(
            RoundCanon.PressureThresholdQ, Def.Card,
            TEXT("knockdown_pressure_threshold"));
        if (OutRows)
        {
            OutRows->Add(FString::Printf(
                TEXT("P|%d|%d|%s|landed|force=%lld|region=%s\n"),
                Tick, Atk, *A.PunchMove, (long long)PressureQ, *TargetRegion));
        }
        Round.TryKnockdown(1 - Atk, PressureQ, ThresholdQ, RoundCanon, OutRows);
        A.bInFlight = false;
    }
}

void FUppercutFightSession::Step(TArray<FString>* OutRows)
{
    if (!bReady || Round.IsFinished()) { return; }

    Round.Tick = Tick;

    if (Round.Phase == EUppercutRoundPhase::Counting)
    {
        Round.TickCount(RoundCanon, ConditionCanon,
                        Fighter[0].Condition, Fighter[1].Condition, OutRows);
        ++Tick;
        return;
    }

    TickEvasions(OutRows);
    ResolveContacts(OutRows);
    if (Round.IsFinished()) { ++Tick; return; }

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

    for (int32 i = 0; i < 2; ++i)
    {
        if (Fighter[i].RecoveryTicks > 0) { --Fighter[i].RecoveryTicks; }
        if (!Fighter[i].Range.bInFlight)
        {
            Fighter[i].ArmWorkLeadQ = FMath::Max(
                (int64)0,
                Fighter[i].ArmWorkLeadQ - PunchEconomyCanon.RecoveryPerIdleTick);
            Fighter[i].ArmWorkRearQ = FMath::Max(
                (int64)0,
                Fighter[i].ArmWorkRearQ - PunchEconomyCanon.RecoveryPerIdleTick);
        }
    }

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
