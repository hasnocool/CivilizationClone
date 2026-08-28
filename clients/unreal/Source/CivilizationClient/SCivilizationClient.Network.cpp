// clients/unreal/Source/CivilizationClient/SCivilizationClient.Network.cpp
#include "SCivilizationClient.h"
#include "CivilizationApiClient.h"

void SCivilizationClient::SetStatus(const FString& Text, bool bError)
{
    Status = Text;
    bStatusError = bError;
    Rebuild();
}

void SCivilizationClient::Connect()
{
    Api->Configure(ApiUrl);
    SetStatus(TEXT("Connecting…"));
    const TWeakPtr<SCivilizationClient> WeakThis = SharedThis(this);
    Api->Health([WeakThis](const FCivApiResponse& Health)
    {
        const auto Self = WeakThis.Pin(); if (!Self) return;
        if (!Health.bOk) { Self->SetStatus(TEXT("Health check failed: ") + Health.Detail, true); return; }
        Self->Api->Civilizations([WeakThis](const FCivApiResponse& Response)
        {
            const auto Pinned = WeakThis.Pin(); if (!Pinned) return;
            if (!Response.bOk) { Pinned->SetStatus(TEXT("Civilization discovery failed: ") + Response.Detail, true); return; }
            Pinned->Civilizations.Reset();
            for (const auto& Value : Response.Array) if (Value.IsValid() && Value->Type == EJson::Object) Pinned->Civilizations.Add(Value->AsObject());
            if (Pinned->Civilizations.Num() == 0) { Pinned->SetStatus(TEXT("Server returned no civilizations"), true); return; }
            for (int32 Index = 0; Index < Pinned->Players.Num(); ++Index) Pinned->Players[Index].CivilizationIndex = Index % Pinned->Civilizations.Num();
            Pinned->Mode = EMode::Lobby;
            Pinned->SetStatus(TEXT("Connected. Configure a hotseat game."));
        });
    });
}

void SCivilizationClient::CreateAndStart()
{
    if (GameIdInput.TrimStartAndEnd().IsEmpty()) { SetStatus(TEXT("Game ID is required"), true); return; }
    SetStatus(TEXT("Creating game…"));
    const TWeakPtr<SCivilizationClient> WeakThis = SharedThis(this);
    Api->CreateGame(GameIdInput.TrimStartAndEnd(), Seed, PlayerCount, MapRadius, [WeakThis](const FCivApiResponse& Response)
    {
        const auto Self = WeakThis.Pin(); if (!Self) return;
        if (!Response.bOk || !Response.Object.IsValid()) { Self->SetStatus(TEXT("Create game failed: ") + Response.Detail, true); return; }
        Self->GameId = StringField(Response.Object, TEXT("game_id"));
        Self->AdminToken = StringField(Response.Object, TEXT("admin_token"));
        if (Self->AdminToken.IsEmpty()) { Self->SetStatus(TEXT("Server did not return admin credential"), true); return; }
        Self->PlayerTokens.Reset();
        Self->JoinNextPlayer(0);
    });
}

void SCivilizationClient::JoinNextPlayer(int32 Index)
{
    if (Index >= PlayerCount)
    {
        const TWeakPtr<SCivilizationClient> WeakThis = SharedThis(this);
        Api->StartGame(GameId, AdminToken, [WeakThis](const FCivApiResponse& Response)
        {
            const auto Self = WeakThis.Pin(); if (!Self) return;
            bool bAccepted = false;
            if (!Response.bOk || !Response.Object.IsValid() || !Response.Object->TryGetBoolField(TEXT("accepted"), bAccepted) || !bAccepted)
            { Self->SetStatus(TEXT("Start game failed: ") + (Response.bOk ? Self->FeedbackText(Response.Object) : Response.Detail), true); return; }
            Self->AdminToken.Reset();
            Self->ViewerId = Self->Players[0].Id;
            Self->ViewerGeneration++;
            Self->LastEventSequence = -1;
            Self->EventLog.Reset();
            Self->Mode = EMode::Game;
            Self->SetStatus(TEXT("Game started"));
            Self->RefreshAll();
        });
        return;
    }

    FPlayerConfig& Player = Players[Index];
    const FString Id = Player.Id.TrimStartAndEnd();
    const FString Name = Player.Name.TrimStartAndEnd();
    Player.Id = Id;
    Player.Name = Name;
    const FString Civ = CivilizationId(Player.CivilizationIndex);
    const TWeakPtr<SCivilizationClient> WeakThis = SharedThis(this);
    Api->JoinPlayer(GameId, AdminToken, Id, Name, Civ, [WeakThis, Index, Id](const FCivApiResponse& Response)
    {
        const auto Self = WeakThis.Pin(); if (!Self) return;
        bool bAccepted = false;
        if (!Response.bOk || !Response.Object.IsValid() || !Response.Object->TryGetBoolField(TEXT("accepted"), bAccepted) || !bAccepted)
        { Self->SetStatus(FString::Printf(TEXT("Player %d enrollment failed: %s"), Index + 1, *(Response.bOk ? Self->FeedbackText(Response.Object) : Response.Detail)), true); return; }
        const FString Token = StringField(Response.Object, TEXT("player_token"));
        if (Token.IsEmpty()) { Self->SetStatus(TEXT("Server did not return player credential"), true); return; }
        Self->PlayerTokens.Add(Id, Token);
        Self->JoinNextPlayer(Index + 1);
    });
}

void SCivilizationClient::RefreshAll()
{
    if (bRequestInFlight || Mode != EMode::Game) return;
    const FString* Token = PlayerTokens.Find(ViewerId);
    if (!Token) return;
    bRequestInFlight = true;
    const FString Viewer = ViewerId;
    const int32 Generation = ViewerGeneration;
    const FString TokenCopy = *Token;
    const TWeakPtr<SCivilizationClient> WeakThis = SharedThis(this);

    Api->State(GameId, TokenCopy, [WeakThis, Viewer, Generation, TokenCopy](const FCivApiResponse& StateResponse)
    {
        const auto Self = WeakThis.Pin(); if (!Self) return;
        if (Generation != Self->ViewerGeneration || Viewer != Self->ViewerId) { Self->bRequestInFlight = false; return; }
        if (!StateResponse.bOk || !StateResponse.Object.IsValid()) { Self->bRequestInFlight = false; Self->SetStatus(TEXT("State refresh failed: ") + StateResponse.Detail, true); return; }
        const TSharedPtr<FJsonObject> NewState = StateResponse.Object;
        Self->Api->LegalActions(Self->GameId, TokenCopy, [WeakThis, Viewer, Generation, TokenCopy, NewState](const FCivApiResponse& LegalResponse)
        {
            const auto Pinned = WeakThis.Pin(); if (!Pinned) return;
            if (Generation != Pinned->ViewerGeneration || Viewer != Pinned->ViewerId) { Pinned->bRequestInFlight = false; return; }
            if (!LegalResponse.bOk || !LegalResponse.Object.IsValid()) { Pinned->bRequestInFlight = false; Pinned->SetStatus(TEXT("Legal-action refresh failed: ") + LegalResponse.Detail, true); return; }
            const TSharedPtr<FJsonObject> NewLegal = LegalResponse.Object;
            Pinned->Api->Events(Pinned->GameId, TokenCopy, Pinned->LastEventSequence, [WeakThis, Viewer, Generation, NewState, NewLegal](const FCivApiResponse& EventResponse)
            {
                const auto Final = WeakThis.Pin(); if (!Final) return;
                if (Generation != Final->ViewerGeneration || Viewer != Final->ViewerId) { Final->bRequestInFlight = false; return; }
                if (!EventResponse.bOk) { Final->bRequestInFlight = false; Final->SetStatus(TEXT("Event refresh failed: ") + EventResponse.Detail, true); return; }
                Final->State = NewState;
                Final->Legal = NewLegal;
                for (const auto& Value : EventResponse.Array)
                {
                    if (!Value.IsValid() || Value->Type != EJson::Object) continue;
                    const auto Event = Value->AsObject();
                    Final->EventLog.Add(Event);
                    Final->LastEventSequence = FMath::Max(Final->LastEventSequence, IntField(Event, TEXT("sequence"), -1));
                }
                if (Final->EventLog.Num() > 100) Final->EventLog.RemoveAt(0, Final->EventLog.Num() - 100);
                Final->bRequestInFlight = false;
                Final->Rebuild();
            });
        });
    });
}

void SCivilizationClient::CycleViewer()
{
    if (PlayerCount <= 0) return;
    int32 Current = 0;
    for (int32 Index = 0; Index < PlayerCount; ++Index) if (Players[Index].Id == ViewerId) { Current = Index; break; }
    ViewerId = Players[(Current + 1) % PlayerCount].Id;
    ViewerGeneration++;
    State.Reset(); Legal.Reset(); EventLog.Reset(); LastEventSequence = -1;
    SelectedUnitId.Reset(); SelectedSettlementId.Reset(); SelectedQ = SelectedR = MAX_int32;
    bRequestInFlight = false; NextRefreshTime = 0.0;
    SetStatus(TEXT("Viewer switched to ") + ViewerId);
}

void SCivilizationClient::SubmitCommand(const FString& CommandType, const TSharedRef<FJsonObject>& PayloadValue)
{
    if (!State.IsValid() || ViewerId.IsEmpty()) return;
    const FString* Token = PlayerTokens.Find(ViewerId); if (!Token) return;
    const int32 Version = IntField(State, TEXT("state_version"), -1);
    const int32 Generation = ViewerGeneration;
    const FString Viewer = ViewerId;
    const TWeakPtr<SCivilizationClient> WeakThis = SharedThis(this);
    Api->Command(GameId, *Token, Viewer, Version, CommandType, PayloadValue, [WeakThis, Generation, Viewer, CommandType](const FCivApiResponse& Response)
    {
        const auto Self = WeakThis.Pin(); if (!Self) return;
        if (Generation != Self->ViewerGeneration || Viewer != Self->ViewerId) return;
        bool bAccepted = false;
        if (!Response.bOk || !Response.Object.IsValid() || !Response.Object->TryGetBoolField(TEXT("accepted"), bAccepted)) { Self->SetStatus(CommandType + TEXT(" failed: ") + Response.Detail, true); return; }
        if (!bAccepted) { Self->SetStatus(Self->FeedbackText(Response.Object), true); return; }
        Self->Status = TEXT("Accepted: ") + CommandType; Self->bStatusError = false;
        if (CommandType == TEXT("MoveUnit") || CommandType == TEXT("AttackUnit") || CommandType == TEXT("FoundSettlement")) Self->SelectedUnitId.Reset();
        Self->RefreshAll();
    });
}
