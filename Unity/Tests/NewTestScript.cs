using System;
using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using Object = UnityEngine.Object;

public class NewTestScript {
    const float waitTime = .160f;

    [Test]
    public void NewTestScriptSimplePasses() {
    }

    // A UnityTest behaves like a coroutine in PlayMode
    // and allows you to yield null to skip a frame in EditMode
    [UnityTest]
    public IEnumerator NewTestScriptWithEnumeratorPasses() {
        /*
         * Prerequisites for test:
         * The game with the given game Key should have two Players. Username: a Password: a, Username: b Password: b
         * Both Players should have $100 in their account.
         * Should have a patch type with a and b group presets
        */

        float wager = 1;

        var go = this.SetupEmeraldController();

        #region Test Login

        // Test that PlayerInvalid login is thrown when invalid credentials are given
        EmeraldController.Login("asdf", "asdf", p => { throw new Exception("Should throw an exception"); }, e => { Assert.AreEqual(e.GetType(), typeof(PlayerInvalidLogin)); });

        // Get player a and make sure their properties are correct
        EmeraldController.Login("a", "a", p => { this.testPlayer(p, "a", 100f); });

        // Get player b and make sure their properties are correct
        EmeraldController.Login("b", "b", p => { this.testPlayer(p, "b", 100f); });

        #endregion

        yield return new WaitForSeconds(waitTime);

        #region Test CreateMatch

        // Assert that a negative Wager throws a match creation error
        EmeraldController.CreateMatch(-1, null, () => { throw new Exception(); }, (e) => { Assert.AreEqual(e.GetType(), typeof(MatchCreationError)); });

        float pool = 0;

        // Test Create Match with types
        EmeraldController.CreateMatch(wager, "Type1", () => { this.TestMatch(EmeraldController.Match, wager, new string[] {"a", "b"}); });

        yield return new WaitForSeconds(waitTime);

        // Test Create Match without tytpes

        EmeraldController.AbortMatch(() => { EmeraldController.CreateMatch(wager, null, () => { this.TestMatchCreation(EmeraldController.Match, wager); }); });

        yield return new WaitForSeconds(waitTime);

        // Test that the match cant be started with a player that is quit
        EmeraldController.StartMatch(() => { throw new Exception(); }, e => { Assert.AreEqual(typeof(MatchStartMatchError), e.GetType()); });

        #endregion

        #region Test CreatePlayerGroup

        yield return new WaitForSeconds(waitTime);

        // Test if CreatePlayerGroup with an empty group Name throws an exception
        EmeraldController.CreatePlayerGroup("", (g) => { throw new Exception(); }, e => { Assert.AreEqual(e.GetType(), typeof(MatchCreateUserGroupError)); });

        yield return new WaitForSeconds(waitTime);

        string[] groupNames = new string[] {"a"};

        // Create player group a
        EmeraldController.CreatePlayerGroup("a", (g) => { this.TestMatch(EmeraldController.Match, wager, new string[] {"a"}); });

        groupNames = new string[] {"a", "b"};

        // Create player group b
        yield return new WaitForSeconds(waitTime);
        EmeraldController.CreatePlayerGroup("b", (g) => { this.TestMatch(EmeraldController.Match, wager, new string[] {"a", "b"}); });

        // Test that creating a duplicate player group throws an MatchCreateUserGroupError
        EmeraldController.CreatePlayerGroup("a", (g) => { throw new Exception(); }, e => { Assert.AreEqual(e.GetType(), typeof(MatchCreateUserGroupError)); });

        #endregion

        yield return new WaitForSeconds(waitTime);

        #region Test AddPlayerToGroup

        // Try adding a player to a group that doesn't exist
        EmeraldController.AddPlayerToGroup("asdf", "a", (g) => { throw new Exception(); }, e => { Assert.AreEqual(e.GetType(), typeof(PlayerGroupNotFoundException)); });

        // Try adding a player that doesn't exist to a group
        EmeraldController.AddPlayerToGroup("a", "asdf", (g) => { throw new Exception(); }, e => { Assert.AreEqual(e.GetType(), typeof(PlayerNotFoundException)); });

        EmeraldController.AddPlayerToGroup(EmeraldController.Match.PlayerGroups[0], "asdf", (g) => { throw new Exception(); }, e => { Assert.AreEqual(e.GetType(), typeof(PlayerNotFoundException)); });

        pool += wager;
        // Add a player using the group overload
        EmeraldController.AddPlayerToGroup(EmeraldController.Match.PlayerGroups[0], "a", (g) => {
            var pg = EmeraldController.Match.PlayerGroups[0];
            Assert.AreEqual(1, pg.Players.Count);
            Assert.AreEqual("a", pg.Players[0].Username);
        });

        pool += wager;
        // Add a player using the group Name overload
        EmeraldController.AddPlayerToGroup("b", "b", (g) => {
            var pg2 = EmeraldController.Match.PlayerGroups[1];
            Assert.AreEqual(1, pg2.Players.Count);
            Assert.AreEqual("b", pg2.Players[0].Username);
        });

        // Try adding a player to a group twice
        EmeraldController.AddPlayerToGroup(EmeraldController.Match.PlayerGroups[0], "a", (g) => { throw new Exception(); }, e => { Assert.AreEqual(typeof(PlayerGroupAddPlayerError), e.GetType()); });

        yield return new WaitForSeconds(waitTime);

        this.TestMatch(EmeraldController.Match, wager, groupNames, pool);

        #endregion

        #region Test PlayerQuit

        // Test that player quit with player that doesn't exist throws an error
        EmeraldController.PlayerQuit("FakeAuthToken", () => { throw new Exception(); }, e => { Assert.AreEqual(typeof(PlayerNotFound), e.GetType()); });

        EmeraldController.PlayerQuit("9999999", () => { throw new Exception(); }, e => { Assert.AreEqual(typeof(PlayerNotFound), e.GetType()); });

        pool -= wager;
        // First Player should quit
        EmeraldController.PlayerQuit(EmeraldController.Match.PlayerGroups[0].Players[0].AuthToken, () => {
            this.TestMatch(EmeraldController.Match, wager, groupNames, pool);
            Assert.AreEqual(0, EmeraldController.Match.PlayerGroups[0].Players.Count);
        });
        yield return new WaitForSeconds(waitTime);
        // Test that the match cant be started with a player that is quit
        EmeraldController.StartMatch(() => { throw new Exception(); }, e => { Assert.AreEqual(typeof(MatchStartMatchError), e.GetType()); });

        #endregion

        yield return new WaitForSeconds(waitTime);

        #region Test RemovePlayerGroup

        // Test that exception is thrown when trying to remove a group that doesn't exist
        EmeraldController.RemovePlayerGroup("asdf", () => { throw new Exception(); }, e => { Assert.AreEqual(typeof(PlayerGroupNotFoundException), e.GetType()); });

        groupNames = new string[] {"b"};
        // Test that group a is removed
        EmeraldController.RemovePlayerGroup("a", () => {
            Assert.AreEqual(1, EmeraldController.Match.PlayerGroups.Count);
            this.TestMatch(EmeraldController.Match, wager, groupNames, pool);
        });

        #endregion

        yield return new WaitForSeconds(waitTime);

        #region Test Recreate PlayerGroup (a)

        groupNames = new string[] {"b", "a"};

        EmeraldController.CreatePlayerGroup("a", (g) => { this.TestMatch(EmeraldController.Match, wager, groupNames, pool); });

        #endregion

        yield return new WaitForSeconds(waitTime);

        #region Test Player rejoin match

        pool += wager;

        // Add a player using the group overload
        EmeraldController.AddPlayerToGroup(EmeraldController.Match.PlayerGroups[1], "a", (g) => {
            this.TestMatch(EmeraldController.Match, wager, groupNames, pool);
            var pg = EmeraldController.Match.PlayerGroups[1];
            Assert.AreEqual(1, pg.Players.Count);
            Assert.AreEqual("a", pg.Players[0].Username);
        });

        #endregion

        yield return new WaitForSeconds(waitTime);

        #region Test StartMatch

        // Try to end the match before it started
        EmeraldController.EndMatch(EmeraldController.Match.PlayerGroups[0], () => { throw new Exception(); }, e => { Assert.AreEqual(typeof(MatchEndMatchError), e.GetType()); });
        yield return new WaitForSeconds(waitTime);
        // Test that matchstart works
        EmeraldController.StartMatch(() => { this.TestMatch(EmeraldController.Match, wager, groupNames, pool, MatchState.Active); });
        yield return new WaitForSeconds(waitTime);
        //Try to start the match after it's already started.
        EmeraldController.StartMatch(() => { throw new Exception(); }, e => { Assert.AreEqual(typeof(MatchStartMatchError), e.GetType()); });

        #endregion

        yield return new WaitForSeconds(waitTime);

        #region Test EndMatch

        pool = 0;
        // Test that endmatch works
        EmeraldController.EndMatch(EmeraldController.Match.PlayerGroups[0], () => {
            this.TestMatch(EmeraldController.Match, wager, groupNames, pool, MatchState.Finished);
            var winningPlayer = EmeraldController.Match.PlayerGroups[0].Players[0];
            Assert.AreEqual(101f, winningPlayer.Balance);
            var losingPlayer = EmeraldController.Match.PlayerGroups[1].Players[0];
            Assert.AreEqual(99f, losingPlayer.Balance);
        });
        yield return new WaitForSeconds(waitTime);
        EmeraldController.EndMatch(EmeraldController.Match.PlayerGroups[0], () => { throw new Exception(); }, e => { Assert.AreEqual(typeof(MatchEndMatchError), e.GetType()); });

        yield return new WaitForSeconds(waitTime);

        #endregion

        yield return new WaitForSeconds(waitTime);

        #region Test AbortMatch

        // Try to abort a match that has already ended.
        EmeraldController.AbortMatch(() => { throw new Exception(); }, e => { Assert.AreEqual(typeof(MatchAbortMatchError), e.GetType()); });

        yield return new WaitForSeconds(waitTime);
        pool = 0;
        wager = 1;
        groupNames = new string[] {};
        // Test abortmatch just after creation
        EmeraldController.CreateMatch(wager, null, () => { EmeraldController.AbortMatch(() => { this.TestMatch(EmeraldController.Match, wager, groupNames, pool, MatchState.Aborted); }); });
        yield return new WaitForSeconds(waitTime);

        // Test after Players added
        EmeraldController.CreateMatch(wager, null, () => {
            pool += wager;
            groupNames = new string[] {"a"};
            var playerA = EmeraldController.GetPlayer("a");
            var playerB = EmeraldController.GetPlayer("b");
            EmeraldController.CreateSoloPlayerGroup(playerA.AuthToken, g => {
                this.TestMatch(EmeraldController.Match, wager, groupNames, pool);
                Assert.AreEqual(98, playerA.Balance);

                pool += wager;
                groupNames = new string[] {"a", "b"};
                EmeraldController.CreateSoloPlayerGroup(playerB.AuthToken, g2 => {
                    this.TestMatch(EmeraldController.Match, wager, groupNames, pool);
                    Assert.AreEqual(100, playerB.Balance);

                    pool = 0;
                    EmeraldController.AbortMatch(() => {
                        this.TestMatch(EmeraldController.Match, wager, groupNames, pool, MatchState.Aborted);
                        Assert.AreEqual(101, playerB.Balance);
                        Assert.AreEqual(99, playerA.Balance);
                    });
                });
            });
        });
        yield return new WaitForSeconds(waitTime);

        // Test after start
        EmeraldController.CreateMatch(wager, null, () => {
            pool += wager;
            groupNames = new string[] {"a"};
            var playerA = EmeraldController.GetPlayer("a");
            var playerB = EmeraldController.GetPlayer("b");
            EmeraldController.CreateSoloPlayerGroup(playerA.AuthToken, g => {
                this.TestMatch(EmeraldController.Match, wager, groupNames, pool);
                Assert.AreEqual(98, playerA.Balance);

                pool += wager;
                groupNames = new string[] {"a", "b"};
                EmeraldController.CreateSoloPlayerGroup(playerB.AuthToken, g2 => {
                    this.TestMatch(EmeraldController.Match, wager, groupNames, pool);
                    Assert.AreEqual(100, playerB.Balance);
                    EmeraldController.StartMatch(() => {
                        this.TestMatch(EmeraldController.Match, wager, groupNames, pool, MatchState.Active);
                        pool = 0;
                        EmeraldController.AbortMatch(() => {
                            this.TestMatch(EmeraldController.Match, wager, groupNames, pool, MatchState.Aborted);
                            Assert.AreEqual(101, playerB.Balance);
                            Assert.AreEqual(99, playerA.Balance);
                        });
                    });
                });
            });
        });
        yield return new WaitForSeconds(waitTime);
        EmeraldController.Login("c", "c");
        yield return new WaitForSeconds(waitTime);
        // Test with multiple Players a team
        EmeraldController.CreateMatch(wager, null, () => {
            pool += wager;
            groupNames = new string[] {"a"};
            var playerA = EmeraldController.GetPlayer("a");
            var playerB = EmeraldController.GetPlayer("b");
            var playerC = EmeraldController.GetPlayer("c");
            EmeraldController.CreateSoloPlayerGroup(playerA.AuthToken, g => {
                this.TestMatch(EmeraldController.Match, wager, groupNames, pool);
                Assert.AreEqual(98, playerA.Balance);

                pool += wager;
                groupNames = new string[] {"a", "b"};
                EmeraldController.CreateSoloPlayerGroup(playerB.AuthToken, g2 => {
                    this.TestMatch(EmeraldController.Match, wager, groupNames, pool);
                    Assert.AreEqual(100, playerB.Balance);

                    pool += wager;
                    EmeraldController.AddPlayerToGroup("b", "c", g3 => {
                        EmeraldController.StartMatch(() => {
                            this.TestMatch(EmeraldController.Match, wager, groupNames, pool, MatchState.Active);
                            pool = 0;
                            EmeraldController.AbortMatch(() => {
                                this.TestMatch(EmeraldController.Match, wager, groupNames, pool, MatchState.Aborted);
                                Assert.AreEqual(101, playerB.Balance);
                                Assert.AreEqual(99, playerA.Balance);
                                Assert.AreEqual(100, playerC.Balance);
                                ;
                            });
                        });
                    });
                });
            });
        });

        #endregion

        yield return new WaitForSeconds(waitTime);

        // Test endmatch with multiple Players a team
        EmeraldController.CreateMatch(wager, null, () => {
            pool += wager;
            groupNames = new string[] {"a"};
            var playerA = EmeraldController.GetPlayer("a");
            var playerB = EmeraldController.GetPlayer("b");
            var playerC = EmeraldController.GetPlayer("c");
            EmeraldController.CreateSoloPlayerGroup(playerA.AuthToken, g => {
                this.TestMatch(EmeraldController.Match, wager, groupNames, pool);
                Assert.AreEqual(98, playerA.Balance);

                pool += wager;
                groupNames = new string[] {"a", "b"};
                EmeraldController.CreateSoloPlayerGroup(playerB.AuthToken, g2 => {
                    this.TestMatch(EmeraldController.Match, wager, groupNames, pool);
                    Assert.AreEqual(100, playerB.Balance);

                    pool += wager;
                    EmeraldController.AddPlayerToGroup("b", "c", g3 => {
                        EmeraldController.StartMatch(() => {
                            this.TestMatch(EmeraldController.Match, wager, groupNames, pool, MatchState.Active);
                            pool = 0;
                            EmeraldController.EndMatch("b", () => {
                                this.TestMatch(EmeraldController.Match, wager, groupNames, pool, MatchState.Finished);
                                Assert.AreEqual(101.5, playerB.Balance);
                                Assert.AreEqual(98, playerA.Balance);
                                Assert.AreEqual(100.5, playerC.Balance);
                                Debug.Log("Test Finished");
                            });
                        });
                    });
                });
            });
        });
        yield return new WaitForSeconds(waitTime);
        Object.Destroy(go);
        yield return new WaitForEndOfFrame();
        yield return new WaitForEndOfFrame();
        Assert.Throws<NoEmeraldControllerInstanceException>(() => {
            var match = EmeraldController.Match;
        });
        yield return null;
    }

    private GameObject SetupEmeraldController() {
        var go = new GameObject();
        go.AddComponent<EmeraldController>();
        Assert.AreEqual(EmeraldController.GameKey, "52cdd96a-4dac-4399-a8b9-19a8e7b878f5");
        return go;
    }

    private void TestMatch(Match m, float wager, string[] groupNames, float pool = 0, MatchState matchState = MatchState.Registering) {
        // Standard for every match creation
        this.testMatchPreStart(m, wager, pool, matchState);

        if (groupNames.Length > 0)
            Assert.AreEqual(groupNames.Length, m.PlayerGroups.Count);
        for (int i = 0; i < groupNames.Length; i++) {
            Assert.AreEqual(groupNames[i], m.PlayerGroups[i].Name);
        }
    }

    private void TestMatchCreation(Match m, float wager) {
        this.TestMatch(m, wager, new string[] {});
    }

    private void testMatchPreStart(Match m, float wager, float pool, MatchState matchState) {
        Assert.AreEqual(EmeraldController.Match, m);
        Assert.NotNull(m.DateCreated);
        if (matchState != MatchState.Aborted) {
            if (matchState == MatchState.Registering)
                Assert.IsNull(m.DateStarted);
            else
                Assert.IsNotNull(m.DateStarted);
        }
        if (matchState == MatchState.Registering || matchState == MatchState.Active)
            Assert.IsNull(m.DateFinished);
        else
            Assert.IsNotNull(m.DateFinished);
        Assert.NotNull(m.Key);
        Assert.AreEqual(pool, m.Pool);
        Assert.AreEqual(matchState, m.State);
        Assert.AreEqual(wager, m.Wager);
    }

    private void testPlayer(Player p, string username, float balance) {
        Assert.AreEqual(username, p.Username);
        Assert.AreEqual(balance, p.Balance);
    }
}