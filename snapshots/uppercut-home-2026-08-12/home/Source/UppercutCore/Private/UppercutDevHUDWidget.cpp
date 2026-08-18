// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:55 UTC | START ]
#include "UppercutDevHUDWidget.h"
#include "Components/TextBlock.h"

void UUppercutDevHUDWidget::BindFightSubsystem(UUppercutFightSubsystem* Subsystem)
{
    FightSubsystem = Subsystem;
}

void UUppercutDevHUDWidget::RefreshFromView(const FUppercutFightView& View)
{
    if (RoundClockText)
    {
        const int32 Left = FMath::Max(0, View.TickBudget - View.Tick);
        RoundClockText->SetText(FText::FromString(
            FString::Printf(TEXT("R1 %d:%02d"), Left / 3600, (Left / 60) % 60)));
    }
    if (SeedHashText)
    {
        SeedHashText->SetText(FText::FromString(
            FString::Printf(TEXT("seed=%d hash=%s"), View.Seed, *View.MarkerHash)));
    }
    OnViewUpdated(View);
}
// [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 07:55 UTC | END ]
