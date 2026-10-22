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
          "Venues and comments are examples. Communities are real, with sources. Supabase, Grok and Cognee are not connected yet.",
        ])
      : null;
    document.body.prepend(header, banner || "");
  }

  window.SameRoomUI = {
    el: el,
    clear: clear,
    param: param,
    pricingLabel: pricingLabel,
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
    [
      ["Communities", "data.js, with a source per card", "live"],
      ["Venues", "Supabase", api.status.supabase],
      ["Natural-language search", "Grok via /api/ask", api.status.grok],
      ["Comment references", "Cognee graph", api.status.cognee],
    ].forEach(function (row) {
      status.append(el("li", null, [
        el("span", null, [el("strong", null, row[0]), " · ", row[1]]),
        el("span", { class: row[2] === "live" ? "state live" : "state" }, row[2]),
      ]));
    });
  }
})();
