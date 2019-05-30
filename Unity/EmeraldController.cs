using System;
using System.Collections;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Globalization;
using System.Linq;
using UnityEngine;
using UnityEngine.Networking;

public class EmeraldController : MonoBehaviour {
    private const string baseSite = "http://127.0.0.1:8000/";

    private static string site = baseSite;

    private static EmeraldController instance;

    internal static List<Player> players;

    public string gameKey = "52cdd96a-4dac-4399-a8b9-19a8e7b878f5";

    public bool Sandbox = true;

    private Match match;

    internal static EmeraldController Instance {
        get {
            if (instance == null)
                throw new NoEmeraldControllerInstanceException();
            return instance;
        }
    }

    public static ReadOnlyCollection<Player> Players {
        get { return players.AsReadOnly(); }
    }

    public static string GameKey {
        get { return Instance.gameKey; }
    }

    public static Match Match {
        get { return Instance.match; }
    }

    private void Awake() {
        players = new List<Player>();
        if (instance != null)
            throw new MultipleEmeraldControllersException();
        instance = this;
        if (this.Sandbox)
            site = baseSite + "sandbox/";
    }

    private void OnDestroy() {
        if (Instance == this)
            instance = null;
    }

    public static bool MatchAlive() {
        if (Match == null) return false;
        return (Match.State == MatchState.Registering || Match.State == MatchState.Active) && Match.Key != string.Empty;
    }

    public static Player GetPlayer(string username) {
        try {
            return players.Find(p => p.Username == username);
        } catch (InvalidOperationException) {
            throw new PlayerNotFoundException();
        }
    }

    private static void HandleError(string errorMessage) {
        var error = JsonUtility.FromJson<Error>(errorMessage);
        var ex = EmeraldException.GetException(error);
        throw ex;
    }

    #region Program requests

    #region Login

    /// <include file='Emerald.xml' path='docs/members[Name="EmeraldController"]/Login'/>
    public static void Login(string username, string password, Action<Player> callback = null, Action<Exception> eHandler = null) {
        WWWForm form;
        try {
            if (players.Find(u => u.Username == username) != null) {
                throw new InvalidOperationException("The given player is already logged in.");
            }
            form = CreateLoginForm(username, password);
        } catch (Exception e) {
            if (eHandler != null) {
                eHandler(e);
                return;
            } else throw;
        }
        Instance.StartCoroutine(SendPost(site + "authtoken/", form, authtoken => { Login(authtoken.Value, callback, eHandler); }, eHandler));
    }

    public static void Login(string key, Action<Player> callback = null, Action<Exception> eHandler = null) {
        Instance.login(key, callback, eHandler);
    }

    private void login(string key, Action<Player> callback, Action<Exception> eHandler) {
        var token = new Token {Value = key};
        var headers = new Dictionary<string, string> {
            {this.Sandbox ? "SANDBOXAUTHORIZATION" : "AUTHORIZATION", "Token " + token.Value},
            {"GAMEKEY", GameKey}
        };
        this.StartCoroutine(SendGet(site + "playerinfo/", player =>
        {
            var existingPlayer = players.FirstOrDefault(p => p.AuthToken == player.AuthToken);
            if (existingPlayer != null)
            {
                existingPlayer.update(player);
            }
            else
            {
                players.Add(player);
            }
            
            if (callback != null)
                callback(player);
        }, eHandler, headers));
    }

    #endregion

    #region Logout

    public static void Logout(Player player) {
        // What if the player isn't logged in
        players.Remove(player);
    }

    #endregion

    #region UpdatePlayerInfo

    /// <include file='Emerald.xml' path='docs/members[Name="EmeraldController"]/Login'/>
    public static void UpdatePlayerInfo(string username, Action<Player> callback = null, Action<Exception> eHandler = null) {
        Player player;
        try {
            player = players.Find(u => u.Username == username);
        } catch (Exception e) {
            if (eHandler != null) {
                eHandler(e);
                return;
            } else throw;
        }

        UpdatePlayerInfo(player, callback, eHandler);
    }

    public static void UpdatePlayerInfo(Player player, Action<Player> callback, Action<Exception> eHandler) {
        var headers = CreateHeadersWithToken(player);
        Instance.StartCoroutine(SendGet(site + "playerinfo/", (p) => {
            if (callback != null)
                callback(player);
        }, eHandler, headers));
    }

    #endregion

    /// <include file='Emerald.xml' path='docs/members[Name="EmeraldController"]/CreateMatch'/>
    public static void CreateMatch(float wager, string matchType = null, Action callback = null, Action<Exception> eHandler = null) {
        if (MatchAlive()) {
            var e = new MatchAliveException();
            if (eHandler == null) throw e;
            eHandler(e);
            return;
        }
        WWWForm form = CreateMatchForm(wager, matchType);
        Instance.StartCoroutine(SendPost(site + "creatematch/", form, () => {
            if (callback != null)
                callback();
        }, eHandler, true));
    }

    public static void CreateMatch(float wager, Action callback, Action<Exception> eHandler = null) {
        CreateMatch(wager, null, callback, eHandler);
    }

    public static void StartMatch(Action callback = null, Action<Exception> eHandler = null) {
        var form = new WWWForm();
        form.AddField("gameKey", GameKey);
        AddMatchKeyToForm(form);
        Instance.StartCoroutine(SendPost((site + "startmatch/"), form, () => {
            if (callback != null)
                callback();
        }, eHandler));
    }

    #region EndMatch

    public static void EndMatch(PlayerGroup playerGroup, Action callback = null, Action<Exception> eHandler = null) {
        var groupName = playerGroup.Name;
        EndMatch(groupName, callback, eHandler);
    }

    /// <include file='Emerald.xml' path='docs/members[Name="EmeraldController"]/EndMatch'/>
    public static void EndMatch(string groupName, Action callback = null, Action<Exception> eHandler = null) {
        var form = new WWWForm();
        form.AddField("gameKey", GameKey);
        AddMatchKeyToForm(form);
        form.AddField("groupName", groupName);
        Instance.StartCoroutine(SendPost(site + "endmatch/", form, () => {
            if (callback != null)
                callback();
        }, eHandler));
    }

    #endregion

    #region UpdateMatch

    /// <include file='Emerald.xml' path='docs/members[Name="EmeraldController"]/UpdateMatch'/>
    public static void UpdateMatch(Action callback, Action<Exception> eHandler = null) {
        var form = new WWWForm();
        form.AddField("gameKey", GameKey);
        AddMatchKeyToForm(form);
        Instance.StartCoroutine(SendPost(site + "getmatch/", form, () => {
            if (callback != null)
                callback();
        }, eHandler));
    }

    #endregion

    /// <include file='Emerald.xml' path='docs/members[Name="EmeraldController"]/CreatePlayerGroup'/>
    public static void CreatePlayerGroup(string groupName, Action<PlayerGroup> callback = null, Action<Exception> eHandler = null) {
        var form = new WWWForm();
        form.AddField("gameKey", GameKey);
        AddMatchKeyToForm(form);
        form.AddField("groupName", groupName);
        Instance.StartCoroutine(SendPost(site + "createplayergroup/", form, () => { PlayerGroupCallback(groupName, callback, eHandler); }, eHandler));
    }

    public static void CreateSoloPlayerGroup(Player player, Action<PlayerGroup> callback = null, Action<Exception> eHandler = null) {
        CreateSoloPlayerGroup(player.AuthToken, callback, eHandler);
    }

    public static void CreateSoloPlayerGroup(string authToken, Action<PlayerGroup> callback = null, Action<Exception> eHandler = null) {
        var form = new WWWForm();
        form.AddField("gameKey", GameKey);
        AddMatchKeyToForm(form);
        form.AddField("auth_token", authToken);
        Instance.StartCoroutine(SendPost(site + "createsoloplayergroup/", form, () =>
        {
            var group = players.First(p => p.AuthToken == authToken).PlayerGroup;
            if (callback != null)
                callback(group);
        }, eHandler));
    }

    #region AddPlayerToGroup

    /// <include file='Emerald.xml' path='docs/members[Name="EmeraldController"]/AddPlayerToGroup'/>
    public static void AddPlayerToGroup(string groupName, string playerUsername, Action<PlayerGroup> callback = null,
                                        Action<Exception> eHandler = null) {
        string key;
        try {
            key = GetPlayerKey(playerUsername);
        } catch (PlayerNotFoundException e) {
            if (eHandler != null) {
                eHandler(e);
                return;
            } else throw;
        }
        AddPlayerToGroupToken(groupName, key, callback, eHandler);
    }

    public static void AddPlayerToGroup(string groupName, Player player, Action<PlayerGroup> callback = null,
                                        Action<Exception> eHandler = null) {
        var key = player.AuthToken;
        AddPlayerToGroupToken(groupName, key, callback, eHandler);
    }

    public static void AddPlayerToGroup(PlayerGroup group, string playerUsername, Action<PlayerGroup> callback = null,
                                        Action<Exception> eHandler = null) {
        AddPlayerToGroup(group.Name, playerUsername, callback, eHandler);
    }

    public static void AddPlayerToGroup(PlayerGroup group, Player player, Action<PlayerGroup> callback = null,
                                        Action<Exception> eHandler = null) {
        var groupName = group.Name;
        var key = player.AuthToken;
        AddPlayerToGroupToken(groupName, key, callback, eHandler);
    }

    public static void AddPlayerToGroupToken(string groupName, string key, Action<PlayerGroup> callback = null,
                                             Action<Exception> eHandler = null) {
        PlayerGroup playerGroup;

        try {
            playerGroup = FindPlayerGroupByName(groupName);
        } catch (PlayerGroupNotFoundException e) {
            if (eHandler != null) {
                eHandler(e);
                return;
            } else throw;
        }

        var form = new WWWForm();
        form.AddField("gameKey", GameKey);
        form.AddField("groupName", playerGroup.Name);
        form.AddField("auth_token", key);
        AddMatchKeyToForm(form);
        Instance.StartCoroutine(SendPost(site + "addplayertogroup/", form, () => { PlayerGroupCallback(groupName, callback, eHandler); }, eHandler));
    }

    #endregion

    #region RemovePlayerGroup

    public static void RemovePlayerGroup(PlayerGroup group, Action callback = null,
                                         Action<Exception> eHandler = null) {
        var groupName = group.Name;
        RemovePlayerGroup(groupName, callback, eHandler);
    }

    public static void RemovePlayerGroup(string groupName, Action callback = null,
                                         Action<Exception> eHandler = null) {
        PlayerGroup playerGroup;

        try {
            playerGroup = FindPlayerGroupByName(groupName);
        } catch (PlayerGroupNotFoundException e) {
            if (eHandler != null) {
                eHandler(e);
                return;
            } else throw;
        }

        var form = new WWWForm();
        form.AddField("gameKey", GameKey);
        form.AddField("groupName", playerGroup.Name);
        AddMatchKeyToForm(form);
        Instance.StartCoroutine(SendPost(site + "removeplayergroup/", form, () => {
            if (callback != null)
                callback();
        }, eHandler));
    }

    #endregion

    public static void AbortMatch(Action callback = null, Action<Exception> eHandler = null) {
        var form = new WWWForm();
        form.AddField("gameKey", GameKey);
        AddMatchKeyToForm(form);
        Instance.StartCoroutine(SendPost(site + "abortmatch/", form, () => {
            if (callback != null)
                callback();
        }, eHandler));
    }

    #region PlayerQuit

    public static void PlayerQuit(Player player, Action callback = null,
                                  Action<Exception> eHandler = null) {
        PlayerQuit(player.AuthToken, callback, eHandler);
    }

    public static void PlayerQuit(string authToken, Action callback = null, Action<Exception> eHandler = null) {
        var form = new WWWForm();
        form.AddField("gameKey", GameKey);
        AddMatchKeyToForm(form);
        form.AddField("auth_token", authToken);
        Instance.StartCoroutine(SendPost(site + "playerquit/", form, () => {
            if (callback != null)
                callback();
        }, eHandler));
    }

    #endregion

    #endregion

    #region Helpers

    /// <include file='Emerald.xml' path='docs/members[Name="EmeraldController"]/createHeadersWithToken'/>
    private static Dictionary<string, string> CreateHeadersWithToken(Player player) {
        var headers = new Dictionary<string, string> {{Instance.Sandbox ? "SANDBOXAUTHORIZATION" : "AUTHORIZATION", "Token " + player.AuthToken}, {"GAMEKEY", GameKey}};
        return headers;
    }

    private static void AddMatchKeyToForm(WWWForm form) {
        form.AddField("matchKey", Match.Key);
    }

    private static WWWForm CreateLoginForm(string username, string password) {
        var form = new WWWForm();
        form.AddField("username", username);
        form.AddField("password", password);
        form.AddField("gameKey", GameKey);

        return form;
    }

    private static WWWForm CreateMatchForm(float wager, string matchType = null) {
        var form = new WWWForm();
        form.AddField("gameKey", GameKey);
        form.AddField("wager", wager.ToString(CultureInfo.InvariantCulture));
        if (matchType != null)
            form.AddField("matchType", matchType);
        return form;
    }

    private static string GetPlayerKey(string username) {
        try {
            return Players.First(u => u.Username == username).AuthToken;
        } catch (InvalidOperationException) {
            throw new PlayerNotFoundException();
        }
    }

    private static void PlayerGroupCallback(string groupName, Action<PlayerGroup> callback, Action<Exception> eHandler) {
        try {
            var group = FindPlayerGroupByName(groupName);
            if (callback != null)
                callback(group);
        } catch (PlayerGroupNotFoundException e) {
            if (eHandler != null)
                eHandler(e);
        }
    }

    private static PlayerGroup FindPlayerGroupByName(string groupName) {
        try {
            return Instance.match.PlayerGroups.First(u => u.Name == groupName);
        } catch (InvalidOperationException) {
            throw new PlayerGroupNotFoundException();
        }
    }

    private static bool HandleNetWorkHttpError(UnityWebRequest www, Action<Exception> eHandler) {
        if (www.isNetworkError || www.isHttpError) {
            try {
                HandleError(www.downloadHandler.text);
            } catch (EmeraldException e) {
                if (eHandler != null)
                    eHandler(e);
                else throw;
            } catch (Exception) {
                if (eHandler != null)
                    eHandler(new Exception(www.error));
                else throw;
            }

            return true;
        }
        return false;
    }

    private static Player GetPlayerFromWebRequest(UnityWebRequest www) {
        var player = JsonUtility.FromJson<Player>(www.downloadHandler.text);
        if (player.AuthToken == null)
            HandleError(www.downloadHandler.text);
        return player;
    }

    private static Match GetMatchFromWebRequest(UnityWebRequest www) {
        var match = JsonUtility.FromJson<Match>(www.downloadHandler.text);
        if (match.Key == null)
            HandleError(www.downloadHandler.text);
        return match;
    }

    private static IEnumerator SendGet(string url, Action<Player> callback, Action<Exception> eHandler, Dictionary<string, string> headers = null) {
        using (UnityWebRequest www = UnityWebRequest.Get(url)) {
            if (headers != null) {
                foreach (var header in headers) {
                    www.SetRequestHeader(header.Key, header.Value);
                }
            }

            yield return www.SendWebRequest();

            if (HandleNetWorkHttpError(www, eHandler))
                yield break;

            // TODO Should convert JSON to object here
            try {
                var player = GetPlayerFromWebRequest(www);
                callback(player);
            } catch (Exception e) {
                if (eHandler != null) {
                    eHandler(e);
                } else throw;
            }
        }
    }

    private static IEnumerator SendPost(string url, WWWForm postData, Action callback, Action<Exception> eHandler, bool newMatch = false) {
        using (UnityWebRequest www = UnityWebRequest.Post(url, postData)) {
            yield return www.SendWebRequest();

            if (HandleNetWorkHttpError(www, eHandler))
                yield break;

            // TODO Should convert JSON to object here
            try {
                var match = GetMatchFromWebRequest(www);
                match.LastServerTime = DateTime.Parse(www.GetResponseHeader("ServerTime"));
                if (Instance.match == null || newMatch)
                    Instance.match = match;
                else {
                    // If the new match is the newest update from the server update the match
                    if (DateTime.Compare(match.LastServerTime, Instance.match.LastServerTime) >= 0)
                        Instance.match.update(match);
                }

                callback();
            } catch (Exception e) {
                if (eHandler != null) {
                    eHandler(e);
                } else throw;
            }
        }
    }

    private static IEnumerator SendPost(string url, WWWForm postData, Action<Token> callback, Action<Exception> eHandler) {
        using (UnityWebRequest www = UnityWebRequest.Post(url, postData)) {
            yield return www.SendWebRequest();

            if (HandleNetWorkHttpError(www, eHandler))
                yield break;

            try {
                var token = JsonUtility.FromJson<Token>(www.downloadHandler.text);
                if (token.Value == null)
                    HandleError(www.downloadHandler.text);
                callback(token);
            } catch (Exception e) {
                if (eHandler != null) {
                    eHandler(e);
                } else throw;
            }
        }
    }

    #endregion
}

public class Error {
    public int Code;

    public string Message;
}

public class MultipleEmeraldControllersException : Exception {
    public MultipleEmeraldControllersException() : base("Cannot have more than one emerald controller") {
    }
}

public class NoEmeraldControllerInstanceException : Exception {
    public NoEmeraldControllerInstanceException() : base("There is no instance of EmeraldController in the scene make sure to attach EmeraldController to a game object in the scene.") {
    }
}

public class NoMatchException : Exception {
    public NoMatchException() : base("No match in the player controller. Make sure a match has been created.") {
    }
}

public class PlayerGroupNotFoundException : Exception {
    public PlayerGroupNotFoundException() : base("No player group in the match with the given Name") {
    }
}

public class PlayerNotFoundException : Exception {
    public PlayerNotFoundException() : base("Player not found in the EmeraldController.") {
    }
}

public class MatchAliveException : Exception {
    public MatchAliveException() : base("Cannot create a match while the current match is still alive. End or abort the current match before creating a new one.") {
    }
}