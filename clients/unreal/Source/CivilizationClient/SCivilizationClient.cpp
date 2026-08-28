// clients/unreal/Source/CivilizationClient/SCivilizationClient.cpp
#include "SCivilizationClient.h"
#include "CivilizationApiClient.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Input/SEditableTextBox.h"
#include "Widgets/Input/SSpinBox.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SCanvas.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Text/STextBlock.h"

void SCivilizationClient::Construct(const FArguments& Args)
{
    Api = MakeShared<FCivilizationApiClient>();
    SetCanTick(true);
    Players.SetNum(4);
    for (int32 Index = 0; Index < Players.Num(); ++Index)
    {
        Players[Index].Id = FString::Printf(TEXT("p%d"), Index + 1);
        Players[Index].Name = FString::Printf(TEXT("Player %d"), Index + 1);
        Players[Index].CivilizationIndex = Index;
    }

    ChildSlot
    [
        SNew(SBorder).Padding(12)
        [
            SAssignNew(Root, SVerticalBox)
        ]
    ];
    Rebuild();
}

void SCivilizationClient::Tick(const FGeometry& AllottedGeometry, double InCurrentTime, float InDeltaTime)
{
    SCompoundWidget::Tick(AllottedGeometry, InCurrentTime, InDeltaTime);
    if (Mode == EMode::Game && !bRequestInFlight && InCurrentTime >= NextRefreshTime)
    {
        NextRefreshTime = InCurrentTime + 1.0;
        RefreshAll();
    }
}

void SCivilizationClient::Rebuild()
{
    if (!Root.IsValid()) return;
    Root->ClearChildren();
    Root->AddSlot().AutoHeight().Padding(4)
    [
        SNew(STextBlock).Text(FText::FromString(TEXT("CivilizationClone — Unreal Engine Client")))
    ];
    Root->AddSlot().AutoHeight().Padding(4)
    [
        SNew(STextBlock)
        .Text_Lambda([this]() { return FText::FromString(Status); })
        .ColorAndOpacity_Lambda([this]() { return FSlateColor(bStatusError ? FLinearColor(1.0f, 0.35f, 0.3f) : FLinearColor(0.72f, 0.8f, 0.9f)); })
    ];

    switch (Mode)
    {
        case EMode::Connect: BuildConnect(); break;
        case EMode::Lobby: BuildLobby(); break;
        case EMode::Game: BuildGame(); break;
    }
}

void SCivilizationClient::BuildConnect()
{
    Root->AddSlot().AutoHeight().Padding(4)
    [
        SNew(SHorizontalBox)
        + SHorizontalBox::Slot().AutoWidth().Padding(2)[SNew(STextBlock).Text(FText::FromString(TEXT("API")))]
        + SHorizontalBox::Slot().FillWidth(1.0f).Padding(2)
        [
            SNew(SEditableTextBox).Text(FText::FromString(ApiUrl))
            .OnTextChanged_Lambda([this](const FText& Text) { ApiUrl = Text.ToString(); })
        ]
        + SHorizontalBox::Slot().AutoWidth().Padding(2)
        [
            SNew(SButton).Text(FText::FromString(TEXT("Connect"))).OnClicked_Lambda([this]() { Connect(); return FReply::Handled(); })
        ]
    ];
}

void SCivilizationClient::BuildLobby()
{
    Root->AddSlot().AutoHeight().Padding(4)[SNew(STextBlock).Text(FText::FromString(TEXT("New hotseat game")))];
    Root->AddSlot().AutoHeight().Padding(4)
    [
        SNew(SHorizontalBox)
        + SHorizontalBox::Slot().FillWidth(1.0f).Padding(2)
        [SNew(SEditableTextBox).Text(FText::FromString(GameIdInput)).HintText(FText::FromString(TEXT("Game ID"))).OnTextChanged_Lambda([this](const FText& Text) { GameIdInput = Text.ToString(); })]
        + SHorizontalBox::Slot().AutoWidth().Padding(2)
        [SNew(SSpinBox<int32>).MinValue(0).MaxValue(MAX_int32).Value(Seed).OnValueChanged_Lambda([this](int32 Value) { Seed = Value; })]
        + SHorizontalBox::Slot().AutoWidth().Padding(2)
        [SNew(SSpinBox<int32>).MinValue(2).MaxValue(10).Value(MapRadius).OnValueChanged_Lambda([this](int32 Value) { MapRadius = Value; })]
        + SHorizontalBox::Slot().AutoWidth().Padding(2)
        [SNew(SSpinBox<int32>).MinValue(2).MaxValue(4).Value(PlayerCount).OnValueChanged_Lambda([this](int32 Value) { PlayerCount = Value; Rebuild(); })]
    ];

    for (int32 Index = 0; Index < PlayerCount; ++Index)
    {
        Root->AddSlot().AutoHeight().Padding(3)
        [
            SNew(SHorizontalBox)
            + SHorizontalBox::Slot().AutoWidth().Padding(2)
            [SNew(SEditableTextBox).MinDesiredWidth(80).Text(FText::FromString(Players[Index].Id)).OnTextChanged_Lambda([this, Index](const FText& Text) { Players[Index].Id = Text.ToString(); })]
            + SHorizontalBox::Slot().AutoWidth().Padding(2)
            [SNew(SEditableTextBox).MinDesiredWidth(160).Text(FText::FromString(Players[Index].Name)).OnTextChanged_Lambda([this, Index](const FText& Text) { Players[Index].Name = Text.ToString(); })]
            + SHorizontalBox::Slot().AutoWidth().Padding(2)
            [
                SNew(SButton).Text(FText::FromString(CivilizationName(Players[Index].CivilizationIndex)))
                .OnClicked_Lambda([this, Index]()
                {
                    if (Civilizations.Num() > 0) Players[Index].CivilizationIndex = (Players[Index].CivilizationIndex + 1) % Civilizations.Num();
                    Rebuild();
                    return FReply::Handled();
                })
            ]
        ];
    }

    Root->AddSlot().AutoHeight().Padding(5)
    [SNew(SButton).Text(FText::FromString(TEXT("Create & Start Game"))).OnClicked_Lambda([this]() { CreateAndStart(); return FReply::Handled(); })];
}

void SCivilizationClient::BuildGame()
{
    FString Summary = TEXT("No state");
    if (State.IsValid())
    {
        const TSharedPtr<FJsonObject>* Viewer = nullptr;
        if (State->TryGetObjectField(TEXT("viewer"), Viewer) && Viewer && Viewer->IsValid())
        {
            Summary = FString::Printf(TEXT("Turn %d | active %s | %s | G %d S %d C %d"),
                IntField(State, TEXT("turn")), *StringField(State, TEXT("active_player_id"), TEXT("-")),
                *StringField(*Viewer, TEXT("civilization_id")), IntField(*Viewer, TEXT("gold")), IntField(*Viewer, TEXT("science")), IntField(*Viewer, TEXT("culture")));
        }
    }

    Root->AddSlot().AutoHeight().Padding(3)
    [
        SNew(SHorizontalBox)
        + SHorizontalBox::Slot().AutoWidth().Padding(2)[SNew(STextBlock).Text(FText::FromString(TEXT("Viewer")))]
        + SHorizontalBox::Slot().AutoWidth().Padding(2)[SNew(SButton).Text(FText::FromString(ViewerId)).OnClicked_Lambda([this]() { CycleViewer(); return FReply::Handled(); })]
        + SHorizontalBox::Slot().AutoWidth().Padding(2)[SNew(SButton).Text(FText::FromString(TEXT("Refresh"))).OnClicked_Lambda([this]() { RefreshAll(); return FReply::Handled(); })]
        + SHorizontalBox::Slot().FillWidth(1.0f).HAlign(HAlign_Right).Padding(2)[SNew(STextBlock).Text(FText::FromString(Summary))]
    ];

    Root->AddSlot().FillHeight(1.0f).Padding(3)
    [
        SNew(SHorizontalBox)
        + SHorizontalBox::Slot().FillWidth(1.0f).Padding(2)[BuildMap()]
        + SHorizontalBox::Slot().AutoWidth().Padding(2)[SNew(SBox).WidthOverride(390)[BuildSidePanel()]]
    ];
}
