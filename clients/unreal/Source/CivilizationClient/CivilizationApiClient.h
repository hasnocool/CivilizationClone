// clients/unreal/Source/CivilizationClient/CivilizationApiClient.h
#pragma once

#include "CoreMinimal.h"
#include "Dom/JsonObject.h"

struct FCivApiResponse
{
    bool bOk = false;
    int32 Status = 0;
    FString Detail;
    TSharedPtr<FJsonObject> Object;
    TArray<TSharedPtr<FJsonValue>> Array;
};

using FCivApiCallback = TFunction<void(const FCivApiResponse&)>;

class FCivilizationApiClient : public TSharedFromThis<FCivilizationApiClient>
{
public:
    FCivilizationApiClient();
    void Configure(const FString& Url);
    void Health(FCivApiCallback Callback);
    void Civilizations(FCivApiCallback Callback);
    void CreateGame(const FString& GameId, int32 Seed, int32 PlayerCount, int32 Radius, FCivApiCallback Callback);
    void JoinPlayer(const FString& GameId, const FString& AdminToken, const FString& PlayerId, const FString& Name, const FString& CivilizationId, FCivApiCallback Callback);
    void StartGame(const FString& GameId, const FString& AdminToken, FCivApiCallback Callback);
    void Command(const FString& GameId, const FString& Token, const FString& PlayerId, int32 ExpectedVersion, const FString& CommandType, const TSharedRef<FJsonObject>& Payload, FCivApiCallback Callback);
    void State(const FString& GameId, const FString& Token, FCivApiCallback Callback);
    void LegalActions(const FString& GameId, const FString& Token, FCivApiCallback Callback);
    void Events(const FString& GameId, const FString& Token, int32 AfterSequence, FCivApiCallback Callback);

private:
    FString BaseUrl = TEXT("http://127.0.0.1:8000");
    FString ClientId;
    int64 CommandNumber = 0;

    FString NextCommandId(const FString& Prefix);
    static FString Path(const FString& Value);
    void Request(const FString& Verb, const FString& PathValue, const FString& Body, const FString& Token, bool bArrayResponse, FCivApiCallback Callback);
};
