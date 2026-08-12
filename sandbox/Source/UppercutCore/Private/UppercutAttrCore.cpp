// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
#include "UppercutAttrCore.h"

#include "Dom/JsonObject.h"
#include "Dom/JsonValue.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

namespace
{
    int64 QFromFloat(double V)
    {
        return (int64)FMath::RoundToDouble(V * 10000.0);
    }

    bool LoadJson(const FString& Path, TSharedPtr<FJsonObject>& Out, FString& Err)
    {
        FString Text;
        if (!FFileHelper::LoadFileToString(Text, *Path))
        {
            Err = FString::Printf(TEXT("cannot read %s"), *Path);
            return false;
        }
        const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
        if (!FJsonSerializer::Deserialize(Reader, Out) || !Out.IsValid())
        {
            Err = FString::Printf(TEXT("bad json %s"), *Path);
            return false;
        }
        return true;
    }
}

int64 FUppercutAttrCanon::Multiplier(const FUppercutFighterCard& Card,
                                     const FString& Scales) const
{
    for (const FUppercutAttrEffect& E : Effects)
    {
        if (E.Scales != Scales) { continue; }
        const int32* PV = Card.Attributes.Find(E.Attribute);
        if (!PV) { return UppercutAttrOne; }
        const int32 V = FMath::Clamp(*PV, -100, 100);
        const int32 T = V + 100; // 0..200
        return E.MultAtMinus100
            + ((E.MultAtPlus100 - E.MultAtMinus100) * (int64)T) / 200;
    }
    return UppercutAttrOne;
}

int64 FUppercutAttrCanon::Apply(int64 ValueQ, const FUppercutFighterCard& Card,
                                const FString& Scales) const
{
    return (ValueQ * Multiplier(Card, Scales)) / UppercutAttrOne;
}

bool UppercutLoadAttrCanon(const FString& RepoDir, FUppercutAttrCanon& Out,
                           FString& OutError)
{
    Out = FUppercutAttrCanon();
    TSharedPtr<FJsonObject> Root;
    if (!LoadJson(RepoDir / TEXT("data/attribute_effects.json"), Root, OutError))
    {
        return false;
    }
    const TArray<TSharedPtr<FJsonValue>>* Arr = nullptr;
    if (!Root->TryGetArrayField(TEXT("effects"), Arr) || !Arr)
    {
        OutError = TEXT("attribute_effects.json missing effects[]");
        return false;
    }
    for (const TSharedPtr<FJsonValue>& Item : *Arr)
    {
        const TSharedPtr<FJsonObject> O = Item->AsObject();
        if (!O.IsValid()) { continue; }
        FUppercutAttrEffect E;
        O->TryGetStringField(TEXT("attribute"), E.Attribute);
        O->TryGetStringField(TEXT("scales"), E.Scales);
        double Lo = 1.0, Hi = 1.0;
        O->TryGetNumberField(TEXT("multiplier_at_minus_100"), Lo);
        O->TryGetNumberField(TEXT("multiplier_at_plus_100"), Hi);
        E.MultAtMinus100 = QFromFloat(Lo);
        E.MultAtPlus100 = QFromFloat(Hi);
        Out.Effects.Add(E);
    }
    return true;
}

bool UppercutLoadFighterCard(const FString& RepoDir, const FString& FighterId,
                             FUppercutFighterCard& Out, FString& OutError)
{
    Out = FUppercutFighterCard();
    Out.Id = FighterId;
    const FString Path = RepoDir / TEXT("fixtures/fighters/legal")
        / (FighterId + TEXT(".json"));
    TSharedPtr<FJsonObject> Root;
    if (!LoadJson(Path, Root, OutError))
    {
        return false;
    }
    const TSharedPtr<FJsonObject>* Attrs = nullptr;
    if (!Root->TryGetObjectField(TEXT("attributes"), Attrs) || !Attrs)
    {
        OutError = TEXT("fighter card missing attributes");
        return false;
    }
    for (const TPair<FString, TSharedPtr<FJsonValue>>& Pair : (*Attrs)->Values)
    {
        Out.Attributes.Add(Pair.Key, (int32)Pair.Value->AsNumber());
    }
    return true;
}
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]
