"use strict";

// Report here (Task-35, 2026-09-16): the community's own word, recorded on the phone that is
// standing in it. Every other line on the community screen is a publisher's claim; this one is
// the person's. It is stored in IndexedDB beside the pack (store.js) and travels only when
// someone chooses to send it -- as one ASCII line the SMS and mesh channels already carry.
//
// This file computes nothing about a service and reads no requirement figure: it records what a
// person tapped plus what the browser already knows about its own connection (layer rule 4).
// It makes no request of any kind (layer rule 7), and it never opens a camera or a microphone
// (layer rule 8). navigator.geolocation appears once, inside the save handler, behind the
// checkbox that is unchecked by default.
window.CrosscheckReport = (() => {
  const PREFIX = "CR1";
  const FIELD_COUNT = 9;
  // The line has to fit one mesh packet, like the statement texts (app.js: MESH_MAX_BYTES).
  const MAX_BYTES = 200;
  const GEO_TIMEOUT_MS = 8000;

  const STATUSES = [
    { id: "works", label: "Works" },
    { id: "slow", label: "Slow" },
    { id: "none", label: "No connection" },
  ];
  const STATUS_COUNT_LABEL = { works: "works", slow: "slow", none: "no connection" };
  const CARRIERS = [
    { id: "telstra", label: "Telstra" },
    { id: "optus", label: "Optus" },
    { id: "tpg", label: "TPG" },
    { id: "other", label: "Other" },
    { id: "-", label: "Don't know" },
  ];
  const MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
  ];

  const ABSENT = "-";
  const ASCII_RE = /^[ -~]+$/;
  const ID_RE = /^[0-9]{1,6}$/;
  const TIME_RE = /^[0-9]{12}$/;
  const TYPE_RE = /^[a-z0-9-]{1,12}$/;
  const RTT_RE = /^[0-9]{1,6}$/;
  const DOWNLINK_RE = /^[0-9]{1,4}\.[0-9]$/;
  const POSITION_RE = /^-?[0-9]{1,3}\.[0-9]{2},-?[0-9]{1,3}\.[0-9]{2}$/;

  const statusIds = STATUSES.map((entry) => entry.id);
  const carrierIds = CARRIERS.map((entry) => entry.id);

  // The built-in pack element is the id list a line is checked against: an id that is not one
  // of the 96 is not a report about anywhere. Built once -- the element's text never changes,
  // a received pack only replaces the variable app.js renders from (store.js, Task-24).
  let knownIds = null;
  const isKnownId = (id) => {
    if (knownIds === null) {
      const pack = JSON.parse(document.getElementById("pack").textContent);
      knownIds = new Set(pack.communities.map((community) => community.id));
    }
    return knownIds.has(id);
  };

  const pad = (value, width) => String(value).padStart(width, "0");

  const round2 = (value) => Math.round(value * 100) / 100;

  // The record's absent fields are null; the line writes them as "-". format and parse are
  // inverses over records in that canonical shape (rtt an integer, downlink one decimal,
  // position two decimals).
  const format = (record) => {
    const hasPosition =
      record.lat !== null && record.lat !== undefined &&
      record.lon !== null && record.lon !== undefined;
    return [
      PREFIX,
      String(record.id),
      record.time,
      record.status,
      record.carrier === null || record.carrier === undefined ? ABSENT : record.carrier,
      record.effectiveType === null || record.effectiveType === undefined
        ? ABSENT
        : record.effectiveType,
      record.rtt === null || record.rtt === undefined ? ABSENT : String(Math.round(record.rtt)),
      record.downlink === null || record.downlink === undefined
        ? ABSENT
        : Number(record.downlink).toFixed(1),
      hasPosition ? `${record.lat.toFixed(2)},${record.lon.toFixed(2)}` : ABSENT,
    ].join("|");
  };

  // Returns null for anything that is not exactly one well-formed line: a wrong prefix, a wrong
  // field count, an unknown status or carrier, a malformed figure, or an id that is not in the
  // pack. Nothing half-understood is ever stored or counted.
  const parse = (line) => {
    if (typeof line !== "string" || !ASCII_RE.test(line) || line.length > MAX_BYTES) {
      return null;
    }
    const fields = line.split("|");
    if (fields.length !== FIELD_COUNT || fields[0] !== PREFIX) {
      return null;
    }
    const [, idText, time, status, carrier, effectiveType, rtt, downlink, position] = fields;
    if (!ID_RE.test(idText) || !isKnownId(Number(idText))) {
      return null;
    }
    if (!TIME_RE.test(time) || !statusIds.includes(status) || !carrierIds.includes(carrier)) {
      return null;
    }
    if (effectiveType !== ABSENT && !TYPE_RE.test(effectiveType)) {
      return null;
    }
    if (rtt !== ABSENT && !RTT_RE.test(rtt)) {
      return null;
    }
    if (downlink !== ABSENT && !DOWNLINK_RE.test(downlink)) {
      return null;
    }
    if (position !== ABSENT && !POSITION_RE.test(position)) {
      return null;
    }
    const [lat, lon] = position === ABSENT ? [null, null] : position.split(",").map(Number);
    return {
      id: Number(idText),
      time,
      status,
      carrier: carrier === ABSENT ? null : carrier,
      effectiveType: effectiveType === ABSENT ? null : effectiveType,
      rtt: rtt === ABSENT ? null : Number(rtt),
      downlink: downlink === ABSENT ? null : Number(downlink),
      lat,
      lon,
    };
  };

  const stamp = (date) =>
    `${date.getUTCFullYear()}${pad(date.getUTCMonth() + 1, 2)}${pad(date.getUTCDate(), 2)}` +
    `${pad(date.getUTCHours(), 2)}${pad(date.getUTCMinutes(), 2)}`;

  const prettyDate = (time) =>
    `${Number(time.slice(6, 8))} ${MONTHS[Number(time.slice(4, 6)) - 1]} ${time.slice(0, 4)}`;

  // --- DOM ---------------------------------------------------------------------------------

  const el = (tag, attrs, ...children) => {
    const node = document.createElement(tag);
    if (attrs) {
      for (const [key, value] of Object.entries(attrs)) {
        if (value !== null && value !== undefined) {
          node.setAttribute(key, value);
        }
      }
    }
    for (const child of children) {
      if (child === null || child === undefined || child === false) {
        continue;
      }
      node.appendChild(child instanceof Node ? child : document.createTextNode(String(child)));
    }
    return node;
  };

  // The HTML parser places <svg> and <path> in the SVG namespace; reading it back keeps a
  // namespace URL literal out of this file (layer rule 7 forbids one).
  const SVG_NS = (() => {
    const template = document.createElement("template");
    template.innerHTML = "<svg><path></path></svg>";
    return template.content.firstChild.namespaceURI;
  })();

  const svg = (tag, attrs) => {
    const node = document.createElementNS(SVG_NS, tag);
    for (const [key, value] of Object.entries(attrs || {})) {
      node.setAttribute(key, value);
    }
    return node;
  };

  // Clipboard first, an off-screen textarea where the Clipboard API is refused (the same two
  // paths app.js: copyText takes; this file cannot reach into that closure).
  const copyText = async (text) => {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (error) {
        // Fall through to the textarea.
      }
    }
    const area = el("textarea", {
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

  const flash = (button, label, copied) => {
    button.textContent = copied ? "Copied" : "Copy failed. Select the text and copy it manually.";
    setTimeout(() => {
      button.textContent = label;
    }, copied ? 2000 : 4000);
  };

  // Set by renderReports so a save made in the form below updates the count line above it in
  // the same render; null when the count line is not on screen.
  let refreshCount = null;

  // --- the form ----------------------------------------------------------------------------

  // The one place in the app that asks the phone where it is, and only when the box is ticked.
  // A refusal, an error or eight seconds of silence all mean "no position": nothing is shown,
  // because a person who declined does not need to be told off for it.
  const askPosition = () =>
    new Promise((resolve) => {
      if (!navigator.geolocation) {
        resolve(null);
        return;
      }
      let settled = false;
      const finish = (value) => {
        if (!settled) {
          settled = true;
          resolve(value);
        }
      };
      setTimeout(() => finish(null), GEO_TIMEOUT_MS);
      try {
        navigator.geolocation.getCurrentPosition(
          (position) =>
            finish({
              lat: round2(position.coords.latitude),
              lon: round2(position.coords.longitude),
            }),
          () => finish(null),
          { timeout: GEO_TIMEOUT_MS, maximumAge: 0 },
        );
      } catch (error) {
        finish(null);
      }
    });

  // What the browser already knows about its own connection, sanitised into the line's shape;
  // a field the browser does not publish stays null and prints as "-".
  const connectionFields = () => {
    const connection = navigator.connection;
    if (!connection) {
      return { effectiveType: null, rtt: null, downlink: null };
    }
    const effectiveType =
      typeof connection.effectiveType === "string" && TYPE_RE.test(connection.effectiveType)
        ? connection.effectiveType
        : null;
    const rtt = Number.isFinite(connection.rtt) ? Math.round(connection.rtt) : null;
    const downlink = Number.isFinite(connection.downlink)
      ? Number(Number(connection.downlink).toFixed(1))
      : null;
    return { effectiveType, rtt, downlink };
  };

  const renderLine = (line) => {
    const copyButton = el("button", { type: "button", class: "report-line__copy" }, "Copy line");
    copyButton.addEventListener("click", async () => {
      flash(copyButton, "Copy line", await copyText(line));
    });
    const smsLink = el(
      "a",
      { class: "report-line__sms", href: `sms:?body=${encodeURIComponent(line)}` },
      "Send as SMS",
    );
    const code = window.CrosscheckQR.encode(line, "M");
    const qr = svg("svg", {
      class: "report-line__qr",
      role: "img",
      "aria-label": "QR code of this report line",
      viewBox: `0 0 ${code.size} ${code.size}`,
      "shape-rendering": "crispEdges",
    });
    qr.appendChild(svg("path", { class: "qr__modules", d: window.CrosscheckQR.toSvgPath(code) }));
    return el(
      "div",
      { class: "report-line__block" },
      el("pre", { class: "report-line" }, line),
      el("div", { class: "report-line__actions" }, copyButton, smsLink),
      qr,
    );
  };

  const renderForm = (community) => {
    const form = el("div", { class: "report-form" });
    let status = null;
    let carrier = null;

    const saveButton = el(
      "button",
      { type: "button", class: "button button--primary report-form__save", disabled: "" },
      "Save report",
    );

    const statusRow = el("fieldset", { class: "report-form__row" }, el("legend", {}, "Status"));
    const statusButtons = STATUSES.map((entry) => {
      const button = el(
        "button",
        { type: "button", class: "report-form__status", "aria-pressed": "false" },
        entry.label,
      );
      button.addEventListener("click", () => {
        status = entry.id;
        statusButtons.forEach((other) =>
          other.setAttribute("aria-pressed", other === button ? "true" : "false"),
        );
        saveButton.removeAttribute("disabled");
      });
      statusRow.appendChild(button);
      return button;
    });

    const carrierRow = el(
      "fieldset",
      { class: "report-form__row chips" },
      el("legend", {}, "Carrier (optional)"),
    );
    const carrierButtons = CARRIERS.map((entry) => {
      const button = el(
        "button",
        { type: "button", class: "chip report-form__carrier", "aria-pressed": "false" },
        entry.label,
      );
      button.addEventListener("click", () => {
        carrier = entry.id === ABSENT ? null : entry.id;
        carrierButtons.forEach((other) =>
          other.setAttribute("aria-pressed", other === button ? "true" : "false"),
        );
      });
      carrierRow.appendChild(button);
      return button;
    });

    const locationBox = el("input", { type: "checkbox", class: "report-form__checkbox" });
    const locationLabel = el(
      "label",
      { class: "report-form__location" },
      locationBox,
      "Include my position (about 1 km)",
    );

    const result = el("div", { class: "report-form__result" });

    saveButton.addEventListener("click", async () => {
      saveButton.setAttribute("disabled", "");
      saveButton.textContent = "Saving";
      const connection = connectionFields();
      const position = locationBox.checked ? await askPosition() : null;
      const line = format({
        id: community.id,
        time: stamp(new Date()),
        status,
        carrier,
        effectiveType: connection.effectiveType,
        rtt: connection.rtt,
        downlink: connection.downlink,
        lat: position ? position.lat : null,
        lon: position ? position.lon : null,
      });
      let saved = true;
      try {
        await window.CrosscheckStore.saveReport(line);
      } catch (error) {
        saved = false;
      }
      result.textContent = "";
      if (!saved) {
        result.appendChild(
          el(
            "p",
            { class: "report-error", role: "alert" },
            "Could not save this report on this phone. You can still copy or send this line.",
          ),
        );
      }
      result.appendChild(renderLine(line));
      saveButton.textContent = "Save report";
      saveButton.removeAttribute("disabled");
      if (saved && refreshCount) {
        await refreshCount();
      }
    });

    form.appendChild(el("p", { class: "report-form__note" }, "What is your phone doing here?"));
    form.appendChild(statusRow);
    form.appendChild(carrierRow);
    form.appendChild(locationLabel);
    form.appendChild(saveButton);
    form.appendChild(result);
    return form;
  };

  // --- the count line, the import fold and Copy evidence ------------------------------------

  const countText = (lines) => {
    const records = lines.map(parse).filter(Boolean);
    if (records.length === 0) {
      return "Saved on this phone: none yet";
    }
    const counts = statusIds.map(
      (id) =>
        `${records.filter((record) => record.status === id).length} ${STATUS_COUNT_LABEL[id]}`,
    );
    const latest = records.map((record) => record.time).sort().pop();
    return `Saved on this phone: ${records.length} · ${counts.join(", ")} · latest ${prettyDate(latest)}`;
  };

  const lineCount = (text) =>
    String(text)
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean).length;

  // One block: the count line, the fold that takes lines in, and Copy evidence. `headerLines`
  // is the pack half of the evidence block, assembled by app.js from pack strings (only app.js
  // reads the pack's service words); this file appends the stored reports and the sentence
  // that says what the app does and does not know.
  const renderReports = (community, headerLines) => {
    const countLine = el("p", { class: "reports-line" }, "Saved on this phone: none yet");

    const refresh = async () => {
      const lines = await window.CrosscheckStore.reportsFor(community.id);
      countLine.textContent = countText(lines);
    };
    refreshCount = refresh;

    const textarea = el("textarea", {
      class: "reports-fold__text",
      rows: "3",
      "aria-label": "Report lines to add",
    });
    const importResult = el("p", { class: "reports-import__result" });
    const importButton = el(
      "button",
      { type: "button", class: "button button--secondary reports-import" },
      "Add",
    );
    importButton.addEventListener("click", async () => {
      const text = textarea.value;
      const kept = await window.CrosscheckStore.importReports(text);
      importResult.textContent = `Added ${kept} of ${lineCount(text)} lines`;
      await refresh();
    });
    const fold = el(
      "details",
      { class: "reports-fold" },
      el("summary", {}, "Import report lines from another phone"),
      textarea,
      importButton,
      importResult,
    );

    const evidenceButton = el(
      "button",
      { type: "button", class: "evidence-button" },
      "Copy evidence",
    );
    evidenceButton.addEventListener("click", async () => {
      const lines = await window.CrosscheckStore.reportsFor(community.id);
      const text = [
        ...headerLines,
        ...lines,
        `Crosscheck does not measure signal; reports are what people in ${community.name} ` +
          "recorded on their own phones.",
      ].join("\n");
      flash(evidenceButton, "Copy evidence", await copyText(text));
    });

    const block = el(
      "section",
      { class: "community-reports reports section", "aria-labelledby": "community-reports-title" },
      el("h2", { class: "community-reports__title", id: "community-reports-title" }, "Community reports"),
      countLine,
      fold,
      evidenceButton,
    );
    refresh();
    return block;
  };

  return { format, parse, stamp, prettyDate, renderForm, renderReports };
})();
