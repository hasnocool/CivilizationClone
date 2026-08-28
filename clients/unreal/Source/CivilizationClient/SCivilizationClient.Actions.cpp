// clients/unreal/Source/CivilizationClient/SCivilizationClient.Actions.cpp
#include "SCivilizationClient.h"

namespace
{
TSharedRef<FJsonObject> PayloadString(const FString& Key, const FString& Value)
{
    const TSharedRef<FJsonObject> Result = MakeShared<FJsonObject>();
    Result->SetStringField(Key, Value);
    return Result;
}
}

FReply SCivilizationClient::OnTileClicked(int32 Q, int32 R)
{
    SelectedQ = Q; SelectedR = R;
    for (const auto& Unit : ObjectArray(State, TEXT("units")))
    {
        if (IntField(Unit, TEXT("q")) != Q || IntField(Unit, TEXT("r")) != R) continue;
        const FString Owner = StringField(Unit, TEXT("owner_id"));
        if (Owner == ViewerId) { SelectedUnitId = StringField(Unit, TEXT("unit_id")); Rebuild(); return FReply::Handled(); }
        if (!SelectedUnitId.IsEmpty())
        {
            const auto P = MakeShared<FJsonObject>(); P->SetStringField(TEXT("attacker_id"), SelectedUnitId); P->SetStringField(TEXT("defender_id"), StringField(Unit, TEXT("unit_id"))); SubmitCommand(TEXT("AttackUnit"), P); return FReply::Handled();
        }
    }
    for (const auto& City : ObjectArray(State, TEXT("settlements")))
    {
        if (IntField(City, TEXT("q")) == Q && IntField(City, TEXT("r")) == R && StringField(City, TEXT("owner_id")) == ViewerId)
        { SelectedSettlementId = StringField(City, TEXT("settlement_id")); Rebuild(); return FReply::Handled(); }
    }
    if (!SelectedUnitId.IsEmpty())
    {
        const auto P = MakeShared<FJsonObject>(); P->SetStringField(TEXT("unit_id"), SelectedUnitId); P->SetNumberField(TEXT("q"), Q); P->SetNumberField(TEXT("r"), R); SubmitCommand(TEXT("MoveUnit"), P);
    }
    else Rebuild();
    return FReply::Handled();
}

void SCivilizationClient::SetWorkedTile(bool bWorked)
{
    if (SelectedSettlementId.IsEmpty() || SelectedQ == MAX_int32) { SetStatus(TEXT("Choose a settlement and tile first"), true); return; }
    const auto P = MakeShared<FJsonObject>(); P->SetStringField(TEXT("settlement_id"), SelectedSettlementId); P->SetNumberField(TEXT("q"), SelectedQ); P->SetNumberField(TEXT("r"), SelectedR); P->SetBoolField(TEXT("worked"), bWorked); SubmitCommand(TEXT("SetWorkedTile"), P);
}

void SCivilizationClient::DiplomacyCommand(const FString& CommandType)
{
    const auto Relations = ObjectArray(State, TEXT("diplomacy"));
    if (!Relations.IsValidIndex(DiplomacyIndex)) return;
    SubmitCommand(CommandType, PayloadString(TEXT("target_player_id"), StringField(Relations[DiplomacyIndex], TEXT("other_player_id"))));
}

FString SCivilizationClient::CivilizationName(int32 Index) const
{
    if (!Civilizations.IsValidIndex(Index)) return TEXT("No civilization");
    return StringField(Civilizations[Index], TEXT("name"), StringField(Civilizations[Index], TEXT("civilization_id"), TEXT("?")));
}

FString SCivilizationClient::CivilizationId(int32 Index) const
{
    return Civilizations.IsValidIndex(Index) ? StringField(Civilizations[Index], TEXT("civilization_id")) : TEXT("river_compact");
}

FString SCivilizationClient::SelectionText() const
{
    TArray<FString> Parts;
    if (!SelectedUnitId.IsEmpty()) Parts.Add(TEXT("unit ") + SelectedUnitId);
    if (!SelectedSettlementId.IsEmpty()) Parts.Add(TEXT("settlement ") + SelectedSettlementId);
    if (SelectedQ != MAX_int32) Parts.Add(FString::Printf(TEXT("tile (%d,%d)"), SelectedQ, SelectedR));
    return Parts.Num() == 0 ? TEXT("none") : FString::Join(Parts, TEXT(", "));
}

FString SCivilizationClient::FeedbackText(const TSharedPtr<FJsonObject>& Response) const
{
    if (!Response.IsValid()) return TEXT("Command rejected");
    TArray<FString> Lines;
    for (const auto& Item : ObjectArray(Response, TEXT("feedback"))) Lines.Add(StringField(Item, TEXT("code"), TEXT("ERROR")) + TEXT(": ") + StringField(Item, TEXT("message")));
    return Lines.Num() == 0 ? TEXT("Command rejected") : FString::Join(Lines, TEXT(" | "));
}

TArray<FString> SCivilizationClient::ResearchOptions() const
{
    TArray<FString> Result;
    if (State.IsValid())
    {
        const TSharedPtr<FJsonObject>* Viewer = nullptr; const TSharedPtr<FJsonObject>* Research = nullptr;
        if (State->TryGetObjectField(TEXT("viewer"), Viewer) && Viewer && Viewer->IsValid() && (*Viewer)->TryGetObjectField(TEXT("research"), Research) && Research && Research->IsValid())
        {
            const TArray<TSharedPtr<FJsonValue>>* Values = nullptr;
            if ((*Research)->TryGetArrayField(TEXT("available"), Values) && Values) for (const auto& Value : *Values) Result.Add(Value->AsString());
        }
    }
    if (Result.Num() == 0 && Legal.IsValid())
    {
        for (const auto& Decision : ObjectArray(Legal, TEXT("mandatory_decisions")))
        {
            if (StringField(Decision, TEXT("kind")) != TEXT("research")) continue;
            const TArray<TSharedPtr<FJsonValue>>* Values = nullptr;
            if (Decision->TryGetArrayField(TEXT("options"), Values) && Values) for (const auto& Value : *Values) Result.Add(Value->AsString());
        }
    }
    return Result;
}

TArray<TSharedPtr<FJsonObject>> SCivilizationClient::ObjectArray(const TSharedPtr<FJsonObject>& Object, const FString& Field) const
{
    TArray<TSharedPtr<FJsonObject>> Result;
    if (!Object.IsValid()) return Result;
    const TArray<TSharedPtr<FJsonValue>>* Values = nullptr;
    if (!Object->TryGetArrayField(Field, Values) || !Values) return Result;
    for (const auto& Value : *Values) if (Value.IsValid() && Value->Type == EJson::Object) Result.Add(Value->AsObject());
    return Result;
}

FString SCivilizationClient::StringField(const TSharedPtr<FJsonObject>& Object, const FString& Field, const FString& Default)
{
    if (!Object.IsValid()) return Default;
    FString Value; return Object->TryGetStringField(Field, Value) ? Value : Default;
}

int32 SCivilizationClient::IntField(const TSharedPtr<FJsonObject>& Object, const FString& Field, int32 Default)
{
    if (!Object.IsValid()) return Default;
    double Value = Default; return Object->TryGetNumberField(Field, Value) ? static_cast<int32>(Value) : Default;
}
