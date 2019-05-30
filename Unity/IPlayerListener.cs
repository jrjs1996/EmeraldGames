/// <summary>
/// Listens to a player in a match.
/// </summary>
public interface IPlayerListener {
    /// <summary>
    /// Called when there has been a change to the player. eg. Balance has changed.
    /// </summary>
    void OnChange();
}