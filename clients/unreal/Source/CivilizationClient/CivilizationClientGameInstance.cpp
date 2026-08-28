// clients/unreal/Source/CivilizationClient/CivilizationClientGameInstance.cpp
#include "CivilizationClientGameInstance.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "SCivilizationClient.h"

void UCivilizationClientGameInstance::Init()
{
    Super::Init();
    if (IsRunningDedicatedServer()) return;
    ClientWidget = SNew(SCivilizationClient);
    if (GEngine && GEngine->GameViewport)
        GEngine->GameViewport->AddViewportWidgetContent(ClientWidget.ToSharedRef(), 100);
}

void UCivilizationClientGameInstance::Shutdown()
{
    if (ClientWidget.IsValid() && GEngine && GEngine->GameViewport)
        GEngine->GameViewport->RemoveViewportWidgetContent(ClientWidget.ToSharedRef());
    ClientWidget.Reset();
    Super::Shutdown();
}
