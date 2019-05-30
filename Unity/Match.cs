using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Reflection;
using UnityEngine;

[Serializable]
public class Match {
    [SerializeField] private float wager;

    [SerializeField] private string date_created;

    [SerializeField] private string date_finished;

    [SerializeField] private string date_started;

    [SerializeField] private string key;

    private List<IMatchListener> listeners;

    [SerializeField] private float pool;

    [SerializeField] private MatchState state;

    [SerializeField] private List<PlayerGroup> playerGroups;

    internal DateTime LastServerTime;

    public Match() {
        this.listeners = new List<IMatchListener>();
    }

    public ReadOnlyCollection<PlayerGroup> PlayerGroups {
        get { return this.playerGroups.AsReadOnly(); }
    }

    public MatchState State {
        get { return this.state; }
    }

    public float Pool {
        get { return this.pool; }
    }

    public string Key {
        get { return this.key; }
    }

    public DateTime? DateStarted {
        get { return this.GetDate(this.date_started); }
    }

    public DateTime? DateFinished {
        get { return this.GetDate(this.date_finished); }
    }

    public DateTime? DateCreated {
        get { return this.GetDate(this.date_created); }
    }

    public float Wager {
        get { return this.wager; }
    }

    private DateTime? GetDate(string date) {
        DateTime result;
        if (DateTime.TryParse(date, out result))
            return result;
        return null;
    }

    public bool PlayerInMatch(string authToken) {
        return this.playerGroups.Exists(g => g.Players.FirstOrDefault(p => p.AuthToken == authToken) != null);
    }

    public void AddListener(IMatchListener listener) {
        this.listeners.Add(listener);
    }

    public void update(string updatedMatchJson) {
        JsonUtility.FromJsonOverwrite(updatedMatchJson, this);
        this.OnChange();
    }

    internal void update(Match newMatch) {
        foreach (var playerGroup in newMatch.PlayerGroups) {
            var existingPlayerGroup = this.PlayerGroups.FirstOrDefault(g => g.Name == playerGroup.Name);
            if (existingPlayerGroup != null)
                existingPlayerGroup.update(playerGroup);
            else {
                var newGroup = new PlayerGroup();
                newGroup.update(playerGroup);
                this.playerGroups.Add(newGroup);
                this.OnAdd(playerGroup);
            }
        }

        for (var i = this.PlayerGroups.Count - 1; i >= 0; i--) {
            if (newMatch.PlayerGroups.Any(ng => ng.Name == this.PlayerGroups[i].Name)) continue;
            var pg = this.playerGroups.ElementAt(i);
            this.OnRemove(pg);
            this.playerGroups.RemoveAt(i);
        }

        var fields = typeof(Match).GetFields(BindingFlags.NonPublic |
                                             BindingFlags.Instance).ToList();

        foreach (var field in fields) {
            if (field.Name != "playerGroups")
                field.SetValue(this, field.GetValue(newMatch));
        }

        this.OnChange();
    }

    private void Add(PlayerGroup playerGroup) {
        this.playerGroups.Add(playerGroup);
        this.OnChange();
    }

    private void OnChange() {
        foreach (var listener in this.listeners) listener.OnChange();
    }

    private void OnAdd(PlayerGroup playerGroup) {
        foreach (var listener in this.listeners) listener.OnAdd(playerGroup);
    }

    private void OnRemove(PlayerGroup playerGroup) {
        foreach (var listener in this.listeners) listener.OnRemove(playerGroup);
    }
}