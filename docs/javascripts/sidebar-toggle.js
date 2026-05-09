(function () {
  var STORAGE_KEY = "nexus.navCollapsed";
  var BTN_CLASS = "nexus-nav-toggle";

  function isCollapsed() {
    try {
      return localStorage.getItem(STORAGE_KEY) === "1";
    } catch (e) {
      return false;
    }
  }

  function setCollapsed(value) {
    try {
      localStorage.setItem(STORAGE_KEY, value ? "1" : "0");
    } catch (e) {}
  }

  function applyState(btn) {
    var collapsed = document.body.classList.contains("nav-collapsed");
    if (btn) {
      btn.setAttribute("aria-expanded", String(!collapsed));
      btn.setAttribute(
        "title",
        collapsed ? "Expand sidebar" : "Collapse sidebar"
      );
    }
  }

  function init() {
    if (document.querySelector("." + BTN_CLASS)) return;

    if (isCollapsed()) {
      document.body.classList.add("nav-collapsed");
    }

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = BTN_CLASS;
    btn.setAttribute("aria-label", "Toggle navigation sidebar");
    btn.innerHTML =
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="14" height="14" aria-hidden="true">' +
      '<path fill="currentColor" d="M15.41 7.41 14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>' +
      "</svg>";
    btn.addEventListener("click", function () {
      var nowCollapsed = document.body.classList.toggle("nav-collapsed");
      setCollapsed(nowCollapsed);
      applyState(btn);
    });

    document.body.appendChild(btn);
    applyState(btn);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
