// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:55 UTC | START ]
#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "UppercutFightSubsystem.h"
#include "UppercutDevHUDWidget.generated.h"

// C++ base for WBP_UppercutDevHUD (PRO-8). Blueprint subclass binds text
// blocks to RefreshFromView; presentation only mirrors GetView() (Decision 0012).
UCLASS(Abstract, Blueprintable)
class UPPERCUTCORE_API UUppercutDevHUDWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Uppercut|HUD")
    void BindFightSubsystem(UUppercutFightSubsystem* Subsystem);

    UFUNCTION(BlueprintCallable, Category = "Uppercut|HUD")
    void RefreshFromView(const FUppercutFightView& View);

protected:
    UPROPERTY(BlueprintReadOnly, meta = (BindWidgetOptional), Category = "Uppercut|HUD")
    class UTextBlock* RoundClockText = nullptr;

    UPROPERTY(BlueprintReadOnly, meta = (BindWidgetOptional), Category = "Uppercut|HUD")
    UTextBlock* SeedHashText = nullptr;

    UFUNCTION(BlueprintImplementableEvent, Category = "Uppercut|HUD")
    void OnViewUpdated(const FUppercutFightView& View);

    UPROPERTY()
    TObjectPtr<UUppercutFightSubsystem> FightSubsystem;
};
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:55 UTC | END ]
