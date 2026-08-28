// clients/unity/Assets/Scripts/CivilizationClientBootstrap.cs
using UnityEngine;

namespace CivilizationClone.UnityClient
{
    internal static class CivilizationClientBootstrap
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Install()
        {
            if (Object.FindFirstObjectByType<CivilizationClientApp>() != null) return;
            var gameObject = new GameObject("CivilizationClone Unity Client");
            Object.DontDestroyOnLoad(gameObject);
            gameObject.AddComponent<CivilizationClientApp>();
        }
    }
}
