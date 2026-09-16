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
  // Reassigned once, at most, by maybeApplyStoredPack below (Task-24): every render reads this
  // variable through closure, so swapping it and calling route() again is the whole update.
  let pack = JSON.parse(document.getElementById("pack").textContent);
  const builtInBuilt = pack.built;

  if (pack.pack_version !== 2) {
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
      // Plain text, not chips: testers read the chips as buttons (Task-30).
      h(
        "p",
        { class: "present-list" },
        community.present.length
          ? community.present.map((item) => item.name).join(" · ")
          : "Not recorded",
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

  // What each verdict word means, in the words of pipeline/rules.py, for a first-time reader
  // (Task-30). Static labels: the verdicts themselves still come from the pack.
  const VERDICT_MEANING = {
    works: "the best available path meets the published requirement",
    degraded: "may work, but falls short of the requirement",
    fails: "no published path can carry it",
    nodata: "no source records enough to judge",
  };

  // Not .verdict-badge: tests count those per service row and per compare column.
  const renderVerdictLegend = () =>
    h(
      "ul",
      { class: "verdict-legend" },
      Object.keys(VERDICTS).map((verdictId) =>
        h(
          "li",
          { class: "verdict-legend__item" },
          h(
            "span",
            { class: `legend-badge legend-badge--${verdictId}` },
            h("span", { "aria-hidden": "true" }, VERDICTS[verdictId].glyph),
            VERDICTS[verdictId].word,
          ),
          ` ${VERDICT_MEANING[verdictId]}`,
        ),
      ),
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
    // After the four answers, not before them: the answer is what a reader came for.
    section.appendChild(renderVerdictLegend());
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
  // work, dropped whole (never cut mid-word) if the text would pass the limit. Services join
  // with " - ", not the "·" the rest of the UI uses, so the body stays in the GSM-7 alphabet
  // and the SMS uses fewer segments (Task-26; BACKLOG 2026-09-15, Task-13).
  const statementShort = (community) => {
    const firstNotWorks = community.services.find((service) => service.verdict !== "works");
    const build = (withReason) =>
      `${community.name}: ${community.services
        .map((service) => {
          const label = `${SMS_LABEL[service.service] || service.service} ${statementWord(service.verdict)}`;
          return withReason && service === firstNotWorks ? `${label} (${plain(service.reason)})` : label;
        })
        .join(" - ")}. Crosscheck, data ${pack.built}.`;
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
    // Folded by default (Task-30): the attribution lines stay one tap away, as the licences
    // require, without filling the bottom of every screen.
    const sources = h(
      "details",
      { class: "footer__sources" },
      h("summary", { class: "footer__summary" }, `Sources and licences (${pack.attributions.length})`),
    );
    for (const item of pack.attributions) {
      const parts = [item.text];
      if (item.licence) {
        parts.push(item.licence);
      }
      const span = h("span", { class: "footer__source" }, parts.join(" · "));
      if (item.date) {
        span.appendChild(document.createTextNode(" · "));
        span.appendChild(h("span", { class: "fig fig--xs" }, item.date));
      }
      sources.appendChild(span);
    }
    footer.appendChild(sources);
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

  // Great-circle distance in km between two latitude/longitude points (mean Earth diameter
  // 12,742 km). Layout for "Use my location", not a verdict (Task-30).
  const distanceKm = (lat1, lon1, lat2, lon2) => {
    const rad = Math.PI / 180;
    const a =
      Math.sin(((lat2 - lat1) * rad) / 2) ** 2 +
      Math.cos(lat1 * rad) * Math.cos(lat2 * rad) * Math.sin(((lon2 - lon1) * rad) / 2) ** 2;
    return 12742 * Math.asin(Math.sqrt(a));
  };

  const nearestCommunity = (lat, lon) => {
    let best = null;
    for (const community of pack.communities) {
      const km = distanceKm(lat, lon, community.lat, community.lon);
      if (!best || km < best.km) {
        best = { community, km };
      }
    }
    return best;
  };

  // Shown once on the community "Use my location" opened, then cleared.
  let locateNote = null;

  const renderLocate = (community) => {
    const status = h("p", { class: "locate-status", role: "status" });
    if (locateNote && locateNote.id === community.id) {
      status.textContent = locateNote.text;
    }
    locateNote = null;
    const button = h("button", { type: "button", class: "locate-button" }, "Use my location");
    const fail = () => {
      button.disabled = false;
      status.textContent = "Location not available on this phone";
    };
    button.addEventListener("click", () => {
      if (!navigator.geolocation) {
        fail();
        return;
      }
      button.disabled = true;
      status.textContent = "Finding your location...";
      // The phone's own GPS answers with no network; nothing is stored or sent.
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const found = nearestCommunity(position.coords.latitude, position.coords.longitude);
          locateNote = {
            id: found.community.id,
            text: `Nearest community: ${found.community.name}, ${Math.round(found.km)} km away`,
          };
          const hash = `#/community/${found.community.id}`;
          if (location.hash === hash) {
            route();
          } else {
            location.hash = hash;
          }
        },
        fail,
        { enableHighAccuracy: true, timeout: 15000, maximumAge: 600000 },
      );
    });
    return [button, status];
  };

  // One bar for search and compare (Task-30): a result opens its community, and its Compare
  // button compares it with the community on screen.
  const renderSearch = (current) => {
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
        const item = h("li", { class: "search-results__item" }, row);
        if (current && community.id !== current.id) {
          const compare = h("button", { type: "button", class: "result-row__compare" }, "Compare");
          compare.addEventListener("click", () => {
            location.hash = `#/compare/${current.id}/${community.id}`;
          });
          item.appendChild(compare);
        }
        results.appendChild(item);
      }
    });
    return [
      h(
        "div",
        { class: "search" },
        input,
        current ? h("div", { class: "search__tools" }, renderLocate(current)) : null,
      ),
      results,
    ];
  };

  // Set when a compare route names no known community: Screen 1 opens with its search focused.
  let openSearch = false;

  const renderCommunity = (id) => {
    const community =
      pack.communities.find((c) => c.id === id) ||
      pack.communities.find((c) => c.id === DEFAULT_ID);
    main.textContent = "";
    for (const node of renderSearch(community)) {
      main.appendChild(node);
    }
    if (openSearch) {
      openSearch = false;
      main.querySelector(".search-input").focus();
    }
    main.appendChild(
      h(
        "p",
        { class: "intro" },
        "What published sources say about phone and internet at this community, and what that allows. Crosscheck does not measure signal.",
      ),
    );
    const header = renderHeader(community);
    header.appendChild(renderFreshness(community));
    main.appendChild(header);
    // Plainest answer first (Task-30): what works, then who says so, then the detail.
    const services = renderServices(community);
    services.appendChild(renderStatementButtons(community));
    main.appendChild(services);
    main.appendChild(renderPublishers(community));
    main.appendChild(renderPresent(community));
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

  // Task-29: deterministic grouping of the points visible under the active filter into zoom
  // clusters. Pure (no DOM, no pack), so it is unit-testable from the browser test as
  // window.__map.cluster below and produces identical output for identical input every call.
  const CLUSTER_RADIUS = 12;
  const CLUSTER_MAX_ZOOM = 5;

  // Walk ascending y, then x, then id; each unassigned point takes every other unassigned point
  // within CLUSTER_RADIUS / zoom (Euclidean, view-box units) into its own group; two or more
  // members become a cluster at the centroid, one member stays a single (Task-29 Execution
  // Guide). No clustering at zoom 5 or more.
  const cluster = (points, zoom) => {
    if (zoom >= CLUSTER_MAX_ZOOM) {
      return { clusters: [], singles: [...points] };
    }
    const radius = CLUSTER_RADIUS / zoom;
    const sorted = [...points].sort((a, b) => a.y - b.y || a.x - b.x || a.id - b.id);
    const assigned = new Set();
    const clusters = [];
    const singles = [];
    for (const seed of sorted) {
      if (assigned.has(seed.id)) {
        continue;
      }
      const members = [seed];
      assigned.add(seed.id);
      for (const other of sorted) {
        if (assigned.has(other.id)) {
          continue;
        }
        if (Math.hypot(seed.x - other.x, seed.y - other.y) <= radius) {
          members.push(other);
          assigned.add(other.id);
        }
      }
      if (members.length === 1) {
        singles.push(seed);
        continue;
      }
      const verdicts = { works: 0, degraded: 0, fails: 0, nodata: 0 };
      for (const member of members) {
        verdicts[member.verdict] = (verdicts[member.verdict] || 0) + 1;
      }
      clusters.push({
        id: members
          .map((m) => m.id)
          .sort((a, b) => a - b)
          .join("-"),
        x: members.reduce((sum, m) => sum + m.x, 0) / members.length,
        y: members.reduce((sum, m) => sum + m.y, 0) / members.length,
        count: members.length,
        verdicts,
        members: members.map((m) => m.id).sort((a, b) => a - b),
        minX: Math.min(...members.map((m) => m.x)),
        maxX: Math.max(...members.map((m) => m.x)),
        minY: Math.min(...members.map((m) => m.y)),
        maxY: Math.max(...members.map((m) => m.y)),
      });
    }
    return { clusters, singles };
  };

  // Exposed for the browser test, following the existing window.__statement pattern.
  window.__map = { cluster };

  // ``layersRaw`` is the hash's own ``layers`` value (or null when absent): threaded through
  // unchanged so selecting a point or switching a filter never clobbers a carrier toggle state.
  const mapHash = (filterId, selectedId, layersRaw) => {
    let hash = `#/map?filter=${filterId}`;
    if (selectedId !== null && selectedId !== undefined) {
      hash += `&selected=${selectedId}`;
    }
    if (layersRaw !== null && layersRaw !== undefined) {
      hash += `&layers=${layersRaw}`;
    }
    return hash;
  };

  // Point markup and geometry of design/screens/assets/build.mjs (s = 5, hit r = 16, ring r = 9).
  const renderPoint = (community, isSelected, filterId, layersRaw) => {
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
      location.hash = mapHash(filterId, community.id, layersRaw);
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

  // Cluster marker geometry (Task-29 Execution Guide): a filled circle, the count as text, and a
  // ring split into arcs by the members' telehealth verdict counts using stroke-dasharray on
  // stacked circles, coloured with the same verdict tokens the points use. Counter-scaled the
  // same way as the points (app.css), so it keeps a constant screen size at any zoom.
  const CLUSTER_RING_R = 9;
  const CLUSTER_VERDICT_ORDER = ["works", "degraded", "fails", "nodata"];

  const clusterRingArcs = (cl) => {
    const circumference = 2 * Math.PI * CLUSTER_RING_R;
    let offset = 0;
    const arcs = [];
    for (const verdict of CLUSTER_VERDICT_ORDER) {
      const count = cl.verdicts[verdict] || 0;
      if (count === 0) {
        continue;
      }
      const length = (count / cl.count) * circumference;
      arcs.push(
        s("circle", {
          class: `map__cluster-arc map__cluster-arc--${verdict}`,
          cx: f1(cl.x),
          cy: f1(cl.y),
          r: CLUSTER_RING_R,
          "stroke-dasharray": `${length.toFixed(2)} ${(circumference - length).toFixed(2)}`,
          "stroke-dashoffset": (-offset).toFixed(2),
        }),
      );
      offset += length;
    }
    return arcs;
  };

  // ``onActivate`` is the zoom-to-bounding-box handler attachMapView owns; kept as a parameter
  // so this stays a plain renderer with no closure over the view/zoom state.
  const renderClusterMarker = (cl, onActivate) => {
    const group = s(
      "g",
      {
        class: "map__cluster",
        role: "button",
        tabindex: "0",
        "aria-label": `${cl.count} communities`,
        "data-id": cl.id,
        "data-count": String(cl.count),
        "data-works": String(cl.verdicts.works || 0),
        "data-degraded": String(cl.verdicts.degraded || 0),
        "data-fails": String(cl.verdicts.fails || 0),
        "data-nodata": String(cl.verdicts.nodata || 0),
      },
      s("circle", { class: "map__hit", cx: f1(cl.x), cy: f1(cl.y), r: 16 }),
      s("circle", { class: "map__cluster-fill", cx: f1(cl.x), cy: f1(cl.y), r: CLUSTER_RING_R }),
      ...clusterRingArcs(cl),
      s(
        "text",
        { class: "map__cluster-count", x: f1(cl.x), y: f1(cl.y + 3), "text-anchor": "middle" },
        String(cl.count),
      ),
    );
    const activate = () => onActivate(cl);
    group.addEventListener("click", activate);
    group.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        activate();
      }
    });
    return group;
  };

  const renderFilterTabs = (active, selectedId, layersRaw) => {
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
        location.hash = mapHash(
          filter.id,
          filter.ids.includes(selectedId) ? selectedId : null,
          layersRaw,
        );
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

  // Map layers (Task-21, Part 2 "Map layer" seam): the pack's own order already draws area
  // (coverage) layers first, then line (region) layers, then point (town) layers -- exactly
  // the Execution Guide's draw order -- so the app never hand-orders layer ids.
  const slugOf = (layer) => (layer.id.startsWith("cov-") ? layer.id.slice(4) : layer.id);

  const renderLayerGroup = (layer, visibleSlugs) => {
    const g = s("g", { class: `map__layer map__layer--${layer.kind}`, "data-layer": layer.id });
    if (layer.kind === "area") {
      if (!visibleSlugs.has(slugOf(layer))) {
        g.setAttribute("hidden", "");
      }
      for (const d of layer.paths) {
        g.appendChild(s("path", { class: "map__layer-shape", d }));
      }
    } else if (layer.kind === "line") {
      for (const d of layer.paths) {
        g.appendChild(s("path", { class: "map__layer-shape", d }));
      }
    } else if (layer.kind === "point") {
      for (const point of layer.paths) {
        g.appendChild(
          s(
            "g",
            { class: "map__town" },
            s("circle", { class: "map__town-dot", cx: f1(point.x), cy: f1(point.y), r: 2 }),
            s(
              "text",
              { class: "map__town-label", x: f1(point.x + 4), y: f1(point.y + 1) },
              point.label,
            ),
          ),
        );
      }
    }
    return g;
  };

  // One chip per area (coverage) layer; its slug (the layer id with any "cov-" prefix
  // dropped) is what the hash's "layers" query carries, e.g. "&layers=telstra,optus".
  const renderLayerChips = (areaLayers, visibleSlugs, filterId, selectedId, layersRaw) => {
    const bar = h("div", { class: "chips layer-chips" });
    for (const layer of areaLayers) {
      const slug = slugOf(layer);
      const chip = h(
        "button",
        {
          type: "button",
          class: "chip layer-chip",
          "aria-pressed": visibleSlugs.has(slug) ? "true" : "false",
        },
        layer.label,
      );
      chip.addEventListener("click", () => {
        const next = new Set(visibleSlugs);
        if (next.has(slug)) {
          next.delete(slug);
        } else {
          next.add(slug);
        }
        const allSlugs = areaLayers.map(slugOf);
        const nextRaw = allSlugs.every((one) => next.has(one))
          ? null
          : allSlugs.filter((one) => next.has(one)).join(",");
        location.hash = mapHash(filterId, selectedId, nextRaw);
      });
      bar.appendChild(chip);
    }
    return bar;
  };

  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

  // A viewBox coordinate formatted without a forced decimal (unlike f1): "300", not "300.0",
  // so the resting and reset viewBox reads exactly "0 0 300 480" (Task-21 DoD).
  const vnum = (value) => String(Math.round(value * 100) / 100);

  const BASE_VIEW = { x: 0, y: 0, w: 300, h: 480 };
  const ZOOM_MIN = 1;
  const ZOOM_MAX = 8;
  // Community labels appear once zoomed at least this far in (Task-21 Execution Guide).
  const LABEL_ZOOM = 3;

  // Zoom (wheel, pinch) and pan (one-pointer drag) over the map's viewBox, plus the labels
  // that appear once zoomed in far enough and the Task-29 point clusters. Point/ring/label
  // geometry stays a constant screen size at any zoom through the CSS transform keyed on the
  // --map-zoom custom property this sets (app.css), rather than by rebuilding every point's own
  // radius on each zoom step.
  const attachMapView = (svg, shownCommunities, selectedId, pointGroupsById) => {
    const view = { ...BASE_VIEW };
    let zoom = ZOOM_MIN;
    const labelsGroup = s("g", { class: "map__zoom-labels" });
    svg.appendChild(labelsGroup);
    const clustersLayer = s("g", { class: "map__clusters" });
    svg.appendChild(clustersLayer);

    // Task-29: recompute clusters (and, since they depend on which points are clustered, the
    // zoom labels too) for the current zoom. Never called from a pan-only move; see the
    // scheduling below.
    const updateClustering = () => {
      const level = clamp(Math.round(zoom), ZOOM_MIN, ZOOM_MAX);
      const candidates = shownCommunities
        .filter((community) => community.id !== selectedId)
        .map((community) => ({
          id: community.id,
          x: community.x,
          y: community.y,
          verdict: telehealthVerdict(community),
        }));
      const { clusters } = cluster(candidates, zoom);
      const clusteredIds = new Set();
      for (const group of clusters) {
        for (const id of group.members) {
          clusteredIds.add(id);
        }
      }
      for (const [id, group] of pointGroupsById) {
        if (id !== selectedId && clusteredIds.has(id)) {
          group.setAttribute("hidden", "");
        } else {
          group.removeAttribute("hidden");
        }
      }
      clustersLayer.textContent = "";
      for (const group of clusters) {
        clustersLayer.appendChild(renderClusterMarker(group, zoomToCluster));
      }
      labelsGroup.textContent = "";
      if (level >= LABEL_ZOOM) {
        for (const community of shownCommunities) {
          if (community.id === selectedId || clusteredIds.has(community.id)) {
            continue; // selected already carries its own label; clustered members draw none
          }
          labelsGroup.appendChild(
            s(
              "text",
              {
                class: "map__label",
                x: f1(community.x),
                y: f1(community.y - 8),
                "text-anchor": "middle",
              },
              community.name,
            ),
          );
        }
      }
    };

    // Coalesces every zoom change within one frame into a single recompute (wheel and pinch can
    // fire many times before the next paint); a plain click (reset, tap-to-cluster) recomputes
    // immediately instead, since it is a single discrete change, not a rapid stream.
    let clusterFrame = null;
    const scheduleClusterUpdate = () => {
      if (clusterFrame !== null) {
        return;
      }
      clusterFrame = requestAnimationFrame(() => {
        clusterFrame = null;
        updateClustering();
      });
    };

    const apply = () => {
      svg.setAttribute(
        "viewBox",
        `${vnum(view.x)} ${vnum(view.y)} ${vnum(view.w)} ${vnum(view.h)}`,
      );
      const level = clamp(Math.round(zoom), ZOOM_MIN, ZOOM_MAX);
      svg.setAttribute("data-zoom", String(level));
      svg.style.setProperty("--map-zoom", String(zoom));
    };

    // Tap or Enter on a cluster (Task-29 Execution Guide): the viewBox becomes the bounding box
    // of its members with 20 percent padding, clamped to zoom 1-8 and to the map bounds.
    const zoomToCluster = (group) => {
      const paddedW = Math.max(group.maxX - group.minX, 0.001) * 1.2;
      const paddedH = Math.max(group.maxY - group.minY, 0.001) * 1.2;
      const targetZoom = clamp(
        Math.min(BASE_VIEW.w / paddedW, BASE_VIEW.h / paddedH),
        ZOOM_MIN,
        ZOOM_MAX,
      );
      const newW = BASE_VIEW.w / targetZoom;
      const newH = BASE_VIEW.h / targetZoom;
      const cx = (group.minX + group.maxX) / 2;
      const cy = (group.minY + group.maxY) / 2;
      view.x = clamp(cx - newW / 2, BASE_VIEW.x, BASE_VIEW.x + BASE_VIEW.w - newW);
      view.y = clamp(cy - newH / 2, BASE_VIEW.y, BASE_VIEW.y + BASE_VIEW.h - newH);
      view.w = newW;
      view.h = newH;
      zoom = targetZoom;
      apply();
      updateClustering();
    };

    const toSvgPoint = (clientX, clientY) => {
      const rect = svg.getBoundingClientRect();
      return {
        x: view.x + ((clientX - rect.left) / rect.width) * view.w,
        y: view.y + ((clientY - rect.top) / rect.height) * view.h,
      };
    };

    const zoomAt = (factor, anchorX, anchorY) => {
      const newZoom = clamp(zoom * factor, ZOOM_MIN, ZOOM_MAX);
      const newW = BASE_VIEW.w / newZoom;
      const newH = BASE_VIEW.h / newZoom;
      const ratioX = (anchorX - view.x) / view.w;
      const ratioY = (anchorY - view.y) / view.h;
      view.x = anchorX - ratioX * newW;
      view.y = anchorY - ratioY * newH;
      view.w = newW;
      view.h = newH;
      zoom = newZoom;
      apply();
      scheduleClusterUpdate();
    };

    svg.classList.add("map--zoomable");
    svg.addEventListener(
      "wheel",
      (event) => {
        event.preventDefault();
        const point = toSvgPoint(event.clientX, event.clientY);
        zoomAt(event.deltaY < 0 ? 1.2 : 1 / 1.2, point.x, point.y);
      },
      { passive: false },
    );

    const pointers = new Map();
    let pinchStartDistance = null;
    let pinchStartZoom = null;
    const distance = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
    const midpoint = (a, b) => ({ x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 });

    svg.addEventListener("pointerdown", (event) => {
      // No setPointerCapture: capturing on every pointerdown (including a plain tap on a
      // community point) intercepts the click the point's own listener needs (Task-08).
      pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
      if (pointers.size === 2) {
        const [a, b] = [...pointers.values()];
        pinchStartDistance = distance(a, b);
        pinchStartZoom = zoom;
      }
    });

    svg.addEventListener("pointermove", (event) => {
      if (!pointers.has(event.pointerId)) {
        return;
      }
      const previous = pointers.get(event.pointerId);
      pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
      if (pointers.size === 1) {
        const rect = svg.getBoundingClientRect();
        view.x -= ((event.clientX - previous.x) / rect.width) * view.w;
        view.y -= ((event.clientY - previous.y) / rect.height) * view.h;
        apply();
      } else if (pointers.size === 2 && pinchStartDistance) {
        const [a, b] = [...pointers.values()];
        const mid = midpoint(a, b);
        const point = toSvgPoint(mid.x, mid.y);
        const targetZoom = clamp(
          pinchStartZoom * (distance(a, b) / pinchStartDistance),
          ZOOM_MIN,
          ZOOM_MAX,
        );
        zoomAt(targetZoom / zoom, point.x, point.y);
      }
    });

    const endPointer = (event) => {
      pointers.delete(event.pointerId);
      if (pointers.size < 2) {
        pinchStartDistance = null;
        pinchStartZoom = null;
      }
    };
    svg.addEventListener("pointerup", endPointer);
    svg.addEventListener("pointercancel", endPointer);
    svg.addEventListener("pointerleave", endPointer);

    const reset = () => {
      view.x = BASE_VIEW.x;
      view.y = BASE_VIEW.y;
      view.w = BASE_VIEW.w;
      view.h = BASE_VIEW.h;
      zoom = ZOOM_MIN;
      apply();
      updateClustering();
    };

    apply();
    updateClustering();
    return { reset };
  };

  const renderMap = (filterId, selectedId, layersRaw) => {
    const filter = pack.filters.find((f) => f.id === filterId) || pack.filters[0];
    const shown = pack.communities.filter((c) => filter.ids.includes(c.id));
    const selected = pack.communities.find((c) => c.id === selectedId) || null;
    // The selected point is drawn last so its ring and label sit above its neighbours.
    const ordered = [
      ...shown.filter((c) => c !== selected),
      ...shown.filter((c) => c === selected),
    ];
    const areaLayers = pack.layers.filter((layer) => layer.kind === "area");
    const visibleSlugs =
      layersRaw === null || layersRaw === undefined
        ? new Set(areaLayers.map(slugOf))
        : new Set(layersRaw.split(",").filter(Boolean));
    // Kept by id so attachMapView can hide and show them again as clusters form and split
    // (Task-29), without rebuilding the point markup on every zoom change.
    const pointGroups = ordered.map((c) => renderPoint(c, c === selected, filter.id, layersRaw));
    const pointGroupsById = new Map(ordered.map((c, i) => [c.id, pointGroups[i]]));
    const svg = s(
      "svg",
      {
        class: "map",
        role: "img",
        "aria-label": `Map of the Northern Territory, ${shown.length} of ${pack.count} communities shown`,
        viewBox: "0 0 300 480",
      },
      // The land is the base terrain the layers and points sit on: painted first, not last
      // (a deliberate departure from a literal reading of the Execution Guide's draw-order
      // sentence -- its own opaque --map-land fill, drawn after the coverage layers, painted
      // over every one of them; see this task's Status notes).
      s("g", { class: "map__land" }, s("path", { d: pack.outline })),
      ...pack.layers.map((layer) => renderLayerGroup(layer, visibleSlugs)),
      ...pointGroups,
    );
    main.textContent = "";
    const bar = renderFilterTabs(filter, selected ? selected.id : null, layersRaw);
    main.appendChild(bar);
    main.appendChild(
      renderLayerChips(areaLayers, visibleSlugs, filter.id, selected ? selected.id : null, layersRaw),
    );
    main.appendChild(svg);
    const mapView = attachMapView(svg, shown, selected ? selected.id : null, pointGroupsById);
    const resetButton = h(
      "button",
      { type: "button", class: "button button--secondary map-controls__reset" },
      "Reset view",
    );
    resetButton.addEventListener("click", () => mapView.reset());
    main.appendChild(resetButton);
    main.appendChild(renderLegend(shown.length));
    if (selected) {
      for (const node of renderMapPanel(selected)) {
        main.appendChild(node);
      }
    }
    const activeTab = bar.querySelector("[aria-selected=true]");
    activeTab.scrollIntoView({ inline: "nearest", block: "nearest" });
    watchOverflow(bar);
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
          { class: "link-row link-row--changes" },
          h(
            "span",
            { class: "link-row__text" },
            h("a", { class: "text-link", href: `#/community/${item.id}` }, item.name),
            `: ${item.text}`,
          ),
          h(
            "span",
            { class: "source-line link-row__date" },
            h("span", { class: "fig fig--xs" }, item.date),
          ),
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

  let lastPath = null;

  const route = () => {
    if (!location.hash) {
      location.hash = DEFAULT_HASH;
    }
    const hash = location.hash || DEFAULT_HASH;
    const screen = screenOf(hash);
    // A new screen or community opens at its top (Task-30): the previous scroll offset hid the
    // map filters and the search results on a phone. Query-only changes (a map selection) keep it.
    const path = hash.split("?")[0];
    if (path !== lastPath) {
      lastPath = path;
      window.scrollTo(0, 0);
    }
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
      const layersParam = query.has("layers") ? query.get("layers") : null;
      renderMap(
        query.get("filter") || "all",
        selectedParam ? Number(selectedParam) : null,
        layersParam,
      );
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

  // The app works offline either way (it renders data_pack.json, requests nothing at runtime),
  // so the chip says that rather than "Online", which misled testers into thinking the app
  // needed a connection (Task-26; BACKLOG 2026-09-15, Task-07).
  const setChip = () => {
    chip.textContent = navigator.onLine ? "Offline-ready" : "Offline";
  };

  // Task-24: a pack held in the browser's own storage (store.js) that is newer than the
  // built-in one. The chip sits beside the existing offline chip; index.html carries no markup
  // for it (only app.js owns this feature), so the wrapper and the chip are both built here.
  const updateChipText = h("span", { class: "update-chip__text" });
  const useBuiltInButton = h(
    "button",
    { type: "button", class: "update-chip__button" },
    "Use built-in pack",
  );
  const updateChip = h("span", { class: "chip update-chip", hidden: "" }, updateChipText, useBuiltInButton);
  const headerChips = h("span", { class: "header-chips" });
  chip.replaceWith(headerChips);
  headerChips.appendChild(chip);
  headerChips.appendChild(updateChip);

  useBuiltInButton.addEventListener("click", async () => {
    try {
      await window.CrosscheckStore.clear();
    } catch (error) {
      // Storage is optional; a reload with nothing stored returns to the built-in pack anyway.
    }
    location.reload();
  });

  // Swaps to a stored pack that is newer than the built-in one, if any, and re-renders once.
  // Runs after the first synchronous render from the built-in pack so the existing browser
  // tests that wait for the first screen keep passing (Execution Guide).
  const maybeApplyStoredPack = async () => {
    let stored = null;
    try {
      stored = await window.CrosscheckStore.load();
    } catch (error) {
      stored = null;
    }
    if (stored && typeof stored.built === "string" && stored.built > builtInBuilt) {
      pack = stored;
      updateChipText.textContent = `Pack updated ${stored.built}`;
      updateChip.hidden = false;
      renderFooter();
      route();
    }
  };

  // A scrollable tab row says which side hides more tabs (Task-30): Chrome on Android shows no
  // scrollbar, so without this nothing tells a reader the row scrolls. app.css fades that edge.
  const updateOverflow = (bar) => {
    const hidden = bar.scrollWidth - bar.clientWidth;
    const sides = [];
    if (bar.scrollLeft > 1) {
      sides.push("left");
    }
    if (bar.scrollLeft < hidden - 1) {
      sides.push("right");
    }
    bar.setAttribute("data-overflow", sides.join(" "));
  };

  const watchOverflow = (bar) => {
    bar.addEventListener("scroll", () => updateOverflow(bar), { passive: true });
    updateOverflow(bar);
  };

  window.addEventListener("resize", () => {
    for (const bar of document.querySelectorAll(".tabs")) {
      updateOverflow(bar);
    }
  });
  watchOverflow(document.querySelector(".top-bar .tabs"));

  window.addEventListener("hashchange", route);
  window.addEventListener("online", setChip);
  window.addEventListener("offline", setChip);
  setChip();
  renderFooter();
  route();
  registerHost();
  maybeApplyStoredPack();
})();
