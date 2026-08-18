// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 19:55 UTC | START ]
#include "UppercutCanonSource.h"

// SHA-256, FIPS 180-4. One copy for the module: every phase's loader hashes its
// canon with the same code, so two phases can never disagree about what a file's
// hash is.

namespace
{
    const uint32 K[64] = {
        0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
        0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
        0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
        0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
        0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
        0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
        0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
        0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2 };

    uint32 Rotr(uint32 X, uint32 N) { return (X >> N) | (X << (32 - N)); }
}

FString UppercutSha256Hex(const uint8* Data, uint64 Len)
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
    FString Hex;
    for (int32 i = 0; i < 8; ++i)
    {
        Hex += FString::Printf(TEXT("%08x"), H[i]);
    }
    return Hex;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 19:55 UTC | END ]
