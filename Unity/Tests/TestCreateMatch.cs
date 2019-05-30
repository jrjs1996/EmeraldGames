using System;
using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using Object = UnityEngine.Object;

namespace Tests {
    public class TestCreateMatch {
        const float waitTime = .160f;

        [UnityTest]
        public IEnumerator Test() {
            // Try to create a match while instance is null
            Assert.Throws<NoEmeraldControllerInstanceException>(() => { EmeraldController.CreateMatch(1); });
            Assert.Throws<NoEmeraldControllerInstanceException>(() => { EmeraldController.CreateMatch(1, "Type1"); });

            var go = Object.Instantiate(new GameObject());
            go.AddComponent<EmeraldController>();

            yield return new WaitForSeconds(waitTime);
            // Should create a match
            EmeraldController.CreateMatch(1, () => {
                Assert.AreEqual(1, EmeraldController.Match.Wager);
                Assert.AreEqual(0, EmeraldController.Match.Pool);
                Assert.AreEqual(MatchState.Registering, EmeraldController.Match.State);
                // Should throw an exception because the match is alive
                EmeraldController.CreateMatch(2, () => { throw new Exception(); }, e => { Assert.AreEqual(typeof(MatchAliveException), e.GetType()); });
                // Abort the match
                EmeraldController.AbortMatch(() => {
                    Assert.AreEqual(MatchState.Aborted, EmeraldController.Match.State);
                    // Should be successful
                    EmeraldController.CreateMatch(2, () => {
                        Assert.AreEqual(2, EmeraldController.Match.Wager);
                        Assert.AreEqual(0, EmeraldController.Match.Pool);
                        Assert.AreEqual(MatchState.Registering, EmeraldController.Match.State);
                        // Log the users in and create their groups
                        EmeraldController.Login("a", "a", p => {
                            EmeraldController.CreateSoloPlayerGroup(p, g => {
                                EmeraldController.Login("b", "b", p2 => {
                                    EmeraldController.CreateSoloPlayerGroup(p, g2 => {
                                        EmeraldController.StartMatch(() => {
                                            // Should throw exception when there trying to create while a match is in progress
                                            EmeraldController.CreateMatch(2, () => { throw new Exception(); }, e => { Assert.AreEqual(typeof(MatchAliveException), e.GetType()); });
                                            // End the match
                                            EmeraldController.EndMatch(g, () => {
                                                // Test creatematch when match is finished.
                                                EmeraldController.CreateMatch(2, () => { Debug.Log("TestCreateMatchFinished"); });
                                            });
                                        });
                                    });
                                });
                            });
                        });
                    });
                });
            }, null);

            yield return new WaitForSeconds(waitTime);
            yield return null;
        }
    }
}