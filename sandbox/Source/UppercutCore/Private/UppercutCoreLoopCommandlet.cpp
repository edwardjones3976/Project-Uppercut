// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 05:10 UTC | START ]
#include "UppercutCoreLoopCommandlet.h"

#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

// SHA-256 (FIPS 180-4), file-local exactly like the Phase H probe's - the
// hash the stream reports is defined by this file and the analyzer alone.
namespace UppercutLoopSha256
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

    struct FLoopCanon
    {
        FString Sha[5];               // movement, condition, guard, cpu, moves
        TArray<int64> BMin, BMax;
        int64 Hyst = 0, Axis = 0, Ropes = 0, RopeRetreat = 0, MinSep = 0, Stride = 0;
        int64 DirAdvance = 0, DirRetreat = 0, DirLateral = 0, DirExhausted = 0;
        int64 Mobility = 0, Hold = 0, StMax = 0, Regen = 0, ExhaustedQ = 0;
        int32 Interval = 0, JabBand = -1;
        struct FMove { int64 Cost = 0; int32 Frames = 0; };
        FMove Jab, StepIn, StepOut, StepLateral;
        double FCost = 0, FRegen = 0, FMax = 0, FHold = 0;
    };

    bool LoadJson(const FString& Path, TSharedPtr<FJsonObject>& OutRoot, FString& OutSha)
    {
        TArray<uint8> Bytes;
        if (!FFileHelper::LoadFileToArray(Bytes, *Path)) { return false; }
        uint8 Sha[32];
        UppercutLoopSha256::Hash(Bytes.GetData(), Bytes.Num(), Sha);
        OutSha.Reset();
        for (int32 i = 0; i < 32; ++i) { OutSha += FString::Printf(TEXT("%02x"), Sha[i]); }
        FString Text;
        FFileHelper::BufferToString(Text, Bytes.GetData(), Bytes.Num());
        const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
        return FJsonSerializer::Deserialize(Reader, OutRoot) && OutRoot.IsValid();
    }
}

int32 UUppercutCoreLoopCommandlet::Main(const FString& Params)
{
    uint32 Seed = 0; int32 Ticks = 0; FString Repo, OutPath;
    FParse::Value(*Params, TEXT("seed="), Seed);
    FParse::Value(*Params, TEXT("ticks="), Ticks);
    FParse::Value(*Params, TEXT("repo="), Repo);
    FParse::Value(*Params, TEXT("out="), OutPath);
    if (Ticks <= 0 || Repo.IsEmpty() || OutPath.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreLoop: need -seed= -ticks= -repo= -out="));
        return 1;
    }

    const TCHAR* Rel[5] = { TEXT("data/movement_model.json"), TEXT("data/condition_model.json"),
                            TEXT("data/guard_evasion_model.json"), TEXT("data/cpu_decision_model.json"),
                            TEXT("data/moves/generic_sandbox_moves.json") };
    TSharedPtr<FJsonObject> Root[5];
    FLoopCanon C;
    for (int32 i = 0; i < 5; ++i)
    {
        if (!LoadJson(Repo / Rel[i], Root[i], C.Sha[i]))
        {
            UE_LOG(LogTemp, Error, TEXT("UppercutCoreLoop: cannot read %s"), Rel[i]);
            return 1;
        }
    }

    // movement
    const TSharedPtr<FJsonObject> RB = Root[0]->GetObjectField(TEXT("range_bands"));
    FString JabBandKey;
    {
        const TArray<TSharedPtr<FJsonValue>> Bands = RB->GetArrayField(TEXT("bands"));
        for (const TSharedPtr<FJsonValue>& V : Bands)
        {
            const TSharedPtr<FJsonObject> B = V->AsObject();
            C.BMin.Add(Q(B->GetNumberField(TEXT("min_ru"))));
            C.BMax.Add(B->HasTypedField<EJson::Number>(TEXT("max_ru"))
                       ? Q(B->GetNumberField(TEXT("max_ru"))) : (int64)990000);
        }
        C.Hyst = Q(RB->GetNumberField(TEXT("hysteresis_ru")));
        const TSharedPtr<FJsonObject> Track =
            Root[0]->GetObjectField(TEXT("ring"))->GetObjectField(TEXT("track"));
        C.Axis = Q(Track->GetNumberField(TEXT("axis_length_ru")));
        C.Ropes = Q(Track->GetNumberField(TEXT("back_to_ropes_ru")));
        C.RopeRetreat = Q(Track->GetNumberField(TEXT("rope_retreat_multiplier")));
        C.MinSep = Q(Root[0]->GetObjectField(TEXT("separation"))
                     ->GetNumberField(TEXT("min_center_distance_ru")));
        const TSharedPtr<FJsonObject> Loco = Root[0]->GetObjectField(TEXT("locomotion"));
        for (const TSharedPtr<FJsonValue>& V : Loco->GetArrayField(TEXT("modes")))
        {
            const TSharedPtr<FJsonObject> M = V->AsObject();
            if (M->GetStringField(TEXT("posture_mode")) == TEXT("boxing_steps"))
            {
                C.Stride = Q(M->GetNumberField(TEXT("stride_length_ru")));
            }
        }
        const TSharedPtr<FJsonObject> Dir = Loco->GetObjectField(TEXT("directional"));
        C.DirAdvance = Q(Dir->GetNumberField(TEXT("advance_stride_multiplier")));
        C.DirRetreat = Q(Dir->GetNumberField(TEXT("retreat_stride_multiplier")));
        C.DirLateral = Q(Dir->GetNumberField(TEXT("lateral_stride_multiplier")));
        C.DirExhausted = Q(Dir->GetNumberField(TEXT("exhausted_stride_multiplier")));
    }
    // condition
    {
        const TSharedPtr<FJsonObject> St = Root[1]->GetObjectField(TEXT("stamina"));
        C.StMax = Q(St->GetNumberField(TEXT("max")));
        C.Regen = Q(St->GetNumberField(TEXT("regen_per_tick_idle")));
        C.ExhaustedQ = (int64)FMath::RoundToDouble(
            (double)C.StMax * St->GetNumberField(TEXT("exhausted_threshold_fraction")));
        C.FMax = St->GetNumberField(TEXT("max"));
        C.FRegen = St->GetNumberField(TEXT("regen_per_tick_idle"));
    }
    // guard: high_guard
    for (const TSharedPtr<FJsonValue>& V : Root[2]->GetArrayField(TEXT("postures")))
    {
        const TSharedPtr<FJsonObject> P = V->AsObject();
        if (P->GetStringField(TEXT("id")) == TEXT("high_guard"))
        {
            C.Mobility = Q(P->GetNumberField(TEXT("mobility_multiplier")));
            C.Hold = Q(P->GetNumberField(TEXT("stamina_per_tick")));
            C.FHold = P->GetNumberField(TEXT("stamina_per_tick"));
        }
    }
    // cpu
    C.Interval = (int32)Root[3]->GetObjectField(TEXT("reaction"))
        ->GetNumberField(TEXT("decision_interval_ticks"));
    // moves
    for (const TSharedPtr<FJsonValue>& V : Root[4]->GetArrayField(TEXT("moves")))
    {
        const TSharedPtr<FJsonObject> M = V->AsObject();
        const FString Id = M->GetStringField(TEXT("id"));
        FLoopCanon::FMove Mv;
        Mv.Cost = Q(M->GetNumberField(TEXT("stamina_cost")));
        Mv.Frames = (int32)M->GetNumberField(TEXT("startup_frames"))
                  + (int32)M->GetNumberField(TEXT("recovery_frames"));
        if (Id == TEXT("jab_lead"))
        {
            C.Jab = Mv;
            C.FCost = M->GetNumberField(TEXT("stamina_cost"));
            const FString BandKey = M->GetStringField(TEXT("range_band"));
            const TArray<TSharedPtr<FJsonValue>> Bands = RB->GetArrayField(TEXT("bands"));
            for (int32 bi = 0; bi < Bands.Num(); ++bi)
            {
                if (Bands[bi]->AsObject()->GetStringField(TEXT("key")) == BandKey) { C.JabBand = bi; }
            }
        }
        else if (Id == TEXT("step_in")) { C.StepIn = Mv; }
        else if (Id == TEXT("step_out")) { C.StepOut = Mv; }
        else if (Id == TEXT("step_lateral")) { C.StepLateral = Mv; }
    }

    // ---- the loop, exactly as the contract computes it ----------------------
    FString Out;
    Out += TEXT("H|phase=I\n");
    const TCHAR* ShaName[5] = { TEXT("movement"), TEXT("condition"), TEXT("guard"),
                                TEXT("cpu"), TEXT("moves") };
    for (int32 i = 0; i < 5; ++i)
    {
        Out += FString::Printf(TEXT("H|canon_%s=%s\n"), ShaName[i], *C.Sha[i]);
    }
    Out += FString::Printf(TEXT("H|seed=%u\nH|ticks=%d\nH|interval=%d\n"), Seed, Ticks, C.Interval);

    int64 Pos[2] = { C.Axis / 2 - 4500, C.Axis / 2 + 4500 };
    int64 St[2] = { C.StMax, C.StMax };
    int32 Committed[2] = { 0, 0 };
    int32 Band = 2;
    uint32 X = Seed;
    uint64 Fnv = FnvOffset;
    int64 Rows = 0, Delivered = 0, Whiffs = 0, Steps = 0, Held = 0, Idles = 0, Transitions = 0;

    auto EmitD = [&](const FString& Row)
    {
        Out += Row;
        const FTCHARToUTF8 Utf8(*Row);
        const uint8* P = (const uint8*)Utf8.Get();
        for (int32 b = 0; b < Utf8.Length(); ++b) { Fnv = (Fnv ^ P[b]) * FnvPrime; }
        ++Rows;
    };

    for (int32 T = 1; T <= Ticks; ++T)
    {
        for (int32 I = 0; I < 2; ++I)
        {
            bool bHeld = false;
            if (Committed[I] > 0)
            {
                --Committed[I];
                bHeld = true;
            }
            else
            {
                St[I] = FMath::Min(C.StMax, St[I] + C.Regen);
                St[I] = FMath::Max((int64)0, St[I] - C.Hold);
            }
            if (T % C.Interval != 0) { continue; }
            if (bHeld)
            {
                ++Held;
                EmitD(FString::Printf(TEXT("D|%d|%d|held|0|%lld|%lld|%lld|%d|%lld|%lld|-\n"),
                    T, I, Pos[0], Pos[1], Pos[1] - Pos[0], Band, St[0], St[1]));
                continue;
            }
            X = LcgA * X + LcgC;
            const int32 Choice = (int32)(X % 5u);
            const TCHAR* ActionName[5] = { TEXT("step_in"), TEXT("step_out"),
                TEXT("step_lateral"), TEXT("jab_lead"), TEXT("idle") };
            FString Flags;
            if (Choice == 4)
            {
                ++Idles;
            }
            else if (Choice == 3)
            {
                St[I] = FMath::Max((int64)0, St[I] - C.Jab.Cost);
                Committed[I] = C.Jab.Frames;
                if (Band == C.JabBand) { ++Delivered; }
                else { ++Whiffs; Flags += TEXT("w"); }
            }
            else
            {
                const FLoopCanon::FMove& Mv = (Choice == 0) ? C.StepIn
                    : (Choice == 1) ? C.StepOut : C.StepLateral;
                St[I] = FMath::Max((int64)0, St[I] - Mv.Cost);
                Committed[I] = Mv.Frames;
                ++Steps;
                int64 Mul = (Choice == 0) ? C.DirAdvance
                    : (Choice == 1) ? C.DirRetreat : C.DirLateral;
                Mul = (Mul * C.Mobility) / 10000;
                if (St[I] < C.ExhaustedQ)
                {
                    Mul = (Mul * C.DirExhausted) / 10000;
                    Flags += TEXT("e");
                }
                if (Choice != 2)
                {
                    const int32 Toward = (I == 0) ? 1 : -1;
                    const int32 Sign = (Choice == 0) ? Toward : -Toward;
                    const bool bOnRopes = FMath::Min(Pos[I], C.Axis - Pos[I]) <= C.Ropes;
                    if (bOnRopes && Choice == 1)
                    {
                        Mul = (Mul * C.RopeRetreat) / 10000;
                        Flags += TEXT("r");
                    }
                    const int64 Mag = (C.Stride * Mul) / 10000;
                    Pos[I] = FMath::Clamp(Pos[I] + Sign * Mag, (int64)0, C.Axis);
                    if (Pos[1] - Pos[0] < C.MinSep)
                    {
                        if (I == 0) { Pos[0] = Pos[1] - C.MinSep; }
                        else { Pos[1] = Pos[0] + C.MinSep; }
                        Pos[0] = FMath::Max((int64)0, Pos[0]);
                        Pos[1] = FMath::Min(C.Axis, Pos[1]);
                        Flags += TEXT("m");
                    }
                    const int64 Sep = Pos[1] - Pos[0];
                    const int64 Lo = C.BMin[Band] - C.Hyst;
                    const int64 Hi = C.BMax[Band] + C.Hyst;
                    int32 Next = Band + (Sep > Hi ? 1 : 0) - (Sep < Lo ? 1 : 0);
                    Next = FMath::Clamp(Next, 0, C.BMin.Num() - 1);
                    if (Next != Band) { ++Transitions; }
                    Band = Next;
                }
            }
            EmitD(FString::Printf(TEXT("D|%d|%d|%s|%u|%lld|%lld|%lld|%d|%lld|%lld|%s\n"),
                T, I, ActionName[Choice], X, Pos[0], Pos[1], Pos[1] - Pos[0], Band,
                St[0], St[1], Flags.IsEmpty() ? TEXT("-") : *Flags));
        }
    }

    // ---- the float-conformance probe: reported, not judged ------------------
    {
        double S = C.FMax;
        for (int32 K = 1; K <= 1000; ++K)
        {
            S = S - C.FCost / 4.0;
            S = S + C.FRegen * 3.0;
            S = S * 0.9995;
            S = S + C.FHold;
            if (S > C.FMax) { S = C.FMax; }
            if (K % 100 == 0)
            {
                uint64 Bits = 0;
                FMemory::Memcpy(&Bits, &S, sizeof(double));
                Out += FString::Printf(TEXT("F|%d|%016llx\n"), K, Bits);
            }
        }
    }

    Out += FString::Printf(TEXT("S|rows=%lld|delivered=%lld|whiffs=%lld|steps=%lld|held=%lld")
        TEXT("|idles=%lld|transitions=%lld|fnv1a64=%016llx\n"),
        Rows, Delivered, Whiffs, Steps, Held, Idles, Transitions, Fnv);

    IFileManager::Get().MakeDirectory(*FPaths::GetPath(OutPath), true);
    if (!FFileHelper::SaveStringToFile(Out, *OutPath,
            FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM))
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreLoop: cannot write %s"), *OutPath);
        return 1;
    }
    UE_LOG(LogTemp, Display, TEXT("UppercutCoreLoop: %lld rows, %lld transitions -> %s"),
           Rows, Transitions, *OutPath);
    return 0;
}
// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 05:10 UTC | END ]
