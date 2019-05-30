/// <summary>
/// Interface for objects that listen to the Match in the playerController.
/// </summary>
public interface IMatchListener {
    /// <summary>
    /// Called when there is a change to the match.
    /// </summary>
    void OnChange();

    void OnAdd(PlayerGroup addedPlayerGroup);

    void OnRemove(PlayerGroup removedPlayerGroup);
}