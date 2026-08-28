// clients/unreal/Source/CivilizationClient/SCivilizationClient.Map.cpp
#include "SCivilizationClient.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Input/SEditableTextBox.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SCanvas.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Text/STextBlock.h"

namespace
{
TSharedRef<FJsonObject> Payload()
{
    return MakeShared<FJsonObject>();
}

TSharedRef<FJsonObject> PayloadString(const FString& Key, const FString& Value)
{
    const TSharedRef<FJsonObject> Result = MakeShared<FJsonObject>();
    Result->SetStringField(Key, Value);
    return Result;
}

FLinearColor TerrainColor(const FString& Terrain, const FString& Visibility)
{
    if (Visibility == TEXT("discovered")) return FLinearColor(0.22f, 0.22f, 0.24f, 1.0f);
    if (Terrain == TEXT("water")) return FLinearColor(0.15f, 0.35f, 0.65f, 1.0f);
    if (Terrain == TEXT("grassland")) return FLinearColor(0.24f, 0.55f, 0.22f, 1.0f);
    if (Terrain == TEXT("plains")) return FLinearColor(0.55f, 0.60f, 0.28f, 1.0f);
    if (Terrain == TEXT("hills")) return FLinearColor(0.45f, 0.36f, 0.25f, 1.0f);
    if (Terrain == TEXT("desert")) return FLinearColor(0.72f, 0.58f, 0.25f, 1.0f);
    if (Terrain == TEXT("tundra")) return FLinearColor(0.55f, 0.60f, 0.65f, 1.0f);
    return FLinearColor::Gray;
}
}

TSharedRef<SWidget> SCivilizationClient::BuildMap()
{
    if (!State.IsValid()) return SNew(SBorder)[SNew(STextBlock).Text(FText::FromString(TEXT("Waiting for map state…")))];
    const TSharedPtr<FJsonObject>* Map = nullptr;
    if (!State->TryGetObjectField(TEXT("map"), Map) || !Map || !Map->IsValid()) return SNew(STextBlock).Text(FText::FromString(TEXT("No map")));

    const TSharedRef<SCanvas> Canvas = SNew(SCanvas);
    const auto Tiles = ObjectArray(*Map, TEXT("tiles"));
    const auto Units = ObjectArray(State, TEXT("units"));
    const auto Settlements = ObjectArray(State, TEXT("settlements"));

    for (const TSharedPtr<FJsonObject>& Tile : Tiles)
    {
        const int32 Q = IntField(Tile, TEXT("q"));
        const int32 R = IntField(Tile, TEXT("r"));
        const float X = 340.0f + Q * 52.0f;
        const float Y = 280.0f + (R + Q * 0.5f) * 42.0f;
        FString Marker;
        for (const auto& Unit : Units)
            if (IntField(Unit, TEXT("q")) == Q && IntField(Unit, TEXT("r")) == R) Marker += StringField(Unit, TEXT("owner_id")) == ViewerId ? TEXT(" U") : TEXT(" E");
        for (const auto& City : Settlements)
            if (IntField(City, TEXT("q")) == Q && IntField(City, TEXT("r")) == R) Marker += StringField(City, TEXT("owner_id")) == ViewerId ? TEXT(" C") : TEXT(" X");

        const FString Terrain = StringField(Tile, TEXT("terrain"), TEXT("?"));
        const FString Label = FString::Printf(TEXT("%s%s\n%d,%d"), *Terrain.Left(2).ToUpper(), *Marker, Q, R);
        Canvas->AddSlot().Position(FVector2D(X, Y)).Size(FVector2D(62.0f, 38.0f))
        [
            SNew(SButton)
            .ButtonColorAndOpacity(TerrainColor(Terrain, StringField(Tile, TEXT("visibility"))))
            .OnClicked_Lambda([this, Q, R]() { return OnTileClicked(Q, R); })
            [SNew(STextBlock).Text(FText::FromString(Label))]
        ];
    }
    return SNew(SBorder)[Canvas];
}

TSharedRef<SWidget> SCivilizationClient::BuildSidePanel()
{
    const TSharedRef<SVerticalBox> Box = SNew(SVerticalBox);
    Box->AddSlot().AutoHeight().Padding(2)[SNew(STextBlock).Text(FText::FromString(TEXT("Selection")))];
    Box->AddSlot().AutoHeight().Padding(2)[SNew(STextBlock).Text(FText::FromString(SelectionText()))];
    Box->AddSlot().AutoHeight().Padding(2)[SNew(SButton).Text(FText::FromString(TEXT("Found Settlement"))).OnClicked_Lambda([this]() { SubmitCommand(TEXT("FoundSettlement"), PayloadString(TEXT("unit_id"), SelectedUnitId)); return FReply::Handled(); })];

    const TArray<FString> Research = ResearchOptions();
    Box->AddSlot().AutoHeight().Padding(5, 8, 5, 2)[SNew(STextBlock).Text(FText::FromString(TEXT("Research")))];
    if (Research.Num() > 0)
    {
        ResearchIndex = FMath::Clamp(ResearchIndex, 0, Research.Num() - 1);
        Box->AddSlot().AutoHeight().Padding(2)
        [SNew(SButton).Text(FText::FromString(TEXT("Research: ") + Research[ResearchIndex])).OnClicked_Lambda([this, Count = Research.Num()]() { ResearchIndex = (ResearchIndex + 1) % Count; Rebuild(); return FReply::Handled(); })];
        Box->AddSlot().AutoHeight().Padding(2)
        [SNew(SButton).Text(FText::FromString(TEXT("Choose Research"))).OnClicked_Lambda([this]() { const auto Options = ResearchOptions(); if (Options.IsValidIndex(ResearchIndex)) SubmitCommand(TEXT("ChooseResearch"), PayloadString(TEXT("technology_id"), Options[ResearchIndex])); return FReply::Handled(); })];
    }

    Box->AddSlot().AutoHeight().Padding(5, 8, 5, 2)[SNew(STextBlock).Text(FText::FromString(TEXT("Settlement / Production")))];
    Box->AddSlot().AutoHeight().Padding(2)[SNew(STextBlock).Text(FText::FromString(TEXT("Settlement: ") + (SelectedSettlementId.IsEmpty() ? TEXT("none") : SelectedSettlementId)))];
    Box->AddSlot().AutoHeight().Padding(2)
    [
        SNew(SHorizontalBox)
        + SHorizontalBox::Slot().FillWidth(1.0f).Padding(1)[SNew(SButton).Text(FText::FromString(TEXT("Work tile"))).OnClicked_Lambda([this]() { SetWorkedTile(true); return FReply::Handled(); })]
        + SHorizontalBox::Slot().FillWidth(1.0f).Padding(1)[SNew(SButton).Text(FText::FromString(TEXT("Unwork tile"))).OnClicked_Lambda([this]() { SetWorkedTile(false); return FReply::Handled(); })]
    ];
    Box->AddSlot().AutoHeight().Padding(2)[SNew(SButton).Text(FText::FromString(TEXT("Kind: ") + ProductionKind)).OnClicked_Lambda([this]() { ProductionKind = ProductionKind == TEXT("unit") ? TEXT("building") : TEXT("unit"); Rebuild(); return FReply::Handled(); })];
    Box->AddSlot().AutoHeight().Padding(2)[SNew(SEditableTextBox).Text(FText::FromString(ProductionId)).HintText(FText::FromString(TEXT("definition id"))).OnTextChanged_Lambda([this](const FText& Text) { ProductionId = Text.ToString(); })];
    Box->AddSlot().AutoHeight().Padding(2)[SNew(SButton).Text(FText::FromString(TEXT("Queue Production"))).OnClicked_Lambda([this]()
    {
        const auto P = MakeShared<FJsonObject>(); P->SetStringField(TEXT("settlement_id"), SelectedSettlementId); P->SetStringField(TEXT("kind"), ProductionKind); P->SetStringField(TEXT("definition_id"), ProductionId); SubmitCommand(TEXT("QueueProduction"), P); return FReply::Handled();
    })];
    Box->AddSlot().AutoHeight().Padding(2)[SNew(SButton).Text(FText::FromString(TEXT("Cancel First Queue Item"))).OnClicked_Lambda([this]()
    {
        const auto P = MakeShared<FJsonObject>(); P->SetStringField(TEXT("settlement_id"), SelectedSettlementId); P->SetNumberField(TEXT("index"), 0); SubmitCommand(TEXT("CancelProduction"), P); return FReply::Handled();
    })];

    const auto Relations = ObjectArray(State, TEXT("diplomacy"));
    Box->AddSlot().AutoHeight().Padding(5, 8, 5, 2)[SNew(STextBlock).Text(FText::FromString(TEXT("Diplomacy")))];
    if (Relations.Num() > 0)
    {
        DiplomacyIndex = FMath::Clamp(DiplomacyIndex, 0, Relations.Num() - 1);
        const auto Relation = Relations[DiplomacyIndex];
        const FString TargetLabel = FString::Printf(TEXT("Target: %s (%s)"), *StringField(Relation, TEXT("other_player_id")), *StringField(Relation, TEXT("status")));
        Box->AddSlot().AutoHeight().Padding(2)[SNew(SButton).Text(FText::FromString(TargetLabel)).OnClicked_Lambda([this, Count = Relations.Num()]() { DiplomacyIndex = (DiplomacyIndex + 1) % Count; Rebuild(); return FReply::Handled(); })];
        Box->AddSlot().AutoHeight().Padding(2)
        [
            SNew(SHorizontalBox)
            + SHorizontalBox::Slot().FillWidth(1.0f).Padding(1)[SNew(SButton).Text(FText::FromString(TEXT("Declare War"))).OnClicked_Lambda([this]() { DiplomacyCommand(TEXT("DeclareWar")); return FReply::Handled(); })]
            + SHorizontalBox::Slot().FillWidth(1.0f).Padding(1)[SNew(SButton).Text(FText::FromString(TEXT("Offer Peace"))).OnClicked_Lambda([this]() { DiplomacyCommand(TEXT("OfferPeace")); return FReply::Handled(); })]
        ];
        Box->AddSlot().AutoHeight().Padding(2)
        [
            SNew(SHorizontalBox)
            + SHorizontalBox::Slot().FillWidth(1.0f).Padding(1)[SNew(SButton).Text(FText::FromString(TEXT("Accept Peace"))).OnClicked_Lambda([this]() { DiplomacyCommand(TEXT("AcceptPeace")); return FReply::Handled(); })]
            + SHorizontalBox::Slot().FillWidth(1.0f).Padding(1)[SNew(SButton).Text(FText::FromString(TEXT("Reject Peace"))).OnClicked_Lambda([this]() { DiplomacyCommand(TEXT("RejectPeace")); return FReply::Handled(); })]
        ];
    }

    Box->AddSlot().AutoHeight().Padding(5, 8, 5, 2)[SNew(STextBlock).Text(FText::FromString(TEXT("Turn")))];
    Box->AddSlot().AutoHeight().Padding(2)
    [
        SNew(SHorizontalBox)
        + SHorizontalBox::Slot().FillWidth(1.0f).Padding(1)[SNew(SButton).Text(FText::FromString(TEXT("End Turn"))).OnClicked_Lambda([this]() { SubmitCommand(TEXT("EndTurn"), Payload()); return FReply::Handled(); })]
        + SHorizontalBox::Slot().FillWidth(1.0f).Padding(1)[SNew(SButton).Text(FText::FromString(TEXT("Concede"))).OnClicked_Lambda([this]() { SubmitCommand(TEXT("Concede"), Payload()); return FReply::Handled(); })]
    ];

    TArray<FString> Actions;
    if (Legal.IsValid())
    {
        const TArray<TSharedPtr<FJsonValue>>* Values = nullptr;
        if (Legal->TryGetArrayField(TEXT("actions"), Values) && Values) for (const auto& Value : *Values) Actions.Add(Value->AsString());
    }
    Box->AddSlot().AutoHeight().Padding(5, 8, 5, 2)[SNew(STextBlock).Text(FText::FromString(TEXT("Legal: ") + FString::Join(Actions, TEXT(", "))))];
    Box->AddSlot().AutoHeight().Padding(5, 8, 5, 2)[SNew(STextBlock).Text(FText::FromString(TEXT("Authorized events")))];
    for (int32 Index = FMath::Max(0, EventLog.Num() - 30); Index < EventLog.Num(); ++Index)
        Box->AddSlot().AutoHeight().Padding(1)[SNew(STextBlock).Text(FText::FromString(FString::Printf(TEXT("#%d %s"), IntField(EventLog[Index], TEXT("sequence")), *StringField(EventLog[Index], TEXT("event_type")))))];

    return SNew(SScrollBox) + SScrollBox::Slot()[Box];
}
