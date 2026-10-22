(function () {
  const room = window.SAME_ROOM;
  const page = document.body.dataset.page;

  function el(tag, attrs, children) {
    const node = document.createElement(tag);
    Object.entries(attrs || {}).forEach(function (entry) {
      const key = entry[0];
      const value = entry[1];
      if (key === "class") node.className = value;
      else if (key.slice(0, 2) === "on" && typeof value === "function") {
        node.addEventListener(key.slice(2), value);
      } else if (value != null && value !== false) node.setAttribute(key, value);
    });
    [].concat(children || []).forEach(function (child) {
      if (child == null || child === false) return;
      node.append(child.nodeType ? child : document.createTextNode(String(child)));
    });
    return node;
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function param(name) {
    const value = new URLSearchParams(location.search).get(name);
    return value == null ? "" : value;
  }

  function selectedPair(ids) {
    if (ids.length !== 2) return null;
    const a = room.byId(ids[0]);
    const b = room.byId(ids[1]);
    if (!a || !b) return null;
    return { a: a, b: b };
  }

  function pageUrl(state) {
    const query = new URLSearchParams();
    query.set("a", state.ids[0]);
    query.set("b", state.ids[1]);
    if (state.idea.trim()) query.set("idea", state.idea.trim());
    if (state.notes.trim()) query.set("notes", state.notes.trim());
    if (state.when.trim()) query.set("when", state.when.trim());
    if (state.where.trim()) query.set("where", state.where.trim());
    return "event.html?" + query.toString();
  }

  function initDesk() {
    const roster = document.querySelector("#roster");
    const composer = document.querySelector("#composer");
    if (window.SameRoomUI) window.SameRoomUI.shell("desk");
    const stored = readDraft();
    const state = stored || {
      ids: ["outpost", "hackradar"],
      idea: "",
      notes: "",
      when: "Thursday 5 November 2026, 18:30",
      where: "London — place to confirm",
    };

    const preset = room.byId(param("a"));
    if (preset && state.ids.indexOf(preset.id) === -1) {
      state.ids = [preset.id].concat(state.ids).slice(0, 2);
    }

    function persist() {
      try {
        sessionStorage.setItem("same-room-draft", JSON.stringify(state));
      } catch (error) {
        /* private mode can block storage; the page still works */
      }
    }

    function render() {
      const pair = selectedPair(state.ids);
      const plan = pair ? room.draft(pair.a, pair.b, state.idea) : null;
      clear(roster);
      clear(composer);

      const badges = el("div", { class: "badges" });
      roster.append(
        el("h2", { class: "label" }, "In the room"),
        el("p", { class: "hint" }, "Pick two. Deselect one to change the pair."),
        badges
      );

      const ordered = room.communities.slice().sort(function (left, right) {
        const leftSelected = state.ids.indexOf(left.id) === -1 ? 1 : 0;
        const rightSelected = state.ids.indexOf(right.id) === -1 ? 1 : 0;
        return leftSelected - rightSelected;
      });

      ordered.forEach(function (community) {
        const pressed = state.ids.indexOf(community.id) !== -1;
        badges.append(
          el(
            "button",
            {
              class: "badge",
              type: "button",
              "aria-pressed": pressed ? "true" : "false",
              onclick: function () {
                const index = state.ids.indexOf(community.id);
                if (index !== -1) {
                  state.ids.splice(index, 1);
                } else if (state.ids.length < 2) {
                  state.ids.push(community.id);
                } else {
                  const note = document.querySelector("#limit");
                  if (note) note.hidden = false;
                  return;
                }
                render();
              },
            },
            [
              el("strong", null, community.name),
              el("span", { class: "leads" }, community.leads.join(", ")),
              el("span", { class: "focus" }, community.focus),
            ]
          )
        );
      });

      composer.append(
        el("h2", { class: "label" }, "The page"),
        el(
          "p",
          { class: "hint", id: "limit", hidden: "hidden" },
          "Two communities fit on the page. Deselect one first."
        )
      );

      if (!plan) {
        composer.append(el("p", null, "Select two communities to draft the page."));
        persist();
        return;
      }

      const idea = el("input", {
        id: "idea",
        type: "text",
        value: state.idea,
        placeholder: plan.suggestion,
        oninput: function (event) {
          state.idea = event.target.value;
          paintSheet();
        },
      });

      composer.append(
        el("label", { class: "field" }, [el("span", null, "Idea"), idea]),
        el(
          "button",
          {
            class: "suggestion",
            type: "button",
            onclick: function () {
              state.idea = plan.suggestion;
              render();
              const field = document.querySelector("#idea");
              if (field) field.focus();
            },
          },
          "Use this idea"
        )
      );

      const when = el("input", {
        id: "when",
        type: "text",
        value: state.when,
        oninput: function (event) {
          state.when = event.target.value;
          paintSheet();
        },
      });
      const where = el("input", {
        id: "where",
        type: "text",
        value: state.where,
        oninput: function (event) {
          state.where = event.target.value;
          paintSheet();
        },
      });
      composer.append(
        el("div", { class: "row" }, [
          el("label", { class: "field" }, [el("span", null, "When"), when]),
          el("label", { class: "field" }, [el("span", null, "Where"), where]),
        ])
      );

      const notes = el("textarea", {
        id: "notes",
        placeholder: "A sentence from Slack, Discord, or the person next to you. Leave this empty rather than guessing.",
        oninput: function (event) {
          state.notes = event.target.value;
          paintSheet();
        },
      });
      notes.value = state.notes;
      composer.append(
        el("label", { class: "field" }, [el("span", null, "What members actually said"), notes])
      );

      const sheet = el("article", { class: "sheet", id: "sheet" });
      const publish = el("a", { class: "publish", id: "publish" }, "Publish live page");
      composer.append(sheet, el("div", { class: "actions" }, [
        publish,
        el("p", { class: "hint" }, "Opens the page you would send the two leads."),
      ]));

      function paintSheet() {
        const current = room.draft(pair.a, pair.b, state.idea);
        clear(sheet);
        const ask = el("ul", { class: "ask" });
        current.questions.forEach(function (line) {
          ask.append(el("li", null, line));
        });
        const said = state.notes.trim()
          ? el("blockquote", { class: "note" }, state.notes.trim())
          : el("p", { class: "hint" }, "Nothing pasted yet. These questions stay questions.");

        sheet.append(
          el("div", { class: "sheet-body" }, [
            el(
              "p",
              { class: "sheet-kicker" },
              state.idea.trim() ? pair.a.name + " × " + pair.b.name : "Proposed collab"
            ),
            el("h2", { class: "sheet-title" }, current.title),
            el("p", { class: "reason" }, current.reason),
            el("dl", { class: "facts" }, [
              el("div", null, [el("dt", null, "Hosts"), el("dd", null, current.hosts.join(", "))]),
              el("div", null, [el("dt", null, "When"), el("dd", null, state.when || "To confirm")]),
              el("div", null, [el("dt", null, "Where"), el("dd", null, state.where || "To confirm")]),
              el("div", null, [el("dt", null, "Next action"), el("dd", null, current.nextAction)]),
            ]),
            el("h2", { class: "label" }, state.notes.trim() ? "From the channel" : "Ask this. Don’t invent the answer."),
            state.notes.trim() ? said : ask,
          ])
        );
        publish.href = pageUrl(state);
        publish.setAttribute("aria-disabled", "false");
        persist();
      }

      paintSheet();
      persist();
    }

    render();
  }

  function readDraft() {
    try {
      const saved = JSON.parse(sessionStorage.getItem("same-room-draft") || "null");
      if (!saved || !Array.isArray(saved.ids)) return null;
      const ids = saved.ids.filter(function (id) {
        return room.byId(id);
      }).slice(0, 2);
      return {
        ids: ids,
        idea: String(saved.idea || ""),
        notes: String(saved.notes || ""),
        when: String(saved.when || ""),
        where: String(saved.where || ""),
      };
    } catch (error) {
      return null;
    }
  }

  function initEvent() {
    const root = document.querySelector("#event");
    const a = room.byId(param("a"));
    const b = room.byId(param("b"));
    clear(root);

    if (!a || !b || a.id === b.id) {
      root.append(
        el("div", { class: "warn" }, [
          el("h1", null, "This page needs two communities."),
          el("p", null, "Go back to the desk and publish a pair."),
          el("p", null, el("a", { href: "desk.html" }, "Back to the desk")),
        ])
      );
      return;
    }

    const idea = param("idea");
    const notes = param("notes");
    const when = param("when");
    const where = param("where");
    const plan = room.draft(a, b, idea);
    document.title = plan.title + " — Same Room";

    const ask = el("ul", { class: "ask" });
    plan.questions.forEach(function (line) {
      ask.append(el("li", null, line));
    });

    const invites = el("div", null);
    plan.invites.forEach(function (item) {
      const why = item.overlap.length ? item.overlap.join(", ") : "Also in the room";
      invites.append(
        el("div", { class: "invite" }, [
          el("b", null, item.community.name),
          el("span", { class: "hint" }, why),
        ])
      );
    });

    const sources = el("ul", { class: "sources" });
    plan.sources.forEach(function (item) {
      const line = item.url
        ? [item.name + ": ", el("a", { href: item.url }, item.source)]
        : [item.name + ": " + item.source];
      sources.append(el("li", null, line));
    });

    root.append(
      el("p", { class: "eyebrow noprint" }, [
        el("a", { href: "desk.html" }, "Same Room"),
        "  ·  live page",
      ]),
      el("article", { class: "sheet" }, [
        el("div", { class: "sheet-body" }, [
          el("p", { class: "sheet-kicker" }, idea ? a.name + " × " + b.name : "Proposed collab"),
          el("h1", { class: "sheet-title" }, plan.title),
          el("p", { class: "reason" }, plan.reason),
          el("dl", { class: "facts" }, [
            el("div", null, [el("dt", null, "Hosts"), el("dd", null, plan.hosts.join(", "))]),
            el("div", null, [
              el("dt", null, "When"),
              el("dd", null, when || "To confirm"),
              el("dt", { class: "again" }, "Where"),
              el("dd", null, where || "To confirm"),
            ]),
          ]),
          el("h2", { class: "label" }, "What is public"),
          el("p", null, [el("strong", null, a.name + ". "), a.focus]),
          el("p", null, [el("strong", null, b.name + ". "), b.focus]),
          notes
            ? el("h2", { class: "label" }, "Pasted on the desk — not verified")
            : el("h2", { class: "label" }, "Ask this. Don’t invent the answer."),
          notes ? el("blockquote", { class: "note" }, notes) : ask,
          el("h2", { class: "label" }, "Also invite"),
          invites,
          el("h2", { class: "label" }, "Next action"),
          el("p", null, plan.nextAction),
        ]),
      ]),
      el("section", { class: "noprint" }, [
        el("h2", { class: "label" }, "Memory used"),
        el("p", { class: "hint" }, "Only these public lines. Nothing here is a member quote unless it was pasted on the desk."),
        sources,
      ])
    );
  }

  if (page === "desk") initDesk();
  if (page === "event") initEvent();
})();
