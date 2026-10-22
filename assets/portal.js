/* Shared shell for portal pages: header, mock banner, small DOM helpers. */
(function () {
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
    return new URLSearchParams(location.search).get(name) || "";
  }

  const pricingLabels = {
    free: "Free",
    paid: "Paid",
    on_request: "Price on request",
    unknown: "Price to confirm",
  };

  function pricingLabel(pricing) {
    return pricingLabels[pricing.type] || "Price to confirm";
  }

  function when(event) {
    if (event.allDay) {
      const day = function (d) {
        return new Date(d + "T12:00:00Z").toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short", year: "numeric" });
      };
      // iCal all-day end dates are exclusive: the last day is the one before.
      const last = event.endsAt && new Date(Date.parse(event.endsAt + "T12:00:00Z") - 864e5).toISOString().slice(0, 10);
      return last && last > event.startsAt ? day(event.startsAt) + " – " + day(last) : day(event.startsAt);
    }
    return new Date(event.startsAt).toLocaleString("en-GB", {
      weekday: "short", day: "numeric", month: "short", year: "numeric",
      hour: "2-digit", minute: "2-digit", timeZone: "Europe/London",
    }) + " London time";
  }

  function exampleTag(entity) {
    return entity.example ? el("span", { class: "tag tag-example" }, "Example") : null;
  }

  function sourceChip(source) {
    const label = "Source · " + source.label;
    return source.url
      ? el("a", { class: "chip", href: source.url, rel: "noopener" }, label)
      : el("span", { class: "chip" }, label);
  }

  function shell(active) {
    const api = window.SameRoomAPI;
    const nav = [
      ["index.html", "Home", "home"],
      ["discover.html", "Discover", "discover"],
      ["desk.html", "Pair communities", "desk"],
    ];
    const header = el("header", { class: "site" }, [
      el("div", { class: "site-inner" }, [
        el("a", { class: "brand", href: "index.html" }, [
          el("img", { src: "assets/logo.svg", alt: "", width: "32", height: "32" }),
          el("span", null, "Same Room"),
        ]),
        el("nav", { "aria-label": "Main" }, nav.map(function (item) {
          return el("a", { href: item[0], "aria-current": item[2] === active ? "page" : null }, item[1]);
        })),
      ]),
    ]);
    const banner = api && api.status.mock
      ? el("p", { class: "mock-banner" }, [
          el("strong", null, "Mockup. "),
          "Venues and comments are examples. Communities and Luma events are real, with sources. Supabase, Grok and Cognee are not connected yet.",
        ])
      : null;
    document.body.prepend(header, banner || "");
  }

  window.SameRoomUI = {
    el: el,
    clear: clear,
    param: param,
    pricingLabel: pricingLabel,
    when: when,
    exampleTag: exampleTag,
    sourceChip: sourceChip,
    shell: shell,
  };

  if (document.body.dataset.page === "home") initHome();

  function initHome() {
    shell("home");
    const api = window.SameRoomAPI;
    const strip = document.querySelector("#communities");
    window.SAME_ROOM.communities.forEach(function (c) {
      strip.append(el("a", { class: "pill", href: "discover.html?id=" + c.id }, c.name));
    });
    const status = document.querySelector("#status");
    const next = document.querySelector("#next-events");
    api.upcomingEvents(6).then(function (events) {
      events.forEach(function (e) {
        next.append(el("a", { class: "card", href: "discover.html?id=" + e.id }, [
          el("p", { class: "card-k" }, when(e)),
          el("strong", { class: "card-title" }, e.name),
          el("p", { class: "card-body" }, e.location || "Address shown to registered guests"),
          el("p", { class: "card-source" }, "Luma · " + e.calendars.map(function (c) { return c.name; }).join(", ")),
        ]));
      });
    });
    [
      ["Communities", "data.js, with a source per card", "live"],
      ["Events", "public Luma calendars, luma.js", api.status.luma],
      ["Venues", "Supabase", api.status.supabase],
      ["Natural-language search", "Grok via /api/ask", api.status.grok],
      ["Comment references", "Cognee graph", api.status.cognee],
    ].forEach(function (row) {
      status.append(el("li", null, [
        el("span", null, [el("strong", null, row[0]), " · ", row[1]]),
        el("span", { class: /^(live|imported)/.test(row[2]) ? "state live" : "state" }, row[2]),
      ]));
    });
  }
})();
