// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 18:40 UTC | START ]
#include "UppercutCoreConditionCommandlet.h"

#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 05:10 UTC | START edit: Decision 0023 header ]
#include "UppercutCanonHash.h"   // UppercutCanonHeaderLines
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 05:10 UTC | END edit ]

// SHA-256 (FIPS 180-4), file-local like every evidence probe's.
namespace UppercutCondSha256
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

    int64 Q(double V) { return (int64)FMath::RoundToDouble(V * 10000.0); }

    struct FNMove
    {
        int64 Cost = 0;
        int32 Frames = 0, Startup = 0, Active = 0;
        int64 Ext = 0;
        int64 Impact = 0;            // punch_model.delivered_impact, fixed point
        FString Height, Region;
        bool bPunch = false;
    };

    struct FNPosture
    {
        int64 Mobility = 0, Hold = 0;
        // Phase L could precompute which lanes a posture covers. Phase N cannot:
        // the arms wear down, so the same guard covers less as the fight goes on.
        // What survives to load time is the AUTHORED extent; coverage is decided
        // per punch, per fighter, per tick.
        TMap<FString, int64> Ext;
    };

    // The six regions this phase can reach, in stream order.
    struct FNCondition
    {
        int64 Head = 0, Jaw = 0, TorsoUp = 0, TorsoLow = 0, ArmL = 0, ArmR = 0;

        int64& ByName(const FString& R)
        {
            if (R == TEXT("head")) { return Head; }
            if (R == TEXT("jaw_chin")) { return Jaw; }
            if (R == TEXT("torso_upper")) { return TorsoUp; }
            if (R == TEXT("torso_lower")) { return TorsoLow; }
            if (R == TEXT("arm_left")) { return ArmL; }
            return ArmR;
        }
    };

    bool LoadJsonN(const FString& Path, TSharedPtr<FJsonObject>& OutRoot, FString& OutSha)
    {
        TArray<uint8> Bytes;
        if (!FFileHelper::LoadFileToArray(Bytes, *Path)) { return false; }
        uint8 Sha[32];
        UppercutCondSha256::Hash(Bytes.GetData(), Bytes.Num(), Sha);
        OutSha.Reset();
        for (int32 i = 0; i < 32; ++i) { OutSha += FString::Printf(TEXT("%02x"), Sha[i]); }
        FString Text;
        FFileHelper::BufferToString(Text, Bytes.GetData(), Bytes.Num());
        const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
        return FJsonSerializer::Deserialize(Reader, OutRoot) && OutRoot.IsValid();
    }
}

int32 UUppercutCoreConditionCommandlet::Main(const FString& Params)
{
    uint32 Seed = 0; int32 Ticks = 0; FString Repo, OutPath;
    FParse::Value(*Params, TEXT("seed="), Seed);
    FParse::Value(*Params, TEXT("ticks="), Ticks);
    FParse::Value(*Params, TEXT("repo="), Repo);
    FParse::Value(*Params, TEXT("out="), OutPath);
    if (Ticks <= 0 || Repo.IsEmpty() || OutPath.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreCondition: need -seed= -ticks= -repo= -out="));
        return 1;
    }

    const TCHAR* Rel[9] = { TEXT("data/movement_model.json"), TEXT("data/condition_model.json"),
                            TEXT("data/guard_evasion_model.json"), TEXT("data/cpu_decision_model.json"),
                            TEXT("data/moves/generic_sandbox_moves.json"), TEXT("data/animation_model.json"),
                            TEXT("data/collision_model.json"), TEXT("data/pose_geometry.json"),
                            TEXT("data/punch_model.json") };
    TSharedPtr<FJsonObject> Root[9];
    FString Sha[9];
    for (int32 i = 0; i < 9; ++i)
    {
        if (!LoadJsonN(Repo / Rel[i], Root[i], Sha[i]))
        {
            UE_LOG(LogTemp, Error, TEXT("UppercutCoreCondition: cannot read %s"), Rel[i]);
            return 1;
        }
    }

    // movement
    TArray<int64> BMin, BMax;
    const TSharedPtr<FJsonObject> RB = Root[0]->GetObjectField(TEXT("range_bands"));
    for (const TSharedPtr<FJsonValue>& V : RB->GetArrayField(TEXT("bands")))
    {
        const TSharedPtr<FJsonObject> B = V->AsObject();
        BMin.Add(Q(B->GetNumberField(TEXT("min_ru"))));
        BMax.Add(B->HasTypedField<EJson::Number>(TEXT("max_ru"))
                 ? Q(B->GetNumberField(TEXT("max_ru"))) : (int64)990000);
    }
    const int64 Hyst = Q(RB->GetNumberField(TEXT("hysteresis_ru")));
    const TSharedPtr<FJsonObject> Track =
        Root[0]->GetObjectField(TEXT("ring"))->GetObjectField(TEXT("track"));
    const int64 Axis = Q(Track->GetNumberField(TEXT("axis_length_ru")));
    const int64 Ropes = Q(Track->GetNumberField(TEXT("back_to_ropes_ru")));
    const int64 RopeRetreat = Q(Track->GetNumberField(TEXT("rope_retreat_multiplier")));
    const int64 MinSep = Q(Root[0]->GetObjectField(TEXT("separation"))
                           ->GetNumberField(TEXT("min_center_distance_ru")));
    int64 Stride = 0;
    const TSharedPtr<FJsonObject> Loco = Root[0]->GetObjectField(TEXT("locomotion"));
    for (const TSharedPtr<FJsonValue>& V : Loco->GetArrayField(TEXT("modes")))
    {
        const TSharedPtr<FJsonObject> M = V->AsObject();
        if (M->GetStringField(TEXT("posture_mode")) == TEXT("boxing_steps"))
        {
            Stride = Q(M->GetNumberField(TEXT("stride_length_ru")));
        }
    }
    const TSharedPtr<FJsonObject> Dir = Loco->GetObjectField(TEXT("directional"));
    const int64 DirAdvance = Q(Dir->GetNumberField(TEXT("advance_stride_multiplier")));
    const int64 DirRetreat = Q(Dir->GetNumberField(TEXT("retreat_stride_multiplier")));
    const int64 DirLateral = Q(Dir->GetNumberField(TEXT("lateral_stride_multiplier")));
    const int64 DirExhausted = Q(Dir->GetNumberField(TEXT("exhausted_stride_multiplier")));
    // condition
    const TSharedPtr<FJsonObject> StObj = Root[1]->GetObjectField(TEXT("stamina"));
    const int64 StMax = Q(StObj->GetNumberField(TEXT("max")));
    const int64 Regen = Q(StObj->GetNumberField(TEXT("regen_per_tick_idle")));
    const int64 ExhaustedQ = (int64)FMath::RoundToDouble(
        (double)StMax * StObj->GetNumberField(TEXT("exhausted_threshold_fraction")));
    const double FMaxD = StObj->GetNumberField(TEXT("max"));
    const double FRegenD = StObj->GetNumberField(TEXT("regen_per_tick_idle"));
    // pose geometry basics
    const int64 HalfDepth = Q(Root[7]->GetObjectField(TEXT("body"))->GetNumberField(TEXT("half_depth_ru")));
    const TSharedPtr<FJsonObject> GObj = Root[7]->GetObjectField(TEXT("guard"));
    const int64 PlaneOff = Q(GObj->GetNumberField(TEXT("plane_offset_ru")));
    const int64 Thr = Q(GObj->GetNumberField(TEXT("plane_interception_min_extent")));
    const int64 Retracted = Q(Root[7]->GetObjectField(TEXT("fist"))->GetNumberField(TEXT("retracted_ru")));
    // committed defense
    const int64 CdMult = Q(Root[2]->GetObjectField(TEXT("committed_defense"))
        ->GetNumberField(TEXT("guard_extent_multiplier_while_committed")));
    // the condition layer: capacities, impairment coefficients, the graded band
    int64 Cap = 0;
    for (const TSharedPtr<FJsonValue>& V : Root[1]->GetArrayField(TEXT("damage_regions")))
    {
        const TSharedPtr<FJsonObject> D = V->AsObject();
        if (D->GetStringField(TEXT("region")) == TEXT("head"))
        {
            Cap = Q(D->GetNumberField(TEXT("capacity")));
        }
    }
    const TSharedPtr<FJsonObject> ImpObj = Root[1]->GetObjectField(TEXT("impairment"));
    const int64 RegenFloor = Q(ImpObj->GetNumberField(
        TEXT("stamina_regen_multiplier_at_full_torso")));
    const int64 GuardFloor = Q(ImpObj->GetNumberField(
        TEXT("guard_extent_multiplier_at_full_arms")));
    const int64 ArmFrac = Q(ImpObj->GetNumberField(
        TEXT("arm_damage_fraction_of_blocked_force")));
    // Every landing in this probe is graded solid - the contract's named
    // simplification. Grading needs an alignment the core does not compute yet.
    int64 BandForce = 0;
    for (const TSharedPtr<FJsonValue>& V : Root[6]->GetArrayField(TEXT("quality_bands")))
    {
        const TSharedPtr<FJsonObject> B = V->AsObject();
        if (B->GetStringField(TEXT("class")) == TEXT("solid"))
        {
            BandForce = Q(B->GetNumberField(TEXT("delivered_force_fraction")));
        }
    }
    const TSharedPtr<FJsonObject> DiObj = Root[8]->GetObjectField(TEXT("delivered_impact"));
    const int64 ImpMin = Q(DiObj->GetNumberField(TEXT("min_impact_scalar")));
    const int64 ImpMax = Q(DiObj->GetNumberField(TEXT("max_impact_scalar")));
    // guard volumes by class
    TArray<TPair<FString, FString>> VolByClass;      // (class, volume id)
    for (const TSharedPtr<FJsonValue>& V :
         Root[6]->GetObjectField(TEXT("volumes"))->GetArrayField(TEXT("guard_volumes")))
    {
        const TSharedPtr<FJsonObject> GV = V->AsObject();
        VolByClass.Emplace(GV->GetStringField(TEXT("height_class")),
                           GV->GetStringField(TEXT("id")));
    }
    // the two postures
    TMap<FString, FNPosture> Postures;
    double FHoldD = 0.0;
    for (const TSharedPtr<FJsonValue>& V : Root[2]->GetArrayField(TEXT("postures")))
    {
        const TSharedPtr<FJsonObject> P = V->AsObject();
        const FString Id = P->GetStringField(TEXT("id"));
        if (Id != TEXT("high_guard") && Id != TEXT("tight_elbow")) { continue; }
        FNPosture Ps;
        Ps.Mobility = Q(P->GetNumberField(TEXT("mobility_multiplier")));
        Ps.Hold = Q(P->GetNumberField(TEXT("stamina_per_tick")));
        if (Id == TEXT("high_guard")) { FHoldD = P->GetNumberField(TEXT("stamina_per_tick")); }
        const TSharedPtr<FJsonObject> Ex = P->GetObjectField(TEXT("extents"));
        for (const TPair<FString, FString>& VC : VolByClass)
        {
            double ExtVal = 0.0;
            if (Ex->TryGetNumberField(VC.Value, ExtVal))
            {
                Ps.Ext.Add(VC.Key, Q(ExtVal));
            }
        }
        Postures.Add(Id, Ps);
    }
    // slip
    int32 SlipStartup = 0, SlipActive = 0, SlipFrames = 0;
    int64 SlipCost = 0;
    for (const TSharedPtr<FJsonValue>& V : Root[2]->GetArrayField(TEXT("evasions")))
    {
        const TSharedPtr<FJsonObject> E = V->AsObject();
        if (E->GetStringField(TEXT("id")) == TEXT("slip_lead"))
        {
            SlipActive = (int32)E->GetNumberField(TEXT("active_ticks"));
        }
    }
    // cpu
    const int32 Interval = (int32)Root[3]->GetObjectField(TEXT("reaction"))
        ->GetNumberField(TEXT("decision_interval_ticks"));
    // pose maps
    TMap<FString, FString> HeightByInteraction;
    for (const TSharedPtr<FJsonValue>& V :
         Root[7]->GetArrayField(TEXT("height_by_guard_interaction")))
    {
        const TSharedPtr<FJsonObject> E = V->AsObject();
        HeightByInteraction.Add(E->GetStringField(TEXT("guard_interaction")),
                                E->GetStringField(TEXT("height_class")));
    }
    TMap<FString, int64> ExtByMove;
    for (const TSharedPtr<FJsonValue>& V :
         Root[7]->GetObjectField(TEXT("fist"))->GetArrayField(TEXT("extension_by_move")))
    {
        const TSharedPtr<FJsonObject> E = V->AsObject();
        ExtByMove.Add(E->GetStringField(TEXT("move_id")), Q(E->GetNumberField(TEXT("extended_ru"))));
    }
    TMap<FString, TSharedPtr<FJsonObject>> Anim;
    for (const TSharedPtr<FJsonValue>& V : Root[5]->GetArrayField(TEXT("move_animations")))
    {
        const TSharedPtr<FJsonObject> A = V->AsObject();
        Anim.Add(A->GetStringField(TEXT("move_id")), A);
    }
    // delivered_impact normalizes over the PUNCH table's own stamina range - the
    // offensive categories only, so a step's cost can never move a punch's power.
    int64 CostLo = 0, CostHi = 0;
    {
        bool bFirst = true;
        const TCHAR* Offensive[6] = { TEXT("jab"), TEXT("cross"), TEXT("hook"),
                                      TEXT("uppercut"), TEXT("overhand"), TEXT("body_shot") };
        for (const TSharedPtr<FJsonValue>& V : Root[4]->GetArrayField(TEXT("moves")))
        {
            const TSharedPtr<FJsonObject> M = V->AsObject();
            FString Cat;
            if (!M->TryGetStringField(TEXT("category"), Cat)) { continue; }
            bool bOff = false;
            for (const TCHAR* O : Offensive) { bOff |= (Cat == O); }
            if (!bOff) { continue; }
            const int64 C = Q(M->GetNumberField(TEXT("stamina_cost")));
            if (bFirst) { CostLo = CostHi = C; bFirst = false; }
            CostLo = FMath::Min(CostLo, C);
            CostHi = FMath::Max(CostHi, C);
        }
    }

    // moves
    TMap<FString, FNMove> Moves;
    double FCostD = 0.0;
    const TCHAR* PunchIds[5] = { TEXT("jab_lead"), TEXT("cross_rear"), TEXT("hook_lead"),
                                 TEXT("uppercut_rear"), TEXT("body_straight_rear") };
    for (const TSharedPtr<FJsonValue>& V : Root[4]->GetArrayField(TEXT("moves")))
    {
        const TSharedPtr<FJsonObject> M = V->AsObject();
        const FString Id = M->GetStringField(TEXT("id"));
        bool bIsPunch = false;
        for (const TCHAR* P : PunchIds) { bIsPunch |= (Id == P); }
        const bool bIsStep = Id == TEXT("step_in") || Id == TEXT("step_out")
            || Id == TEXT("step_lateral");
        if (Id == TEXT("slip_lead"))
        {
            SlipCost = Q(M->GetNumberField(TEXT("stamina_cost")));
            SlipStartup = (int32)M->GetNumberField(TEXT("startup_frames"));
            SlipFrames = SlipStartup + SlipActive
                       + (int32)M->GetNumberField(TEXT("recovery_frames"));
            continue;
        }
        if (!bIsPunch && !bIsStep) { continue; }
        FNMove Mv;
        Mv.Cost = Q(M->GetNumberField(TEXT("stamina_cost")));
        if (bIsPunch)
        {
            const TSharedPtr<FJsonObject> A = Anim[Id];
            Mv.bPunch = true;
            Mv.Startup = (int32)A->GetNumberField(TEXT("startup_ticks"));
            Mv.Active = (int32)A->GetNumberField(TEXT("active_ticks"));
            Mv.Frames = Mv.Startup + Mv.Active + (int32)A->GetNumberField(TEXT("recovery_ticks"));
            Mv.Ext = ExtByMove[Id];
            Mv.Height = HeightByInteraction[M->GetStringField(TEXT("guard_interaction"))];
            Mv.Region = M->GetArrayField(TEXT("target_regions"))[0]->AsString();
            const int64 Tt = ((Mv.Cost - CostLo) * 10000) / (CostHi - CostLo);
            Mv.Impact = ImpMin + (Tt * (ImpMax - ImpMin)) / 10000;
            if (Id == TEXT("jab_lead")) { FCostD = M->GetNumberField(TEXT("stamina_cost")); }
        }
        else
        {
            Mv.Frames = (int32)M->GetNumberField(TEXT("startup_frames"))
                      + (int32)M->GetNumberField(TEXT("recovery_frames"));
        }
        Moves.Add(Id, Mv);
    }

    // ---- the loop -----------------------------------------------------------
    FString Out;
    Out += TEXT("H|phase=N\n");
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 05:10 UTC | START edit: Decision 0023 header ]
    // Decision 0023's migration reached this phase's ANALYZER and not this
    // commandlet, so the two had disagreed since 2026-08-07 - the analyzer
    // emitting the dual-hash header while this still wrote the whole-file one.
    // Nothing caught it because Phase N had no runner that re-derives the C++
    // stream; tools/engine/prove_phase.py, written 2026-08-08, found it on its
    // first run. All 1274 event rows were already identical and every old
    // H|canon_X= equalled the contract's H|canon_X_raw=, so this finishes an
    // ordered migration rather than moving a fight. The pins are generated
    // from the already-migrated analyzer, so this brings the C++ INTO
    // agreement with them and no pin moves.
    const TCHAR* ShaName[9] = { TEXT("movement"), TEXT("condition"), TEXT("guard"), TEXT("cpu"),
                                TEXT("moves"), TEXT("animation"), TEXT("collision"), TEXT("pose"),
                                TEXT("punch") };
    TArray<TPair<FString, FString>> Entries;
    for (int32 i = 0; i < 9; ++i)
    {
        Entries.Add(TPair<FString, FString>(FString(ShaName[i]), FString(Rel[i])));
    }
    {
        TArray<FString> HeaderLines;
        FString HeaderError;
        if (!UppercutCanonHeaderLines(Repo, Entries, HeaderLines, HeaderError))
        {
            UE_LOG(LogTemp, Error, TEXT("UppercutCoreCondition: header: %s"),
                   *HeaderError);
            return 1;
        }
        for (const FString& L : HeaderLines) { Out += L + TEXT("\n"); }
    }
    // [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 05:10 UTC | END edit ]
    Out += FString::Printf(TEXT("H|seed=%u\nH|ticks=%d\nH|interval=%d\nH|graded=solid\n"),
                           Seed, Ticks, Interval);

    int64 Pos[2] = { Axis / 2 - 4500, Axis / 2 + 4500 };
    int64 St[2] = { StMax, StMax };
    int32 Committed[2] = { 0, 0 };
    FString PunchMove[2];
    int32 PunchT0[2] = { 0, 0 };
    FString Posture[2] = { TEXT("high_guard"), TEXT("high_guard") };
    int32 SlipFrom[2] = { 1000000000, 1000000000 };
    int32 SlipUntil[2] = { 0, 0 };
    int32 Band = 2;
    uint32 X = Seed;
    uint64 Fnv = FnvOffset;
    int64 Rows = 0, Punches = 0, Blocked = 0, Landed = 0, Whiffed = 0, Dodged = 0;
    int64 Steps = 0, Switches = 0, Slips = 0, Held = 0, Idles = 0, Transitions = 0;
    FNCondition Cond[2];
    int64 DamageTotal = 0, Opened = 0;

    // The mean of two regions as a 0..10000 fraction of capacity. Division order
    // matters and is fixed here so the C++ and the Python cannot round apart.
    auto Frac = [&](int64 A, int64 B) { return ((A * 10000) / Cap + (B * 10000) / Cap) / 2; };
    auto RegenMult = [&](const FNCondition& C)
    {
        return 10000 - ((10000 - RegenFloor) * Frac(C.TorsoUp, C.TorsoLow)) / 10000;
    };
    auto GuardMult = [&](const FNCondition& C)
    {
        return 10000 - ((10000 - GuardFloor) * Frac(C.ArmL, C.ArmR)) / 10000;
    };
    // The defender's effective coverage in one lane, right now. This is the phase
    // in one expression: the authored extent, worn by the arms, and cut again if
    // he is caught inside his own commitment.
    auto Extent = [&](const FString& Pid, const FString& Height, int64 GMult, bool bComm)
    {
        const int64* E = Postures[Pid].Ext.Find(Height);
        int64 Ex = E ? *E : 0;
        Ex = (Ex * GMult) / 10000;
        if (bComm) { Ex = (Ex * CdMult) / 10000; }
        return Ex;
    };

    auto GC = [](const FString& P) { return P == TEXT("high_guard") ? TEXT("h") : TEXT("t"); };
    auto Emit = [&](const FString& Row)
    {
        Out += Row;
        const FTCHARToUTF8 Utf8(*Row);
        const uint8* P = (const uint8*)Utf8.Get();
        for (int32 b = 0; b < Utf8.Length(); ++b) { Fnv = (Fnv ^ P[b]) * FnvPrime; }
        ++Rows;
    };
    auto ExtAt = [&](const FNMove& Mv, int32 M)
    {
        return Retracted + ((Mv.Ext - Retracted) * M) / (Mv.Startup + Mv.Active);
    };

    static const TCHAR* ActionName[11] = { TEXT("step_in"), TEXT("step_out"),
        TEXT("step_lateral"), TEXT("jab_lead"), TEXT("cross_rear"), TEXT("hook_lead"),
        TEXT("uppercut_rear"), TEXT("body_straight_rear"), TEXT("switch_guard"),
        TEXT("slip_lead"), TEXT("idle") };

    for (int32 T = 1; T <= Ticks; ++T)
    {
        for (int32 I = 0; I < 2; ++I)
        {
            if (!PunchMove[I].IsEmpty())
            {
                const FNMove& Mv = Moves[PunchMove[I]];
                const int32 Kk = T - PunchT0[I];
                if (Kk > Mv.Startup && Kk <= Mv.Startup + Mv.Active)
                {
                    const int64 TipExt = ExtAt(Mv, Kk);
                    const int32 Opp = 1 - I;
                    int64 Tip, Plane, Surface;
                    bool bArrivedPlane, bArrivedSurface;
                    if (I == 0)
                    {
                        Tip = Pos[0] + TipExt;
                        Surface = Pos[1] - HalfDepth;
                        Plane = Surface - PlaneOff;
                        bArrivedPlane = Tip >= Plane;
                        bArrivedSurface = Tip >= Surface;
                    }
                    else
                    {
                        Tip = Pos[1] - TipExt;
                        Surface = Pos[0] + HalfDepth;
                        Plane = Surface + PlaneOff;
                        bArrivedPlane = Tip <= Plane;
                        bArrivedSurface = Tip <= Surface;
                    }
                    const bool bDCommitted = Committed[Opp] > 0;
                    const bool bDSlipping = SlipFrom[Opp] < T && T <= SlipUntil[Opp];
                    const int64 GMult = GuardMult(Cond[Opp]);
                    const int64 DExt = Extent(Posture[Opp], Mv.Height, GMult, bDCommitted);
                    const int64 FreshExt = Extent(Posture[Opp], Mv.Height, 10000, bDCommitted);
                    FString DFlags;
                    if (bDCommitted) { DFlags += TEXT("c"); }
                    if (bDSlipping) { DFlags += TEXT("s"); }
                    DFlags += GC(Posture[Opp]);
                    const TCHAR* Result = nullptr;
                    FString Region = TEXT("-");
                    int64 Force = 0;
                    if ((bArrivedPlane || bArrivedSurface) && bDSlipping
                        && Mv.Height == TEXT("high"))
                    {
                        Result = TEXT("dodged"); ++Dodged;
                    }
                    else if (bArrivedPlane && DExt >= Thr)
                    {
                        Result = TEXT("blocked"); ++Blocked;
                        // Blocking is not free. The guarding arms take a share of
                        // the impact, and that share is what wears the extent above
                        // down - canon's answer to the passive blocker, arriving
                        // through boxing rather than through a rule (Rule 4).
                        const int64 Absorbed = (Mv.Impact * ArmFrac) / 10000;
                        Cond[Opp].ArmL = FMath::Min(Cap, Cond[Opp].ArmL + Absorbed);
                        Cond[Opp].ArmR = FMath::Min(Cap, Cond[Opp].ArmR + Absorbed);
                    }
                    else if (bArrivedSurface)
                    {
                        Result = TEXT("landed"); Region = Mv.Region; ++Landed;
                        Force = (BandForce * Mv.Impact) / 10000;
                        int64& R = Cond[Opp].ByName(Region);
                        R = FMath::Min(Cap, R + Force * 6);
                        DamageTotal += Force * 6;
                        // Did this land only because the arms had worn the lane
                        // open? That is the phase's claim, counted rather than
                        // asserted.
                        if (FreshExt >= Thr && DExt < Thr) { ++Opened; }
                    }
                    else if (Kk == Mv.Startup + Mv.Active)
                    {
                        Result = TEXT("whiffed"); ++Whiffed;
                    }
                    if (Result)
                    {
                        Emit(FString::Printf(
                            TEXT("P|%d|%d|%s|%s|%s|%d|%lld|%lld|%lld|%s|%lld|%lld\n"),
                            T, I, *PunchMove[I], Result, *Region, Kk, Tip, Plane, Surface,
                            *DFlags, Force, DExt));
                        PunchMove[I].Reset();
                    }
                }
                else if (Kk > Mv.Startup + Mv.Active)
                {
                    PunchMove[I].Reset();
                }
            }
            bool bHeld = false;
            if (Committed[I] > 0)
            {
                --Committed[I];
                bHeld = true;
            }
            else
            {
                // A worked body refills slower. The multiplier scales the
                // REGENERATION only - nothing here may make holding a guard
                // cheaper than it is authored to be.
                St[I] = FMath::Min(StMax, St[I] + (Regen * RegenMult(Cond[I])) / 10000);
                St[I] = FMath::Max((int64)0, St[I] - Postures[Posture[I]].Hold);
            }
            if (T % Interval != 0) { continue; }
            Emit(FString::Printf(TEXT("C|%d|%d|%lld|%lld|%lld|%lld|%lld|%lld|%lld|%lld\n"),
                T, I, Cond[I].Head, Cond[I].Jaw, Cond[I].TorsoUp, Cond[I].TorsoLow,
                Cond[I].ArmL, Cond[I].ArmR, RegenMult(Cond[I]), GuardMult(Cond[I])));
            FString G = FString::Printf(TEXT("%s|%s"), GC(Posture[0]), GC(Posture[1]));
            if (bHeld)
            {
                ++Held;
                Emit(FString::Printf(TEXT("D|%d|%d|held|0|%lld|%lld|%lld|%d|%lld|%lld|%s|-\n"),
                    T, I, Pos[0], Pos[1], Pos[1] - Pos[0], Band, St[0], St[1], *G));
                continue;
            }
            X = LcgA * X + LcgC;
            const int32 Choice = (int32)(X % 11u);
            FString Flags;
            if (Choice == 10)
            {
                ++Idles;
            }
            else if (Choice == 8)
            {
                Posture[I] = (Posture[I] == TEXT("high_guard"))
                    ? TEXT("tight_elbow") : TEXT("high_guard");
                Committed[I] = Interval;      // contract number, named in the analyzer
                ++Switches;
                G = FString::Printf(TEXT("%s|%s"), GC(Posture[0]), GC(Posture[1]));
            }
            else if (Choice == 9)
            {
                St[I] = FMath::Max((int64)0, St[I] - SlipCost);
                Committed[I] = SlipFrames;
                SlipFrom[I] = T + SlipStartup;
                SlipUntil[I] = T + SlipStartup + SlipActive;
                ++Slips;
            }
            else if (Choice >= 3)
            {
                const FString Mid = ActionName[Choice];
                const FNMove& Mv = Moves[Mid];
                St[I] = FMath::Max((int64)0, St[I] - Mv.Cost);
                Committed[I] = Mv.Frames;
                PunchMove[I] = Mid;
                PunchT0[I] = T;
                ++Punches;
            }
            else
            {
                const FString Mid = ActionName[Choice];
                const FNMove& Mv = Moves[Mid];
                St[I] = FMath::Max((int64)0, St[I] - Mv.Cost);
                Committed[I] = Mv.Frames;
                ++Steps;
                int64 Mul = (Choice == 0) ? DirAdvance
                    : (Choice == 1) ? DirRetreat : DirLateral;
                Mul = (Mul * Postures[Posture[I]].Mobility) / 10000;
                if (St[I] < ExhaustedQ)
                {
                    Mul = (Mul * DirExhausted) / 10000;
                    Flags += TEXT("e");
                }
                if (Choice != 2)
                {
                    const int32 Toward = (I == 0) ? 1 : -1;
                    const int32 Sign = (Choice == 0) ? Toward : -Toward;
                    const bool bOnRopes = FMath::Min(Pos[I], Axis - Pos[I]) <= Ropes;
                    if (bOnRopes && Choice == 1)
                    {
                        Mul = (Mul * RopeRetreat) / 10000;
                        Flags += TEXT("r");
                    }
                    const int64 Mag = (Stride * Mul) / 10000;
                    Pos[I] = FMath::Clamp(Pos[I] + Sign * Mag, (int64)0, Axis);
                    if (Pos[1] - Pos[0] < MinSep)
                    {
                        if (I == 0) { Pos[0] = Pos[1] - MinSep; }
                        else { Pos[1] = Pos[0] + MinSep; }
                        Pos[0] = FMath::Max((int64)0, Pos[0]);
                        Pos[1] = FMath::Min(Axis, Pos[1]);
                        Flags += TEXT("m");
                    }
                    const int64 Sep = Pos[1] - Pos[0];
                    const int64 Lo = BMin[Band] - Hyst;
                    const int64 Hi = BMax[Band] + Hyst;
                    int32 Next = Band + (Sep > Hi ? 1 : 0) - (Sep < Lo ? 1 : 0);
                    Next = FMath::Clamp(Next, 0, BMin.Num() - 1);
                    if (Next != Band) { ++Transitions; }
                    Band = Next;
                }
            }
            Emit(FString::Printf(TEXT("D|%d|%d|%s|%u|%lld|%lld|%lld|%d|%lld|%lld|%s|%s\n"),
                T, I, ActionName[Choice], X, Pos[0], Pos[1], Pos[1] - Pos[0], Band,
                St[0], St[1], *G, Flags.IsEmpty() ? TEXT("-") : *Flags));
        }
    }

    // ---- the float-conformance probe: reported, not judged ------------------
    {
        double S = FMaxD;
        for (int32 Kk = 1; Kk <= 1000; ++Kk)
        {
            S = S - FCostD / 4.0;
            S = S + FRegenD * 3.0;
            S = S * 0.9995;
            S = S + FHoldD;
            if (S > FMaxD) { S = FMaxD; }
            if (Kk % 100 == 0)
            {
                uint64 Bits = 0;
                FMemory::Memcpy(&Bits, &S, sizeof(double));
                Out += FString::Printf(TEXT("F|%d|%016llx\n"), Kk, Bits);
            }
        }
    }

    Out += FString::Printf(TEXT("S|rows=%lld|punches=%lld|blocked=%lld|landed=%lld")
        TEXT("|whiffed=%lld|dodged=%lld|steps=%lld|switches=%lld|slips=%lld|held=%lld")
        TEXT("|idles=%lld|transitions=%lld|damage=%lld|opened=%lld|fnv1a64=%016llx\n"),
        Rows, Punches, Blocked, Landed, Whiffed, Dodged, Steps, Switches, Slips, Held,
        Idles, Transitions, DamageTotal, Opened, Fnv);

    IFileManager::Get().MakeDirectory(*FPaths::GetPath(OutPath), true);
    if (!FFileHelper::SaveStringToFile(Out, *OutPath,
            FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM))
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreCondition: cannot write %s"), *OutPath);
        return 1;
    }
    UE_LOG(LogTemp, Display,
           TEXT("UppercutCoreCondition: %lld rows, %lld landed, damage %lld, opened %lld -> %s"),
           Rows, Landed, DamageTotal, Opened, *OutPath);
    return 0;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 18:40 UTC | END ]
