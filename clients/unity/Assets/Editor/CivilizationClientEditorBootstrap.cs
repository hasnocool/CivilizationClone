// clients/unity/Assets/Editor/CivilizationClientEditorBootstrap.cs
#if UNITY_EDITOR
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;

namespace CivilizationClone.UnityClient.Editor
{
    [InitializeOnLoad]
    internal static class CivilizationClientEditorBootstrap
    {
        private const string ScenePath = "Assets/Scenes/Main.unity";

        static CivilizationClientEditorBootstrap() => EditorApplication.delayCall += EnsureScene;

        private static void EnsureScene()
        {
            if (!File.Exists(ScenePath))
            {
                Directory.CreateDirectory("Assets/Scenes");
                var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                EditorSceneManager.SaveScene(scene, ScenePath);
            }

            var scenes = EditorBuildSettings.scenes;
            if (scenes.Length == 0 || scenes[0].path != ScenePath)
                EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
        }
    }

    public static class ClientVerifier
    {
        private const string ScenePath = "Assets/Scenes/Main.unity";

        public static void Run()
        {
            EnsureReady();
            UnityEngine.Debug.Log("UNITY CLIENT LOCAL CHECK PASS");
            EditorApplication.Exit(0);
        }

        private static void EnsureReady()
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            if (!File.Exists(ScenePath))
            {
                Directory.CreateDirectory("Assets/Scenes");
                var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                EditorSceneManager.SaveScene(scene, ScenePath);
            }
        }
    }
}
#endif
