using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace Tests {
    public class TestMatchAlive {
        const float waitTime = .160f;

        [UnityTest]
        public IEnumerator Test() {
            var go = new GameObject();
            go.AddComponent<EmeraldController>();
            Assert.False(EmeraldController.MatchAlive());

            EmeraldController.CreateMatch(1, null, () => {
                Assert.True(EmeraldController.MatchAlive());
                EmeraldController.AbortMatch(() => {
                    Assert.False(EmeraldController.MatchAlive());
                    EmeraldController.CreateMatch(2, null, () => { });
                });
            });
            yield return new WaitForSeconds(waitTime);
            EmeraldController.Login("a", "a", p => {
                EmeraldController.CreateSoloPlayerGroup(p, g => {
                    EmeraldController.Login("b", "b", p2 => {
                        EmeraldController.CreateSoloPlayerGroup(p2, g2 => {
                            EmeraldController.StartMatch(() => {
                                Assert.True(EmeraldController.MatchAlive());
                                EmeraldController.EndMatch(g, () => { Assert.False(EmeraldController.MatchAlive()); });
                                Debug.Log("TestMatchAlive finished");
                            });
                        });
                    });
                });
            });
            yield return new WaitForSeconds(waitTime);
            Object.Destroy(go);
            yield return null;
        }
    }
}