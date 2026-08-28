// clients/unreal/Source/CivilizationClient/CivilizationClientGameInstance.h
#pragma once

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "CivilizationClientGameInstance.generated.h"

class SCivilizationClient;

UCLASS()
class CIVILIZATIONCLIENT_API UCivilizationClientGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;
    virtual void Shutdown() override;

private:
    TSharedPtr<SCivilizationClient> ClientWidget;
};
