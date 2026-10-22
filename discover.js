/* Discover: ask or filter, see results with sources; ?id= opens one card. */
(function () {
  const ui = window.SameRoomUI;
  const api = window.SameRoomAPI;
  const el = ui.el;
  const root = document.querySelector("#discover");

  ui.shell("discover");
  if (ui.param("id")) showEntity(ui.param("id"));
  else showSearch();

  function showSearch() {
    const state = {
      ask: ui.param("ask"),
      kind: ui.param("kind") || "all",
      minCapacity: "",
      freeOnly: false,
    };

    const input = el("input", {
      id: "ask",
      type: "text",
      autocomplete: "off",
      value: state.ask,
      placeholder: "A quiet space for 80 people, free, next Thursday",
    });
    const form = el("form", { class: "askbar", role: "search", onsubmit: function (event) {
      event.preventDefault();
      state.ask = input.value;
      run();
    } }, [
      el("label", { class: "sr-only", for: "ask" }, "Ask Same Room"),
      input,
      el("button", { type: "submit" }, "Ask"),
    ]);

    const examples = el("p", { class: "hint" }, ["Try: "].concat(
      ["quiet venue for 60 people", "free space for 100", "communities for students"].map(function (q, i) {
        return [i ? " · " : "", el("button", { type: "button", class: "linklike", onclick: function () {
          input.value = q;
          state.ask = q;
          run();
        } }, q)];
      }).flat()
    ));

    const tabs = el("div", { class: "tabs", role: "group", "aria-label": "Show" });
    [["all", "All"], ["venue", "Venues"], ["community", "Communities"]].forEach(function (t) {
      tabs.append(el("button", {
        type: "button",
        "aria-pressed": state.kind === t[0] ? "true" : "false",
        onclick: function () {
          state.kind = t[0];
          state.ask = "";
          input.value = "";
          tabs.querySelectorAll("button").forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
          this.setAttribute("aria-pressed", "true");
          run();
        },
      }, t[1]));
    });

    const capacity = el("input", { type: "number", min: "0", step: "10", placeholder: "Any", oninput: function (e) {
      state.minCapacity = e.target.value;
      state.ask = "";
      run();
    } });
    const free = el("input", { type: "checkbox", onchange: function (e) {
      state.freeOnly = e.target.checked;
      state.ask = "";
      run();
    } });

    const filters = el("div", { class: "filters" }, [
      tabs,
      el("label", { class: "field inline" }, [el("span", null, "Min. people"), capacity]),
      el("label", { class: "check" }, [free, " Free only"]),
    ]);

    const answer = el("section", { class: "answer", "aria-live": "polite" });
    const results = el("section", { class: "results" });

    root.append(
      el("h1", { class: "page-title" }, "Discover"),
      el("p", { class: "lede" }, "Venues and communities. Each card says where its facts come from."),
      form,
      examples,
      filters,
      answer,
      results
    );

    function run() {
      results.classList.add("loading");
      const request = state.ask.trim()
        ? api.ask(state.ask)
        : api.discover({ kind: state.kind, minCapacity: state.minCapacity, freeOnly: state.freeOnly });
      request.then(render);
    }

    function render(result) {
      ui.clear(answer);
      ui.clear(results);
      results.classList.remove("loading");

      if (state.ask.trim()) {
        const understood = result.understood || {};
        const read = [];
        if (understood.kind && understood.kind !== "all") read.push(understood.kind + "s");
        if (understood.minCapacity) read.push(understood.minCapacity + "+ people");
        if (understood.freeOnly) read.push("free");
        if (understood.aspect) read.push(understood.aspect + " (from comments)");
        answer.append(
          el("p", { class: "answer-mode" }, [
            el("span", { class: result.mode === "agent" ? "tag" : "tag tag-warn" },
              result.mode === "agent" ? "Grok · mock" : "Filters only"),
            " Read as: " + (read.length ? read.join(", ") : "everything"),
          ])
        );
      }
      result.warnings.forEach(function (w) {
        answer.append(el("p", { class: "warning" }, w));
      });

      if (result.evidenceStatus === "available") {
        answer.append(evidenceBlock(result.evidenceGraph.references, "From comments"));
      } else if (result.evidenceStatus === "no_evidence") {
        answer.append(el("p", { class: "hint" }, "No comment references on that. That does not mean the opposite is true."));
      }

      if (!result.matches.length && !result.toConfirm.length) {
        results.append(el("p", { class: "empty" }, "Nothing documented matches. Loosen a filter, or add a venue with a source."));
        return;
      }
      const grid = el("div", { class: "cards" });
      result.matches.forEach(function (m) { grid.append(card(m)); });
      results.append(grid);

      if (result.toConfirm.length) {
        const extra = el("div", { class: "cards" });
        result.toConfirm.forEach(function (m) { extra.append(card(m)); });
        results.append(
          el("h2", { class: "label" }, "Could fit, to confirm"),
          el("p", { class: "hint" }, "These are missing a fact you filtered on. They are not matches yet."),
          extra
        );
      }
    }

    run();
  }

  const reasonText = {
    capacity_match: "Capacity fits",
    area_match: "Area fits",
    topic_match: "Matches your words",
    documented_free_terms: "Documented free terms",
    documented_host_relation: "Hosted here before",
  };

  function card(match) {
    const e = match.entity;
    const facts = e.kind === "venue"
      ? [
          e.area,
          e.capacity != null ? "Up to " + e.capacity : "Capacity unknown",
          ui.pricingLabel(e.pricing),
        ]
      : [e.leads.join(", ")];
    return el("a", { class: "card", href: "discover.html?id=" + e.id }, [
      el("p", { class: "card-k" }, [e.kind === "venue" ? "Venue" : "Community", ui.exampleTag(e)]),
      el("strong", { class: "card-title" }, e.name),
      el("p", { class: "card-facts" }, facts.filter(Boolean).join(" · ")),
      e.audience ? el("p", { class: "card-body" }, e.audience) : null,
      match.reasonCodes.length || match.unknownFields.length
        ? el("p", { class: "reasons" }, match.reasonCodes.map(function (r) {
            return el("span", { class: "chip chip-ok" }, reasonText[r] || r);
          }).concat(match.unknownFields.map(function (f) {
            return el("span", { class: "chip chip-unknown" }, f + " unknown");
          })))
        : null,
      el("p", { class: "card-source" }, "Source · " + e.sources[0].label),
    ]);
  }

  function evidenceBlock(references, title) {
    const list = el("div", { class: "evidence" });
    references.forEach(function (r) {
      list.append(el("figure", { class: "ref ref-" + r.interpretation }, [
        el("blockquote", null, r.excerpt),
        el("figcaption", null, [
          el("span", { class: "tag tag-example" }, "Example"),
          " " + r.aspect + " · reported " + r.interpretation + " · " + r.experiencedAt,
        ]),
      ]));
    });
    return el("div", { class: "evidence-wrap" }, [
      el("h2", { class: "label" }, title),
      el("p", { class: "hint" }, "Reported experience, not a guarantee. Contradictions stay visible."),
      list,
    ]);
  }

  function showEntity(id) {
    api.getEntity(id).then(function (result) {
      if (!result) {
        root.append(el("div", { class: "warn" }, [
          el("h1", null, "Not in the directory."),
          el("p", null, el("a", { href: "discover.html" }, "Back to Discover")),
        ]));
        return;
      }
      const e = result.entity;
      document.title = e.name + " — Same Room";
      const rows = e.kind === "venue"
        ? [
            ["Area", e.area],
            ["Capacity", e.capacity != null ? "Up to " + e.capacity : null],
            ["Price", ui.pricingLabel(e.pricing) + (e.pricing.conditions ? ". " + e.pricing.conditions : "")],
            ["Opening hours", e.openingHours],
            ["Availability", e.availability.length
              ? e.availability.map(function (a) { return a.startsAt + "–" + a.endsAt + " (checked " + a.checkedAt + ")"; }).join("; ")
              : "To confirm. Opening hours are not availability."],
            ["Equipment", e.av],
          ]
        : [
            ["Leads", e.leads.join(", ")],
            ["What is public", e.audience],
            ["Tags", e.tags.length ? e.tags.join(", ") : null],
          ];

      const facts = el("dl", { class: "factlist" });
      rows.forEach(function (r) {
        facts.append(el("div", null, [
          el("dt", null, r[0]),
          el("dd", { class: r[1] ? null : "unknown" }, r[1] || "Not documented"),
        ]));
      });

      const draftOut = el("div", { class: "draft" });
      const draftForm = el("form", { class: "draft-form", onsubmit: function (event) {
        event.preventDefault();
        const data = new FormData(event.target);
        api.draftRequest(e.id, {
          what: data.get("what"),
          people: data.get("people"),
          when: data.get("when"),
          from: data.get("from"),
        }).then(function (out) {
          ui.clear(draftOut);
          const box = el("textarea", { class: "draft-text", readonly: "readonly", rows: "9" });
          box.value = out.draft;
          draftOut.append(
            box,
            el("div", { class: "actions" }, [
              el("button", { type: "button", class: "publish", onclick: function () {
                navigator.clipboard && navigator.clipboard.writeText(out.draft);
                this.textContent = "Copied";
              } }, "Copy draft"),
              el("p", { class: "hint" }, "Nothing is sent from here."),
            ])
          );
        });
      } }, [
        el("div", { class: "row" }, [
          el("label", { class: "field" }, [el("span", null, "What"), el("input", { name: "what", placeholder: "a community hack night" })]),
          el("label", { class: "field" }, [el("span", null, "People"), el("input", { name: "people", type: "number", min: "1" })]),
        ]),
        el("div", { class: "row" }, [
          el("label", { class: "field" }, [el("span", null, "When"), el("input", { name: "when", placeholder: "Thursday 5 November" })]),
          el("label", { class: "field" }, [el("span", null, "From"), el("input", { name: "from", placeholder: "Your name" })]),
        ]),
        el("button", { type: "submit", class: "secondary" }, "Draft request"),
      ]);

      let evidence = null;
      if (result.evidenceStatus === "available") evidence = evidenceBlock(result.evidenceGraph.references, "What people reported");
      else if (e.kind === "venue") {
        evidence = el("div", { class: "evidence-wrap" }, [
          el("h2", { class: "label" }, "What people reported"),
          el("p", { class: "hint" }, result.evidenceStatus === "unavailable"
            ? "Comment references are temporarily unavailable."
            : "No comments yet."),
        ]);
      }

      root.append(
        el("p", { class: "eyebrow" }, [el("a", { href: "discover.html" }, "Discover"), " / " + (e.kind === "venue" ? "Venue" : "Community")]),
        el("article", { class: "sheet entity" }, [
          el("div", { class: "sheet-body" }, [
            el("p", { class: "sheet-kicker" }, [e.kind === "venue" ? "Venue" : "Community", ui.exampleTag(e)]),
            el("h1", { class: "sheet-title" }, e.name),
            facts,
            el("p", { class: "reasons" }, e.sources.map(ui.sourceChip)),
            e.kind === "community"
              ? el("p", { class: "actions" }, [
                  el("a", { class: "publish", href: "desk.html?a=" + e.id }, "Pair on the desk"),
                ])
              : null,
          ]),
        ]),
        evidence,
        el("section", { class: "band" }, [
          el("h2", { class: "label" }, e.kind === "venue" ? "Ask this venue" : "Write to the leads"),
          draftForm,
          draftOut,
        ])
      );
    });
  }
})();
