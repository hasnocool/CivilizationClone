// clients/unreal/Source/CivilizationClient/SCivilizationClient.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "Dom/JsonObject.h"

class FCivilizationApiClient;
class SVerticalBox;
class SEditableTextBox;

class SCivilizationClient : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SCivilizationClient) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& Args);
    virtual void Tick(const FGeometry& AllottedGeometry, double InCurrentTime, float InDeltaTime) override;

private:
    enum class EMode : uint8 { Connect, Lobby, Game };
    struct FPlayerConfig
    {
        FString Id;
        FString Name;
        int32 CivilizationIndex = 0;
    };

    TSharedPtr<FCivilizationApiClient> Api;
    TSharedPtr<SVerticalBox> Root;
    EMode Mode = EMode::Connect;
    FString ApiUrl = TEXT("http://127.0.0.1:8000");
    FString Status = TEXT("Disconnected");
    bool bStatusError = false;
    TArray<TSharedPtr<FJsonObject>> Civilizations;
    TArray<FPlayerConfig> Players;
    FString GameIdInput = TEXT("unreal-game");
    int32 Seed = 1;
    int32 MapRadius = 4;
    int32 PlayerCount = 2;
    FString GameId;
    FString AdminToken;
    TMap<FString, FString> PlayerTokens;
    FString ViewerId;
    int32 ViewerGeneration = 0;
    TSharedPtr<FJsonObject> State;
    TSharedPtr<FJsonObject> Legal;
    TArray<TSharedPtr<FJsonObject>> EventLog;
    int32 LastEventSequence = -1;
    FString SelectedUnitId;
    FString SelectedSettlementId;
    int32 SelectedQ = MAX_int32;
    int32 SelectedR = MAX_int32;
    int32 ResearchIndex = 0;
    int32 DiplomacyIndex = 0;
    FString ProductionKind = TEXT("unit");
    FString ProductionId = TEXT("settler");
    bool bRequestInFlight = false;
    double NextRefreshTime = 0.0;

    void Rebuild();
    void BuildConnect();
    void BuildLobby();
    void BuildGame();
    TSharedRef<SWidget> BuildMap();
    TSharedRef<SWidget> BuildSidePanel();
    void SetStatus(const FString& Text, bool bError = false);

    void Connect();
    void CreateAndStart();
    void JoinNextPlayer(int32 Index);
    void RefreshAll();
    void CycleViewer();
    void SubmitCommand(const FString& CommandType, const TSharedRef<FJsonObject>& Payload);
    FReply OnTileClicked(int32 Q, int32 R);
    void SetWorkedTile(bool bWorked);
    void DiplomacyCommand(const FString& CommandType);

    FString CivilizationName(int32 Index) const;
    FString CivilizationId(int32 Index) const;
    FString SelectionText() const;
    FString FeedbackText(const TSharedPtr<FJsonObject>& Response) const;
    TArray<FString> ResearchOptions() const;
    TArray<TSharedPtr<FJsonObject>> ObjectArray(const TSharedPtr<FJsonObject>& Object, const FString& Field) const;
    static FString StringField(const TSharedPtr<FJsonObject>& Object, const FString& Field, const FString& Default = TEXT(""));
    static int32 IntField(const TSharedPtr<FJsonObject>& Object, const FString& Field, int32 Default = 0);
};
