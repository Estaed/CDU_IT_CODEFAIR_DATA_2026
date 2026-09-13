"use strict";

// The app renders the pack and routes; it computes no verdict (CLAUDE.md Part 2, layer rule 4).
(() => {
  const DEFAULT_HASH = "#/community/426";
  const SCREENS = ["#/community", "#/map", "#/share"];

  const main = document.querySelector("main");
  const pack = JSON.parse(document.getElementById("pack").textContent);

  if (pack.pack_version !== 1) {
    main.textContent = "Unknown data pack";
    return;
  }

  const tabs = [...document.querySelectorAll("[role=tab]")];
  const chip = document.querySelector(".offline-chip");

  const screenOf = (hash) => SCREENS.find((screen) => hash.startsWith(screen)) || SCREENS[0];

  const render = (text) => {
    const line = document.createElement("p");
    line.textContent = text;
    main.textContent = "";
    main.appendChild(line);
  };

  const route = () => {
    if (!location.hash) {
      location.hash = DEFAULT_HASH;
    }
    const screen = screenOf(location.hash || DEFAULT_HASH);
    let selected = null;
    for (const tab of tabs) {
      const isSelected = tab.getAttribute("href").startsWith(screen);
      tab.setAttribute("aria-selected", isSelected ? "true" : "false");
      if (isSelected) {
        selected = tab;
      }
    }
    if (selected) {
      selected.scrollIntoView({ inline: "nearest", block: "nearest" });
    }
    if (screen === "#/map") {
      render("Map");
    } else if (screen === "#/share") {
      render("Share");
    } else {
      render(`${pack.count} communities`);
    }
  };

  const setChip = () => {
    chip.textContent = navigator.onLine ? "Online" : "Offline";
  };

  window.addEventListener("hashchange", route);
  window.addEventListener("online", setChip);
  window.addEventListener("offline", setChip);
  setChip();
  route();
})();
