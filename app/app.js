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

  // Task-34, 2026-09-16: one shape (a circle) in four fill states, departed from DESIGN.md's
  // triangle/square/dash set (design/screens/README.md); the map's own point geometry follows
  // in Task-33.
  const VERDICTS = {
    works: { glyph: "●", word: "Works" },
    degraded: { glyph: "◐", word: "Degraded" },
    fails: { glyph: "○", word: "Fails" },
    nodata: { glyph: "◌", word: "No data" },
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

  // Task-34, 2026-09-16: one meta line -- "<type> · <region> · <n> people" -- carries the
  // population's source and date as a title attribute rather than a visible line, so the
  // header fits one screen's worth of the fold budget (item 7).
  const renderHeader = (community, headingTag = "h1") => {
    const population = pack.sources[community.population.src];
    return h(
      "div",
      { class: "community-header" },
      h(headingTag, { class: "community-header__name" }, community.name),
      h(
        "div",
        {
          class: "community-header__meta",
          title: `${population.source} · ${population.date}`,
        },
        `${community.type} · ${community.region} · ${community.population.value.toLocaleString("en-US")} people`,
      ),
    );
  };

  // "What exists here": the present chips, then a data-backed fact line per flag the pack
  // carries. BushTel's WiFi hours, STAND site and road-condition free text stay out of the
  // pack until OQ1 is answered (pipeline/pack.py BUSHTEL_TEXT_ALLOWED), so only the two
  // flags the pack does carry (road_seasonal_cut, backhaul_2019) render here.
  // Task-34, 2026-09-16: folded behind "What exists here", closed by default -- one of the
  // screen's four folded sections that keep the first screen under the fold (item 6).
  const renderPresent = (community) => {
    const fold = h(
      "details",
      { class: "present-fold section" },
      h("summary", {}, "What exists here"),
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
        fold.appendChild(
          h(
            "div",
            { class: "fact" },
            "Road access is subject to seasonal closure",
            sourceLine(flag.src),
          ),
        );
      } else if (flag.name === "backhaul_2019") {
        fold.appendChild(
          h("div", { class: "fact" }, `Backhaul: ${flag.value}`, sourceLine(flag.src)),
        );
      }
    }
    return fold;
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
    const section = h("section", { class: "publishers" }, renderAgreement(community));
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

  // Task-34, 2026-09-16: folded behind the agreement line, closed by default (item 4); the
  // wording matches what `renderAgreement` already says, in one line.
  const renderSourcesFold = (community) => {
    const { covered, available, note } = community.agreement;
    const summary =
      note === "Sources agree"
        ? `${available} of ${available} sources agree`
        : `Sources disagree: ${covered} of ${available} say covered`;
    return h(
      "details",
      { class: "sources-fold section" },
      h("summary", {}, summary),
      renderPublishers(community),
    );
  };

  const renderBadge = (verdictId, extraClass) =>
    h(
      "span",
      { class: `verdict-badge verdict-badge--${verdictId}${extraClass ? ` ${extraClass}` : ""}` },
      h("span", { "aria-hidden": "true" }, VERDICTS[verdictId].glyph),
      VERDICTS[verdictId].word,
    );

  // Task-34, 2026-09-16: the row is `button.service-row` itself (Task-07's wrapping div and
  // inner button collapse into one element); tapping it toggles the detail beneath -- reason,
  // assumption if any, and the sources -- so the closed row costs one line of height (item 3,
  // item 7). `service-row__button` is kept as a second class only to reuse
  // `design/screens/screens.css`'s existing block/padding/border rule for that selector.
  const renderServiceRow = (service) => {
    const button = h(
      "button",
      { type: "button", class: "service-row service-row__button", "aria-expanded": "false" },
      h(
        "span",
        { class: "service-row__top" },
        h(
          "span",
          { class: "service-row__label" },
          h(
            "span",
            { class: `service-row__glyph service-row__glyph--${service.verdict}`, "aria-hidden": "true" },
            VERDICTS[service.verdict].glyph,
          ),
          h("span", { class: "service-row__name" }, SERVICE_LABEL[service.service] || service.service),
        ),
        renderBadge(service.verdict, "service-row__badge"),
      ),
    );
    const detailChildren = [h("p", { class: "service-row__reason" }, figures(service.reason))];
    if (service.assumption) {
      detailChildren.push(
        h(
          "div",
          { class: "assumption-note" },
          h("span", { class: "assumption-note__label" }, "Assumption"),
          " ",
          figures(service.assumption),
        ),
      );
    }
    if (service.sources.length) {
      detailChildren.push(
        h(
          "div",
          { class: "service-row__sources" },
          service.sources.map((source) => labeledSourceLine(source.label, source.src)),
        ),
      );
    }
    const detail = h("div", { class: "service-row__detail", hidden: "" }, detailChildren);
    button.addEventListener("click", () => {
      const expanded = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", expanded ? "false" : "true");
      detail.hidden = expanded;
    });
    return [button, detail];
  };

  // Task-34, 2026-09-16: `.services` is one card, not a `.section` (no title, no legend --
  // item 3, item 6): the four answers, closed, are what a reader came for.
  const renderServices = (community) => {
    const card = h(
      "div",
      { class: "services" },
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
      for (const node of renderServiceRow(service)) {
        card.appendChild(node);
      }
    }
    return card;
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

  // Task-34, 2026-09-16: a stub (item 5). Task-35 owns what a tap here actually does; this
  // only records the intent in the hash so the route survives a reload.
  const renderReportButton = (community) => {
    const button = h("button", { type: "button", class: "report-button" }, "Report here");
    button.addEventListener("click", () => {
      location.hash = `#/community/${community.id}?report`;
    });
    return button;
  };

  // Task-34, 2026-09-16: the three statement buttons and the freshness line, unchanged in
  // behaviour and selectors, folded behind "Share" (item 5).
  const renderShareFold = (community) =>
    h(
      "details",
      { class: "share-fold section" },
      h("summary", {}, "Share"),
      renderStatementButtons(community),
      renderFreshness(community),
    );

  // Task-34, 2026-09-16: the two-action row under the sources fold (item 5, item 7).
  // Task-35: `?report` in the hash opens the form under the row, so the route survives a reload.
  const renderActionsRow = (community) => {
    const row = h(
      "div",
      { class: "actions section" },
      renderReportButton(community),
      renderShareFold(community),
    );
    const query = new URLSearchParams(location.hash.split("?")[1] || "");
    if (query.has("report")) {
      row.appendChild(window.CrosscheckReport.renderForm(community));
    }
    return row;
  };

  // Task-35: the pack half of the Copy evidence block -- this is the only file that reads the
  // pack's service words, so report.js takes these lines already assembled and appends the
  // stored reports and the closing sentence (Task-35 contract item 6).
  const evidenceHeader = (community) => {
    const cite = (srcId) => {
      const entry = pack.sources[srcId];
      return `(${entry.source}, ${entry.date})`;
    };
    return [
      `${community.name} (BushTel id ${community.id})`,
      ...community.services.map((service) => {
        const label = SERVICE_LABEL[service.service] || service.service;
        const source = service.sources.length ? ` ${cite(service.sources[0].src)}` : "";
        return `${label}: ${VERDICTS[service.verdict].word} — ${plain(service.reason)}${source}`;
      }),
      ...community.publishers.map((publisher) => {
        const says = SAYS_LABEL[publisher.says_covered] || publisher.says_covered;
        return `${publisher.publisher}: ${says} — ${plain(publisher.detail)} ${cite(publisher.src)}`;
      }),
    ];
  };

  // Task-34, 2026-09-16: folded behind "Who to ask" (the old title "Who does what"), closed by
  // default (item 6).
  const renderActions = (community) =>
    h(
      "details",
      { class: "actions-fold section" },
      h("summary", {}, "Who to ask"),
      h(
        "ul",
        { class: "actions__list" },
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
    // Task-34, 2026-09-16: no intro line, no verdict legend (item 3); the four rows, closed,
    // are the whole answer, and everything past them folds behind a summary (item 6, item 7).
    main.appendChild(renderHeader(community));
    main.appendChild(renderServices(community));
    main.appendChild(renderSourcesFold(community));
    main.appendChild(renderActionsRow(community));
    // Task-35: the community's own reports -- the count line, the paste-in fold and Copy
    // evidence -- sit under the sources fold, and below the row whose Report here button
    // writes one: above that row they would push it past Task-34's 780 px fold budget.
    main.appendChild(window.CrosscheckReport.renderReports(community, evidenceHeader(community)));
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

  // Task-33: generalised from the telehealth-only lookup so the map's service selector can
  // recolour points, clusters and the legend by any of the pack's four services.
  const serviceVerdict = (community, serviceId) =>
    community.services.find((service) => service.service === serviceId).verdict;

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

  // Task-33: the default service, both for the hash (omitted when selected) and for renderMap's
  // fallback when the query carries none.
  const DEFAULT_SERVICE = "telehealth_video";

  // renderMap rebuilds the whole panel, including details.map-layers, on every hash change (a
  // filter, a selection, a layer toggle or a service change all go through the hash). Whether
  // that fold is open is not part of the hash contract, so it would silently re-close after
  // every chip click without this: the one piece of render state renderMap reads back in.
  let layersFoldOpen = false;

  // ``layersRaw`` is the hash's own ``layers`` value (or null when absent): threaded through
  // unchanged so selecting a point or switching a filter never clobbers a carrier toggle state.
  // ``serviceId`` is threaded the same way (Task-33) so it too survives a filter or selection
  // change; the default is omitted so a plain link still reproduces it.
  const mapHash = (filterId, selectedId, layersRaw, serviceId) => {
    let hash = `#/map?filter=${filterId}`;
    if (selectedId !== null && selectedId !== undefined) {
      hash += `&selected=${selectedId}`;
    }
    if (layersRaw !== null && layersRaw !== undefined) {
      hash += `&layers=${layersRaw}`;
    }
    if (serviceId && serviceId !== DEFAULT_SERVICE) {
      hash += `&service=${serviceId}`;
    }
    return hash;
  };

  // Task-33: one shape, four fill states (Tarik, 2026-09-16: "üçgen kare falan sevmedim"),
  // departed from the triangle/square/dash set of design/screens/assets/build.mjs and recorded
  // in design/screens/README.md. Radius stays that build's own figure (5, hit r = 16, ring r =
  // 9); fill and stroke colours are the verdict text tokens through app.css, which overrides
  // screens.css's now-stale .map__pt--* rules rather than editing them (layer rule 5).
  const renderPoint = (community, isSelected, filterId, layersRaw, serviceId) => {
    const { x, y } = community;
    const size = 5;
    const verdict = serviceVerdict(community, serviceId);
    const shapes = [
      s("circle", { class: `map__pt map__pt--${verdict}`, cx: f1(x), cy: f1(y), r: size }),
    ];
    if (verdict === "degraded") {
      // The left half-disc: an arc from the top point to the bottom point, sweep 0, closed back
      // to the start -- geometry derived from ``size``, not a token (layer rule 5's "SVG
      // geometry inside the pack is data, not CSS" applies the same way to on-the-fly shapes).
      shapes.push(
        s("path", {
          class: "map__pt-half",
          d: `M${f1(x)},${f1(y - size)} A${size},${size} 0 0 0 ${f1(x)},${f1(y + size)} Z`,
        }),
      );
    } else if (verdict === "nodata") {
      shapes[0].setAttribute("stroke-dasharray", `${f1(size)} ${f1(size / 2)}`);
    }
    // Wrapped in one group so the counter-scale transform (app.css) applies to the circle and
    // the degraded half-path together, anchored at the circle's own bounding box -- the half
    // path's own bbox is off-centre, but the union with the full circle it sits inside is not.
    const shape = s("g", { class: "map__pt-shape" }, ...shapes);
    const group = s(
      "g",
      {
        class: `map__pt-group map__community${isSelected ? " map__community--selected" : ""}`,
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
      location.hash = mapHash(filterId, community.id, layersRaw, serviceId);
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

  const renderFilterTabs = (active, selectedId, layersRaw, serviceId) => {
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
          serviceId,
        );
      });
      bar.appendChild(tab);
    }
    return bar;
  };

  // Task-33: one option per pack service, in the pack's own order (never a hardcoded list --
  // Part 2 layer rule 4, the app renders what the pack gives it). Above the filter tabs;
  // changing it recolours the points and clusters and recounts the legend, but leaves the
  // active filter and the selected community alone.
  const SERVICE_ORDER = pack.communities[0].services.map((service) => service.service);

  const renderServiceSelector = (serviceId, filterId, selectedId, layersRaw) => {
    const select = h(
      "select",
      { class: "map-service", "aria-label": "Service shown on the map" },
      SERVICE_ORDER.map((id) => h("option", { value: id }, SERVICE_LABEL[id] || id)),
    );
    select.value = serviceId;
    select.addEventListener("change", () => {
      location.hash = mapHash(filterId, selectedId, layersRaw, select.value);
    });
    return select;
  };

  // Task-33: a tally over the verdicts the pack already carries for the chosen service, all 96
  // communities regardless of the active filter (matching pipeline pack.legend's own scope for
  // telehealth video) -- a count, not a verdict (layer rule 4, same precedent as the cluster
  // ring's per-verdict tally above).
  const legendCounts = (serviceId) => {
    const counts = { works: 0, degraded: 0, fails: 0, nodata: 0 };
    for (const community of pack.communities) {
      counts[serviceVerdict(community, serviceId)] += 1;
    }
    return counts;
  };

  const renderLegend = (shownCount, serviceId) => {
    const all = h("span", { class: "fig fig--xs" }, String(pack.count));
    return h(
      "div",
      { class: "map-legend" },
      h(
        "div",
        { class: "map-legend__row" },
        Object.entries(legendCounts(serviceId)).map(([verdict, count]) =>
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
      h(
        "div",
        { class: "map-legend__subject" },
        `${SERVICE_LABEL[serviceId] || serviceId} · all `,
        all,
        " communities",
      ),
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

  // Task-33: worst-first list under the legend, Fails then Degraded then No data then Works,
  // then by name -- a sort over verdicts the pack already carries, not a verdict itself (Part 2
  // "Pushed down", the same allowance the zoom clusters already use).
  const MAP_LIST_ORDER = ["fails", "degraded", "nodata", "works"];

  const renderMapList = (shown, serviceId) => {
    const rows = [...shown].sort((a, b) => {
      const rank = (c) => MAP_LIST_ORDER.indexOf(serviceVerdict(c, serviceId));
      return rank(a) - rank(b) || a.name.localeCompare(b.name);
    });
    return h(
      "ol",
      { class: "actions map-list" },
      rows.map((community) => {
        const verdict = serviceVerdict(community, serviceId);
        const item = h(
          "li",
          { class: "service-row" },
          h(
            "button",
            { type: "button", class: "service-row__button map-list__row" },
            h(
              "span",
              { class: "service-row__top" },
              h(
                "span",
                { class: "service-row__label" },
                h(
                  "span",
                  { class: `service-row__glyph--${verdict}`, "aria-hidden": "true" },
                  VERDICTS[verdict].glyph,
                ),
                community.name,
              ),
              h("span", {}, VERDICTS[verdict].word),
            ),
          ),
        );
        item.querySelector("button").addEventListener("click", () => {
          location.hash = `#/community/${community.id}`;
        });
        return item;
      }),
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

  // Task-33: "Layers off by default" widens hiding from area layers only to every area or line
  // (region-border) layer; town points stay visible always (contract item 4).
  const isToggleLayer = (layer) => layer.kind === "area" || layer.kind === "line";

  const renderLayerGroup = (layer, visibleSlugs) => {
    const g = s("g", { class: `map__layer map__layer--${layer.kind}`, "data-layer": layer.id });
    if (isToggleLayer(layer) && !visibleSlugs.has(slugOf(layer))) {
      g.setAttribute("hidden", "");
    }
    if (layer.kind === "area" || layer.kind === "line") {
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

  // One chip per area (coverage) layer plus the SA3 region layer (Task-33 contract item 4); its
  // slug (the layer id with any "cov-" prefix dropped) is what the hash's "layers" query
  // carries, e.g. "&layers=telstra,optus". Every layer here starts hidden (renderMap's default
  // visibleSlugs is empty), so the "all off" state -- not "all on" as before Task-33 -- is what
  // the hash omits.
  const renderLayerChips = (toggleLayers, visibleSlugs, filterId, selectedId, layersRaw, serviceId) => {
    const bar = h("div", { class: "chips layer-chips" });
    for (const layer of toggleLayers) {
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
        const allSlugs = toggleLayers.map(slugOf);
        const nextRaw = next.size === 0
          ? null
          : allSlugs.filter((one) => next.has(one)).join(",");
        location.hash = mapHash(filterId, selectedId, nextRaw, serviceId);
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
  const attachMapView = (svg, shownCommunities, selectedId, pointGroupsById, serviceId) => {
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
          verdict: serviceVerdict(community, serviceId),
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

  const renderMap = (filterId, selectedId, layersRaw, serviceId) => {
    const filter = pack.filters.find((f) => f.id === filterId) || pack.filters[0];
    const shown = pack.communities.filter((c) => filter.ids.includes(c.id));
    const selected = pack.communities.find((c) => c.id === selectedId) || null;
    const service = SERVICE_ORDER.includes(serviceId) ? serviceId : DEFAULT_SERVICE;
    // The selected point is drawn last so its ring and label sit above its neighbours.
    const ordered = [
      ...shown.filter((c) => c !== selected),
      ...shown.filter((c) => c === selected),
    ];
    // Task-33: area (coverage) and line (region-border) layers are both toggled through the
    // same chip row and both start hidden; town points are never in this list (contract item 4).
    const toggleLayers = pack.layers.filter(isToggleLayer);
    const visibleSlugs =
      layersRaw === null || layersRaw === undefined
        ? new Set()
        : new Set(layersRaw.split(",").filter(Boolean));
    // Kept by id so attachMapView can hide and show them again as clusters form and split
    // (Task-29), without rebuilding the point markup on every zoom change.
    const pointGroups = ordered.map((c) =>
      renderPoint(c, c === selected, filter.id, layersRaw, service),
    );
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
    main.appendChild(
      renderServiceSelector(service, filter.id, selected ? selected.id : null, layersRaw),
    );
    const bar = renderFilterTabs(filter, selected ? selected.id : null, layersRaw, service);
    main.appendChild(bar);
    const layersDetails = h(
      "details",
      { class: "section map-layers", open: layersFoldOpen ? "" : null },
      h("summary", {}, "Layers"),
      renderLayerChips(
        toggleLayers,
        visibleSlugs,
        filter.id,
        selected ? selected.id : null,
        layersRaw,
        service,
      ),
    );
    layersDetails.addEventListener("toggle", () => {
      layersFoldOpen = layersDetails.open;
    });
    main.appendChild(layersDetails);
    main.appendChild(svg);
    const mapView = attachMapView(svg, shown, selected ? selected.id : null, pointGroupsById, service);
    const resetButton = h(
      "button",
      { type: "button", class: "button button--secondary map-controls__reset" },
      "Reset view",
    );
    resetButton.addEventListener("click", () => mapView.reset());
    main.appendChild(resetButton);
    main.appendChild(renderLegend(shown.length, service));
    main.appendChild(renderMapList(shown, service));
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
        query.get("service") || DEFAULT_SERVICE,
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
