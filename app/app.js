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

  const renderAgreement = (community) =>
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
    );

  const renderPublishers = (community) => {
    const section = h(
      "section",
      { class: "section" },
      h("h2", { class: "section__title" }, "What the sources say"),
      renderAgreement(community),
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

  const renderBadge = (verdictId) =>
    h(
      "span",
      { class: `verdict-badge verdict-badge--${verdictId}` },
      h("span", { "aria-hidden": "true" }, VERDICTS[verdictId].glyph),
      VERDICTS[verdictId].word,
    );

  const renderServiceRow = (service) => {
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
        renderBadge(service.verdict),
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

  // Short service names for the SMS text, where every character counts.
  const SMS_LABEL = {
    telehealth_video: "Telehealth video",
    school_video_meeting: "School video",
    mygov_text: "myGov",
    voice_sms: "Voice/SMS",
  };

  const SMS_MAX_CHARS = 300;

  const statementWord = (verdict) => (verdict === "nodata" ? "NOT RECORDED" : verdict.toUpperCase());

  const plain = (text) => String(text).split("`").join("");

  const oldestSource = (community) =>
    `Oldest source: ${pack.sources[community.freshness.source].source} · ${community.freshness.date}`;

  // One SMS-sized line from pack strings: the reason only for the first service that does not
  // work, dropped whole (never cut mid-word) if the text would pass the limit.
  const statementShort = (community) => {
    const firstNotWorks = community.services.find((service) => service.verdict !== "works");
    const build = (withReason) =>
      `${community.name}: ${community.services
        .map((service) => {
          const label = `${SMS_LABEL[service.service] || service.service} ${statementWord(service.verdict)}`;
          return withReason && service === firstNotWorks ? `${label} (${plain(service.reason)})` : label;
        })
        .join(" · ")}. Crosscheck, data ${pack.built}.`;
    const full = build(true);
    return full.length < SMS_MAX_CHARS ? full : build(false);
  };

  const statementLong = (community) => {
    const population = pack.sources[community.population.src];
    const services = community.services.map(
      (service) =>
        `${SERVICE_LABEL[service.service] || service.service}: ${statementWord(service.verdict)}, ${plain(service.reason)}.`,
    );
    return [
      `${community.name} (${community.region}) has a population of ${community.population.value.toLocaleString("en-US")} (${population.source}, ${population.date}).`,
      `${community.agreement.covered} of ${community.agreement.available} sources say covered (${community.agreement.note}).`,
      `Best available path: ${plain(community.path.note)} (${community.path.rule}, ${community.path.date}).`,
      ...services,
      `${oldestSource(community)}.`,
      "Every figure is from a published source; the app measures nothing.",
    ].join(" ");
  };

  // Byte size limit for one LoRa/Meshtastic packet payload (Task-22): the app never talks to a
  // radio, but the text must be short enough to be pasted into one packet by hand.
  const MESH_MAX_BYTES = 200;

  const byteLength = (text) => new TextEncoder().encode(text).length;

  // The third statement: community name and "crosscheck" always stay; the fields between them
  // (the four services, the agreement count, the build date) are dropped from the end, least
  // essential first, until the whole line fits one mesh packet.
  const statementMesh = (community) => {
    const serviceParts = community.services.map(
      (service) => `${SMS_LABEL[service.service] || service.service} ${statementWord(service.verdict)}`,
    );
    const droppable = [
      ...serviceParts,
      `agree ${community.agreement.covered}/${community.agreement.available}`,
      pack.built.slice(0, 10),
    ];
    for (let count = droppable.length; count >= 0; count -= 1) {
      const text = [community.name, ...droppable.slice(0, count), "crosscheck"].join(" - ");
      if (byteLength(text) <= MESH_MAX_BYTES) {
        return text;
      }
    }
    throw new Error(`statementMesh: ${community.name} exceeds ${MESH_MAX_BYTES} bytes`);
  };

  // Clipboard first; a selected off-screen textarea where the Clipboard API is refused.
  const copyText = async (text) => {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(text);
        return;
      } catch (error) {
        // Fall through to the textarea.
      }
    }
    const area = h("textarea", {
      class: "statement-copy",
      readonly: "",
      "aria-hidden": "true",
      style: "position: fixed; opacity: 0",
    });
    area.value = text;
    document.body.appendChild(area);
    area.select();
    document.execCommand("copy");
    area.remove();
  };

  const renderStatementButtons = (community) => {
    const smsLink = h(
      "a",
      { class: "button button--primary", href: `sms:?body=${encodeURIComponent(statementShort(community))}` },
      "Send as SMS",
    );
    const copyButton = h("button", { type: "button", class: "button button--secondary" }, "Copy statement");
    let resetTimer = null;
    copyButton.addEventListener("click", async () => {
      await copyText(statementLong(community));
      copyButton.textContent = "Copied";
      clearTimeout(resetTimer);
      resetTimer = setTimeout(() => {
        copyButton.textContent = "Copy statement";
      }, 2000);
    });
    const meshText = statementMesh(community);
    const meshButton = h(
      "button",
      { type: "button", class: "button", "data-text": meshText },
      "Copy mesh text",
    );
    let meshResetTimer = null;
    meshButton.addEventListener("click", async () => {
      await copyText(meshText);
      meshButton.textContent = "Copied";
      clearTimeout(meshResetTimer);
      meshResetTimer = setTimeout(() => {
        meshButton.textContent = "Copy mesh text";
      }, 2000);
    });
    const meshCaption = h(
      "div",
      { class: "source-line" },
      `Fits one LoRa mesh packet (${MESH_MAX_BYTES} bytes)`,
    );
    return h(
      "div",
      { class: "share" },
      h("div", { class: "share-card__buttons" }, smsLink, copyButton, meshButton, meshCaption),
    );
  };

  const renderFreshness = (community) =>
    h(
      "span",
      { class: "source-line community-header__freshness" },
      `Oldest source: ${pack.sources[community.freshness.source].source} · `,
      h("span", { class: "fig fig--xs" }, community.freshness.date),
    );

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

  const renderSearch = ({
    inputClass = "search-input",
    placeholder = `Search ${pack.count} communities`,
    label = "Search communities",
    hashFor = (community) => `#/community/${community.id}`,
  } = {}) => {
    const results = h("ul", { class: "search-results" });
    const input = h("input", {
      class: inputClass,
      type: "search",
      placeholder,
      "aria-label": label,
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
          location.hash = hashFor(community);
        });
        results.appendChild(h("li", {}, row));
      }
    });
    return [h("div", { class: "search" }, input), results];
  };

  // Set when a compare route names no known community: Screen 1 opens with its search focused.
  let openSearch = false;

  const renderCommunity = (id) => {
    const community =
      pack.communities.find((c) => c.id === id) ||
      pack.communities.find((c) => c.id === DEFAULT_ID);
    main.textContent = "";
    for (const node of renderSearch()) {
      main.appendChild(node);
    }
    main.appendChild(
      h(
        "div",
        { class: "compare-search" },
        renderSearch({
          inputClass: "compare-search__input",
          placeholder: "Compare with...",
          label: "Compare with...",
          hashFor: (other) => `#/compare/${community.id}/${other.id}`,
        }),
      ),
    );
    if (openSearch) {
      openSearch = false;
      main.querySelector(".search-input").focus();
    }
    const header = renderHeader(community);
    header.appendChild(renderFreshness(community));
    main.appendChild(header);
    main.appendChild(renderPresent(community));
    main.appendChild(renderPublishers(community));
    const services = renderServices(community);
    services.appendChild(renderStatementButtons(community));
    main.appendChild(services);
    main.appendChild(renderActions(community));
  };

  // One compare column: the header block with its name linking back, the agreement headline
  // and the four verdict badges (Task-15).
  const renderCompareColumn = (community) => {
    const header = renderHeader(community, "h2");
    const name = header.querySelector(".community-header__name");
    name.textContent = "";
    name.appendChild(
      h("a", { class: "text-link", href: `#/community/${community.id}` }, community.name),
    );
    return h(
      "div",
      { class: "compare__column" },
      header,
      renderAgreement(community),
      community.services.map((service) =>
        h(
          "div",
          { class: "service-row__top compare__service" },
          h("span", { class: "service-row__name" }, SERVICE_LABEL[service.service] || service.service),
          renderBadge(service.verdict),
        ),
      ),
    );
  };

  const renderCompare = (a, b) => {
    main.textContent = "";
    main.appendChild(h("div", { class: "compare" }, renderCompareColumn(a), renderCompareColumn(b)));
  };

  // Exposed for the browser test, which runs the builders over every community in the pack.
  window.__statement = { short: statementShort, long: statementLong, mesh: statementMesh };

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

  // The page as a standalone file: the rendered screen and host-only links are dropped, so the
  // copy is the built file again and renders itself when opened.
  const pageHtml = () => {
    const copy = document.documentElement.cloneNode(true);
    copy.querySelector("main").textContent = "";
    copy.querySelector("footer.footer").textContent = "";
    for (const link of copy.querySelectorAll("link[rel=manifest]")) {
      link.remove();
    }
    return `<!DOCTYPE html>\n${copy.outerHTML}`;
  };

  const saveFile = () => {
    const url = URL.createObjectURL(new Blob([pageHtml()], { type: "text/html" }));
    const link = h("a", { href: url, download: "crosscheck.html", hidden: "" });
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const shareApp = async () => {
    if (navigator.share) {
      const file = new File([pageHtml()], "crosscheck.html", { type: "text/html" });
      try {
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
          await navigator.share({ files: [file], title: "Crosscheck" });
        } else {
          await navigator.share({ url: pack.app_url, title: "Crosscheck" });
        }
        return;
      } catch (error) {
        if (error.name === "AbortError") {
          return;
        }
      }
    }
    saveFile();
  };

  const renderShare = () => {
    const sizes = Object.fromEntries(
      document
        .querySelector("meta[name=crosscheck-sizes]")
        .content.split(";")
        .map((pair) => pair.split("=")),
    );
    const kb = (bytes) => `${Math.floor(Number(bytes) / 1024)} KB`;
    const shareButton = h("button", { type: "button", class: "button button--primary" }, "Share this app");
    const saveButton = h("button", { type: "button", class: "button button--secondary" }, "Save file");
    shareButton.addEventListener("click", shareApp);
    saveButton.addEventListener("click", saveFile);
    main.textContent = "";
    const changes = renderChanges(pack);
    const transfer = h("div", { class: "transfer" });
    main.appendChild(
      h(
        "div",
        { class: "share" },
        h(
          "div",
          { class: "share-card" },
          h("div", { class: "share-card__qr" }, document.getElementById("qr").content.cloneNode(true)),
          h(
            "div",
            { class: "share-card__meta" },
            h(
              "div",
              {},
              "Data pack ",
              h("span", { class: "fig" }, pack.built),
              " · ",
              h("span", { class: "fig" }, kb(sizes.pack)),
            ),
            h("div", {}, "App ", h("span", { class: "fig" }, kb(sizes.app))),
            h(
              "span",
              { class: "source-line" },
              "Crosscheck build · ",
              h("span", { class: "fig fig--xs" }, pack.built),
            ),
          ),
          h("div", { class: "share-card__buttons" }, shareButton, saveButton),
          h(
            "p",
            { class: "share-card__statement" },
            "Crosscheck shows what published sources say about a community's connectivity and what that allows. It does not measure signal. Every value shows its source and date.",
          ),
        ),
        transfer,
        changes,
      ),
    );
    // The camera loop and the camera read live in transfer.js (layer rule 8); this screen only
    // gives it the container and the same page bytes Save file writes.
    window.CrosscheckTransfer.mount(transfer, pageHtml);
  };

  // The Changes list is ordered by the pipeline; the browser does no sorting or filtering
  // (Task-14 Execution Guide).
  const renderChanges = (pack) => {
    if (!pack.changes) {
      return null;
    }
    const { from, to, items } = pack.changes;
    const section = h(
      "section",
      { class: "section" },
      h("h2", { class: "section__title" }, `Changes ${from} -> ${to}`),
    );
    if (items.length === 0) {
      section.appendChild(h("div", { class: "source-line" }, `No changes between ${from} and ${to}`));
      return section;
    }
    for (const item of items) {
      section.appendChild(
        h(
          "div",
          { class: "link-row" },
          h("a", { class: "text-link", href: `#/community/${item.id}` }, item.name),
          `: ${item.text} · `,
          h("span", { class: "source-line" }, h("span", { class: "fig fig--xs" }, item.date)),
        ),
      );
    }
    return section;
  };

  // Host-only install support: never touched over file://, so the single file stands alone.
  const registerHost = () => {
    if (location.protocol !== "https:") {
      return;
    }
    document.head.appendChild(h("link", { rel: "manifest", href: "manifest.webmanifest" }));
    if ("serviceWorker" in navigator) {
      window.__swRegistered = true;
      navigator.serviceWorker.register("sw.js").catch(() => {});
    }
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
      renderShare();
    } else if (hash.startsWith("#/compare")) {
      // An unknown id falls back to the known one's community route, or Screen 1 with the
      // search open when neither is known.
      const found = hash
        .split("?")[0]
        .split("/")
        .slice(2, 4)
        .map((part) => pack.communities.find((c) => c.id === Number(part)))
        .filter(Boolean);
      if (found.length === 2) {
        renderCompare(found[0], found[1]);
      } else if (found.length === 1) {
        location.replace(`#/community/${found[0].id}`);
      } else {
        openSearch = true;
        location.replace(DEFAULT_HASH);
      }
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
  registerHost();
})();
