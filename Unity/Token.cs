using System;
using UnityEngine;

[Serializable]
internal class Token {
    [SerializeField] private string token;

    public string Value {
        get { return this.token; }
        set { this.token = value; }
    }
}