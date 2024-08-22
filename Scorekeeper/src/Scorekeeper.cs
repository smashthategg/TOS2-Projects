using System.IO;
using System;
using SML;
using Cinematics.Players;
using HarmonyLib;
using Server.Shared.Info;
using Services;
using System.Collections.Generic;
using Game.Interface;
using Server.Shared.State;
using Server.Shared.Extensions;

namespace Scorekeeper
{
    [Mod.SalemMod]
    public class Main
    {
        public static void Start()
        {
            Scorekeeper.Utils.Logger.Log(ModInfo.PLUGIN_NAME + " has loaded!");

            // Get the directory of the Town of Salem 2
            string tos2Directory = AppDomain.CurrentDomain.BaseDirectory;
            
            // Construct the path to the "Scorekeeper" directory
            string dataDirectory = Path.Combine(tos2Directory, "SalemModLoader/ModFolders/Scorekeeper");

            Scorekeeper.Utils.Logger.Log(string.Format("TOS2 path: {0}  {1}", new object[] { tos2Directory, dataDirectory }));

            // Ensure the "Scorekeeper" directory exists
            if (!Directory.Exists(dataDirectory))
            {
                Directory.CreateDirectory(dataDirectory);
                Scorekeeper.Utils.Logger.Log("created Scorekeeper directory");
            }
        }
    }
    public static class ModInfo
    {
        public const string PLUGIN_GUID = "Scorekeeper";

        public const string PLUGIN_NAME = "Scorekeeper";

        public const string PLUGIN_VERSION = "1.0.0";
    }

    public class Scorebook
    {
        public static Dictionary<string, string> players = new Dictionary<string, string>();

        public static bool ingame = false;

        [HarmonyPatch(typeof(RoleRevealCinematicPlayer), "HandleOnMyIdentityChanged")]
        public class SavePlayers
        {
            // Token: 0x06000017 RID: 23 RVA: 0x00002490 File Offset: 0x00000690
            [HarmonyPostfix]
            public static void Postfix(RoleRevealCinematicPlayer __instance)
            {
                ingame = true;
                Scorebook.players.Clear();
                foreach (DiscussionPlayerObservation discussionPlayerObservation in Service.Game.Sim.info.discussionPlayers)
                {
                    Scorebook.players[discussionPlayerObservation.Data.gameName] = discussionPlayerObservation.Data.accountName;
                    Scorekeeper.Utils.Logger.Log(string.Format("added {0}", discussionPlayerObservation.Data.accountName));
                }

            }
        }

        [HarmonyPatch(typeof(HudLobbyPreviousGamePanel), "OnPreviousGameInfoChanged")]
        public class SaveGameResults
        {
            // Token: 0x0600001E RID: 30 RVA: 0x0000297C File Offset: 0x00000B7C
            [HarmonyPostfix]
            public static void Postfix(PreviousGameData previousGameData)
            {

                // Get the directory of the Town of Salem 2
                string tos2Directory = AppDomain.CurrentDomain.BaseDirectory;

                // Construct the path to the "Scorekeeper" directory
                string dataDirectory = Path.Combine(tos2Directory, "SalemModLoader/ModFolders/Scorekeeper");

                string filename = string.Format("{0}/{1:yyyy-MM-dd}-{2}.txt", new object[]
                {
                    dataDirectory,
                    DateTime.Now,
                    DateTime.Now.ToString("t").Replace(":", "-")
                });

                if (ingame)
                {
                    using (StreamWriter writer = new StreamWriter(filename, true))
                    {
                        foreach (PreviousGameEntry entry in previousGameData.entries)
                        {
                            string line = string.Format("{0} {1} ({2}) {3} {4} {5}", new object[]
                            {
                                entry.playerPosition + 1,
                                entry.gameName,
                                Scorebook.players.ContainsKey(entry.gameName) ? Scorebook.players[entry.gameName] : "Unknown",
                                entry.originalRole.GetRoleData().roleName,
                                entry.won ? "W" : "L",
                                entry.alive ? "A" : "D"
                            });

                            writer.WriteLine(line);
                        }
                    }
                    ingame = false;
                }
            }
        }
    }
}