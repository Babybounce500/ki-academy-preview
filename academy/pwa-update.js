(function installPwaUpdateBridge() {
  if (!("serviceWorker" in navigator)) return;

  const version = "1";
  const workerUrl = `./service-worker.js?v=${version}`;

  navigator.serviceWorker.addEventListener("message", event => {
    if (event.data?.type !== "SW_UPDATED") return;
    // Preserve the persisted tab session. Fresh HTML arrives on the next
    // deliberate navigation; background updates are not destructive.
    document.documentElement.dataset.swReady = "updated";
  });

  const register = () => navigator.serviceWorker
    .register(workerUrl, { updateViaCache: "none" })
    .then(registration => registration.update())
    .catch(() => undefined);

  if (document.readyState === "loading") {
    window.addEventListener("load", register, { once: true });
  } else {
    register();
  }
})();
