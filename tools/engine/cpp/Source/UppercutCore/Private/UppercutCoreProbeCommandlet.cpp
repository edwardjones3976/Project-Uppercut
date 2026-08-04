// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 03:42 UTC | START ]
#include "UppercutCoreProbeCommandlet.h"

#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

// ---- SHA-256, self-contained ------------------------------------------------
// Implemented inline rather than through an engine wrapper so the hash the
// stream reports is defined by this file and the Python analyzer alone -
// FIPS 180-4, the same bytes hashlib.sha256 sees.
namespace UppercutSha256
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

// ---- the contract's constants (tools/engine/analyze_core_scaffold.py) ------
static const uint32 LcgA = 1664525u;
static const uint32 LcgC = 1013904223u;
static const uint32 DistMod = 60001u;      // 0..6.0000 ru, 1e-4 fixed point
static const int32  StartBand = 2;         // same opening band as the reference
static const uint64 FnvOffset = 14695981039346656037ull;
static const uint64 FnvPrime = 1099511628211ull;

int32 UUppercutCoreProbeCommandlet::Main(const FString& Params)
{
    uint32 Seed = 0; int32 Steps = 0; FString CanonPath, OutPath;
    FParse::Value(*Params, TEXT("seed="), Seed);
    FParse::Value(*Params, TEXT("steps="), Steps);
    FParse::Value(*Params, TEXT("canon="), CanonPath);
    FParse::Value(*Params, TEXT("out="), OutPath);
    if (Steps <= 0 || CanonPath.IsEmpty() || OutPath.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreProbe: need -seed= -steps= -canon= -out="));
        return 1;
    }

    // Canon in: exact bytes, hashed exactly as the analyzer hashes them.
    TArray<uint8> CanonBytes;
    if (!FFileHelper::LoadFileToArray(CanonBytes, *CanonPath))
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreProbe: cannot read canon %s"), *CanonPath);
        return 1;
    }
    uint8 Sha[32];
    UppercutSha256::Hash(CanonBytes.GetData(), CanonBytes.Num(), Sha);
    FString ShaHex;
    for (int32 i = 0; i < 32; ++i) { ShaHex += FString::Printf(TEXT("%02x"), Sha[i]); }

    FString CanonText;
    FFileHelper::BufferToString(CanonText, CanonBytes.GetData(), CanonBytes.Num());
    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(CanonText);
    if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreProbe: canon is not JSON"));
        return 1;
    }
    const TSharedPtr<FJsonObject> RangeBands = Root->GetObjectField(TEXT("range_bands"));
    const TArray<TSharedPtr<FJsonValue>> Bands = RangeBands->GetArrayField(TEXT("bands"));
    // Quantize authored bounds to 1e-4 ru integers. Values are authored at
    // <= 3 decimals, where C++ and Python IEEE doubles agree exactly; a null
    // max_ru is open-ended and quantizes to 99 ru, per the contract.
    TArray<int64> BMinQ, BMaxQ;
    for (const TSharedPtr<FJsonValue>& V : Bands)
    {
        const TSharedPtr<FJsonObject> B = V->AsObject();
        BMinQ.Add((int64)FMath::RoundToDouble(B->GetNumberField(TEXT("min_ru")) * 10000.0));
        double MaxRu = 99.0;
        if (B->HasTypedField<EJson::Number>(TEXT("max_ru")))
        {
            MaxRu = B->GetNumberField(TEXT("max_ru"));
        }
        BMaxQ.Add((int64)FMath::RoundToDouble(MaxRu * 10000.0));
    }
    const int64 HystQ = (int64)FMath::RoundToDouble(
        RangeBands->GetNumberField(TEXT("hysteresis_ru")) * 10000.0);

    // Deterministic integer walk: the Phase D hysteresis rule, third
    // implementation, same canon. No engine RNG, no floats, no wall clock.
    FString OutStr;
    OutStr += FString::Printf(TEXT("H|canon_sha256=%s\n"), *ShaHex);
    OutStr += FString::Printf(TEXT("H|seed=%u\n"), Seed);
    OutStr += FString::Printf(TEXT("H|steps=%d\n"), Steps);
    uint32 X = Seed;
    int32 Band = StartBand;
    int32 Transitions = 0;
    uint64 Fnv = FnvOffset;
    for (int32 i = 0; i < Steps; ++i)
    {
        X = LcgA * X + LcgC;                       // uint32 wraparound is the mod
        const int64 DistQ = (int64)(X % DistMod);
        const int64 Lo = BMinQ[Band] - HystQ;
        const int64 Hi = BMaxQ[Band] + HystQ;
        int32 Next = Band + (DistQ > Hi ? 1 : 0) - (DistQ < Lo ? 1 : 0);
        Next = FMath::Clamp(Next, 0, BMinQ.Num() - 1);
        if (Next != Band) { ++Transitions; }
        Band = Next;
        const FString Row = FString::Printf(TEXT("R|%d|%u|%lld|%d\n"), i, X, DistQ, Band);
        OutStr += Row;
        // FNV-1a 64 over the row's UTF-8 bytes, newline included. Rows are
        // pure ASCII, so the TCHAR->UTF-8 mapping is the identity.
        const FTCHARToUTF8 Utf8(*Row);
        const uint8* P = (const uint8*)Utf8.Get();
        for (int32 b = 0; b < Utf8.Length(); ++b)
        {
            Fnv = (Fnv ^ P[b]) * FnvPrime;         // uint64 wraparound is the mod
        }
    }
    OutStr += FString::Printf(TEXT("S|rows=%d|transitions=%d|fnv1a64=%016llx\n"),
                              Steps, Transitions, Fnv);

    IFileManager::Get().MakeDirectory(*FPaths::GetPath(OutPath), true);
    if (!FFileHelper::SaveStringToFile(OutStr, *OutPath,
            FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM))
    {
        UE_LOG(LogTemp, Error, TEXT("UppercutCoreProbe: cannot write %s"), *OutPath);
        return 1;
    }
    UE_LOG(LogTemp, Display, TEXT("UppercutCoreProbe: %d rows, %d transitions -> %s"),
           Steps, Transitions, *OutPath);
    return 0;
}
// [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 03:42 UTC | END ]
