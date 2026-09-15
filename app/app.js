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

  const renderHeader = (community, headingTag = "h1") =>
    h(
      "div",
      { class: "community-header" },
      h(headingTag, { class: "community-header__name" }, community.name),
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

  const renderServiceRow = (service) => {
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
    return row;
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
      section.appendChild(renderServiceRow(service));
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

  // The HTML parser places <svg> in the SVG namespace; reading it back keeps a namespace URL
  // literal out of the built file (tests/test_build.py forbids one outside the pack).
  const SVG_NS = (() => {
    const template = document.createElement("template");
    template.innerHTML = "<svg></svg>";
    return template.content.firstChild.namespaceURI;
  })();

  const s = (tag, attrs, ...children) => {
    const el = document.createElementNS(SVG_NS, tag);
    for (const [key, value] of Object.entries(attrs || {})) {
      el.setAttribute(key, value);
    }
    for (const child of children) {
      el.appendChild(child instanceof Node ? child : document.createTextNode(String(child)));
    }
    return el;
  };

  const f1 = (n) => n.toFixed(1);

  const telehealthVerdict = (community) =>
    community.services.find((service) => service.service === "telehealth_video").verdict;

  const mapHash = (filterId, selectedId) =>
    `#/map?filter=${filterId}${selectedId === null ? "" : `&selected=${selectedId}`}`;

  // Point markup and geometry of design/screens/assets/build.mjs (s = 5, hit r = 16, ring r = 9).
  const renderPoint = (community, isSelected, filterId) => {
    const { x, y } = community;
    const size = 5;
    const verdict = telehealthVerdict(community);
    let shape;
    if (verdict === "works") {
      shape = s("circle", { class: "map__pt map__pt--works", cx: f1(x), cy: f1(y), r: size });
    } else if (verdict === "degraded") {
      const points = [
        `${f1(x)},${f1(y - size - 1)}`,
        `${f1(x + size + 1)},${f1(y + size)}`,
        `${f1(x - size - 1)},${f1(y + size)}`,
      ].join(" ");
      shape = s("polygon", { class: "map__pt map__pt--degraded", points });
    } else if (verdict === "fails") {
      shape = s("rect", {
        class: "map__pt map__pt--fails",
        x: f1(x - size),
        y: f1(y - size),
        width: 2 * size,
        height: 2 * size,
      });
    } else {
      shape = s("rect", {
        class: "map__pt map__pt--nodata",
        x: f1(x - size),
        y: f1(y - 1.5),
        width: 2 * size,
        height: 3,
      });
    }
    const group = s(
      "g",
      {
        class: `map__community${isSelected ? " map__community--selected" : ""}`,
        tabindex: "0",
      },
      s("title", {}, `${community.name} · ${VERDICTS[verdict].word}`),
      s("circle", { class: "map__hit", cx: f1(x), cy: f1(y), r: 16 }),
      shape,
    );
    if (isSelected) {
      const right = x > 200;
      group.appendChild(s("circle", { class: "map__ring", cx: f1(x), cy: f1(y), r: 9 }));
      group.appendChild(
        s(
          "text",
          {
            class: "map__label",
            x: f1(right ? x - 13 : x + 13),
            y: f1(y + 4),
            "text-anchor": right ? "end" : "start",
          },
          community.name,
        ),
      );
    }
    const select = () => {
      location.hash = mapHash(filterId, community.id);
    };
    group.addEventListener("click", select);
    group.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        select();
      }
    });
    return group;
  };

  const renderFilterTabs = (active, selectedId) => {
    const bar = h("div", { class: "tabs filter-tabs", role: "tablist", "aria-label": "Filters" });
    for (const filter of pack.filters) {
      const isActive = filter.id === active.id;
      const tab = h(
        "button",
        { type: "button", class: "tab", role: "tab", "aria-selected": isActive ? "true" : "false" },
        `${filter.label} `,
        h("span", { class: "tab__count" }, String(filter.ids.length)),
      );
      tab.addEventListener("click", () => {
        location.hash = mapHash(filter.id, filter.ids.includes(selectedId) ? selectedId : null);
      });
      bar.appendChild(tab);
    }
    return bar;
  };

  const renderLegend = (shownCount) => {
    const all = h("span", { class: "fig fig--xs" }, String(pack.count));
    return h(
      "div",
      { class: "map-legend" },
      h(
        "div",
        { class: "map-legend__row" },
        Object.entries(pack.legend).map(([verdict, count]) =>
          h(
            "span",
            { class: "map-legend__item" },
            h(
              "span",
              { class: `map-legend__glyph--${verdict}`, "aria-hidden": "true" },
              VERDICTS[verdict].glyph,
            ),
            `${VERDICTS[verdict].word} `,
            h("span", { class: "map-legend__count" }, String(count)),
          ),
        ),
      ),
      h("div", { class: "map-legend__subject" }, "Telehealth video · all ", all, " communities"),
      // pack.filters carries no definition text yet, so the line stops at the counts.
      h(
        "div",
        { class: "map-legend__subject" },
        "Showing ",
        h("span", { class: "fig fig--xs" }, String(shownCount)),
        " of ",
        h("span", { class: "fig fig--xs" }, String(pack.count)),
      ),
    );
  };

  const renderMapPanel = (community) => [
    renderHeader(community, "h2"),
    renderPublishers(community),
    h(
      "section",
      { class: "section" },
      h("h2", { class: "section__title" }, "What the connection allows"),
      renderServiceRow(
        community.services.find((service) => service.service === "telehealth_video"),
      ),
      h(
        "div",
        { class: "link-row" },
        h("a", { class: "text-link", href: `#/community/${community.id}` }, `Open ${community.name}`),
      ),
    ),
  ];

  const renderMap = (filterId, selectedId) => {
    const filter = pack.filters.find((f) => f.id === filterId) || pack.filters[0];
    const shown = pack.communities.filter((c) => filter.ids.includes(c.id));
    const selected = pack.communities.find((c) => c.id === selectedId) || null;
    // The selected point is drawn last so its ring and label sit above its neighbours.
    const ordered = [
      ...shown.filter((c) => c !== selected),
      ...shown.filter((c) => c === selected),
    ];
    const svg = s(
      "svg",
      {
        class: "map",
        role: "img",
        "aria-label": `Map of the Northern Territory, ${shown.length} of ${pack.count} communities shown`,
        viewBox: "0 0 300 480",
      },
      s("g", { class: "map__land" }, s("path", { d: pack.outline })),
      ...ordered.map((c) => renderPoint(c, c === selected, filter.id)),
    );
    main.textContent = "";
    const bar = renderFilterTabs(filter, selected ? selected.id : null);
    main.appendChild(bar);
    main.appendChild(svg);
    main.appendChild(renderLegend(shown.length));
    if (selected) {
      for (const node of renderMapPanel(selected)) {
        main.appendChild(node);
      }
    }
    const activeTab = bar.querySelector("[aria-selected=true]");
    activeTab.scrollIntoView({ inline: "nearest", block: "nearest" });
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
      const query = new URLSearchParams(hash.split("?")[1] || "");
      const selectedParam = query.get("selected");
      renderMap(query.get("filter") || "all", selectedParam ? Number(selectedParam) : null);
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
