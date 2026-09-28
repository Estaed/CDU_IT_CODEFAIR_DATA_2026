"use strict";

// The app renders the pack and routes; it computes no verdict (CLAUDE.md Part 2, layer rule 4).
(() => {
  const DEFAULT_HASH = "#/";
  const DEFAULT_ID = 426;
  // Task-41, 2026-09-17: Priority is the fourth tab and sits second, because the analyst's
  // sixty seconds (PRD §2) start with the ranked list (CLAUDE.md Blueprint, "Entry points").
  const SCREENS = ["#/community", "#/priority", "#/map", "#/share"];

  const SERVICE_LABEL = {
    telehealth_video: "Telehealth video",
    school_video_meeting: "School video meeting",
    mygov_text: "myGov and banking",
    voice_sms: "Voice and SMS",
  };

  const MAP_SERVICE_LABEL = {
    telehealth_video: "See a doctor by video",
    school_video_meeting: "Join a school lesson by video",
    mygov_text: "Use myGov and banking",
    voice_sms: "Call and text",
  };

  const SERVICE_QUESTION = {
    telehealth_video: "see a doctor by video",
    school_video_meeting: "join a school lesson by video",
    mygov_text: "use myGov and banking",
    voice_sms: "call and text",
  };

  const KIND_LABEL = {
    predicted: "carrier's prediction",
    listed: "government list",
    licensed: "licence register",
    portal: "community portal",
    measured: "drive test",
  };

  // Task-41, 2026-09-17: the five feature names pipeline/reliability.py emits as the two drivers
  // of a community's reliability word, in the words a person reads. A name this map does not
  // know falls through to the pipeline's own, so a new feature is never hidden -- it just reads
  // raw until a line is added here.
  const DRIVER_LABEL = {
    site_km: "distance to the claiming carrier's nearest licensed site",
    depth_km: "depth inside the claimed polygon",
    sites_10km: "licensed sites within 10 km",
    sites_20km: "licensed sites within 20 km",
    carriers_claiming: "carriers claiming coverage",
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

  if (pack.pack_version !== 3) {
    main.textContent = "This copy cannot read its data. Open the latest address once with internet.";
    return;
  }

  const tabs = [...document.querySelectorAll(".top-bar__inner > .tabs .tab")];
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
            h("span", { class: "kind-chip" }, KIND_LABEL[publisher.kind] || publisher.kind),
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
        ? `Do the sources agree? Yes, ${available} of ${available}`
        : `Do the sources agree? No: ${covered} of ${available} say covered`;
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

  const renderServiceIcon = (serviceId) => {
    const paths = {
      telehealth_video: ["M9 3h6v6h6v6h-6v6H9v-6H3V9h6z"],
      school_video_meeting: ["m3 10 9-5 9 5-9 5z", "M7 12v5c3 2 7 2 10 0v-5"],
      mygov_text: ["M3 10h18", "M5 10v8M9 10v8M15 10v8M19 10v8", "M3 18h18", "m4 8 8-5 8 5"],
      voice_sms: ["M6 4h4l2 5-3 2c2 4 4 6 8 8l2-3 5 2v4c0 1-1 2-2 2C10 24 2 16 2 6c0-1 1-2 2-2z"],
    };
    return s(
      "svg",
      {
        class: "service-icon",
        viewBox: "0 0 24 24",
        fill: "none",
        stroke: "currentColor",
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        "aria-hidden": "true",
        focusable: "false",
      },
      ...(paths[serviceId] || paths.mygov_text).map((d) => s("path", { d })),
    );
  };

  // Task-34, 2026-09-16: the row is `button.service-row` itself (Task-07's wrapping div and
  // inner button collapse into one element); tapping it toggles the detail beneath -- reason,
  // assumption if any, and the sources -- so the closed row costs one line of height (item 3,
  // item 7). `service-row__button` is kept as a second class only to reuse
  // `design/screens/screens.css`'s existing block/padding/border rule for that selector.
  const renderServiceRow = (service, path) => {
    const button = h(
      "button",
      { type: "button", class: "service-row service-row__button", "aria-expanded": "false" },
      h(
        "span",
        { class: "service-row__top" },
        h(
          "span",
          { class: "service-row__label" },
          renderServiceIcon(service.service),
          h(
            "span",
            { class: "service-row__name" },
            SERVICE_QUESTION[service.service] || SERVICE_LABEL[service.service] || service.service,
          ),
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
    detailChildren.push(
      h(
        "p",
        { class: "service-row__path" },
        "The best connection this community can get: ",
        figures(path.note),
        ` · ${path.rule} `,
        h("span", { class: "fig fig--xs" }, path.date),
      ),
    );
    const detail = h("div", { class: "service-row__detail", hidden: "" }, detailChildren);
    const card = h("div", { class: "service-card" }, button, detail);
    const setExpanded = (one, expanded) => {
      one.querySelector(".service-row").setAttribute("aria-expanded", expanded ? "true" : "false");
      one.querySelector(".service-row__detail").hidden = !expanded;
      one.classList.toggle("service-card--expanded", expanded);
    };
    // One card open at a time: opening a card closes the one already open.
    button.addEventListener("click", () => {
      const expanded = button.getAttribute("aria-expanded") === "true";
      for (const other of card.parentElement?.querySelectorAll(".service-card--expanded") || []) {
        setExpanded(other, false);
      }
      setExpanded(card, !expanded);
    });
    return card;
  };

  // Task-45, 2026-09-21: the card asks what the connection allows; its path note belongs in
  // each opened row so the summary sentence can answer the screen's first question.
  const renderServices = (community) => {
    const card = h(
      "div",
      { class: "services" },
      h("div", { class: "services__question" }, "Can people here…"),
    );
    const grid = h("div", { class: "services__grid" });
    for (const service of community.services) {
      grid.appendChild(renderServiceRow(service, community.path));
    }
    card.appendChild(grid);
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

  // Clipboard first; a selected off-screen textarea where the Clipboard API is refused.
  const copyText = async (text) => {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
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
    let copied = false;
    try {
      copied = document.execCommand("copy");
    } catch (error) {
      copied = false;
    }
    area.remove();
    return copied;
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
      const copied = await copyText(statementLong(community));
      copyButton.textContent = copied ? "Copied" : "Copy failed. Select the text and copy it manually.";
      clearTimeout(resetTimer);
      resetTimer = setTimeout(() => {
        copyButton.textContent = "Copy statement";
      }, copied ? 2000 : 4000);
    });
    return h(
      "div",
      { class: "share" },
      h("div", { class: "share-card__buttons" }, smsLink, copyButton),
    );
  };

  const renderFreshness = (community) =>
    h(
      "span",
      { class: "source-line community-header__freshness" },
      `Oldest source: ${pack.sources[community.freshness.source].source} · `,
      h("span", { class: "fig fig--xs" }, community.freshness.date),
    );

  // Task-54: the same action opens and closes the form. Query state keeps the form reload-safe.
  const renderReportButton = (community) => {
    const query = new URLSearchParams(location.hash.split("?")[1] || "");
    const isOpen = query.has("report");
    const button = h(
      "button",
      {
        type: "button",
        class: "report-button",
        "aria-expanded": isOpen ? "true" : "false",
      },
      isOpen ? "Close report" : "Report here",
    );
    button.addEventListener("click", () => {
      if (isOpen) {
        query.delete("report");
      } else {
        query.set("report", "");
      }
      const suffix = query.size ? `?${query}` : "";
      location.hash = `#/community/${community.id}${suffix}`;
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

  // Task-45, 2026-09-21: the compact two-action row comes before the sources fold so it stays
  // inside the first phone viewport. Task-35: `?report` in the hash opens its form.
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

  // Task-41, 2026-09-17: the two lines the fourth batch adds to the community screen, and the
  // pieces the Priority tab below shares with them. Every figure here is read from the pack and
  // printed: the rank, the intervention and the reliability word are all decided in
  // pipeline/prioritise.py and pipeline/reliability.py (layer rule 9).
  const PRIORITY_ALL = "all";
  const PRIORITY_GROUPS = [
    ["service", "Service gaps", "A source-based verdict says video care or calls and texts fail. Confirm locally before investment."],
    ["check", "Check the evidence", "Coverage claims or link quality need checking before choosing a fix."],
    ["monitor", "Monitor", "Current sources do not point to a specific fix."],
  ];

  const priorityHash = (word) =>
    word === PRIORITY_ALL ? "#/priority" : `#/priority?intervention=${encodeURIComponent(word)}`;

  const interventionOf = (index) => pack.priority_interventions[index];

  // `none` is the pack's word for a community no carrier polygon covers, so there is no claim
  // for the model to have been right or wrong about; it carries no drivers.
  const RELIABILITY_NONE_REASON = "no carrier claims coverage here";

  const reliabilityTail = (reliability) =>
    reliability.word === "none"
      ? RELIABILITY_NONE_REASON
      : reliability.drivers.map((name) => DRIVER_LABEL[name] || name).join(", ");

  const priorityText = (community) => {
    const one = interventionOf(community.priority.i);
    const group = PRIORITY_GROUPS.find(([id]) => id === priorityRowOf(community).g);
    return `${group[1]} · Priority #${community.priority.rank} of ${pack.count} · ${one.word} · ${one.addressee}`;
  };

  const renderPriorityLine = (community) =>
    h(
      "p",
      { class: "priority-line" },
      h(
        "a",
        {
          class: "text-link",
          href: priorityHash(interventionOf(community.priority.i).word),
        },
        priorityText(community),
      ),
    );

  // The source tap is the same one every other citation gets; the honesty note the pipeline
  // wrote on that source entry (an extrapolation from audited roads, not a measurement here)
  // rides on it as a title, the way the header already carries the population's citation.
  const renderReliabilityLine = (community) => {
    const reliability = community.claim_reliability;
    const entry = pack.sources[reliability.src];
    const source = sourceLine(reliability.src);
    if (entry.note) {
      source.setAttribute("title", entry.note);
    }
    return h(
      "details",
      { class: "reliability-line" },
      h(
        "summary",
        {},
        "How far to trust the coverage map here: ",
        h("span", { class: "reliability-line__word" }, reliability.word),
      ),
      h("p", { class: "reliability-line__body" }, reliabilityTail(reliability), " ", source),
    );
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
      // Task-41: the two fourth-batch lines, after the service lines and before the publishers.
      priorityText(community),
      `Map claim reliability: ${community.claim_reliability.word} · ` +
        `${reliabilityTail(community.claim_reliability)} ${cite(community.claim_reliability.src)}`,
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
      status.textContent = "We couldn't use your location. Search for a community instead.";
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

  // One bar for search (Task-30): a result opens its community.
  const renderSearch = (current) => {
    const results = h("ul", { class: "search-results" });
    const empty = h(
      "p",
      { class: "results__empty", hidden: "" },
      "No communities match that search.",
    );
    const input = h("input", {
      class: "search-input",
      type: "search",
      placeholder: `Search ${pack.count} communities`,
      "aria-label": "Search communities",
    });
    input.addEventListener("input", () => {
      const query = input.value.trim().toLowerCase();
      results.textContent = "";
      empty.hidden = true;
      if (!query) {
        return;
      }
      const matches = pack.communities.filter((c) => matchesQuery(c, query));
      if (!matches.length) {
        empty.hidden = false;
        return;
      }
      for (const community of matches) {
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
        results.appendChild(item);
      }
    });
    return [
      h(
        "div",
        { class: "search" },
        current ? h("div", { class: "search__tools" }, input, renderLocate(current)) : input,
      ),
      results,
      empty,
    ];
  };

  const summaryReason = (reason) => {
    const text = String(reason);
    return /[.!?]$/.test(text.trim()) ? text : `${text}.`;
  };

  const renderCommunitySummary = (community) => {
    const { covered, available } = community.agreement;
    const coverage =
      available === 0
        ? `No source makes a coverage claim about ${community.name}.`
        : covered === available
          ? `All \`${available}\` sources say ${community.name} has mobile coverage.`
          : covered === 0
            ? `None of \`${available}\` sources says ${community.name} has mobile coverage.`
            : `\`${covered}\` of \`${available}\` sources say ${community.name} has mobile coverage; they disagree.`;
    const telehealth = community.services.find((service) => service.service === "telehealth_video");
    let health;
    if (telehealth.verdict === "works") {
      health = "A video call with a doctor should work here.";
    } else if (telehealth.verdict === "degraded") {
      const assumption = telehealth.assumption ? telehealth.assumption.split(". ") : [];
      if (assumption.length >= 2) {
        const first = assumption[0];
        const a1 = `${first.charAt(0).toLowerCase()}${first.slice(1)}`;
        health = `A video call with a doctor is not proven to work here. It ${a1}. ${assumption[1]}.`;
      } else {
        health = `A video call with a doctor is not proven to work here: ${summaryReason(telehealth.reason)}`;
      }
    } else if (telehealth.verdict === "fails") {
      health = `A video call with a doctor will not work here: ${summaryReason(telehealth.reason)}`;
    } else {
      health = "No health centre is recorded here, so a doctor's video call is not assessed.";
    }
    return h("p", { class: "community-summary" }, figures(coverage), " ", figures(health));
  };

  const renderCommunity = (id) => {
    const community =
      pack.communities.find((c) => c.id === id) ||
      pack.communities.find((c) => c.id === DEFAULT_ID);
    main.textContent = "";
    for (const node of renderSearch(community)) {
      main.appendChild(node);
    }
    // Task-34, 2026-09-16: no intro line, no verdict legend (item 3); the four rows, closed,
    // are the whole answer, and everything past them folds behind a summary (item 6, item 7).
    main.appendChild(renderHeader(community));
    main.appendChild(renderCommunitySummary(community));
    main.appendChild(renderServices(community));
    main.appendChild(renderActionsRow(community));
    // Task-41, 2026-09-17: where it ranks and whether the coverage claim holds sit below the
    // actions row -- above that row they would push it past Task-34's 780 px fold budget.
    // 2026-09-28 (Tarik Base, design/deviations.md): the folds and those two lines are one
    // grouped card of rows instead of five ruled strips, and the community's own reports
    // (Task-35) follow as a card of their own, still below the row that writes them.
    main.appendChild(
      h(
        "div",
        { class: "details-group" },
        renderSourcesFold(community),
        renderPriorityLine(community),
        renderReliabilityLine(community),
        renderPresent(community),
        renderActions(community),
      ),
    );
    main.appendChild(window.CrosscheckReport.renderReports(community, evidenceHeader(community)));
  };

  // Exposed for the browser test, which runs the builders over every community in the pack.
  window.__statement = { short: statementShort, long: statementLong };

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

  const serviceVerdict = (community, serviceId) =>
    community.services.find((service) => service.service === serviceId).verdict;

  const MAP_LENSES = ["fix", "service", "sources"];
  const DEFAULT_LENS = "fix";
  const DEFAULT_SERVICE = "telehealth_video";
  const DEFAULT_FILTER = "all";
  const REGION_SLUGS = [...new Set(pack.communities.map((community) => community.region))].map(
    (name) => ({ name, slug: name.toLowerCase().replaceAll(" ", "-") }),
  );

  const sourceState = (community) => {
    const measured = community.publishers.some(
      (publisher) => publisher.kind === "measured" && publisher.says_covered === "not-covered",
    );
    if (measured) {
      return "measured";
    }
    return community.agreement.note === "Sources disagree" ? "disagree" : "agree";
  };

  const priorityRowOf = (community) =>
    pack.priority.find((row) => row.id === community.id) || community.priority;

  const mapTier = (community) => {
    const rank = priorityRowOf(community).rank;
    return rank <= 10 ? 1 : rank <= 30 ? 2 : 3;
  };

  const mapRadius = (community, state) => {
    if (state.lens === "fix") {
      // The numbered disc is sized for its number; every other place is one dot size, its tier
      // told by ink or grey: a bigger dot read as "more of something" (Datawrapper, 2026-09-28).
      return [11, 4, 4][mapTier(community) - 1];
    }
    if (state.lens === "service") {
      return 6;
    }
    const source = sourceState(community);
    return source === "measured" ? 8 : source === "disagree" ? 6 : 3.5;
  };

  const mapHash = (state) => {
    const params = [];
    if (state.lens && state.lens !== DEFAULT_LENS) {
      params.push(`lens=${state.lens}`);
    }
    if (state.region) {
      params.push(`region=${state.region}`);
    }
    if (state.filter && state.filter !== DEFAULT_FILTER) {
      params.push(`filter=${state.filter}`);
    }
    if (state.selected !== null && state.selected !== undefined) {
      params.push(`selected=${state.selected}`);
    }
    if (state.layers) {
      params.push(`layers=${state.layers}`);
    }
    if (state.service && state.service !== DEFAULT_SERVICE) {
      params.push(`service=${state.service}`);
    }
    return params.length ? `#/map?${params.join("&")}` : "#/map";
  };

  const DECLUTTER_DISTANCE = 6;
  const DECLUTTER_LIMIT = 14;
  const DECLUTTER_FULL_ZOOM = 8;

  // A deterministic relaxation separates points by their display radii while keeping every
  // point within the map's movement budget. The final offset is linearly withdrawn as the view
  // approaches zoom 8, so the layout has no hidden state and identical calls return identical arrays.
  const declutter = (points, zoom) => {
    if (zoom >= DECLUTTER_FULL_ZOOM) {
      return points.map((point) => ({ ...point }));
    }
    const placed = points.map((point) => ({ ...point }));
    for (let pass = 0; pass < 1200; pass += 1) {
      let separated = true;
      for (let i = 0; i < placed.length; i += 1) {
        for (let j = i + 1; j < placed.length; j += 1) {
          let dx = placed[j].x - placed[i].x;
          let dy = placed[j].y - placed[i].y;
          let distance = Math.hypot(dx, dy);
          const radius = (point) => Number.isFinite(Number(point.r)) ? Number(point.r) : 3;
          const required = Math.max(DECLUTTER_DISTANCE, radius(placed[i]) + radius(placed[j]) + 1);
          if (distance >= required) {
            continue;
          }
          separated = false;
          if (distance < 0.0001) {
            const turn = ((Number(placed[i].id) * 37 + Number(placed[j].id) * 17) % 360) * Math.PI / 180;
            dx = Math.cos(turn);
            dy = Math.sin(turn);
            distance = 1;
          }
          const push = (required - distance) / 2 + 0.002;
          placed[i].x -= (dx / distance) * push;
          placed[i].y -= (dy / distance) * push;
          placed[j].x += (dx / distance) * push;
          placed[j].y += (dy / distance) * push;
        }
      }
      for (let i = 0; i < placed.length; i += 1) {
        const dx = placed[i].x - points[i].x;
        const dy = placed[i].y - points[i].y;
        const distance = Math.hypot(dx, dy);
        if (distance > DECLUTTER_LIMIT) {
          placed[i].x = points[i].x + (dx / distance) * DECLUTTER_LIMIT;
          placed[i].y = points[i].y + (dy / distance) * DECLUTTER_LIMIT;
        }
      }
      if (separated) {
        break;
      }
    }
    const factor = Math.max(0, Math.min(1, (DECLUTTER_FULL_ZOOM - Math.max(1, zoom)) / 7));
    return placed.map((point, index) => ({
      ...points[index],
      x: points[index].x + (point.x - points[index].x) * factor,
      y: points[index].y + (point.y - points[index].y) * factor,
    }));
  };

  window.__map = { declutter };

  const renderMapLens = (state) =>
    h(
      "nav",
      { class: "map-lens", "aria-label": "Map lens" },
      [
        ["fix", "Fix first"],
        ["service", "Services"],
        ["sources", "Sources"],
      ].map(([id, label]) =>
        h(
          "a",
          {
            class: "map-lens__option",
            "aria-current": state.lens === id ? "page" : null,
            href: mapHash({ ...state, lens: id }),
          },
          label,
        ),
      ),
    );

  const renderFilterTabs = (active, state) => {
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
        location.hash = mapHash({ ...state, filter: filter.id });
      });
      bar.appendChild(tab);
    }
    return bar;
  };

  const SERVICE_ORDER = pack.communities[0].services.map((service) => service.service);

  const renderServiceSelector = (state) => {
    const select = h(
      "select",
      { class: "map-service", "aria-label": "Service shown on the map" },
      SERVICE_ORDER.map((id) => h("option", { value: id }, MAP_SERVICE_LABEL[id] || id)),
    );
    select.value = state.service;
    select.addEventListener("change", () => {
      location.hash = mapHash({ ...state, service: select.value });
    });
    return select;
  };

  const legendCounts = (serviceId) => {
    const counts = { works: 0, degraded: 0, fails: 0, nodata: 0 };
    for (const community of pack.communities) {
      counts[serviceVerdict(community, serviceId)] += 1;
    }
    return counts;
  };

  const renderLegend = (state) => {
    let items;
    if (state.lens === "fix") {
      const counts = [0, 0, 0];
      for (const community of pack.communities) {
        const rank = priorityRowOf(community).rank;
        counts[rank <= 10 ? 0 : rank <= 30 ? 1 : 2] += 1;
      }
      items = [
        ["map-legend__glyph--fix-one", "●", "Top 10", counts[0]],
        ["map-legend__glyph--fix-two", "●", "11 to 30", counts[1]],
        ["map-legend__glyph--fix-three", "●", "The rest", counts[2]],
      ];
    } else if (state.lens === "service") {
      items = Object.entries(legendCounts(state.service)).map(([verdict, count]) => [
        `map-legend__glyph--${verdict}`,
        VERDICTS[verdict].glyph,
        VERDICTS[verdict].word,
        count,
      ]);
    } else {
      const counts = { measured: 0, disagree: 0, agree: 0 };
      for (const community of pack.communities) {
        counts[sourceState(community)] += 1;
      }
      items = [
        ["map-legend__glyph--source-measured", "○", "Drive test found no signal inside claimed coverage", counts.measured],
        ["map-legend__glyph--source-disagree", "●", "Sources disagree on mobile coverage", counts.disagree],
        ["map-legend__glyph--source-agree", "●", "Sources agree on mobile coverage", counts.agree],
      ];
    }
    return h(
      "div",
      { class: "map-legend" },
      items.map(([className, glyph, label, count]) =>
        h(
          "span",
          { class: "map-legend__item" },
          h("span", { class: className, "aria-hidden": "true" }, glyph),
          `${label} `,
          h("span", { class: "fig map-legend__count" }, "(" + count + ")"),
        ),
      ),
      h(
        "span",
        { class: "map-legend__heat" },
        h("span", { class: "map-legend__heat-swatch", "aria-hidden": "true" }),
        "Shaded: where carriers claim 4G (darker: more carriers)",
      ),
    );
  };

  // 2026-09-28 (Tarik): the carriers' own coverage claims as one shaded surface under every
  // lens, so the map shows where the claims are and the communities they miss. The three
  // carrier layers the pack already carries are drawn once more in one tint, overlapping; the
  // per-carrier toggles under "Highlight and layers" stay as they were.
  const renderHeat = () =>
    s(
      "g",
      { class: "map__heat", "aria-hidden": "true" },
      ...pack.layers
        .filter((layer) => layer.kind === "area")
        .flatMap((layer) => layer.paths.map((d) => s("path", { d }))),
    );

  const MAP_LIST_ORDER = ["fails", "degraded", "nodata", "works"];

  const isDimmed = (community, state, filter) =>
    !filter.ids.includes(community.id) ||
    (state.region && community.region.toLowerCase().replaceAll(" ", "-") !== state.region);

  const renderMapList = (state, filter) => {
    const rows = [...pack.communities].sort((a, b) => {
      const dim = Number(isDimmed(a, state, filter)) - Number(isDimmed(b, state, filter));
      if (dim) {
        return dim;
      }
      if (state.lens === "fix") {
        return priorityRowOf(a).rank - priorityRowOf(b).rank;
      }
      if (state.lens === "service") {
        return (
          MAP_LIST_ORDER.indexOf(serviceVerdict(a, state.service)) -
            MAP_LIST_ORDER.indexOf(serviceVerdict(b, state.service)) ||
          a.name.localeCompare(b.name)
        );
      }
      const order = { measured: 0, disagree: 1, agree: 2 };
      return order[sourceState(a)] - order[sourceState(b)] || a.name.localeCompare(b.name);
    });
    return h(
      "ol",
      { class: "map-list" },
      rows.map((community) => {
        let tail;
        if (state.lens === "fix") {
          const priority = priorityRowOf(community);
          tail = `#${priority.rank} · ${interventionOf(priority.i).word}`;
        } else if (state.lens === "service") {
          tail = VERDICTS[serviceVerdict(community, state.service)].word;
        } else {
          tail = `${community.agreement.covered} of ${community.agreement.available} say covered`;
        }
        return h(
          "li",
          { class: `map-list__item${isDimmed(community, state, filter) ? " map-list__item--dim" : ""}` },
          h(
            "a",
            { class: "map-list__row", href: mapHash({ ...state, selected: community.id }) },
            h("span", { class: "map-list__name" }, community.name),
            h("span", { class: "map-list__value" }, tail),
          ),
        );
      }),
    );
  };

  const renderMapListHeading = (state, filter) => {
    const highlighted = pack.communities.filter(
      (community) => !isDimmed(community, state, filter),
    ).length;
    return h(
      "header",
      { class: "map-list-heading" },
      h("h2", { class: "map-list-heading__title" }, "Communities"),
      h(
        "p",
        { class: "map-list-heading__count" },
        `${highlighted} highlighted of ${pack.count}`,
      ),
      h(
        "p",
        { class: "map-list-heading__note" },
        "Highlighted communities are listed first; the rest stay faded.",
      ),
    );
  };

  const renderMapCard = (community) => {
    const card = h("section", { class: "map-card" });
    if (!community) {
      card.appendChild(h("p", { class: "map-card__hint" }, "Tap a community."));
      return card;
    }
    const priority = priorityRowOf(community);
    card.appendChild(h("h2", { class: "map-card__name" }, community.name));
    card.appendChild(renderCommunitySummary(community));
    card.appendChild(
      h(
        "p",
        { class: "map-card__fix" },
        `Fix first #${priority.rank} of ${pack.priority.length} · ${interventionOf(priority.i).word}`,
      ),
    );
    card.appendChild(
      h(
        "div",
        { class: "map-card__badges" },
        community.services.map((service) =>
          h(
            "span",
            { class: "map-card__badge" },
            h("span", { class: "map-card__service" }, SMS_LABEL[service.service] || service.service),
            renderBadge(service.verdict),
          ),
        ),
      ),
    );
    card.appendChild(
      h("a", { class: "button button--primary", href: `#/community/${community.id}` }, `Open ${community.name}`),
    );
    return card;
  };

  // Map layers (Task-21, Part 2 "Map layer" seam): the pack's own order already draws area
  // (coverage) layers first, then line (region) layers, then point (town) layers -- exactly
  // the Execution Guide's draw order -- so the app never hand-orders layer ids.
  const slugOf = (layer) => (layer.id.startsWith("cov-") ? layer.id.slice(4) : layer.id);

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
              {
                class: "map__town-label",
                "data-for": `town-${point.label.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`,
                x: f1(point.x + 4),
                y: f1(point.y + 1),
              },
              point.label,
            ),
          ),
        );
      }
    }
    return g;
  };

  const renderLayerChips = (toggleLayers, visibleSlugs, state) => {
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
        location.hash = mapHash({ ...state, layers: nextRaw });
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

  const regionView = (regionSlug) => {
    if (!regionSlug) {
      return { ...BASE_VIEW };
    }
    const points = pack.communities.filter(
      (community) => community.region.toLowerCase().replaceAll(" ", "-") === regionSlug,
    );
    const minX = Math.min(...points.map((point) => point.x)) - 12;
    const maxX = Math.max(...points.map((point) => point.x)) + 12;
    const minY = Math.min(...points.map((point) => point.y)) - 12;
    const maxY = Math.max(...points.map((point) => point.y)) + 12;
    return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
  };

  const attachMapView = (svg, communities, state, pointGroupsById, labelsGroup, resetButton) => {
    const view = { ...BASE_VIEW };
    let zoom = ZOOM_MIN;
    const truePoints = communities.map((community) => ({
      id: community.id,
      x: community.x,
      y: community.y,
      r: mapRadius(community, state),
    }));
    const restingPoints = declutter(truePoints, 1);

    // Moving the points is cheap and follows every zoom step; placing the labels measures text
    // and is deferred until a pan or pinch settles, so a gesture never waits on it.
    const positions = new Map();
    let movedAtZoom = null;
    const movePoints = () => {
      movedAtZoom = zoom;
      const factor = Math.max(0, Math.min(1, (DECLUTTER_FULL_ZOOM - zoom) / 7));
      for (let i = 0; i < communities.length; i += 1) {
        const community = communities[i];
        const x = community.x + (restingPoints[i].x - community.x) * factor;
        const y = community.y + (restingPoints[i].y - community.y) * factor;
        positions.set(community.id, { x, y });
        pointGroupsById.get(community.id).setAttribute(
          "transform",
          `translate(${f1(x - community.x)} ${f1(y - community.y)})`,
        );
      }
    };

    const placeLabels = () => {
      labelsGroup.textContent = "";
      const filter = pack.filters.find((one) => one.id === state.filter);
      const labels = [];
      const labeledCommunities = communities
        .filter((community) => {
          const rank = priorityRowOf(community).rank;
          return community.id === state.selected || (state.lens === "fix" && rank <= 10) || zoom >= LABEL_ZOOM;
        })
        .sort(
          (a, b) =>
            Number(
              view.x <= positions.get(b.id).x &&
                positions.get(b.id).x <= view.x + view.w &&
                view.y <= positions.get(b.id).y &&
                positions.get(b.id).y <= view.y + view.h,
            ) -
              Number(
                view.x <= positions.get(a.id).x &&
                  positions.get(a.id).x <= view.x + view.w &&
                  view.y <= positions.get(a.id).y &&
                  positions.get(a.id).y <= view.y + view.h,
              ) ||
            Number(b.id === state.selected) - Number(a.id === state.selected) ||
            priorityRowOf(a).rank - priorityRowOf(b).rank,
        );
      for (const community of labeledCommunities) {
        const rank = priorityRowOf(community).rank;
        const point = positions.get(community.id);
        const label = s(
          "text",
          {
            class: `map__label${isDimmed(community, state, filter) ? " map__label--dim" : ""}`,
            "data-id": String(community.id),
            "data-for": String(community.id),
            x: f1(point.x),
            y: f1(point.y),
            "text-anchor": "start",
          },
          community.name,
        );
        labelsGroup.appendChild(label);
        labels.push({
          element: label,
          point,
          radius: mapRadius(community, state),
          selected: community.id === state.selected,
          town: false,
          tierOne: state.lens === "fix" && mapTier(community) === 1,
          order: community.id === state.selected ? 0 : state.lens === "fix" && rank <= 10 ? 2 : 3,
        });
      }

      const townLabels = [...svg.querySelectorAll(".map__town-label")].map((element) => {
        const dot = element.parentElement.querySelector(".map__town-dot");
        return {
          element,
          point: { x: Number(dot.getAttribute("cx")), y: Number(dot.getAttribute("cy")) },
          radius: Number(dot.getAttribute("r")),
          selected: false,
          town: true,
          tierOne: false,
          order: 1,
        };
      });
      const overlaps = (a, b) =>
        a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height;
      const screenBox = (element) => {
        const box = element.getBoundingClientRect();
        return { x: box.left, y: box.top, width: box.width, height: box.height };
      };
      const labelCentre = (box) => ({
        x: box.x + box.width / 2,
        y: box.y + box.height / 2,
      });
      const ownMarker = (entry) =>
        entry.town
          ? entry.element.parentElement.querySelector(".map__town-dot")
          : pointGroupsById.get(Number(entry.element.getAttribute("data-for")))?.querySelector(".map__hit");
      const allLabels = [...labels, ...townLabels].sort(
        (a, b) => a.order - b.order || a.point.y - b.point.y || String(a.element.textContent).localeCompare(String(b.element.textContent)),
      );

      // Read everything once (one layout), then place by arithmetic and write once: measuring a
      // label after every candidate move forced a layout per candidate and froze the phone.
      for (const entry of townLabels) {
        entry.element.removeAttribute("hidden");
      }
      const svgBox = svg.getBoundingClientRect();
      for (const entry of allLabels) {
        const element = entry.element;
        const box = element.getBBox();
        const x = Number(element.getAttribute("x"));
        const anchorLeft = element.getAttribute("text-anchor") === "end" ? x - box.width : x;
        entry.size = {
          width: box.width,
          height: box.height,
          dx: box.x - anchorLeft,
          dy: box.y - Number(element.getAttribute("y")),
        };
        const marker = ownMarker(entry);
        entry.marker = marker ? screenBox(marker) : null;
      }
      const tierOneBoxes = communities
        .filter((community) => state.lens === "fix" && mapTier(community) === 1)
        .map((community) => ({ id: String(community.id), element: pointGroupsById.get(community.id)?.querySelector(".map__hit") }))
        .filter((marker) => marker.element)
        .map((marker) => ({ id: marker.id, box: screenBox(marker.element) }));
      // Every community's drawn mark, read in the same pass: a name should not sit on a dot.
      const pointBoxes = communities.map((community) => ({
        id: String(community.id),
        box: screenBox(pointGroupsById.get(community.id).querySelector(".map__pt-shape")),
      }));

      const scale = Math.min(svgBox.width / view.w, svgBox.height / view.h);
      const originX = svgBox.left + (svgBox.width - view.w * scale) / 2;
      const originY = svgBox.top + (svgBox.height - view.h * scale) / 2;
      // The label's box in view units, shrunk by its CSS scale(1 / zoom) about its own centre.
      const scaledBox = (entry, x, y, anchor) => {
        const { width, height, dx, dy } = entry.size;
        const centreX = (anchor === "end" ? x - width : x) + dx + width / 2;
        const centreY = y + dy + height / 2;
        return {
          x: centreX - width / zoom / 2,
          y: centreY - height / zoom / 2,
          width: width / zoom,
          height: height / zoom,
        };
      };
      const toScreen = (box) => ({
        x: originX + (box.x - view.x) * scale,
        y: originY + (box.y - view.y) * scale,
        width: box.width * scale,
        height: box.height * scale,
      });
      // Half a pixel of margin absorbs the rounding between this arithmetic and the drawn text.
      const padded = (box) => ({ x: box.x - 0.5, y: box.y - 0.5, width: box.width + 1, height: box.height + 1 });
      const keepsTierOneClear = (entry, box) => {
        if (entry.selected) {
          return true;
        }
        return tierOneBoxes.every((marker) => marker.id === entry.element.getAttribute("data-for") || !overlaps(box, marker.box));
      };
      const keepsOwnTierOneNearest = (entry, box) => {
        if (entry.selected || !entry.tierOne || !tierOneBoxes.length) {
          return true;
        }
        if (!entry.marker) {
          return false;
        }
        const centre = labelCentre(box);
        const own = labelCentre(entry.marker);
        const ownDistance = Math.hypot(centre.x - own.x, centre.y - own.y);
        return tierOneBoxes.every((marker) => {
          const other = labelCentre(marker.box);
          return ownDistance <= Math.hypot(centre.x - other.x, centre.y - other.y);
        });
      };
      const occupied = [];
      const placements = [];
      for (const entry of allLabels) {
        const ownId = entry.town ? null : entry.element.getAttribute("data-for");
        const gap = 8 / zoom;
        const radius = entry.radius / zoom;
        const side = entry.point.x < view.x + view.w * 0.4 ? 1 : -1;
        const sides = [side, -side];
        const verticalOffsets = [0, -gap, gap, -gap / 2, gap / 2];
        const candidates = [];
        for (const sideSign of sides) {
          for (const offset of verticalOffsets) {
            // The label shrinks about its own centre, so x and y are chosen for the shrunk box:
            // its near edge sits beside the marker and its middle on the marker's line, at any zoom.
            const { width, height, dx, dy } = entry.size;
            const shrink = width / 2 - width / zoom / 2;
            candidates.push({
              x: entry.point.x + sideSign * (radius + gap / 2 - shrink) - dx,
              y: entry.point.y + offset - dy - height / 2,
              anchor: sideSign > 0 ? "start" : "end",
            });
          }
        }
        let accepted = null;
        for (const candidate of candidates) {
          const box = scaledBox(entry, candidate.x, candidate.y, candidate.anchor);
          const left = view.x + 0.5;
          const top = view.y + 0.5;
          const right = view.x + view.w - 0.5;
          const bottom = view.y + view.h - 0.5;
          const shiftX = box.x < left ? left - box.x : box.x + box.width > right ? right - box.x - box.width : 0;
          const shiftY = box.y < top ? top - box.y : box.y + box.height > bottom ? bottom - box.y - box.height : 0;
          if (Math.hypot(shiftX, shiftY) > gap) {
            continue;
          }
          let x = Number(f1(candidate.x + shiftX));
          let y = Number(f1(candidate.y + shiftY));
          let screen = toScreen(scaledBox(entry, x, y, candidate.anchor));
          // A label pushed far from its marker by the edge shift is centred back on the marker.
          if (entry.marker) {
            const labelMid = labelCentre(screen);
            const markerMid = labelCentre(entry.marker);
            if (Math.hypot(labelMid.x - markerMid.x, labelMid.y - markerMid.y) > 40 + screen.width / 2) {
              x = Number(f1(x + (markerMid.x - labelMid.x) / scale));
              y = Number(f1(y + (markerMid.y - labelMid.y) / scale));
              screen = toScreen(scaledBox(entry, x, y, candidate.anchor));
            }
          }
          screen = padded(screen);
          if (
            !occupied.some((other) => overlaps(screen, other)) &&
            keepsTierOneClear(entry, screen) &&
            keepsOwnTierOneNearest(entry, screen)
          ) {
            // Of the positions that clear every label and top-ten disc, the first that covers the
            // fewest other communities' dots wins (2026-09-28: names sat on small dots).
            const covered = pointBoxes.filter((one) => one.id !== ownId && overlaps(screen, one.box)).length;
            if (!accepted || covered < accepted.covered) {
              accepted = { x, y, anchor: candidate.anchor, screen, covered };
            }
            if (covered === 0) {
              break;
            }
          }
        }
        if (accepted) {
          occupied.push(accepted.screen);
        }
        placements.push([entry.element, accepted]);
      }
      for (const [label, accepted] of placements) {
        if (accepted) {
          label.setAttribute("x", f1(accepted.x));
          label.setAttribute("y", f1(accepted.y));
          label.setAttribute("text-anchor", accepted.anchor);
          label.removeAttribute("hidden");
        } else {
          label.setAttribute("hidden", "");
        }
      }
      const selectedLabel = labels.find((entry) => entry.selected)?.element;
      [...labelsGroup.children]
        .sort(
          (a, b) =>
            Number(!b.hasAttribute("hidden")) - Number(!a.hasAttribute("hidden")) ||
            Number(b === selectedLabel) - Number(a === selectedLabel),
        )
        .forEach((label) => labelsGroup.appendChild(label));
    };

    const updateLayout = () => {
      movePoints();
      placeLabels();
    };

    const LABEL_SETTLE_MS = 150;
    let labelTimer = null;
    const scheduleLayout = () => {
      if (movedAtZoom !== zoom) {
        movePoints();
      }
      clearTimeout(labelTimer);
      labelTimer = setTimeout(() => {
        labelTimer = null;
        if (svg.isConnected) {
          placeLabels();
        }
      }, LABEL_SETTLE_MS);
    };
    window.addEventListener("resize", scheduleLayout);

    const apply = (layout = false) => {
      svg.setAttribute(
        "viewBox",
        `${vnum(view.x)} ${vnum(view.y)} ${vnum(view.w)} ${vnum(view.h)}`,
      );
      const level = clamp(Math.round(zoom), ZOOM_MIN, ZOOM_MAX);
      svg.setAttribute("data-zoom", String(level));
      svg.style.setProperty("--map-zoom", String(zoom));
      resetButton.hidden = zoom === ZOOM_MIN && !state.region;
      if (layout) {
        scheduleLayout();
      }
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
      apply(true);
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
        apply(true);
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
      if (state.region) {
        location.hash = mapHash({ ...state, region: null });
        return;
      }
      view.x = BASE_VIEW.x;
      view.y = BASE_VIEW.y;
      view.w = BASE_VIEW.w;
      view.h = BASE_VIEW.h;
      zoom = ZOOM_MIN;
      apply();
      updateLayout();
    };

    apply();
    updateLayout();
    if (state.region) {
      const target = regionView(state.region);
      const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
      if (reduced) {
        Object.assign(view, target);
        zoom = clamp(Math.min(BASE_VIEW.w / view.w, BASE_VIEW.h / view.h), ZOOM_MIN, ZOOM_MAX);
        apply();
        updateLayout();
      } else {
        const started = performance.now();
        let settled = false;
        const settle = () => {
          if (settled) {
            return;
          }
          settled = true;
          Object.assign(view, target);
          zoom = clamp(Math.min(BASE_VIEW.w / view.w, BASE_VIEW.h / view.h), ZOOM_MIN, ZOOM_MAX);
          apply();
          updateLayout();
        };
        const animate = (now) => {
          if (settled) {
            return;
          }
          const amount = Math.min(1, (now - started) / 260);
          const eased = amount * (2 - amount);
          for (const key of ["x", "y", "w", "h"]) {
            view[key] = BASE_VIEW[key] + (target[key] - BASE_VIEW[key]) * eased;
          }
          zoom = clamp(Math.min(BASE_VIEW.w / view.w, BASE_VIEW.h / view.h), ZOOM_MIN, ZOOM_MAX);
          apply();
          if (amount < 1) {
            requestAnimationFrame(animate);
          } else {
            settle();
          }
        };
        requestAnimationFrame(animate);
        setTimeout(settle, 100);
      }
    }
    const zoomFromCentre = (factor) =>
      zoomAt(factor, view.x + view.w / 2, view.y + view.h / 2);
    return {
      reset,
      zoomIn: () => zoomFromCentre(1.2),
      zoomOut: () => zoomFromCentre(1 / 1.2),
    };
  };

  const renderPoint = (community, state, filter) => {
    const { x, y } = community;
    const priority = priorityRowOf(community);
    const tier = String(mapTier(community));
    const attributes = {
      class: `map__pt-group map__community${isDimmed(community, state, filter) ? " map__community--dim" : ""}${community.id === state.selected ? " map__community--selected" : ""}`,
      role: "link",
      tabindex: "0",
      "aria-label": `${community.name}, fix first #${priority.rank} of ${pack.count}`,
      "data-id": String(community.id),
    };
    let title;
    let shapes;
    let rankText = null;
    if (state.lens === "fix") {
      attributes["data-tier"] = tier;
      const size = mapRadius(community, state);
      title = `${community.name} · priority ${priority.rank}`;
      shapes = [s("circle", { class: "map__pt map__pt--fix", cx: f1(x), cy: f1(y), r: size })];
      if (tier === "1") {
        // Centred on the disc and drawn inside the disc's own group (below), so both scale
        // about the same centre: a baseline offset grew with the zoom and pushed the number out.
        rankText = s(
          "text",
          {
            class: "map__rank",
            "data-for": String(community.id),
            x: f1(x),
            y: f1(y),
            "text-anchor": "middle",
            "dominant-baseline": "central",
          },
          String(priority.rank),
        );
      }
    } else if (state.lens === "service") {
      const verdict = serviceVerdict(community, state.service);
      const size = mapRadius(community, state);
      title = `${community.name} · ${VERDICTS[verdict].word}`;
      shapes = [s("circle", { class: `map__pt map__pt--${verdict}`, cx: f1(x), cy: f1(y), r: size })];
      if (verdict === "degraded") {
        shapes.push(
          s("path", {
            class: "map__pt-half",
            d: `M${f1(x)},${f1(y - size)} A${size},${size} 0 0 0 ${f1(x)},${f1(y + size)} Z`,
          }),
        );
      } else if (verdict === "nodata") {
        shapes[0].setAttribute("stroke-dasharray", `${f1(size)} ${f1(size / 2)}`);
      }
    } else {
      const source = sourceState(community);
      attributes["data-sources"] = source;
      const size = mapRadius(community, state);
      title = `${community.name} · ${source}`;
      shapes = [s("circle", { class: `map__pt map__pt--source-${source}`, cx: f1(x), cy: f1(y), r: size })];
    }
    const group = s(
      "g",
      attributes,
      s("title", {}, title),
      s("circle", { class: "map__hit", cx: f1(x), cy: f1(y), r: 16 }),
      s("g", { class: "map__pt-shape" }, ...shapes, ...(rankText ? [rankText] : [])),
    );
    if (community.id === state.selected) {
      group.appendChild(s("circle", { class: "map__ring", cx: f1(x), cy: f1(y), r: 9 }));
    }
    const select = () => {
      location.hash = mapHash({ ...state, selected: community.id });
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

  const renderRegions = (state) =>
    h(
      "nav",
      { class: "map-regions", "aria-label": "Map regions" },
      [[null, "All NT"], ...REGION_SLUGS.map((region) => [region.slug, region.name])].map(
        ([slug, label]) =>
          h(
            "a",
            {
              class: "chip",
              "aria-pressed": state.region === slug || (!state.region && slug === null) ? "true" : "false",
              href: mapHash({ ...state, region: slug }),
            },
            label,
          ),
      ),
    );

  const renderMap = (requested) => {
    const filter = pack.filters.find((one) => one.id === requested.filter) ||
      pack.filters.find((one) => one.id === DEFAULT_FILTER) || pack.filters[0];
    const state = {
      lens: MAP_LENSES.includes(requested.lens) ? requested.lens : DEFAULT_LENS,
      region: REGION_SLUGS.some((region) => region.slug === requested.region) ? requested.region : null,
      filter: filter.id,
      selected: pack.communities.some((community) => community.id === requested.selected)
        ? requested.selected
        : null,
      layers: requested.layers,
      service: SERVICE_ORDER.includes(requested.service) ? requested.service : DEFAULT_SERVICE,
    };
    const selected = pack.communities.find((community) => community.id === state.selected) || null;
    const toggleLayers = pack.layers.filter(isToggleLayer);
    const visibleSlugs =
      !state.layers
        ? new Set()
        : new Set(state.layers.split(",").filter((slug) => toggleLayers.some((layer) => slugOf(layer) === slug)));
    state.layers = visibleSlugs.size ? toggleLayers.map(slugOf).filter((slug) => visibleSlugs.has(slug)).join(",") : null;
    const byRank = [...pack.communities].sort(
      (a, b) => priorityRowOf(a).rank - priorityRowOf(b).rank,
    );
    const ordered = [...byRank].sort(
      (a, b) => mapTier(b) - mapTier(a) || priorityRowOf(a).rank - priorityRowOf(b).rank,
    );
    const pointGroups = ordered.map((community) => renderPoint(community, state, filter));
    const pointGroupsById = new Map(ordered.map((community, index) => [community.id, pointGroups[index]]));
    const labelsGroup = s("g", { class: "map__zoom-labels" });
    const svg = s(
      "svg",
      {
        class: "map",
        role: "img",
        "aria-label": `Map of the Northern Territory, ${pack.count} communities`,
        "data-lens": state.lens,
        "data-zoom": "1",
        viewBox: "0 0 300 480",
        preserveAspectRatio: "xMidYMid meet",
      },
      s("g", { class: "map__land" }, s("path", { d: pack.outline })),
      renderHeat(),
      ...pack.layers.filter((layer) => layer.kind !== "point").map((layer) => renderLayerGroup(layer, visibleSlugs)),
      ...pointGroups,
      ...pack.layers.filter((layer) => layer.kind === "point").map((layer) => renderLayerGroup(layer, visibleSlugs)),
      labelsGroup,
    );
    if (state.region) {
      svg.setAttribute("data-region", state.region);
    }
    main.textContent = "";
    main.appendChild(h("h1", { class: "visually-hidden" }, "Map"));
    main.appendChild(renderMapLens(state));
    const resetButton = h(
      "button",
      { type: "button", class: "button button--secondary map-controls__reset", hidden: state.region ? null : "" },
      "Reset view",
    );
    const zoomInButton = h(
      "button",
      { type: "button", class: "map-controls__zoom", "aria-label": "Zoom in" },
      "+",
    );
    const zoomOutButton = h(
      "button",
      { type: "button", class: "map-controls__zoom", "aria-label": "Zoom out" },
      "−",
    );
    const zoomControls = h(
      "div",
      { class: "map-controls", "aria-label": "Map zoom" },
      zoomInButton,
      zoomOutButton,
    );
    const regionTarget = state.region ? regionView(state.region) : null;
    const frameAttributes = {
      class: "map-frame" + (regionTarget ? " map-frame--region" : ""),
    };
    if (regionTarget) {
      frameAttributes.style = "--map-region-ratio: " + regionTarget.w + " / " + regionTarget.h;
    }
    const frame = h(
      "div",
      frameAttributes,
      state.lens === "service" ? renderServiceSelector(state) : null,
      svg,
      resetButton,
      zoomControls,
    );
    main.appendChild(frame);
    const mapView = attachMapView(svg, ordered, state, pointGroupsById, labelsGroup, resetButton);
    resetButton.addEventListener("click", () => mapView.reset());
    zoomInButton.addEventListener("click", () => mapView.zoomIn());
    zoomOutButton.addEventListener("click", () => mapView.zoomOut());
    const legend = renderLegend(state);
    if (filter.id !== DEFAULT_FILTER || state.region) {
      legend.appendChild(h("p", { class: "map-legend__note" }, "Faded points are outside this highlight."));
    }
    main.appendChild(legend);
    main.appendChild(renderMapCard(selected));
    const regions = renderRegions(state);
    main.appendChild(regions);
    const activeRegion = regions.querySelector('[aria-pressed="true"]');
    regions.scrollLeft = activeRegion.offsetLeft - (regions.clientWidth - activeRegion.offsetWidth) / 2;
    const more = h(
      "details",
      { class: "map-more", open: filter.id !== DEFAULT_FILTER || state.layers ? "" : null },
      h("summary", {}, "Highlight and layers"),
      h(
        "section",
        { class: "map-more__group" },
        h("h2", { class: "map-more__group-title" }, "Highlight communities"),
        h(
          "p",
          { class: "map-more__note" },
          "Highlights affect both the map and the list.",
        ),
        renderFilterTabs(filter, state),
      ),
      h(
        "section",
        { class: "map-more__group" },
        h("h2", { class: "map-more__group-title" }, "Map layers"),
        h("p", { class: "map-more__note" }, "Layers change the map only."),
        renderLayerChips(toggleLayers, visibleSlugs, state),
      ),
    );
    main.appendChild(more);
    main.appendChild(renderMapListHeading(state, filter));
    main.appendChild(renderMapList(state, filter));
  };

  // The pipeline puts service gaps, evidence checks and monitoring in order. This screen only
  // prints the pack's group and rank; it never classifies or scores a community.
  const renderPriorityChips = (activeWord) => {
    const bar = h("div", { class: "chips priority-chips" });
    for (const word of [PRIORITY_ALL, ...pack.priority_interventions.map((one) => one.word)]) {
      const button = h(
        "button",
        {
          type: "button",
          class: "chip priority-chip",
          "aria-pressed": word === activeWord ? "true" : "false",
          // The name is the word alone: CSS-generated text would otherwise join the name.
          "aria-label": word === PRIORITY_ALL ? "All" : word,
          // How many rows the option leaves, shown by CSS beside the word; a count of pack rows.
          "data-count": String(
            word === PRIORITY_ALL
              ? pack.priority.length
              : pack.priority.filter((row) => interventionOf(row.i).word === word).length,
          ),
        },
        word === PRIORITY_ALL ? "All" : word,
      );
      button.addEventListener("click", () => {
        location.hash = priorityHash(word);
      });
      bar.appendChild(button);
    }
    return bar;
  };

  const renderPriorityRow = (row) => {
    const community = pack.communities.find((c) => c.id === row.id);
    const one = interventionOf(row.i);
    return h(
      "li",
      { class: "priority-row" },
      h(
        "a",
        { class: "priority-row__link", href: `#/community/${row.id}` },
        h("span", { class: "priority-row__rank fig fig--xs" }, `#${row.rank}`),
        h("span", { class: "priority-row__name" }, community.name),
        renderBadge(serviceVerdict(community, DEFAULT_SERVICE), "priority-row__badge"),
        h("span", { class: "priority-row__word" }, one.word),
        // The reason is one short sentence (at most 99 characters in the pack), so it is shown,
        // not folded: a "Why" fold on each of 96 rows hid what every reader of the list needs.
        h("span", { class: "priority-row__reason" }, figures(row.why)),
      ),
    );
  };

  const renderPriority = (requestedWord) => {
    const known = new Set(pack.priority_interventions.map((one) => one.word));
    const active = known.has(requestedWord) ? requestedWord : PRIORITY_ALL;
    const rows = pack.priority.filter(
      (row) => active === PRIORITY_ALL || interventionOf(row.i).word === active,
    );
    main.textContent = "";
    main.appendChild(
      h(
        "h1",
        { class: "visually-hidden" },
        "What to fix first",
      ),
    );
    main.appendChild(
      h(
        "p",
        { class: "priority-intro" },
        `${pack.priority.length} communities in action order. The score orders places within each group; method and weights are in the report.`,
      ),
    );
    main.appendChild(
      h(
        "details",
        { class: "priority-filters", open: active === PRIORITY_ALL ? null : "" },
        h("summary", {}, "Filter by action"),
        renderPriorityChips(active),
      ),
    );
    for (const [id, title, note] of PRIORITY_GROUPS) {
      const groupRows = rows.filter((row) => row.g === id);
      if (!groupRows.length) {
        continue;
      }
      main.appendChild(
        h(
          "section",
          { class: "priority-group" },
          h("h2", { class: "priority-group__title" }, `${title} (${groupRows.length})`),
          h("p", { class: "priority-group__note" }, note),
          h("ol", { class: "priority-list" }, groupRows.map(renderPriorityRow)),
        ),
      );
    }
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

  const renderHome = () => {
    const headline = pack.headline;
    const communities = headline ? headline.communities : pack.count;
    const figure = (value) => h("span", { class: "fig" }, String(value));
    const actions = h(
      "nav",
      { class: "home__actions", "aria-label": "Start here" },
      h("a", { class: "button button--primary", href: "#/community/426" }, "Find a community"),
      h("a", { class: "button button--secondary", href: "#/priority" }, "What to fix first"),
      h("a", { class: "button button--secondary", href: "#/map" }, "See the map"),
    );
    const children = [
      h("h1", { class: "home__question" }, "Coverage maps say there is signal. Can the clinic run a video call?"),
      h(
        "p",
        { class: "home__lead" },
        "Crosscheck puts every public source about ",
        figure(communities),
        " remote NT communities side by side: what the connection there allows, where the sources disagree, and what to fix first. It works with no network.",
      ),
    ];
    if (headline) {
      children.push(
        h(
          "ul",
          { class: "home__figures" },
          h("li", { class: "home__figure" }, figure(headline.communities), " communities"),
          h(
            "li",
            { class: "home__figure" },
            figure(headline.telehealth_works),
            " of ",
            figure(headline.with_clinic),
            " clinics where a video call is known to work",
          ),
          h("li", { class: "home__figure" }, figure(headline.sources_disagree), " where the sources disagree"),
        ),
      );
    }
    children.push(
      actions,
      h(
        "p",
        { class: "home__note" },
        "A diagnosis, not a fix: every figure is from a published source, and the app measures nothing.",
      ),
    );
    main.textContent = "";
    main.appendChild(h("section", { class: "home" }, children));
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
    main.appendChild(h("h1", { class: "visually-hidden" }, "Share"));
    const transfer = h("div", { class: "transfer" });
    const transferFold = h(
      "details",
      { class: "transfer-fold" },
      h("summary", {}, "Update another phone by camera"),
      transfer,
    );
    transfer.addEventListener("click", () => {
      transferFold.open = true;
    });
    if (new URLSearchParams(location.hash.split("?")[1] || "").has("transfer")) {
      transferFold.open = true;
    }
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
        transferFold,
      ),
    );
    // The camera loop and the camera read live in transfer.js (layer rule 8); this screen only
    // gives it the container and the same page bytes Save file writes.
    window.CrosscheckTransfer.mount(transfer, pageHtml);
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

  const screenOf = (hash) => {
    const path = hash.split("?")[0];
    if (path === "#/") {
      return "#/";
    }
    return SCREENS.find((screen) => path.startsWith(screen)) || "#/";
  };

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
      const isSelected = screen !== "#/" && tab.getAttribute("href").startsWith(screen);
      if (isSelected) {
        tab.setAttribute("aria-current", "page");
      } else {
        tab.removeAttribute("aria-current");
      }
      if (isSelected) {
        selected = tab;
      }
    }
    if (selected) {
      selected.scrollIntoView({ inline: "nearest", block: "nearest" });
    }
    if (screen === "#/") {
      renderHome();
    } else if (screen === "#/priority") {
      const query = new URLSearchParams(hash.split("?")[1] || "");
      renderPriority(query.get("intervention") || PRIORITY_ALL);
    } else if (screen === "#/map") {
      const query = new URLSearchParams(hash.split("?")[1] || "");
      const selectedParam = query.get("selected");
      renderMap({
        lens: query.get("lens") || DEFAULT_LENS,
        region: query.get("region"),
        filter: query.get("filter") || DEFAULT_FILTER,
        selected: selectedParam ? Number(selectedParam) : null,
        layers: query.has("layers") ? query.get("layers") : null,
        service: query.get("service") || DEFAULT_SERVICE,
      });
    } else if (screen === "#/share") {
      renderShare();
    } else {
      const match = hash.match(/^#\/community\/(\d+)/);
      renderCommunity(match ? Number(match[1]) : DEFAULT_ID);
    }
  };

  // The app works offline either way (it renders data_pack.json, requests nothing at runtime),
  // so the chip says that rather than "Online", which misled testers into thinking the app
  // needed a connection (Task-26; BACKLOG 2026-09-15, Task-07). "Works offline" replaced
  // "Offline-ready" on 2026-09-23: "ready" read as a claim that the data is up to date.
  const setChip = () => {
    chip.textContent = navigator.onLine ? "Works offline" : "Offline";
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

  // Tarik Base theme (2026-09-28): light by default; the toggle keeps the choice on this phone.
  // The <head> script in index.html applies a stored "dark" before the first paint. The browser
  // bar follows the canvas token, read from the theme, never retyped.
  const themeToggle = document.querySelector(".theme-toggle");
  const themeColor = document.querySelector('meta[name="theme-color"]');
  const setTheme = (theme) => {
    if (theme === "dark") {
      document.documentElement.dataset.theme = "dark";
    } else {
      delete document.documentElement.dataset.theme;
    }
    themeToggle.setAttribute("aria-pressed", String(theme === "dark"));
    const canvas = getComputedStyle(document.documentElement).getPropertyValue("--color-canvas");
    themeColor.setAttribute("content", canvas.trim());
  };
  themeToggle.addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    try {
      localStorage.setItem("crosscheck-theme", next);
    } catch (error) {
      // Storage is optional; the choice then lasts until the page closes.
    }
    setTheme(next);
  });
  headerChips.appendChild(themeToggle);
  setTheme(document.documentElement.dataset.theme === "dark" ? "dark" : "light");

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
