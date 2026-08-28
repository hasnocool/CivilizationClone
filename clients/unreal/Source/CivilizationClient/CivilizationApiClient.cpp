// clients/unreal/Source/CivilizationClient/CivilizationApiClient.cpp
#include "CivilizationApiClient.h"
#include "GenericPlatform/GenericPlatformHttp.h"
#include "HttpModule.h"
#include "Interfaces/IHttpRequest.h"
#include "Interfaces/IHttpResponse.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

namespace
{
FString JsonString(const TSharedRef<FJsonObject>& Object)
{
    FString Output;
    const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Output);
    FJsonSerializer::Serialize(Object, Writer);
    return Output;
}

FString ErrorDetail(const FString& Content, int32 Status)
{
    TSharedPtr<FJsonObject> Object;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Content);
    if (FJsonSerializer::Deserialize(Reader, Object) && Object.IsValid())
    {
        FString Detail;
        if (Object->TryGetStringField(TEXT("detail"), Detail)) return Detail;
    }
    return FString::Printf(TEXT("HTTP %d"), Status);
}
}

FCivilizationApiClient::FCivilizationApiClient() : ClientId(FGuid::NewGuid().ToString(EGuidFormats::Digits)) {}

void FCivilizationApiClient::Configure(const FString& Url)
{
    BaseUrl = Url.TrimStartAndEnd();
    while (BaseUrl.EndsWith(TEXT("/"))) BaseUrl.LeftChopInline(1);
}

void FCivilizationApiClient::Health(FCivApiCallback Callback) { Request(TEXT("GET"), TEXT("/api/v1/health"), TEXT(""), TEXT(""), false, MoveTemp(Callback)); }
void FCivilizationApiClient::Civilizations(FCivApiCallback Callback) { Request(TEXT("GET"), TEXT("/api/v1/rules/civilizations"), TEXT(""), TEXT(""), true, MoveTemp(Callback)); }

void FCivilizationApiClient::CreateGame(const FString& GameId, int32 Seed, int32 PlayerCount, int32 Radius, FCivApiCallback Callback)
{
    const TSharedRef<FJsonObject> Body = MakeShared<FJsonObject>();
    Body->SetStringField(TEXT("game_id"), GameId);
    Body->SetNumberField(TEXT("seed"), Seed);
    Body->SetNumberField(TEXT("player_count"), PlayerCount);
    Body->SetNumberField(TEXT("map_radius"), Radius);
    Body->SetNumberField(TEXT("water_percent"), 20);
    Body->SetNumberField(TEXT("resource_percent"), 18);
    Request(TEXT("POST"), TEXT("/api/v1/games"), JsonString(Body), TEXT(""), false, MoveTemp(Callback));
}

void FCivilizationApiClient::JoinPlayer(const FString& GameId, const FString& AdminToken, const FString& PlayerId, const FString& Name, const FString& CivilizationId, FCivApiCallback Callback)
{
    const TSharedRef<FJsonObject> Body = MakeShared<FJsonObject>();
    Body->SetStringField(TEXT("command_id"), NextCommandId(TEXT("join")));
    Body->SetStringField(TEXT("player_id"), PlayerId);
    Body->SetStringField(TEXT("name"), Name);
    Body->SetStringField(TEXT("controller"), TEXT("human"));
    Body->SetStringField(TEXT("civilization_id"), CivilizationId);
    Request(TEXT("POST"), FString::Printf(TEXT("/api/v1/games/%s/players"), *Path(GameId)), JsonString(Body), AdminToken, false, MoveTemp(Callback));
}

void FCivilizationApiClient::StartGame(const FString& GameId, const FString& AdminToken, FCivApiCallback Callback)
{
    Command(GameId, AdminToken, TEXT(""), -1, TEXT("StartGame"), MakeShared<FJsonObject>(), MoveTemp(Callback));
}

void FCivilizationApiClient::Command(const FString& GameId, const FString& Token, const FString& PlayerId, int32 ExpectedVersion, const FString& CommandType, const TSharedRef<FJsonObject>& Payload, FCivApiCallback Callback)
{
    const TSharedRef<FJsonObject> Body = MakeShared<FJsonObject>();
    Body->SetStringField(TEXT("command_id"), NextCommandId(CommandType.ToLower()));
    Body->SetStringField(TEXT("command_type"), CommandType);
    if (!PlayerId.IsEmpty()) Body->SetStringField(TEXT("player_id"), PlayerId);
    if (ExpectedVersion >= 0) Body->SetNumberField(TEXT("expected_state_version"), ExpectedVersion);
    Body->SetObjectField(TEXT("payload"), Payload);
    Request(TEXT("POST"), FString::Printf(TEXT("/api/v1/games/%s/commands"), *Path(GameId)), JsonString(Body), Token, false, MoveTemp(Callback));
}

void FCivilizationApiClient::State(const FString& GameId, const FString& Token, FCivApiCallback Callback) { Request(TEXT("GET"), FString::Printf(TEXT("/api/v1/games/%s/state"), *Path(GameId)), TEXT(""), Token, false, MoveTemp(Callback)); }
void FCivilizationApiClient::LegalActions(const FString& GameId, const FString& Token, FCivApiCallback Callback) { Request(TEXT("GET"), FString::Printf(TEXT("/api/v1/games/%s/legal-actions"), *Path(GameId)), TEXT(""), Token, false, MoveTemp(Callback)); }
void FCivilizationApiClient::Events(const FString& GameId, const FString& Token, int32 AfterSequence, FCivApiCallback Callback) { Request(TEXT("GET"), FString::Printf(TEXT("/api/v1/games/%s/events?after_sequence=%d"), *Path(GameId), AfterSequence), TEXT(""), Token, true, MoveTemp(Callback)); }

FString FCivilizationApiClient::NextCommandId(const FString& Prefix) { return FString::Printf(TEXT("unreal-%s-%s-%lld"), *ClientId, *Prefix, ++CommandNumber); }
FString FCivilizationApiClient::Path(const FString& Value) { return FGenericPlatformHttp::UrlEncode(Value); }

void FCivilizationApiClient::Request(const FString& Verb, const FString& PathValue, const FString& Body, const FString& Token, bool bArrayResponse, FCivApiCallback Callback)
{
    const TSharedRef<IHttpRequest, ESPMode::ThreadSafe> Http = FHttpModule::Get().CreateRequest();
    Http->SetURL(BaseUrl + PathValue);
    Http->SetVerb(Verb);
    Http->SetHeader(TEXT("Accept"), TEXT("application/json"));
    if (!Token.IsEmpty()) Http->SetHeader(TEXT("Authorization"), TEXT("Bearer ") + Token);
    if (!Body.IsEmpty()) { Http->SetHeader(TEXT("Content-Type"), TEXT("application/json")); Http->SetContentAsString(Body); }

    Http->OnProcessRequestComplete().BindLambda([bArrayResponse, Callback = MoveTemp(Callback)](FHttpRequestPtr, FHttpResponsePtr Response, bool bConnected) mutable
    {
        FCivApiResponse Result;
        Result.Status = Response.IsValid() ? Response->GetResponseCode() : 0;
        const FString Content = Response.IsValid() ? Response->GetContentAsString() : FString();
        Result.bOk = bConnected && Response.IsValid() && Result.Status >= 200 && Result.Status < 300;
        if (!Result.bOk)
        {
            Result.Detail = Response.IsValid() ? ErrorDetail(Content, Result.Status) : TEXT("network request failed");
            Callback(Result);
            return;
        }

        if (bArrayResponse)
        {
            const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Content);
            if (!FJsonSerializer::Deserialize(Reader, Result.Array)) { Result.bOk = false; Result.Detail = TEXT("server returned invalid JSON array"); }
        }
        else
        {
            const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Content);
            if (!FJsonSerializer::Deserialize(Reader, Result.Object) || !Result.Object.IsValid()) { Result.bOk = false; Result.Detail = TEXT("server returned invalid JSON object"); }
        }
        Callback(Result);
    });

    if (!Http->ProcessRequest())
    {
        FCivApiResponse Result;
        Result.Detail = TEXT("request could not be started");
        Callback(Result);
    }
}
