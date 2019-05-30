/// <summary>
/// Listens to a player group in a match
/// </summary>
public interface IPlayerGroupListener {
    /// <summary>
    /// Called when a player is added to the player group.
    /// </summary>
    /// <param name="addedPlayer"></param>
    void OnAdd(Player addedPlayer);

    void OnRemove(Player removedPlayer);
}