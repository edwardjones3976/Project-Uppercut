// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 03:20 UTC | START ]
#include "UppercutCanonHash.h"

#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "UppercutCanonSource.h"

const TCHAR* UppercutCanonicalizerVersion = TEXT("uppercut-semantic-json-v1");
const TCHAR* UppercutHashContractVersion = TEXT("uppercut-hash-contract-v1");

namespace UppercutCanon
{
    // 2^53. Beyond this an integer is not exactly representable as a double, so
    // the two implementations could disagree about what the file even says.
    static const double MaxExactInt = 9007199254740992.0;

    enum class EType : uint8 { Null, Bool, Number, String, Array, Object };

    struct FValue
    {
        EType Type = EType::Null;
        bool bBool = false;
        double Number = 0.0;
        FString Str;
        TArray<FValue> Items;                       // array, order preserved
        TArray<TPair<FString, FValue>> Members;     // object, insertion order
    };

    // ---------------------------------------------------------------- utf8 --

    static void AppendUtf8(TArray<uint8>& Out, const FString& S)
    {
        FTCHARToUTF8 Conv(*S);
        const uint8* P = (const uint8*)Conv.Get();
        Out.Append(P, Conv.Length());
    }

    static TArray<uint8> Utf8Of(const FString& S)
    {
        TArray<uint8> Out;
        AppendUtf8(Out, S);
        return Out;
    }

    // Sorting keys by UTF-8 BYTES, not by FString. UE compares UTF-16 code
    // units; for characters outside the BMP that ordering differs from UTF-8
    // byte order, and canon is allowed to contain any string.
    // FString::operator== IS CASE-INSENSITIVE IN UNREAL. Every key comparison
    // in this file must therefore be explicit, or "A" and "a" become the same
    // canon field. The cross-language vectors caught this on their first run:
    // the key_sorting case contains both, and the C++ side rejected it as a
    // duplicate key. Left implicit, the same bug would also have let an
    // exclusion pointer spelled `/guard/Note` drop the real `/guard/note`.
    static bool KeyEquals(const FString& A, const FString& B)
    {
        return A.Equals(B, ESearchCase::CaseSensitive);
    }

    static bool Utf8Less(const FString& A, const FString& B)
    {
        const TArray<uint8> X = Utf8Of(A);
        const TArray<uint8> Y = Utf8Of(B);
        const int32 N = FMath::Min(X.Num(), Y.Num());
        for (int32 i = 0; i < N; ++i)
        {
            if (X[i] != Y[i]) { return X[i] < Y[i]; }
        }
        return X.Num() < Y.Num();
    }

    // --------------------------------------------------------------- parser --

    struct FParser
    {
        const TCHAR* P = nullptr;
        const TCHAR* End = nullptr;
        FString Error;

        bool Fail(const FString& Why) { if (Error.IsEmpty()) { Error = Why; } return false; }

        void Space()
        {
            while (P < End && (*P == ' ' || *P == '\t' || *P == '\n' || *P == '\r')) { ++P; }
        }

        bool Literal(const TCHAR* Word)
        {
            const TCHAR* Q = Word;
            while (*Q) { if (P >= End || *P != *Q) { return false; } ++P; ++Q; }
            return true;
        }

        bool ParseValue(FValue& Out);

        bool ParseString(FString& Out)
        {
            if (P >= End || *P != TEXT('"')) { return Fail(TEXT("expected a string")); }
            ++P;
            FString Acc;
            while (true)
            {
                if (P >= End) { return Fail(TEXT("unterminated string")); }
                const TCHAR C = *P;
                if (C == TEXT('"')) { ++P; Out = Acc; return true; }
                if (C == TEXT('\\'))
                {
                    ++P;
                    if (P >= End) { return Fail(TEXT("unterminated escape")); }
                    const TCHAR E = *P++;
                    switch (E)
                    {
                    case TEXT('"'):  Acc.AppendChar(TEXT('"')); break;
                    case TEXT('\\'): Acc.AppendChar(TEXT('\\')); break;
                    case TEXT('/'):  Acc.AppendChar(TEXT('/')); break;
                    case TEXT('b'):  Acc.AppendChar(TEXT('\b')); break;
                    case TEXT('f'):  Acc.AppendChar(TEXT('\f')); break;
                    case TEXT('n'):  Acc.AppendChar(TEXT('\n')); break;
                    case TEXT('r'):  Acc.AppendChar(TEXT('\r')); break;
                    case TEXT('t'):  Acc.AppendChar(TEXT('\t')); break;
                    case TEXT('u'):
                    {
                        if (P + 4 > End) { return Fail(TEXT("truncated \\u escape")); }
                        uint32 Code = 0;
                        for (int32 i = 0; i < 4; ++i)
                        {
                            const TCHAR H = *P++;
                            Code <<= 4;
                            if (H >= TEXT('0') && H <= TEXT('9')) { Code |= (uint32)(H - TEXT('0')); }
                            else if (H >= TEXT('a') && H <= TEXT('f')) { Code |= (uint32)(H - TEXT('a') + 10); }
                            else if (H >= TEXT('A') && H <= TEXT('F')) { Code |= (uint32)(H - TEXT('A') + 10); }
                            else { return Fail(TEXT("bad hex in \\u escape")); }
                        }
                        // Surrogate pairs are re-assembled here so the UTF-8 the
                        // encoder sees matches Python's, which decodes them.
                        Acc.AppendChar((TCHAR)Code);
                        break;
                    }
                    default: return Fail(TEXT("unknown escape"));
                    }
                    continue;
                }
                Acc.AppendChar(C);
                ++P;
            }
        }

        bool ParseNumber(FValue& Out)
        {
            const TCHAR* Start = P;
            if (P < End && (*P == TEXT('-') || *P == TEXT('+'))) { ++P; }
            bool bAny = false;
            while (P < End && *P >= TEXT('0') && *P <= TEXT('9')) { ++P; bAny = true; }
            if (P < End && *P == TEXT('.'))
            {
                ++P;
                while (P < End && *P >= TEXT('0') && *P <= TEXT('9')) { ++P; bAny = true; }
            }
            if (P < End && (*P == TEXT('e') || *P == TEXT('E')))
            {
                ++P;
                if (P < End && (*P == TEXT('-') || *P == TEXT('+'))) { ++P; }
                while (P < End && *P >= TEXT('0') && *P <= TEXT('9')) { ++P; }
            }
            if (!bAny) { return Fail(TEXT("expected a number")); }
            const FString Text(P - Start, Start);
            Out.Type = EType::Number;
            Out.Number = FCString::Atod(*Text);
            return true;
        }
    };

    bool FParser::ParseValue(FValue& Out)
    {
        Space();
        if (P >= End) { return Fail(TEXT("unexpected end of document")); }
        const TCHAR C = *P;

        if (C == TEXT('n'))
        {
            if (!Literal(TEXT("null"))) { return Fail(TEXT("bad literal")); }
            Out.Type = EType::Null;
            return true;
        }
        if (C == TEXT('t'))
        {
            if (!Literal(TEXT("true"))) { return Fail(TEXT("bad literal")); }
            Out.Type = EType::Bool; Out.bBool = true;
            return true;
        }
        if (C == TEXT('f'))
        {
            if (!Literal(TEXT("false"))) { return Fail(TEXT("bad literal")); }
            Out.Type = EType::Bool; Out.bBool = false;
            return true;
        }
        // Decision 0023: NaN and Infinity are not canon values. Python's json
        // accepts them by default, so both sides refuse them explicitly rather
        // than relying on a parser's mood.
        if (C == TEXT('N') || C == TEXT('I'))
        {
            return Fail(TEXT("NaN/Infinity is not a canon value"));
        }
        if (C == TEXT('-') && P + 1 < End && P[1] == TEXT('I'))
        {
            return Fail(TEXT("NaN/Infinity is not a canon value"));
        }
        if (C == TEXT('"'))
        {
            Out.Type = EType::String;
            return ParseString(Out.Str);
        }
        if (C == TEXT('['))
        {
            ++P;
            Out.Type = EType::Array;
            Space();
            if (P < End && *P == TEXT(']')) { ++P; return true; }
            while (true)
            {
                FValue Item;
                if (!ParseValue(Item)) { return false; }
                Out.Items.Add(MoveTemp(Item));
                Space();
                if (P < End && *P == TEXT(',')) { ++P; continue; }
                if (P < End && *P == TEXT(']')) { ++P; return true; }
                return Fail(TEXT("expected ',' or ']'"));
            }
        }
        if (C == TEXT('{'))
        {
            ++P;
            Out.Type = EType::Object;
            Space();
            if (P < End && *P == TEXT('}')) { ++P; return true; }
            while (true)
            {
                Space();
                FString Key;
                if (!ParseString(Key)) { return false; }
                // THE REASON THIS PARSER EXISTS.
                for (const TPair<FString, FValue>& M : Out.Members)
                {
                    if (KeyEquals(M.Key, Key))
                    {
                        return Fail(FString::Printf(
                            TEXT("duplicate key '%s' - JSON parsers silently keep one ")
                            TEXT("of the two, so a file like this means different things ")
                            TEXT("to different readers and cannot have one identity"), *Key));
                    }
                }
                Space();
                if (P >= End || *P != TEXT(':')) { return Fail(TEXT("expected ':'")); }
                ++P;
                FValue Val;
                if (!ParseValue(Val)) { return false; }
                Out.Members.Add(TPair<FString, FValue>(Key, MoveTemp(Val)));
                Space();
                if (P < End && *P == TEXT(',')) { ++P; continue; }
                if (P < End && *P == TEXT('}')) { ++P; return true; }
                return Fail(TEXT("expected ',' or '}'"));
            }
        }
        return ParseNumber(Out);
    }

    static bool Parse(const FString& Text, FValue& Out, FString& OutError)
    {
        FParser Par;
        Par.P = *Text;
        Par.End = *Text + Text.Len();
        if (!Par.ParseValue(Out)) { OutError = Par.Error; return false; }
        Par.Space();
        if (Par.P != Par.End) { OutError = TEXT("trailing content after the document"); return false; }
        return true;
    }

    // -------------------------------------------------------------- numbers --

    static bool NumberText(double V, FString& Out, FString& OutError)
    {
        if (FMath::IsNaN(V) || !FMath::IsFinite(V))
        {
            OutError = TEXT("non-finite number");
            return false;
        }
        if (FMath::Abs(V) >= MaxExactInt)
        {
            OutError = TEXT("integer too large to be exactly representable as a double");
            return false;
        }
        FString Text = FString::Printf(TEXT("%.10f"), V);
        // Refused, not rounded. Quietly truncating a canon value inside the
        // evidence layer would be undetectable.
        if (FCString::Atod(*Text) != V)
        {
            OutError = TEXT("needs more precision than ten decimal places; refused rather than rounded");
            return false;
        }
        // Requirement 3: -0 and 0 are one gameplay quantity.
        if (Text.StartsWith(TEXT("-")) && FCString::Atod(*Text) == 0.0)
        {
            Text = Text.RightChop(1);
        }
        Out = Text;
        return true;
    }

    // -------------------------------------------------------------- encoder --

    static void PutU32(TArray<uint8>& Out, uint32 N)
    {
        Out.Add((uint8)((N >> 24) & 0xff));
        Out.Add((uint8)((N >> 16) & 0xff));
        Out.Add((uint8)((N >> 8) & 0xff));
        Out.Add((uint8)(N & 0xff));
    }

    static void PutString(TArray<uint8>& Out, const FString& S)
    {
        const TArray<uint8> Bytes = Utf8Of(S);
        Out.Add((uint8)'s');
        PutU32(Out, (uint32)Bytes.Num());
        Out.Append(Bytes);
    }

    static bool Encode(const FValue& V, TArray<uint8>& Out, FString& OutError)
    {
        switch (V.Type)
        {
        case EType::Null:  Out.Add((uint8)'n'); return true;
        case EType::Bool:  Out.Add((uint8)(V.bBool ? 't' : 'f')); return true;
        case EType::Number:
        {
            FString Text;
            if (!NumberText(V.Number, Text, OutError)) { return false; }
            const TArray<uint8> Bytes = Utf8Of(Text);
            Out.Add((uint8)'d');
            PutU32(Out, (uint32)Bytes.Num());
            Out.Append(Bytes);
            return true;
        }
        case EType::String: PutString(Out, V.Str); return true;
        case EType::Array:
        {
            Out.Add((uint8)'a');
            PutU32(Out, (uint32)V.Items.Num());
            for (const FValue& Item : V.Items)
            {
                if (!Encode(Item, Out, OutError)) { return false; }
            }
            return true;
        }
        case EType::Object:
        {
            TArray<int32> Order;
            for (int32 i = 0; i < V.Members.Num(); ++i) { Order.Add(i); }
            Order.Sort([&V](int32 A, int32 B)
            {
                return Utf8Less(V.Members[A].Key, V.Members[B].Key);
            });
            Out.Add((uint8)'o');
            PutU32(Out, (uint32)Order.Num());
            for (int32 Index : Order)
            {
                PutString(Out, V.Members[Index].Key);
                if (!Encode(V.Members[Index].Value, Out, OutError)) { return false; }
            }
            return true;
        }
        }
        OutError = TEXT("value has no canonical form");
        return false;
    }

    // -------------------------------------------------------------- pointers --

    // RFC 6901: ~1 is '/', ~0 is '~', and ~1 must be decoded FIRST. Decoding
    // ~0 first turns "~01" into "~1" and then into "/", so a key literally
    // named "~1" would become "/". The order is the specification's, and
    // Replace() chained the other way round is a real bug that only shows on
    // keys nobody expects to exist until canon grows one.
    static FString Unescape(const FString& Seg)
    {
        return Seg.Replace(TEXT("~1"), TEXT("/")).Replace(TEXT("~0"), TEXT("~"));
    }

    static bool SplitPointer(const FString& Pattern, TArray<FString>& Out, FString& OutError)
    {
        if (Pattern.IsEmpty())
        {
            OutError = TEXT("the whole document cannot be non-authoritative");
            return false;
        }
        if (!Pattern.StartsWith(TEXT("/")))
        {
            OutError = FString::Printf(TEXT("pointer '%s' must start with '/'"), *Pattern);
            return false;
        }
        TArray<FString> Raw;
        Pattern.RightChop(1).ParseIntoArray(Raw, TEXT("/"), false);
        for (const FString& R : Raw) { Out.Add(Unescape(R)); }
        if (Out.Num() > 0 && Out.Last() == TEXT("*"))
        {
            OutError = FString::Printf(
                TEXT("pointer '%s' ends in a wildcard, which would delete whole array ")
                TEXT("elements and renumber their neighbours; array order is authoritative"),
                *Pattern);
            return false;
        }
        return true;
    }

    // A concrete path, as SEGMENT VECTORS. Decision 0024 requires this: RFC
    // 6901 escapes '/' as '~1', so `/a~1b` names the single key "a/b" while
    // `/a/b` names "a" then "b". Joining segments back into a slash string to
    // compare them makes those two the same path, and an exclusion aimed at one
    // would silently drop the other - a field nobody classified leaving the
    // evidence envelope. Strings are produced only for humans.
    typedef TArray<FString> FPath;

    static bool PathEquals(const FPath& A, const FPath& B)
    {
        if (A.Num() != B.Num()) { return false; }
        for (int32 i = 0; i < A.Num(); ++i)
        {
            if (!KeyEquals(A[i], B[i])) { return false; }
        }
        return true;
    }

    static void Expand(const FValue& Node, const TArray<FString>& Segs, int32 I,
                       const FPath& Trail, TArray<FPath>& Out)
    {
        if (I == Segs.Num()) { Out.Add(Trail); return; }
        const FString& Seg = Segs[I];
        if (Seg == TEXT("*"))
        {
            if (Node.Type != EType::Array) { return; }
            for (int32 Idx = 0; Idx < Node.Items.Num(); ++Idx)
            {
                FPath Next = Trail;
                Next.Add(FString::FromInt(Idx));
                Expand(Node.Items[Idx], Segs, I + 1, Next, Out);
            }
            return;
        }
        if (Node.Type != EType::Object) { return; }
        for (const TPair<FString, FValue>& M : Node.Members)
        {
            if (KeyEquals(M.Key, Seg))
            {
                FPath Next = Trail;
                Next.Add(Seg);
                Expand(M.Value, Segs, I + 1, Next, Out);
                return;
            }
        }
    }

    // A linear scan with an explicit case-sensitive, segment-wise compare -
    // deliberately not a TSet: UE hashes and compares FString case-insensitively,
    // so a set would let `/guard/Note` match `/guard/note`. The lists are a few
    // dozen pointers; obviously correct matters more here than fast.
    static bool DropContains(const TArray<FPath>& Drop, const FPath& Path)
    {
        for (const FPath& D : Drop)
        {
            if (PathEquals(D, Path)) { return true; }
        }
        return false;
    }

    static void Prune(FValue& Node, const TArray<FPath>& Drop, const FPath& Trail)
    {
        if (Node.Type == EType::Object)
        {
            TArray<TPair<FString, FValue>> Kept;
            for (TPair<FString, FValue>& M : Node.Members)
            {
                FPath Here = Trail;
                Here.Add(M.Key);
                if (DropContains(Drop, Here)) { continue; }
                Prune(M.Value, Drop, Here);
                Kept.Add(MoveTemp(M));
            }
            Node.Members = MoveTemp(Kept);
        }
        else if (Node.Type == EType::Array)
        {
            for (int32 i = 0; i < Node.Items.Num(); ++i)
            {
                FPath Here = Trail;
                Here.Add(FString::FromInt(i));
                Prune(Node.Items[i], Drop, Here);
            }
        }
    }

    static bool Strip(FValue& Doc, const TArray<FString>& Patterns, FString& OutError)
    {
        TArray<FPath> Drop;
        for (const FString& Pattern : Patterns)
        {
            TArray<FString> Segs;
            if (!SplitPointer(Pattern, Segs, OutError)) { return false; }
            TArray<FPath> Hits;
            Expand(Doc, Segs, 0, FPath(), Hits);
            if (Hits.Num() == 0)
            {
                OutError = FString::Printf(
                    TEXT("hash-role pattern '%s' matches nothing in this file; a pattern ")
                    TEXT("that matches nothing today may match something nobody reviewed ")
                    TEXT("tomorrow"), *Pattern);
                return false;
            }
            for (const FPath& H : Hits) { Drop.Add(H); }
        }
        Prune(Doc, Drop, FPath());
        return true;
    }
}

// ------------------------------------------------------------------ public ----

bool UppercutCanonicalBytes(const FString& JsonText,
                            const TArray<FString>& Patterns,
                            TArray<uint8>& OutBytes,
                            FString& OutError)
{
    using namespace UppercutCanon;
    FValue Doc;
    if (!Parse(JsonText, Doc, OutError)) { return false; }
    if (!Strip(Doc, Patterns, OutError)) { return false; }
    OutBytes.Reset();
    return Encode(Doc, OutBytes, OutError);
}

bool UppercutCanonHashes(const FString& JsonText,
                         const TArray<FString>& Patterns,
                         const FString& SchemaIdentity,
                         const FString& PolicyIdentity,
                         const FString& RoleSetIdentity,
                         FString& OutRaw,
                         FString& OutSemantic,
                         FString& OutError)
{
    using namespace UppercutCanon;

    const TArray<uint8> RawBytes = Utf8Of(JsonText);
    OutRaw = UppercutSha256Hex(RawBytes.GetData(), (uint64)RawBytes.Num());

    TArray<uint8> Body;
    if (!UppercutCanonicalBytes(JsonText, Patterns, Body, OutError)) { return false; }

    // Decision 0023 requirement 6, narrowed by Decision 0024. Five fields, NUL
    // separated, exactly as the Python side joins them - and the ORDER is part
    // of the contract, not a convenience.
    TArray<uint8> Payload;
    AppendUtf8(Payload, UppercutCanonicalizerVersion); Payload.Add(0);
    AppendUtf8(Payload, UppercutHashContractVersion);  Payload.Add(0);
    AppendUtf8(Payload, SchemaIdentity);               Payload.Add(0);
    AppendUtf8(Payload, PolicyIdentity);               Payload.Add(0);
    AppendUtf8(Payload, RoleSetIdentity);              Payload.Add(0);
    Payload.Append(Body);

    OutSemantic = UppercutSha256Hex(Payload.GetData(), (uint64)Payload.Num());
    return true;
}

// Which file, at which schema version. Including the path means two canon files
// holding identical values still have different identities, which is correct -
// they are different dependencies.
static bool SchemaIdentityFor(const FString& Text, const FString& Rel,
                              FString& Out, FString& OutError)
{
    using namespace UppercutCanon;
    FValue Doc;
    if (!Parse(Text, Doc, OutError)) { return false; }
    FString Version;
    if (Doc.Type == EType::Object)
    {
        for (const TPair<FString, FValue>& M : Doc.Members)
        {
            if (KeyEquals(M.Key, TEXT("schema_version")) && M.Value.Type == EType::String)
            {
                Version = M.Value.Str;
            }
        }
    }
    Out = FString::Printf(TEXT("%s@%s"), *Rel, *Version);
    return true;
}

bool UppercutCanonHeaderLines(const FString& RepoDir,
                              const TArray<TPair<FString, FString>>& Entries,
                              TArray<FString>& OutLines,
                              FString& OutError)
{
    FString ManifestText;
    const FString ManifestPath = RepoDir / TEXT("data/hash_roles.json");
    if (!FFileHelper::LoadFileToString(ManifestText, *ManifestPath))
    {
        OutError = FString::Printf(TEXT("cannot read %s"), *ManifestPath);
        return false;
    }
    FString PolicyId, ManifestVersion;
    if (!UppercutCanonManifestIdentity(ManifestText, PolicyId, ManifestVersion, OutError))
    {
        return false;
    }
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:13 UTC | START ]
    // Provenance is the repository bytes (LF). Windows checkouts may present
    // CRLF; normalize before hashing so roles_raw matches Linux goldens.
    FString ManifestForRaw = ManifestText;
    ManifestForRaw.ReplaceInline(TEXT("\r\n"), TEXT("\n"));
    ManifestForRaw.ReplaceInline(TEXT("\r"), TEXT("\n"));
    const FTCHARToUTF8 ManifestRawUtf8(*ManifestForRaw);
    const FString ManifestRaw = UppercutSha256Hex((const uint8*)ManifestRawUtf8.Get(),
                                                  (uint64)ManifestRawUtf8.Length());
    // [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:13 UTC | END ]

    // The manifest doc again, this time to read the per-file patterns.
    UppercutCanon::FValue Manifest;
    if (!UppercutCanon::Parse(ManifestText, Manifest, OutError)) { return false; }
    const UppercutCanon::FValue* Files = nullptr;
    for (const TPair<FString, UppercutCanon::FValue>& M : Manifest.Members)
    {
        if (UppercutCanon::KeyEquals(M.Key, TEXT("files"))) { Files = &M.Value; }
    }

    OutLines.Reset();
    OutLines.Add(FString::Printf(TEXT("H|canon_hash_contract=%s"), UppercutHashContractVersion));
    OutLines.Add(FString::Printf(TEXT("H|canon_hash_roles=%s"), *ManifestVersion));
    OutLines.Add(FString::Printf(TEXT("H|canon_hash_policy=%s"), *PolicyId));
    OutLines.Add(FString::Printf(TEXT("H|canon_hash_roles_raw=%s"), *ManifestRaw));

    for (const TPair<FString, FString>& Entry : Entries)
    {
        const FString& Label = Entry.Key;
        const FString& Rel = Entry.Value;

        FString Text;
        const FString Path = RepoDir / Rel;
        if (!FFileHelper::LoadFileToString(Text, *Path))
        {
            OutError = FString::Printf(TEXT("cannot read canon file %s"), *Rel);
            return false;
        }

        // Silence in the manifest means "hash the whole file", never "exclude
        // something". A file nobody classified is fully authoritative.
        TArray<FString> Patterns;
        bool bClassified = false;
        if (Files && Files->Type == UppercutCanon::EType::Object)
        {
            for (const TPair<FString, UppercutCanon::FValue>& F : Files->Members)
            {
                if (!UppercutCanon::KeyEquals(F.Key, Rel)) { continue; }
                bClassified = true;
                for (const TPair<FString, UppercutCanon::FValue>& S : F.Value.Members)
                {
                    if (UppercutCanon::KeyEquals(S.Key, TEXT("non_authoritative"))
                        && S.Value.Type == UppercutCanon::EType::Array)
                    {
                        for (const UppercutCanon::FValue& It : S.Value.Items)
                        {
                            if (It.Type == UppercutCanon::EType::String) { Patterns.Add(It.Str); }
                        }
                    }
                }
            }
        }

        FString RoleSetId;
        if (!UppercutCanonRoleSetIdentity(PolicyId, Rel, Patterns, bClassified,
                                          RoleSetId))
        {
            OutError = FString::Printf(TEXT("%s: cannot derive a role-set identity"), *Rel);
            return false;
        }

        FString SchemaId;
        if (!SchemaIdentityFor(Text, Rel, SchemaId, OutError)) { return false; }

        FString Raw, Semantic;
        if (!UppercutCanonHashes(Text, Patterns, SchemaId, PolicyId, RoleSetId,
                                 Raw, Semantic, OutError))
        {
            OutError = FString::Printf(TEXT("%s: %s"), *Rel, *OutError);
            return false;
        }
        OutLines.Add(FString::Printf(TEXT("H|canon_%s_semantic=%s"), *Label, *Semantic));
        OutLines.Add(FString::Printf(TEXT("H|canon_%s_raw=%s"), *Label, *Raw));
        OutLines.Add(FString::Printf(TEXT("H|canon_%s_roles=%s"), *Label, *RoleSetId));
    }
    return true;
}

// The manifest keys that are GLOBAL policy - they change how every canon file
// is classified. `files` is deliberately absent: that is per-file scope, and
// putting it here is exactly the over-broad binding Decision 0024 removed.
static const TCHAR* GPolicyKeys[] = {
    TEXT("manifest_version"), TEXT("canonicalizer_contract"),
    TEXT("hash_contract_version"), TEXT("default_role"), TEXT("rules"),
    TEXT("coverage"), TEXT("self")
};

static bool IsPolicyKey(const FString& Key)
{
    for (const TCHAR* K : GPolicyKeys)
    {
        if (UppercutCanon::KeyEquals(Key, K)) { return true; }
    }
    return false;
}

bool UppercutCanonRoleSetIdentity(const FString& PolicyIdentity,
                                  const FString& Rel,
                                  const TArray<FString>& Patterns,
                                  bool bClassified,
                                  FString& OutIdentity)
{
    using namespace UppercutCanon;

    // Mirrors the Python body exactly: {"classified", "file",
    // "non_authoritative"} - key order does not matter because the encoder
    // sorts, but the SHAPE does.
    FValue Body;
    Body.Type = EType::Object;

    FValue Classified; Classified.Type = EType::Bool; Classified.bBool = bClassified;
    Body.Members.Add(TPair<FString, FValue>(TEXT("classified"), Classified));

    FValue File; File.Type = EType::String; File.Str = Rel;
    Body.Members.Add(TPair<FString, FValue>(TEXT("file"), File));

    FValue List; List.Type = EType::Array;
    for (const FString& P : Patterns)
    {
        FValue Item; Item.Type = EType::String; Item.Str = P;
        List.Items.Add(Item);
    }
    Body.Members.Add(TPair<FString, FValue>(TEXT("non_authoritative"), List));

    TArray<uint8> Payload;
    AppendUtf8(Payload, PolicyIdentity); Payload.Add(0);
    FString Error;
    if (!Encode(Body, Payload, Error)) { OutIdentity.Reset(); return false; }
    OutIdentity = UppercutSha256Hex(Payload.GetData(), (uint64)Payload.Num());
    return true;
}

bool UppercutCanonManifestIdentity(const FString& ManifestJson,
                                   FString& OutIdentity,
                                   FString& OutVersion,
                                   FString& OutError)
{
    using namespace UppercutCanon;

    FValue Doc;
    if (!Parse(ManifestJson, Doc, OutError)) { return false; }
    if (Doc.Type != EType::Object) { OutError = TEXT("manifest is not an object"); return false; }

    const FValue* Self = nullptr;
    const FValue* Version = nullptr;
    const FValue* Canonicalizer = nullptr;
    const FValue* HashContract = nullptr;
    for (const TPair<FString, FValue>& M : Doc.Members)
    {
        if (KeyEquals(M.Key, TEXT("self"))) { Self = &M.Value; }
        else if (KeyEquals(M.Key, TEXT("manifest_version"))) { Version = &M.Value; }
        else if (KeyEquals(M.Key, TEXT("canonicalizer_contract"))) { Canonicalizer = &M.Value; }
        else if (KeyEquals(M.Key, TEXT("hash_contract_version"))) { HashContract = &M.Value; }
    }
    if (!Self || !Version || Version->Type != EType::String)
    {
        OutError = TEXT("manifest has no 'self' block or no manifest_version");
        return false;
    }
    if (!Canonicalizer || Canonicalizer->Str != UppercutCanonicalizerVersion)
    {
        OutError = TEXT("manifest declares a canonicalizer this build does not implement");
        return false;
    }
    if (!HashContract || HashContract->Str != UppercutHashContractVersion)
    {
        OutError = TEXT("manifest declares a hash contract this build does not implement");
        return false;
    }
    OutVersion = Version->Str;

    // Decision 0024: the GLOBAL policy view. Only the contract-wide keys, and
    // nothing about any particular file - `files` is per-file scope.
    FValue Policy;
    Policy.Type = EType::Object;
    for (const TPair<FString, FValue>& M : Doc.Members)
    {
        if (IsPolicyKey(M.Key)) { Policy.Members.Add(M); }
    }

    // Only those self-exclusions that actually point INSIDE the policy view.
    // A pattern aimed at /files/... would match nothing here, and Strip refuses
    // a pattern that matches nothing - correctly, so it must not be passed.
    TArray<FString> SelfPatterns;
    for (const TPair<FString, FValue>& M : Self->Members)
    {
        if (!KeyEquals(M.Key, TEXT("non_authoritative"))
            || M.Value.Type != EType::Array) { continue; }
        for (const FValue& It : M.Value.Items)
        {
            if (It.Type != EType::String) { continue; }
            TArray<FString> Segs;
            FString Ignored;
            if (!SplitPointer(It.Str, Segs, Ignored)) { continue; }
            if (Segs.Num() > 0 && IsPolicyKey(Segs[0])) { SelfPatterns.Add(It.Str); }
        }
    }

    if (SelfPatterns.Num() > 0 && !Strip(Policy, SelfPatterns, OutError))
    {
        return false;
    }

    // Shallower binding on purpose: the policy identity cannot bind itself.
    TArray<uint8> Payload;
    AppendUtf8(Payload, UppercutCanonicalizerVersion); Payload.Add(0);
    AppendUtf8(Payload, UppercutHashContractVersion);  Payload.Add(0);
    AppendUtf8(Payload, OutVersion);                   Payload.Add(0);
    if (!Encode(Policy, Payload, OutError)) { return false; }
    OutIdentity = UppercutSha256Hex(Payload.GetData(), (uint64)Payload.Num());
    return true;
}
// [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 03:20 UTC | END ]
