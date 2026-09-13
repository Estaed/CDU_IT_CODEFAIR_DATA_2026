"use strict";

// The app renders the pack and routes; it computes no verdict (CLAUDE.md Part 2, layer rule 4).
(() => {
  const DEFAULT_HASH = "#/community/426";
  const DEFAULT_ID = 426;
  const SCREENS = ["#/community", "#/map", "#/share"];

  const SERVICE_LABEL = {
    telehealth_video: "Telehealth video",
    school_video_meeting: "School video meeting",
    mygov_text: "myGov and banking",
    voice_sms: "Voice and SMS",
  };

  const VERDICTS = {
    works: { glyph: "●", word: "Works" },
    degraded: { glyph: "▲", word: "Degraded" },
    fails: { glyph: "■", word: "Fails" },
    nodata: { glyph: "–", word: "No data" },
  };

  const SAYS_LABEL = {
    covered: "Covered",
    "not-covered": "Not covered",
    "not-recorded": "Not recorded",
  };

  const main = document.querySelector("main");
  const footer = document.querySelector("footer.footer");
  const pack = JSON.parse(document.getElementById("pack").textContent);

  if (pack.pack_version !== 1) {
    main.textContent = "Unknown data pack";
    return;
  }

  const tabs = [...document.querySelectorAll("[role=tab]")];
  const chip = document.querySelector(".offline-chip");

  // Small DOM builder: never innerHTML with pack strings (layer rule 4).
  const h = (tag, attrs, ...children) => {
    const el = document.createElement(tag);
    if (attrs) {
      for (const [key, value] of Object.entries(attrs)) {
        if (value !== null && value !== undefined) {
          el.setAttribute(key, value);
        }
      }
    }
    const append = (child) => {
      if (child === null || child === undefined || child === false) {
        return;
      }
      if (Array.isArray(child)) {
        child.forEach(append);
        return;
      }
      if (child instanceof Node) {
        el.appendChild(child);
        return;
      }
      el.appendChild(document.createTextNode(String(child)));
    };
    children.forEach(append);
    return el;
  };

  // Splits a pack reason/detail string on backticks, mirroring design/ds/components/core/Figures.jsx.
  const figures = (text, size = "sm") => {
    const cls = size === "sm" ? "fig" : `fig fig--${size}`;
    return String(text)
      .split("`")
      .map((part, i) => (i % 2 === 1 ? h("span", { class: cls }, part) : part));
  };

  const sourceLine = (srcId) => {
    const entry = pack.sources[srcId];
    return h(
      "span",
      { class: "source-line" },
      `${entry.source} · `,
      h("span", { class: "fig fig--xs" }, entry.date),
    );
  };

  const labeledSourceLine = (label, srcId) => {
    const entry = pack.sources[srcId];
    return h(
      "span",
      { class: "source-line" },
      `${label}: ${entry.source} · `,
      h("span", { class: "fig fig--xs" }, entry.date),
    );
  };

  const renderHeader = (community) =>
    h(
      "div",
      { class: "community-header" },
      h("h1", { class: "community-header__name" }, community.name),
      h(
        "div",
        { class: "community-header__meta" },
        `${community.region} · ${community.type} community`,
      ),
      h(
        "div",
        { class: "community-header__population" },
        h("span", { class: "fig fig--md" }, community.population.value.toLocaleString("en-US")),
        " ",
        h("span", { class: "community-header__unit" }, "people"),
      ),
      sourceLine(community.population.src),
    );

  // "What exists here": the present chips, then a data-backed fact line per flag the pack
  // carries. BushTel's WiFi hours, STAND site and road-condition free text stay out of the
  // pack until OQ1 is answered (pipeline/pack.py BUSHTEL_TEXT_ALLOWED), so only the two
  // flags the pack does carry (road_seasonal_cut, backhaul_2019) render here.
  const renderPresent = (community) => {
    const section = h(
      "section",
      { class: "section" },
      h("h2", { class: "section__title" }, "What exists here"),
      h(
        "div",
        { class: "chips" },
        community.present.map((item) => h("span", { class: "chip" }, item.name)),
      ),
    );
    for (const flag of community.flags) {
      if (flag.name === "road_seasonal_cut" && flag.value) {
        section.appendChild(
          h(
            "div",
            { class: "fact" },
            "Road access is subject to seasonal closure",
            sourceLine(flag.src),
          ),
        );
      } else if (flag.name === "backhaul_2019") {
        section.appendChild(
          h("div", { class: "fact" }, `Backhaul: ${flag.value}`, sourceLine(flag.src)),
        );
      }
    }
    return section;
  };

  const renderPublishers = (community) => {
    const section = h(
      "section",
      { class: "section" },
      h("h2", { class: "section__title" }, "What the sources say"),
      h(
        "div",
        { class: "agreement" },
        h(
          "div",
          { class: "agreement__headline" },
          h("span", { class: "fig fig--lg" }, String(community.agreement.covered)),
          " of ",
          h("span", { class: "fig fig--lg" }, String(community.agreement.available)),
          " sources say covered",
        ),
        h("div", { class: "agreement__note" }, community.agreement.note),
      ),
    );
    for (const publisher of community.publishers) {
      section.appendChild(
        h(
          "div",
          { class: "publisher-row" },
          h(
            "div",
            { class: "publisher-row__top" },
            h("span", { class: "publisher-row__name" }, publisher.publisher),
            h("span", { class: "kind-chip" }, publisher.kind),
            h("span", { class: "says" }, SAYS_LABEL[publisher.says_covered] || publisher.says_covered),
          ),
          h("div", { class: "publisher-row__detail" }, figures(publisher.detail)),
          sourceLine(publisher.src),
        ),
      );
    }
    return section;
  };

  const renderServices = (community) => {
    const section = h(
      "section",
      { class: "section" },
      h("h2", { class: "section__title" }, "What the connection allows"),
      h(
        "div",
        { class: "section__note" },
        "Best available path: ",
        figures(community.path.note),
        ` · ${community.path.rule} `,
        h("span", { class: "fig fig--xs" }, community.path.date),
      ),
    );
    for (const service of community.services) {
      const verdict = VERDICTS[service.verdict];
      const panel = service.sources.length
        ? h(
            "div",
            { class: "service-row__sources", hidden: "" },
            service.sources.map((source) => labeledSourceLine(source.label, source.src)),
          )
        : null;
      const button = h(
        "button",
        { type: "button", class: "service-row__button", "aria-expanded": "false" },
        h(
          "span",
          { class: "service-row__top" },
          h("span", { class: "service-row__name" }, SERVICE_LABEL[service.service] || service.service),
          h(
            "span",
            { class: `verdict-badge verdict-badge--${service.verdict}` },
            h("span", { "aria-hidden": "true" }, verdict.glyph),
            verdict.word,
          ),
        ),
        h("span", { class: "service-row__reason" }, figures(service.reason)),
      );
      button.addEventListener("click", () => {
        const expanded = button.getAttribute("aria-expanded") === "true";
        button.setAttribute("aria-expanded", expanded ? "false" : "true");
        // The sources panel exists in the DOM only while the row is expanded (Task-07 DoD).
        if (panel) {
          if (expanded) {
            panel.remove();
          } else {
            button.after(panel);
          }
        }
      });
      const row = h("div", { class: "service-row" }, button);
      if (service.assumption) {
        row.appendChild(
          h(
            "div",
            { class: "assumption-note" },
            h("span", { class: "assumption-note__label" }, "Assumption"),
            " ",
            figures(service.assumption),
          ),
        );
      }
      section.appendChild(row);
    }
    return section;
  };

  const renderActions = (community) =>
    h(
      "section",
      { class: "section" },
      h("h2", { class: "section__title" }, "Who does what"),
      h(
        "ul",
        { class: "actions" },
        community.actions.map((action) =>
          h(
            "li",
            { class: "actions__item" },
            h("span", { class: "actions__who" }, `${action.who}:`),
            ` ${action.text}`,
          ),
        ),
      ),
    );

  const renderFooter = () => {
    footer.textContent = "";
    for (const item of pack.attributions) {
      const parts = [item.text];
      if (item.licence) {
        parts.push(item.licence);
      }
      const span = h("span", {}, parts.join(" · "));
      if (item.date) {
        span.appendChild(document.createTextNode(" · "));
        span.appendChild(h("span", { class: "fig fig--xs" }, item.date));
      }
      footer.appendChild(span);
    }
    footer.appendChild(
      h(
        "span",
        { class: "footer__team" },
        `CDU IT Code Fair 2026 · Data Innovation Challenge · Team ${pack.team}`,
      ),
    );
    footer.appendChild(h("span", {}, "Crosscheck does not measure signal."));
  };

  const matchesText = (value, query) => {
    const text = value.toLowerCase();
    return text.startsWith(query) || text.includes(query);
  };

  const matchesQuery = (community, query) =>
    matchesText(community.name, query) || community.aliases.some((alias) => matchesText(alias, query));

  const matchedAlias = (community, query) =>
    community.aliases.find((alias) => matchesText(alias, query)) || null;

  const renderSearch = () => {
    const results = h("ul", { class: "search-results" });
    const input = h("input", {
      class: "search-input",
      type: "search",
      placeholder: `Search ${pack.count} communities`,
      "aria-label": "Search communities",
    });
    input.addEventListener("input", () => {
      const query = input.value.trim().toLowerCase();
      results.textContent = "";
      if (!query) {
        return;
      }
      for (const community of pack.communities.filter((c) => matchesQuery(c, query))) {
        const alias = matchedAlias(community, query);
        const row = h(
          "button",
          { type: "button", class: "result-row" },
          h("span", {}, community.name),
          alias ? h("span", { class: "result-row__alias" }, alias) : null,
          h(
            "span",
            { class: "result-row__meta" },
            `${community.region} · `,
            h("span", { class: "fig fig--xs" }, community.population.value.toLocaleString("en-US")),
          ),
        );
        row.addEventListener("click", () => {
          location.hash = `#/community/${community.id}`;
        });
        results.appendChild(h("li", {}, row));
      }
    });
    return [h("div", { class: "search" }, input), results];
  };

  const renderCommunity = (id) => {
    const community =
      pack.communities.find((c) => c.id === id) ||
      pack.communities.find((c) => c.id === DEFAULT_ID);
    main.textContent = "";
    for (const node of renderSearch()) {
      main.appendChild(node);
    }
    main.appendChild(renderHeader(community));
    main.appendChild(renderPresent(community));
    main.appendChild(renderPublishers(community));
    main.appendChild(renderServices(community));
    main.appendChild(renderActions(community));
  };

  const render = (text) => {
    const line = document.createElement("p");
    line.textContent = text;
    main.textContent = "";
    main.appendChild(line);
  };

  const screenOf = (hash) => SCREENS.find((screen) => hash.startsWith(screen)) || SCREENS[0];

  const route = () => {
    if (!location.hash) {
      location.hash = DEFAULT_HASH;
    }
    const hash = location.hash || DEFAULT_HASH;
    const screen = screenOf(hash);
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
      const match = hash.match(/^#\/community\/(\d+)/);
      renderCommunity(match ? Number(match[1]) : DEFAULT_ID);
    }
  };

  const setChip = () => {
    chip.textContent = navigator.onLine ? "Online" : "Offline";
  };

  window.addEventListener("hashchange", route);
  window.addEventListener("online", setChip);
  window.addEventListener("offline", setChip);
  setChip();
  renderFooter();
  route();
})();
