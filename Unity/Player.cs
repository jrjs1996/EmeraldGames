using System;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;

[Serializable]
public class Player {
    private List<IPlayerListener> listeners;

    [NonSerialized]
    internal PlayerGroup playerGroup;

    [SerializeField] private string auth_token;

    [SerializeField] private float balance;

    [SerializeField] private string username;

    public PlayerGroup PlayerGroup
    {
        get { return this.playerGroup; }
    }

    public Player() {
        this.listeners = new List<IPlayerListener>();
    }

    public string Username {
        get { return this.username; }
    }

    public float Balance {
        get { return this.balance; }
    }

    public string AuthToken {
        get { return this.auth_token; }
    }

    internal void update(Player newPlayer) {
        var fields = typeof(Player).GetFields(BindingFlags.NonPublic |
                                              BindingFlags.Instance);

        foreach (var field in fields) {
            field.SetValue(this, field.GetValue(newPlayer));
        }
        this.OnChange();
    }

    public void OnChange() {
        foreach (var listener in this.listeners) listener.OnChange();
    }

    public void AddListener(IPlayerListener listener) {
        this.listeners.Add(listener);
    }
}