// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 21:20 UTC | START ]
#include "UppercutCoreRangeCommandlet.h"

#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

// SHA-256 (FIPS 180-4), file-local like every evidence probe's.
namespace UppercutRangeSha256
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
    const int64 Unbounded = -1;

    int64 Q(double V) { return (int64)FMath::RoundToDouble(V * 10000.0); }

    // Python's // floors; C++ / truncates toward zero. Every scaled quantity in
    // this phase goes through here, so a negative delta cannot round the other
    // way in the port and silently move a fighter one unit further than the
    // contract does. `rope_retreat_multiplier` is 0.0 today and the two agree
    // by luck; this is what makes them agree on purpose.
    int64 FloorDiv(int64 A, int64 B)
    {
        int64 R = A / B;
        if ((A % B != 0) && ((A < 0) != (B < 0))) { --R; }
        return R;
    }

    struct FQMove
    {
        int32 Startup = 0, Active = 0, Frames = 0;
        int64 Ext = 0;
        bool bPunch = false;
    };

    bool LoadJsonQ(const FString& Path, TSharedPtr<FJsonObject>& OutRoot, FString& OutSha)
    {
        TArray<uint8> Bytes;
        if (!FFileHelper::LoadFileToArray(Bytes, *Path)) { return false; }
        uint8 Sha[32];
        UppercutRangeSha256::Hash(Bytes.GetData(), Bytes.Num(), Sha);
        OutSha.Reset();
        for (int32 i = 0; i < 32; ++i) { OutSha += FString::Printf(TEXT("%02x"), Sha[i]); }
        FString Text;
        FFileHelper::BufferToString(Text, Bytes.GetData(), Bytes.Num());
        const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
        return FJsonSerializer::Deserialize(Reader, OutRoot) && OutRoot.IsValid();
    }
}

int32 UUppercutCoreRangeCommandlet::Main(const FString& Params)
{
    uint32 Seed = 0; int32 Ticks = 0; FString Repo, OutPath;
    FParse::Value(*Params, TEXT("seed="), Seed);
    FParse::Value(*Params, TEXT("ticks="), Ticks);
    FParse::Value(*Params, TEXT("repo="), Repo);
    FParse::Value(*Params, TEXT("out="), OutPath);
    if (Ticks <= 0 || Repo.IsEmpty() || OutPath.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreRange: need -seed= -ticks= -repo= -out="));
        return 1;
    }

    // Exactly the four files the phase reads. A fifth would be a claim this
    // contract does not make.
    const TCHAR* Rel[4] = { TEXT("data/movement_model.json"),
                            TEXT("data/moves/generic_sandbox_moves.json"),
                            TEXT("data/animation_model.json"),
                            TEXT("data/pose_geometry.json") };
    const TCHAR* ShaName[4] = { TEXT("movement"), TEXT("moves"),
                                TEXT("animation"), TEXT("pose") };
    TSharedPtr<FJsonObject> Root[4];
    FString Sha[4];
    for (int32 i = 0; i < 4; ++i)
    {
        if (!LoadJsonQ(Repo / Rel[i], Root[i], Sha[i]))
        {
            UE_LOG(LogTemp, Error, TEXT("UppercutCoreRange: cannot read %s"), Rel[i]);
            return 1;
        }
    }

    // ---- canon into the shared integer contract ------------------------------
    TArray<FString> BKey;
    TArray<int64> BLo, BHi;
    const TSharedPtr<FJsonObject> RB = Root[0]->GetObjectField(TEXT("range_bands"));
    for (const TSharedPtr<FJsonValue>& V : RB->GetArrayField(TEXT("bands")))
    {
        const TSharedPtr<FJsonObject> B = V->AsObject();
        BKey.Add(B->GetStringField(TEXT("key")));
        BLo.Add(Q(B->GetNumberField(TEXT("min_ru"))));
        BHi.Add(B->HasTypedField<EJson::Number>(TEXT("max_ru"))
                ? Q(B->GetNumberField(TEXT("max_ru"))) : Unbounded);
    }
    const int64 Hyst = Q(RB->GetNumberField(TEXT("hysteresis_ru")));
    const TSharedPtr<FJsonObject> Loco = Root[0]->GetObjectField(TEXT("locomotion"));
    int64 Stride = 0;
    for (const TSharedPtr<FJsonValue>& V : Loco->GetArrayField(TEXT("modes")))
    {
        const TSharedPtr<FJsonObject> M = V->AsObject();
        if (M->GetStringField(TEXT("posture_mode")) == TEXT("boxing_steps"))
        {
            Stride = Q(M->GetNumberField(TEXT("stride_length_ru")));
        }
    }
    const int64 Cap = Q(Loco->GetNumberField(TEXT("max_frame_displacement_ru")));
    const TSharedPtr<FJsonObject> Dir = Loco->GetObjectField(TEXT("directional"));
    const int64 DirAdvance = Q(Dir->GetNumberField(TEXT("advance_stride_multiplier")));
    const int64 DirRetreat = Q(Dir->GetNumberField(TEXT("retreat_stride_multiplier")));
    const int64 DirLateral = Q(Dir->GetNumberField(TEXT("lateral_stride_multiplier")));
    const int64 MinSep = Q(Root[0]->GetObjectField(TEXT("separation"))
                           ->GetNumberField(TEXT("min_center_distance_ru")));
    const TSharedPtr<FJsonObject> Track =
        Root[0]->GetObjectField(TEXT("ring"))->GetObjectField(TEXT("track"));
    const int64 Axis = Q(Track->GetNumberField(TEXT("axis_length_ru")));
    const int64 Ropes = Q(Track->GetNumberField(TEXT("back_to_ropes_ru")));
    const int64 RopeRetreat = Q(Track->GetNumberField(TEXT("rope_retreat_multiplier")));

    const TSharedPtr<FJsonObject> Pose = Root[3];
    const int64 HalfDepth = Q(Pose->GetObjectField(TEXT("body"))->GetNumberField(TEXT("half_depth_ru")));
    const TSharedPtr<FJsonObject> Fist = Pose->GetObjectField(TEXT("fist"));
    const int64 Retracted = Q(Fist->GetNumberField(TEXT("retracted_ru")));
    TMap<FString, int64> ExtBy;
    for (const TSharedPtr<FJsonValue>& V : Fist->GetArrayField(TEXT("extension_by_move")))
    {
        const TSharedPtr<FJsonObject> E = V->AsObject();
        ExtBy.Add(E->GetStringField(TEXT("move_id")), Q(E->GetNumberField(TEXT("extended_ru"))));
    }

    TMap<FString, TSharedPtr<FJsonObject>> Anim;
    for (const TSharedPtr<FJsonValue>& V : Root[2]->GetArrayField(TEXT("move_animations")))
    {
        Anim.Add(V->AsObject()->GetStringField(TEXT("move_id")), V->AsObject());
    }

    // Every move that declares a band, and the band it declares. The M rows are
    // emitted from this map sorted by id, so a port that iterated a hash map
    // would be caught before the first tick.
    TMap<FString, FString> MoveBand;
    TMap<FString, TSharedPtr<FJsonObject>> Moves;
    for (const TSharedPtr<FJsonValue>& V : Root[1]->GetArrayField(TEXT("moves")))
    {
        const TSharedPtr<FJsonObject> M = V->AsObject();
        Moves.Add(M->GetStringField(TEXT("id")), M);
        FString Band;
        if (M->TryGetStringField(TEXT("range_band"), Band) && !Band.IsEmpty())
        {
            MoveBand.Add(M->GetStringField(TEXT("id")), Band);
        }
    }

    // Nine actions, drawn flat, in the contract's order. The index into this
    // array IS the LCG word modulo nine, so the order is part of the artifact.
    const TCHAR* ActionName[9] = { TEXT("idle"), TEXT("step_in"), TEXT("step_out"),
                                   TEXT("step_lateral"), TEXT("jab_lead"),
                                   TEXT("cross_rear"), TEXT("hook_lead"),
                                   TEXT("uppercut_rear"), TEXT("body_straight_rear") };
    TMap<FString, FQMove> Mv;
    for (int32 a = 1; a < 9; ++a)
    {
        const FString Id = ActionName[a];
        const TSharedPtr<FJsonObject>* M = Moves.Find(Id);
        if (!M)
        {
            UE_LOG(LogTemp, Error, TEXT("UppercutCoreRange: move %s is not in canon"), *Id);
            return 1;
        }
        FQMove D;
        if (a >= 4)
        {
            const TSharedPtr<FJsonObject>* A = Anim.Find(Id);
            if (!A)
            {
                UE_LOG(LogTemp, Error, TEXT("UppercutCoreRange: %s has no animation"), *Id);
                return 1;
            }
            D.bPunch = true;
            D.Startup = (int32)(*A)->GetNumberField(TEXT("startup_ticks"));
            D.Active = (int32)(*A)->GetNumberField(TEXT("active_ticks"));
            D.Frames = D.Startup + D.Active + (int32)(*A)->GetNumberField(TEXT("recovery_ticks"));
            const int64* E = ExtBy.Find(Id);
            D.Ext = E ? *E : 0;
        }
        else
        {
            D.Frames = (int32)(*M)->GetNumberField(TEXT("startup_frames"))
                     + (int32)(*M)->GetNumberField(TEXT("recovery_frames"));
        }
        Mv.Add(Id, D);
    }

    // ---- the canon checks, counted rather than described --------------------
    // Only the count reaches the stream (V|canon_errors), so the order these
    // run in does not matter; that they all run does.
    int32 CanonErrors = 0;
    for (int32 i = 0; i + 1 < BKey.Num(); ++i)
    {
        if (BHi[i] != BLo[i + 1]) { ++CanonErrors; }
    }
    if (BLo[0] != 0) { ++CanonErrors; }
    if (BHi.Last() != Unbounded) { ++CanonErrors; }
    int64 NarrowestBand = MAX_int64;
    for (int32 i = 0; i < BKey.Num(); ++i)
    {
        if (BHi[i] != Unbounded) { NarrowestBand = FMath::Min(NarrowestBand, BHi[i] - BLo[i]); }
    }
    if (Hyst >= NarrowestBand) { ++CanonErrors; }
    if (Stride <= 0 || Cap <= 0) { ++CanonErrors; }
    if (MinSep >= BHi[0]) { ++CanonErrors; }
    for (int32 a = 4; a < 9; ++a)
    {
        const FString Id = ActionName[a];
        if (Mv[Id].Ext <= HalfDepth) { ++CanonErrors; }
        if (Mv[Id].Active <= 0) { ++CanonErrors; }
        if (!MoveBand.Contains(Id)) { ++CanonErrors; }
    }

    // ---- the rules, one lambda each, same names as the contract -------------
    auto BandAt = [&](int64 Sep)
    {
        for (int32 i = 0; i < BKey.Num(); ++i)
        {
            if (Sep >= BLo[i] && (BHi[i] == Unbounded || Sep < BHi[i])) { return i; }
        }
        return BKey.Num() - 1;
    };
    auto ResolveBand = [&](int32 Cur, int64 Sep)
    {
        if (Cur < 0 || Cur >= BKey.Num()) { return BandAt(Sep); }
        if (Sep < BLo[Cur] - Hyst) { return BandAt(Sep); }
        if (BHi[Cur] != Unbounded && Sep >= BHi[Cur] + Hyst) { return BandAt(Sep); }
        return Cur;
    };
    auto InBand = [&](const FString& Id, int32 BandIdx)
    {
        const FString* B = MoveBand.Find(Id);
        return B != nullptr && *B == BKey[BandIdx];
    };
    auto Drain = [&](int64 Pending, int64& OutPending)
    {
        if (Pending == 0) { OutPending = 0; return (int64)0; }
        const int64 Step = FMath::Max(-Cap, FMath::Min(Cap, Pending));
        OutPending = Pending - Step;
        return Step;
    };
    auto ClampSeparation = [&](int64 Sep) { return FMath::Max(MinSep, Sep); };
    auto StepDelta = [&](const FString& Action)
    {
        if (Action == TEXT("step_in")) { return -Stride; }
        if (Action == TEXT("step_out")) { return Stride; }
        return (int64)0;
    };
    auto RopeScaled = [&](int64 Pos, int64 Delta, int64 Opponent)
    {
        if (Delta == 0) { return (int64)0; }
        const bool bRetreating = (Pos < Opponent) ? (Delta < 0) : (Delta > 0);
        if (!bRetreating) { return Delta; }
        const int64 Edge = (Delta < 0) ? Pos : Axis - Pos;
        if (Edge <= Ropes) { return FloorDiv(Delta * RopeRetreat, 10000); }
        return Delta;
    };

    // ---- the four properties, proven here rather than asserted --------------
    auto FootworkIsNotInert = [&]()
    {
        const int64 Start = Q(0.90);
        const int32 Band0 = BandAt(Start);
        int64 Sep = Start;
        int32 Cur = Band0;
        for (int32 i = 0; i < 20; ++i)
        {
            Sep = ClampSeparation(Sep + StepDelta(TEXT("step_in")));
            Cur = ResolveBand(Cur, Sep);
            if (Cur != Band0) { return true; }
        }
        return false;
    };
    auto UppercutIsReachable = [&]()
    {
        const int64 MidSep = Q(0.90);
        if (InBand(TEXT("uppercut_rear"), BandAt(MidSep))) { return false; }
        const int64 Reach = Mv[TEXT("uppercut_rear")].Ext;
        int64 Sep = MidSep;
        int32 Cur = BandAt(MidSep);
        for (int32 i = 0; i < 20; ++i)
        {
            Sep = ClampSeparation(Sep + StepDelta(TEXT("step_in")));
            Cur = ResolveBand(Cur, Sep);
            if (InBand(TEXT("uppercut_rear"), Cur) && Reach >= Sep - HalfDepth) { return true; }
        }
        return false;
    };
    auto HysteresisKillsFlicker = [&]()
    {
        for (int32 i = 0; i < BKey.Num(); ++i)
        {
            if (BHi[i] == Unbounded) { continue; }
            const int32 Here = BandAt(BHi[i] - 1);
            if (ResolveBand(Here, BHi[i] + Hyst / 2) != Here) { return false; }
        }
        return true;
    };
    auto RunningIsFinite = [&]()
    {
        int64 Pos = Axis / 2 - 4500;
        const int64 Opp = Axis / 2 + 4500;
        int64 Last = MIN_int64;
        for (int32 i = 0; i < 200; ++i)
        {
            const int64 D = RopeScaled(Pos, -Cap, Opp);
            Pos = FMath::Max((int64)0, FMath::Min(Axis, Pos + D));
            if (D == 0) { return true; }
            if (Pos == Last) { return true; }
            Last = Pos;
        }
        return false;
    };

    // ---- the header: canon before any tick ----------------------------------
    FString Out;
    Out += TEXT("H|phase=Q\n");
    for (int32 i = 0; i < 4; ++i)
    {
        Out += FString::Printf(TEXT("H|canon_%s=%s\n"), ShaName[i], *Sha[i]);
    }
    Out += FString::Printf(TEXT("H|seed=%u\nH|ticks=%d\n"), Seed, Ticks);
    for (int32 i = 0; i < BKey.Num(); ++i)
    {
        Out += FString::Printf(TEXT("B|%d|%s|%lld|%lld\n"), i, *BKey[i], BLo[i], BHi[i]);
    }
    Out += FString::Printf(
        TEXT("K|hyst=%lld|stride=%lld|cap=%lld|min_sep=%lld|axis=%lld|ropes=%lld")
        TEXT("|rope_retreat=%lld|advance=%lld|retreat=%lld|lateral=%lld")
        TEXT("|half_depth=%lld|retracted=%lld\n"),
        Hyst, Stride, Cap, MinSep, Axis, Ropes, RopeRetreat,
        DirAdvance, DirRetreat, DirLateral, HalfDepth, Retracted);
    TArray<FString> BandedMoves;
    MoveBand.GetKeys(BandedMoves);
    BandedMoves.Sort();
    for (const FString& Id : BandedMoves)
    {
        Out += FString::Printf(TEXT("M|%s|%s\n"), *Id, *MoveBand[Id]);
    }

    // ---- state --------------------------------------------------------------
    int64 Pos[2] = { Axis / 2 - 4500, Axis / 2 + 4500 };
    int64 Pending[2] = { 0, 0 };
    int32 Busy[2] = { 0, 0 };
    bool bInFlight[2] = { false, false };
    FString PunchMove[2];
    int32 PunchT0[2] = { 0, 0 };
    int32 PunchBand[2] = { 0, 0 };
    bool bPunchLegal[2] = { false, false };
    int32 Band[2] = { BandAt(Pos[1] - Pos[0]), BandAt(Pos[1] - Pos[0]) };
    uint32 X = Seed;
    uint64 Fnv = FnvOffset;
    int64 Rows = 0, Decisions = 0, Idles = 0, Steps = 0, Laterals = 0, Punches = 0;
    int64 Landed = 0, WhiffBand = 0, WhiffReach = 0, Transitions = 0;
    int64 Roped = 0, Clamped = 0, Applied = 0;
    int64 SepMin = Pos[1] - Pos[0], SepMax = Pos[1] - Pos[0];

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
            // ---- 1. deliver movement already owed, at most the cap ----------
            if (Pending[i] != 0)
            {
                int64 NextPending = 0;
                const int64 Step = Drain(Pending[i], NextPending);
                Pending[i] = NextPending;
                const int64 Before = Pos[i];
                Pos[i] = FMath::Max((int64)0, FMath::Min(Axis, Pos[i] + Step));
                FString Flags;
                if (Pos[1] - Pos[0] < MinSep)
                {
                    if (i == 0) { Pos[0] = Pos[1] - MinSep; }
                    else { Pos[1] = Pos[0] + MinSep; }
                    Pos[0] = FMath::Max((int64)0, Pos[0]);
                    Pos[1] = FMath::Min(Axis, Pos[1]);
                    // The rest of the stride is refused, not banked.
                    Pending[i] = 0;
                    Flags += TEXT("m");
                    ++Clamped;
                }
                const int64 Moved = Pos[i] - Before;
                if (Moved != 0) { ++Applied; }
                const int64 Sep = Pos[1] - Pos[0];
                SepMin = FMath::Min(SepMin, Sep);
                SepMax = FMath::Max(SepMax, Sep);
                Emit(FString::Printf(TEXT("X|%d|%d|%lld|%lld|%lld|%lld|%lld|%s\n"),
                                     T, i, Moved, Pos[0], Pos[1], Sep, Pending[i],
                                     Flags.IsEmpty() ? TEXT("-") : *Flags));
                for (int32 j = 0; j < 2; ++j)
                {
                    const int32 Nb = ResolveBand(Band[j], Sep);
                    if (Nb != Band[j])
                    {
                        Emit(FString::Printf(TEXT("R|%d|%d|%s|%s|%lld\n"),
                                             T, j, *BKey[Band[j]], *BKey[Nb], Sep));
                        Band[j] = Nb;
                        ++Transitions;
                    }
                }
            }

            // ---- 2. a punch in flight ---------------------------------------
            if (bInFlight[i])
            {
                const FQMove& M = Mv[PunchMove[i]];
                const int32 Kk = T - PunchT0[i];
                const int32 Span = M.Startup + M.Active;
                if (Kk > M.Startup && Kk <= Span)
                {
                    const int64 TipExt = Retracted + FloorDiv((M.Ext - Retracted) * Kk, Span);
                    int64 Tip = 0, Surface = 0;
                    bool bArrived = false;
                    if (i == 0)
                    {
                        Tip = Pos[0] + TipExt;
                        Surface = Pos[1] - HalfDepth;
                        bArrived = Tip >= Surface;
                    }
                    else
                    {
                        Tip = Pos[1] - TipExt;
                        Surface = Pos[0] + HalfDepth;
                        bArrived = Tip <= Surface;
                    }
                    const TCHAR* Result = nullptr;
                    const TCHAR* Reason = TEXT("-");
                    if (bArrived && bPunchLegal[i])
                    {
                        Result = TEXT("landed");
                        ++Landed;
                    }
                    else if (Kk == Span)
                    {
                        Result = TEXT("whiffed");
                        // The band is tested first on purpose: a punch from the
                        // wrong band is refused even when the fist arrived.
                        Reason = bPunchLegal[i] ? TEXT("reach") : TEXT("band");
                        if (bPunchLegal[i]) { ++WhiffReach; } else { ++WhiffBand; }
                    }
                    if (Result != nullptr)
                    {
                        Emit(FString::Printf(
                            TEXT("P|%d|%d|%s|%s|%s|%d|%lld|%lld|%s|%d\n"),
                            T, i, *PunchMove[i], Result, Reason, Kk, Tip, Surface,
                            *BKey[PunchBand[i]], bPunchLegal[i] ? 1 : 0));
                        bInFlight[i] = false;
                    }
                }
                else if (Kk > Span)
                {
                    bInFlight[i] = false;
                }
            }

            // ---- 3. commitment ----------------------------------------------
            // A step keeps draining while its owner is committed: that is what
            // makes "entering is when counters land" true rather than stated.
            if (Busy[i] > 0)
            {
                --Busy[i];
                continue;
            }

            // ---- 4. one decision --------------------------------------------
            X = LcgA * X + LcgC;          // uint32 wraps, which IS mod 2^32
            const int32 Choice = (int32)(X % 9u);
            const FString Action = ActionName[Choice];
            ++Decisions;
            FString Mark = TEXT("-");
            if (Choice == 0)
            {
                ++Idles;
            }
            else if (Choice >= 4)
            {
                Busy[i] = Mv[Action].Frames;
                const bool bLegal = InBand(Action, Band[i]);
                bInFlight[i] = true;
                PunchMove[i] = Action;
                PunchT0[i] = T;
                PunchBand[i] = Band[i];
                bPunchLegal[i] = bLegal;
                ++Punches;
                Mark = bLegal ? TEXT("1") : TEXT("0");
            }
            else
            {
                Busy[i] = Mv[Action].Frames;
                ++Steps;
                if (Choice == 3)
                {
                    // Knowingly inert on one axis, and marked in the row so a
                    // reader never has to infer it from a zero.
                    ++Laterals;
                    Mark = TEXT("l");
                }
                else
                {
                    const int64 Toward = (i == 0) ? 1 : -1;
                    const int64 Sign = (Choice == 1) ? Toward : -Toward;
                    const int64 Mul = (Choice == 1) ? DirAdvance : DirRetreat;
                    const int64 Delta = Sign * FloorDiv(Stride * Mul, 10000);
                    const int64 Scaled = RopeScaled(Pos[i], Delta, Pos[1 - i]);
                    if (Scaled != Delta) { ++Roped; Mark = TEXT("r"); }
                    Pending[i] = Scaled;
                }
            }
            Emit(FString::Printf(TEXT("D|%d|%d|%s|%u|%lld|%lld|%lld|%s|%lld|%s\n"),
                                 T, i, *Action, X, Pos[0], Pos[1], Pos[1] - Pos[0],
                                 *BKey[Band[i]], Pending[i], *Mark));
        }
    }

    // ---- the properties, inside the hash ------------------------------------
    Emit(FString::Printf(TEXT("V|footwork_is_not_inert|%d\n"), FootworkIsNotInert() ? 1 : 0));
    Emit(FString::Printf(TEXT("V|uppercut_is_reachable|%d\n"), UppercutIsReachable() ? 1 : 0));
    Emit(FString::Printf(TEXT("V|hysteresis_kills_flicker|%d\n"), HysteresisKillsFlicker() ? 1 : 0));
    Emit(FString::Printf(TEXT("V|running_is_finite|%d\n"), RunningIsFinite() ? 1 : 0));
    Emit(FString::Printf(TEXT("V|canon_errors|%d\n"), CanonErrors));

    Out += FString::Printf(
        TEXT("S|rows=%lld|decisions=%lld|idles=%lld|steps=%lld|laterals=%lld")
        TEXT("|punches=%lld|landed=%lld|whiff_band=%lld|whiff_reach=%lld")
        TEXT("|transitions=%lld|roped=%lld|clamped=%lld|applied=%lld")
        TEXT("|sep_min=%lld|sep_max=%lld|fnv1a64=%016llx\n"),
        Rows, Decisions, Idles, Steps, Laterals, Punches, Landed, WhiffBand,
        WhiffReach, Transitions, Roped, Clamped, Applied, SepMin, SepMax, Fnv);

    IFileManager::Get().MakeDirectory(*FPaths::GetPath(OutPath), true);
    if (!FFileHelper::SaveStringToFile(Out, *OutPath,
            FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM))
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreRange: cannot write %s"), *OutPath);
        return 1;
    }
    UE_LOG(LogTemp, Display, TEXT("UppercutCoreRange: %lld rows, fnv1a64=%016llx"), Rows, Fnv);
    return 0;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 21:20 UTC | END ]
