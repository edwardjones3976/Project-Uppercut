// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 12:50 UTC | START ]
#include "UppercutCoreEvadeCommandlet.h"

#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

// SHA-256 (FIPS 180-4), file-local like every evidence probe's.
namespace UppercutEvadeSha256
{
    static const uint32 K[64] = {
        0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
        0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
        0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
        0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
        0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
        0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
        0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
        0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2 };

    static uint32 Rotr(uint32 X, uint32 N) { return (X >> N) | (X << (32 - N)); }

    static void Hash(const uint8* Data, uint64 Len, uint8 Out[32])
    {
        uint32 H[8] = { 0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
                        0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19 };
        const uint64 BitLen = Len * 8;
        const uint64 Total = ((Len + 8) / 64 + 1) * 64;
        TArray<uint8> Msg;
        Msg.SetNumZeroed((int32)Total);
        FMemory::Memcpy(Msg.GetData(), Data, Len);
        Msg[(int32)Len] = 0x80;
        for (int32 i = 0; i < 8; ++i)
        {
            Msg[(int32)(Total - 1 - i)] = (uint8)((BitLen >> (8 * i)) & 0xff);
        }
        for (uint64 Chunk = 0; Chunk < Total; Chunk += 64)
        {
            uint32 W[64];
            for (int32 i = 0; i < 16; ++i)
            {
                const uint8* P = Msg.GetData() + Chunk + i * 4;
                W[i] = ((uint32)P[0] << 24) | ((uint32)P[1] << 16) | ((uint32)P[2] << 8) | (uint32)P[3];
            }
            for (int32 i = 16; i < 64; ++i)
            {
                const uint32 S0 = Rotr(W[i - 15], 7) ^ Rotr(W[i - 15], 18) ^ (W[i - 15] >> 3);
                const uint32 S1 = Rotr(W[i - 2], 17) ^ Rotr(W[i - 2], 19) ^ (W[i - 2] >> 10);
                W[i] = W[i - 16] + S0 + W[i - 7] + S1;
            }
            uint32 A = H[0], B = H[1], C = H[2], D = H[3], E = H[4], F = H[5], G = H[6], Hh = H[7];
            for (int32 i = 0; i < 64; ++i)
            {
                const uint32 S1 = Rotr(E, 6) ^ Rotr(E, 11) ^ Rotr(E, 25);
                const uint32 Ch = (E & F) ^ (~E & G);
                const uint32 T1 = Hh + S1 + Ch + K[i] + W[i];
                const uint32 S0 = Rotr(A, 2) ^ Rotr(A, 13) ^ Rotr(A, 22);
                const uint32 Mj = (A & B) ^ (A & C) ^ (B & C);
                const uint32 T2 = S0 + Mj;
                Hh = G; G = F; F = E; E = D + T1; D = C; C = B; B = A; A = T1 + T2;
            }
            H[0] += A; H[1] += B; H[2] += C; H[3] += D;
            H[4] += E; H[5] += F; H[6] += G; H[7] += Hh;
        }
        for (int32 i = 0; i < 8; ++i)
        {
            Out[i * 4 + 0] = (uint8)(H[i] >> 24); Out[i * 4 + 1] = (uint8)(H[i] >> 16);
            Out[i * 4 + 2] = (uint8)(H[i] >> 8);  Out[i * 4 + 3] = (uint8)(H[i]);
        }
    }
}

namespace
{
    const uint32 LcgA = 1664525u;
    const uint32 LcgC = 1013904223u;
    const uint64 FnvOffset = 14695981039346656037ull;
    const uint64 FnvPrime = 1099511628211ull;

    struct FEvasion
    {
        FString Id, Kind;
        int32 Startup = 0, Active = 0, Recovery = 0;
        TArray<FString> Vacates;    // sorted
        TArray<FString> BeatenBy;   // sorted
    };

    struct FRPunch
    {
        FString Id, Category, Region;
        int32 Startup = 0, Active = 0, Frames = 0;
    };

    bool LoadJsonR(const FString& Path, TSharedPtr<FJsonObject>& OutRoot, FString& OutSha)
    {
        TArray<uint8> Bytes;
        if (!FFileHelper::LoadFileToArray(Bytes, *Path)) { return false; }
        uint8 Sha[32];
        UppercutEvadeSha256::Hash(Bytes.GetData(), Bytes.Num(), Sha);
        OutSha.Reset();
        for (int32 i = 0; i < 32; ++i) { OutSha += FString::Printf(TEXT("%02x"), Sha[i]); }
        FString Text;
        FFileHelper::BufferToString(Text, Bytes.GetData(), Bytes.Num());
        const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
        return FJsonSerializer::Deserialize(Reader, OutRoot) && OutRoot.IsValid();
    }

    FString Join(const TArray<FString>& Xs)
    {
        if (Xs.Num() == 0) { return TEXT("-"); }
        FString Out;
        for (int32 i = 0; i < Xs.Num(); ++i)
        {
            if (i) { Out += TEXT(","); }
            Out += Xs[i];
        }
        return Out;
    }
}

int32 UUppercutCoreEvadeCommandlet::Main(const FString& Params)
{
    uint32 Seed = 0; int32 Ticks = 0; FString Repo, OutPath;
    FParse::Value(*Params, TEXT("seed="), Seed);
    FParse::Value(*Params, TEXT("ticks="), Ticks);
    FParse::Value(*Params, TEXT("repo="), Repo);
    FParse::Value(*Params, TEXT("out="), OutPath);
    if (Ticks <= 0 || Repo.IsEmpty() || OutPath.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreEvade: need -seed= -ticks= -repo= -out="));
        return 1;
    }

    // Exactly the three files the phase reads. No separation, no guard, no
    // stamina - those belong to Q, L/O and an open gate respectively.
    const TCHAR* Rel[3] = { TEXT("data/guard_evasion_model.json"),
                            TEXT("data/moves/generic_sandbox_moves.json"),
                            TEXT("data/animation_model.json") };
    const TCHAR* ShaName[3] = { TEXT("guard_evasion"), TEXT("moves"),
                                TEXT("animation") };
    TSharedPtr<FJsonObject> Root[3];
    FString Sha[3];
    for (int32 i = 0; i < 3; ++i)
    {
        if (!LoadJsonR(Repo / Rel[i], Root[i], Sha[i]))
        {
            UE_LOG(LogTemp, Error, TEXT("UppercutCoreEvade: cannot read %s"), Rel[i]);
            return 1;
        }
    }

    // ---- canon ------------------------------------------------------------
    TMap<FString, TSharedPtr<FJsonObject>> MoveTable;
    TMap<FString, FString> Category, Region;
    for (const TSharedPtr<FJsonValue>& V : Root[1]->GetArrayField(TEXT("moves")))
    {
        const TSharedPtr<FJsonObject> M = V->AsObject();
        const FString Id = M->GetStringField(TEXT("id"));
        MoveTable.Add(Id, M);
        FString Cat;
        M->TryGetStringField(TEXT("category"), Cat);
        Category.Add(Id, Cat);
        FString Reg;
        const TArray<TSharedPtr<FJsonValue>>* Regs = nullptr;
        if (M->TryGetArrayField(TEXT("target_regions"), Regs) && Regs->Num() > 0)
        {
            Reg = (*Regs)[0]->AsString();
        }
        Region.Add(Id, Reg);
    }

    TMap<FString, FEvasion> Evasions;
    for (const TSharedPtr<FJsonValue>& V : Root[0]->GetArrayField(TEXT("evasions")))
    {
        const TSharedPtr<FJsonObject> E = V->AsObject();
        FEvasion Ev;
        Ev.Id = E->GetStringField(TEXT("id"));
        Ev.Kind = E->GetStringField(TEXT("kind"));
        E->TryGetNumberField(TEXT("active_ticks"), Ev.Active);
        const TArray<TSharedPtr<FJsonValue>>* Arr = nullptr;
        if (E->TryGetArrayField(TEXT("vacates"), Arr))
        {
            for (const TSharedPtr<FJsonValue>& X : *Arr) { Ev.Vacates.Add(X->AsString()); }
        }
        if (E->TryGetArrayField(TEXT("beaten_by"), Arr))
        {
            for (const TSharedPtr<FJsonValue>& X : *Arr) { Ev.BeatenBy.Add(X->AsString()); }
        }
        Ev.Vacates.Sort();
        Ev.BeatenBy.Sort();
        const FString MoveId = E->GetStringField(TEXT("move_id"));
        if (const TSharedPtr<FJsonObject>* M = MoveTable.Find(MoveId))
        {
            (*M)->TryGetNumberField(TEXT("startup_frames"), Ev.Startup);
            (*M)->TryGetNumberField(TEXT("recovery_frames"), Ev.Recovery);
        }
        Evasions.Add(Ev.Id, Ev);
    }
    const TSharedPtr<FJsonObject> Econ =
        Root[0]->GetObjectField(TEXT("evasion_economy"));
    const bool bOutranks = Econ->GetBoolField(TEXT("outranks_guard"));
    const int32 MistimeTicks = (int32)Econ->GetNumberField(
        TEXT("mistime_penalty_ticks"));

    // The action table, in the contract's order. The index into it IS the LCG
    // word modulo nine, so the order is part of the artifact.
    const TCHAR* PunchIds[6] = { TEXT("jab_lead"), TEXT("cross_rear"),
                                 TEXT("hook_lead"), TEXT("uppercut_rear"),
                                 TEXT("body_straight_rear"),
                                 TEXT("body_hook_lead") };
    const TCHAR* EvasionIds[2] = { TEXT("slip_lead"), TEXT("roll_under") };
    TMap<FString, FRPunch> Punches;
    TMap<FString, TSharedPtr<FJsonObject>> Anim;
    for (const TSharedPtr<FJsonValue>& V :
         Root[2]->GetArrayField(TEXT("move_animations")))
    {
        Anim.Add(V->AsObject()->GetStringField(TEXT("move_id")), V->AsObject());
    }
    for (int32 i = 0; i < 6; ++i)
    {
        const FString Id = PunchIds[i];
        const TSharedPtr<FJsonObject>* A = Anim.Find(Id);
        if (!A)
        {
            UE_LOG(LogTemp, Error, TEXT("UppercutCoreEvade: %s has no animation"), *Id);
            return 1;
        }
        FRPunch P;
        P.Id = Id;
        P.Category = Category.FindRef(Id);
        P.Region = Region.FindRef(Id);
        P.Startup = (int32)(*A)->GetNumberField(TEXT("startup_ticks"));
        P.Active = (int32)(*A)->GetNumberField(TEXT("active_ticks"));
        P.Frames = P.Startup + P.Active
                 + (int32)(*A)->GetNumberField(TEXT("recovery_ticks"));
        Punches.Add(Id, P);
    }

    // ---- the rules, one lambda each, same names as the contract ------------
    auto Beats = [&](const FString& EvId, const FString& MoveId)
    {
        const FString Cat = Category.FindRef(MoveId);
        return !Cat.IsEmpty() && Evasions[EvId].BeatenBy.Contains(Cat);
    };
    auto Evades = [&](const FString& EvId, const FString& MoveId,
                      const FString& Reg)
    {
        const FEvasion* E = Evasions.Find(EvId);
        if (!E || E->Kind != TEXT("active_window")) { return false; }
        if (!E->Vacates.Contains(Reg)) { return false; }
        return !Beats(EvId, MoveId);
    };

    // ---- the four properties, proven rather than asserted ------------------
    auto BodyShotBeatsTheSlip = [&]()
    {
        bool bAny = false;
        for (const TPair<FString, FString>& It : Region)
        {
            if (It.Value != TEXT("torso_upper") && It.Value != TEXT("torso_lower"))
            {
                continue;
            }
            bAny = true;
            if (Evades(TEXT("slip_lead"), It.Key, It.Value)) { return false; }
        }
        return bAny;
    };
    auto UppercutBeatsTheRoll = [&]()
    {
        bool bAny = false;
        for (const TPair<FString, FString>& It : Category)
        {
            if (It.Value != TEXT("uppercut")) { continue; }
            bAny = true;
            const FString Reg = Region.FindRef(It.Key);
            if (!Evasions[TEXT("roll_under")].Vacates.Contains(Reg)) { return false; }
            if (Evades(TEXT("roll_under"), It.Key, Reg)) { return false; }
        }
        return bAny;
    };
    auto SlipEvadesAStraight = [&]()
    {
        bool bAny = false;
        for (const TPair<FString, FString>& It : Category)
        {
            if (It.Value != TEXT("jab") && It.Value != TEXT("cross")) { continue; }
            bAny = true;
            if (!Evades(TEXT("slip_lead"), It.Key, Region.FindRef(It.Key)))
            {
                return false;
            }
        }
        return bAny;
    };
    auto NoEvasionIsStrictlyBetter = [&]()
    {
        // Against the PHASE O punch set, which is what `O.PUNCHES` is in the
        // contract - not this phase's six.
        const TCHAR* OPunches[5] = { TEXT("jab_lead"), TEXT("cross_rear"),
                                     TEXT("hook_lead"), TEXT("uppercut_rear"),
                                     TEXT("body_straight_rear") };
        for (const TPair<FString, FEvasion>& It : Evasions)
        {
            if (It.Value.Kind != TEXT("active_window")) { continue; }
            bool bBeaten = false;
            for (int32 i = 0; i < 5 && !bBeaten; ++i)
            {
                bBeaten = Beats(It.Key, OPunches[i]);
            }
            if (!bBeaten) { return false; }
        }
        return true;
    };

    // ---- canon checks, counted rather than described -----------------------
    int32 CanonErrors = 0;
    TArray<FString> ActiveIds;
    for (const TPair<FString, FEvasion>& It : Evasions)
    {
        if (It.Value.Kind == TEXT("active_window")) { ActiveIds.Add(It.Key); }
        if (It.Value.Kind == TEXT("positional") && It.Value.Vacates.Num() > 0)
        {
            ++CanonErrors;
        }
    }
    ActiveIds.Sort();
    if (ActiveIds.Num() == 0) { ++CanonErrors; }
    const TCHAR* DamageRegions[6] = { TEXT("head"), TEXT("jaw_chin"),
                                      TEXT("torso_upper"), TEXT("torso_lower"),
                                      TEXT("arm_left"), TEXT("arm_right") };
    for (const FString& Id : ActiveIds)
    {
        const FEvasion& E = Evasions[Id];
        if (E.Active <= 0) { ++CanonErrors; }
        if (E.Vacates.Num() == 0) { ++CanonErrors; }
        if (E.BeatenBy.Num() == 0) { ++CanonErrors; }
        FString Band;
        const TSharedPtr<FJsonObject>* M = MoveTable.Find(Id);
        if (!M || !(*M)->TryGetStringField(TEXT("range_band"), Band) || Band.IsEmpty())
        {
            ++CanonErrors;
        }
        for (const FString& R : E.Vacates)
        {
            bool bKnown = false;
            for (int32 i = 0; i < 6 && !bKnown; ++i) { bKnown = (R == DamageRegions[i]); }
            if (!bKnown) { ++CanonErrors; }
        }
    }
    if (!bOutranks) { ++CanonErrors; }
    if (MistimeTicks <= 0) { ++CanonErrors; }
    {
        int32 MinSpan = MAX_int32, MaxSpan = 0;
        for (const TPair<FString, FRPunch>& It : Punches)
        {
            const int32 Span = It.Value.Startup + It.Value.Active;
            MinSpan = FMath::Min(MinSpan, Span);
            MaxSpan = FMath::Max(MaxSpan, Span);
        }
        if (Punches.Num() > 0 && MinSpan == MaxSpan) { ++CanonErrors; }
    }

    // ---- the header: canon before any tick --------------------------------
    FString Out;
    Out += TEXT("H|phase=R\n");
    for (int32 i = 0; i < 3; ++i)
    {
        Out += FString::Printf(TEXT("H|canon_%s=%s\n"), ShaName[i], *Sha[i]);
    }
    Out += FString::Printf(TEXT("H|seed=%u\nH|ticks=%d\n"), Seed, Ticks);
    TArray<FString> EvIds;
    Evasions.GetKeys(EvIds);
    EvIds.Sort();
    for (const FString& Id : EvIds)
    {
        const FEvasion& E = Evasions[Id];
        Out += FString::Printf(TEXT("Y|%s|%s|%d|%d|%s|%s\n"), *Id, *E.Kind,
                               E.Startup, E.Active, *Join(E.Vacates),
                               *Join(E.BeatenBy));
    }
    for (int32 i = 0; i < 6; ++i)
    {
        const FRPunch& P = Punches[PunchIds[i]];
        Out += FString::Printf(TEXT("M|%s|%s|%s|%d|%d\n"), *P.Id,
                               P.Category.IsEmpty() ? TEXT("-") : *P.Category,
                               P.Region.IsEmpty() ? TEXT("-") : *P.Region,
                               P.Startup, P.Active);
    }
    Out += FString::Printf(TEXT("K|outranks_guard=%d|mistime_ticks=%d\n"),
                           bOutranks ? 1 : 0, MistimeTicks);

    // ---- state ------------------------------------------------------------
    int32 Busy[2] = { 0, 0 };
    bool bInFlight[2] = { false, false };
    FString PunchMove[2];
    int32 PunchT0[2] = { 0, 0 };
    bool bEvading[2] = { false, false };
    FString EvName[2];
    int32 EvFrom[2] = { 0, 0 }, EvUntil[2] = { 0, 0 };
    uint32 X = Seed;
    uint64 Fnv = FnvOffset;
    int64 Rows = 0, Commits = 0, NPunch = 0, NEvade = 0, Waits = 0;
    int64 Arrived = 0, Dodged = 0, Countered = 0, WrongRegion = 0, Clear = 0;

    auto Emit = [&](const FString& Row)
    {
        Out += Row;
        const FTCHARToUTF8 Utf8(*Row);
        const uint8* P = (const uint8*)Utf8.Get();
        for (int32 b = 0; b < Utf8.Length(); ++b) { Fnv = (Fnv ^ P[b]) * FnvPrime; }
        ++Rows;
    };

    for (int32 T = 1; T <= Ticks; ++T)
    {
        for (int32 i = 0; i < 2; ++i)
        {
            const int32 Opp = 1 - i;
            // ---- 1. a punch already in the air ----------------------------
            if (bInFlight[i])
            {
                const FRPunch& P = Punches[PunchMove[i]];
                const int32 K = T - PunchT0[i];
                if (K == P.Startup + P.Active)
                {
                    const FString Reg = P.Region.IsEmpty() ? TEXT("-") : P.Region;
                    const bool bActive = bEvading[Opp] && EvFrom[Opp] < T
                                         && T <= EvUntil[Opp];
                    const TCHAR* Result = TEXT("arrived");
                    const TCHAR* Why = TEXT("clear");
                    FString Name = TEXT("-");
                    if (!bActive)
                    {
                        ++Clear;
                    }
                    else
                    {
                        Name = EvName[Opp];
                        if (!Evasions[Name].Vacates.Contains(Reg))
                        {
                            Why = TEXT("region");
                            ++WrongRegion;
                        }
                        else if (Beats(Name, PunchMove[i]))
                        {
                            // Canon's own sentence: the uppercut rises into
                            // where the head is going.
                            Why = TEXT("counter");
                            ++Countered;
                        }
                        else
                        {
                            Result = TEXT("dodged");
                            Why = TEXT("vacated");
                            ++Dodged;
                        }
                    }
                    if (FString(Result) == TEXT("arrived")) { ++Arrived; }
                    Emit(FString::Printf(TEXT("P|%d|%d|%s|%s|%s|%s|%s\n"), T, i,
                                         *PunchMove[i], Result, Why, *Reg, *Name));
                    bInFlight[i] = false;
                }
                else if (K > P.Startup + P.Active)
                {
                    bInFlight[i] = false;
                }
            }

            // ---- 2. an evasion window closing -----------------------------
            if (bEvading[i] && T == EvUntil[i])
            {
                Emit(FString::Printf(TEXT("W|%d|%d|%s|close\n"), T, i, *EvName[i]));
                bEvading[i] = false;
            }

            // ---- 3. commitment --------------------------------------------
            if (Busy[i] > 0)
            {
                --Busy[i];
                continue;
            }

            // ---- 4. one commitment ----------------------------------------
            X = LcgA * X + LcgC;          // uint32 wraps, which IS mod 2^32
            const int32 Choice = (int32)(X % 9u);
            FString Action;
            if (Choice < 6) { Action = PunchIds[Choice]; }
            else if (Choice < 8) { Action = EvasionIds[Choice - 6]; }
            else { Action = TEXT("wait"); }
            ++Commits;
            if (Choice == 8)
            {
                ++Waits;
            }
            else if (Choice < 6)
            {
                Busy[i] = Punches[Action].Frames;
                bInFlight[i] = true;
                PunchMove[i] = Action;
                PunchT0[i] = T;
                ++NPunch;
            }
            else
            {
                const FEvasion& E = Evasions[Action];
                // A committed evasion that catches nothing leaves the defender
                // in recovery with no structure up. Authored, not invented.
                Busy[i] = E.Startup + E.Active + E.Recovery + MistimeTicks;
                bEvading[i] = true;
                EvName[i] = Action;
                EvFrom[i] = T + E.Startup;
                EvUntil[i] = T + E.Startup + E.Active;
                Emit(FString::Printf(TEXT("W|%d|%d|%s|open\n"), T, i, *Action));
                ++NEvade;
            }
            Emit(FString::Printf(TEXT("A|%d|%d|%s|%u\n"), T, i, *Action, X));
        }
    }

    // ---- the properties, inside the hash ----------------------------------
    Emit(FString::Printf(TEXT("V|a_body_shot_beats_the_slip|%d\n"),
                         BodyShotBeatsTheSlip() ? 1 : 0));
    Emit(FString::Printf(TEXT("V|the_uppercut_beats_the_roll|%d\n"),
                         UppercutBeatsTheRoll() ? 1 : 0));
    Emit(FString::Printf(TEXT("V|the_slip_evades_a_straight|%d\n"),
                         SlipEvadesAStraight() ? 1 : 0));
    Emit(FString::Printf(TEXT("V|no_evasion_is_strictly_better|%d\n"),
                         NoEvasionIsStrictlyBetter() ? 1 : 0));
    Emit(FString::Printf(TEXT("V|canon_errors|%d\n"), CanonErrors));

    Out += FString::Printf(
        TEXT("S|rows=%lld|commits=%lld|punches=%lld|evasions=%lld|waits=%lld")
        TEXT("|arrived=%lld|dodged=%lld|countered=%lld|wrong_region=%lld")
        TEXT("|clear=%lld|fnv1a64=%016llx\n"),
        Rows, Commits, NPunch, NEvade, Waits, Arrived, Dodged, Countered,
        WrongRegion, Clear, Fnv);

    IFileManager::Get().MakeDirectory(*FPaths::GetPath(OutPath), true);
    if (!FFileHelper::SaveStringToFile(Out, *OutPath,
            FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM))
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreEvade: cannot write %s"), *OutPath);
        return 1;
    }
    UE_LOG(LogTemp, Display, TEXT("UppercutCoreEvade: %lld rows, fnv1a64=%016llx"),
           Rows, Fnv);
    return 0;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 12:50 UTC | END ]
