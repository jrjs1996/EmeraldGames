using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Reflection;
using UnityEngine;

[Serializable]
public class PlayerGroup {
    private List<IPlayerGroupListener> listeners;

    [SerializeField] private List<Player> players;

    [SerializeField] private string name;

    public PlayerGroup() {
        this.listeners = new List<IPlayerGroupListener>();
        this.players = new List<Player>();
        this.name = "";
    }

    public string Name {
        get { return this.name; }
    }

    public ReadOnlyCollection<Player> Players {
        get { return this.players.AsReadOnly(); }
    }

    internal void update(PlayerGroup newPlayerGroup) {
        foreach (var newPlayer in newPlayerGroup.Players) {
            var existingPlayer = this.Players.FirstOrDefault(p => p.AuthToken == newPlayer.AuthToken);
            // If the player already exists in the group...
            if (existingPlayer != null) {
                existingPlayer.update(newPlayer);
            } else {
                existingPlayer = EmeraldController.Players.FirstOrDefault(p => p.AuthToken == newPlayer.AuthToken);
                // If the player is already logged in to the emerald controller
                if (existingPlayer != null)
                {
                    existingPlayer.update(newPlayer);
                }
                else
                {
                    EmeraldController.players.Add(newPlayer);
                    existingPlayer = newPlayer;
                }
                
                this.AddPlayer(existingPlayer);
            }
        }

        for (var i = this.Players.Count - 1; i >= 0; i--) {
            if (newPlayerGroup.Players.Any(np => np.AuthToken == this.Players[i].AuthToken)) continue;
            var p = this.players.ElementAt(i);
            this.OnRemove(p);
            this.players.RemoveAt(i);
        }

        var fields = typeof(PlayerGroup).GetFields(BindingFlags.NonPublic |
                                                   BindingFlags.Instance).ToList();

        foreach (var field in fields) {
            if (field.Name != "players" && field.Name != "listeners")
                field.SetValue(this, field.GetValue(newPlayerGroup));
        }
    }

    private void AddPlayer(Player player)
    {
        this.players.Add(player);
        player.playerGroup = this;
        this.OnAdd(player);
    }

    private void OnAdd(Player player) {
        foreach (var listener in this.listeners) listener.OnAdd(player);
    }

    private void OnRemove(Player player) {
        foreach (var listener in this.listeners) listener.OnRemove(player);
    }

    public void AddListener(IPlayerGroupListener listener) {
        this.listeners.Add(listener);
    }
}