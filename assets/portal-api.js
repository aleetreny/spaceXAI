/*
 * The only place the portal gets data from. Shapes follow docs/contracts.md.
 * Today it answers from mock data. To connect the API, replace each function
 * body with a fetch to the matching route and keep the return shape.
 *
 * Communities are real (data.js, with sources). Events are real, imported
 * from public Luma feeds into luma.js. Venues and comments are examples:
 * they are labelled as such and must not be read as facts.
 *
 * Add ?fail=grok or ?fail=cognee to any page to see the degraded states.
 */
(function () {
  const room = window.SAME_ROOM;
  const fail = new URLSearchParams(location.search).get("fail") || "";
  const checked = "2026-10-22";

  const exampleSource = {
    id: "example",
    label: "Example source. Replace with a public page.",
    url: null,
    checkedAt: checked,
  };

  const venues = [
    {
      id: "example-venue-a",
      kind: "venue",
      example: true,
      name: "Example Venue A",
      area: "Example area 1",
      capacity: 80,
      pricing: { type: "free", conditions: "Example condition: community events on weeknights" },
      availability: [],
      openingHours: "Example hours: Mon–Fri 09:00–22:00",
      av: "Example: projector, two mics",
      sources: [exampleSource],
    },
    {
      id: "example-venue-b",
      kind: "venue",
      example: true,
      name: "Example Venue B",
      area: "Example area 2",
      capacity: 120,
      pricing: { type: "on_request" },
      availability: [],
      openingHours: null,
      av: null,
      sources: [exampleSource],
    },
    {
      id: "example-venue-c",
      kind: "venue",
      example: true,
      name: "Example Venue C",
      area: "Example area 1",
      capacity: null,
      pricing: { type: "unknown" },
      availability: [],
      openingHours: null,
      av: null,
      sources: [exampleSource],
    },
    {
      id: "example-venue-d",
      kind: "venue",
      example: true,
      name: "Example Venue D",
      area: "Example area 3",
      capacity: 40,
      pricing: { type: "paid", amount: null, conditions: "Example: hourly rate on the venue page" },
      availability: [
        { startsAt: "Example: Thu 5 Nov 18:00", endsAt: "22:00", sourceId: "example", checkedAt: checked },
      ],
      openingHours: null,
      av: "Example: screen",
      sources: [exampleSource],
    },
  ];

  const comments = [
    {
      commentId: "example-c1",
      entityId: "example-venue-a",
      aspect: "noise",
      interpretation: "favorable",
      excerpt: "Example comment about noise. Replace with a real, authorised comment.",
      experiencedAt: "Example date",
    },
    {
      commentId: "example-c2",
      entityId: "example-venue-a",
      aspect: "noise",
      interpretation: "unfavorable",
      excerpt: "Example of a contradicting comment. Both stay visible.",
      experiencedAt: "Example date",
    },
    {
      commentId: "example-c3",
      entityId: "example-venue-b",
      aspect: "accessibility",
      interpretation: "mixed",
      excerpt: "Example comment about step-free access.",
      experiencedAt: "Example date",
    },
  ];

  const luma = window.SAME_ROOM_LUMA || { calendars: [], events: [], notFound: [] };
  const lumaChecked = luma.fetchedAt ? luma.fetchedAt.slice(0, 10) : null;
  const today = new Date().toISOString().slice(0, 10);

  function calendarFor(communityId) {
    return luma.calendars.find(function (c) { return c.communityId === communityId; }) || null;
  }

  const events = luma.events.map(function (e) {
    const calendars = luma.calendars.filter(function (c) { return e.calendarIds.indexOf(c.id) !== -1; });
    return {
      id: e.id,
      kind: "event",
      example: false,
      name: e.title,
      startsAt: e.startsAt,
      endsAt: e.endsAt,
      allDay: e.allDay,
      upcoming: e.startsAt.slice(0, 10) >= today,
      location: e.location,
      addressHidden: e.addressHidden,
      hosts: e.hosts,
      url: e.url,
      calendars: calendars,
      communityIds: calendars.map(function (c) { return c.communityId; }).filter(Boolean),
      sources: [{ id: e.id + "-luma", label: "Luma event page", url: e.url, checkedAt: lumaChecked }],
    };
  });

  function eventsOf(communityId) {
    return events.filter(function (e) { return e.communityIds.indexOf(communityId) !== -1; });
  }

  const communities = room.communities.map(function (c) {
    return {
      id: c.id,
      kind: "community",
      example: false,
      name: c.name,
      leads: c.leads,
      audience: c.focus,
      tags: c.tags,
      sources: [{ id: c.id + "-source", label: c.source, url: c.url || null, checkedAt: checked }],
      luma: calendarFor(c.id),
      lumaSearched: luma.notFound.indexOf(c.id) !== -1,
    };
  });

  // Past events stay reachable by id; search only lists upcoming ones.
  const all = communities.concat(venues, events);

  function wait(value) {
    return new Promise(function (resolve) {
      setTimeout(function () { resolve(value); }, 250);
    });
  }

  function text(entity) {
    return [entity.name, entity.area, entity.audience, entity.location,
      (entity.tags || []).join(" "), (entity.leads || []).join(" "), (entity.hosts || []).join(" "),
      (entity.calendars || []).map(function (c) { return c.name; }).join(" ")]
      .filter(Boolean).join(" ").toLowerCase();
  }

  function byId(id) {
    return all.find(function (e) { return e.id === id; }) || null;
  }

  function evidenceFor(ids, aspect) {
    if (fail === "cognee") return { status: "unavailable", graph: null };
    const hits = comments.filter(function (c) {
      return ids.indexOf(c.entityId) !== -1 && (!aspect || c.aspect === aspect);
    });
    if (!hits.length) return { status: "no_evidence", graph: null };
    return { status: "available", graph: { references: hits, example: true } };
  }

  function filter(params) {
    const q = (params.q || "").trim().toLowerCase();
    const kind = params.kind || "all";
    const minCapacity = Number(params.minCapacity) || 0;
    const freeOnly = Boolean(params.freeOnly);
    const words = q.split(/\s+/).filter(function (w) { return w.length > 1; }).map(function (w) {
      return new RegExp("\\b" + w.replace(/[^a-z0-9]/g, "").replace(/s$/, ""), "i");
    });

    const matches = [];
    const toConfirm = [];
    all.forEach(function (e) {
      if (kind !== "all" && e.kind !== kind) return;
      if (e.kind === "event" && !e.upcoming) return;
      // Events have their own tab; "All" without words would be only events.
      if (e.kind === "event" && kind === "all" && !words.length) return;
      if (words.length && !words.some(function (w) { return w.test(text(e)); })) return;
      const reasons = [];
      const unknown = [];
      if (e.kind === "venue") {
        if (minCapacity) {
          if (e.capacity == null) unknown.push("capacity");
          else if (e.capacity < minCapacity) return;
          else reasons.push("capacity_match");
        }
        if (freeOnly) {
          if (e.pricing.type === "unknown") unknown.push("pricing");
          else if (e.pricing.type !== "free") return;
          else reasons.push("documented_free_terms");
        }
      } else if (minCapacity || freeOnly) {
        return;
      }
      if (words.length) reasons.push("topic_match");
      const match = { entity: e, reasonCodes: reasons, unknownFields: unknown };
      (unknown.length ? toConfirm : matches).push(match);
    });
    return { matches: matches, toConfirm: toConfirm };
  }

  window.SameRoomAPI = {
    status: {
      mock: true,
      luma: luma.fetchedAt ? "imported " + lumaChecked : "not imported",
      supabase: "not connected",
      grok: fail === "grok" ? "down (simulated)" : "not connected",
      cognee: fail === "cognee" ? "down (simulated)" : "not connected",
    },

    discover: function (params) {
      const found = filter(params || {});
      return wait({
        mode: "filters",
        mock: true,
        matches: found.matches,
        toConfirm: found.toConfirm,
        warnings: [],
        evidenceStatus: "not_requested",
      });
    },

    // Mock of POST /api/ask. A real Grok call turns the message into the
    // same filters; this stub reads a few words so the screen can be shown.
    ask: function (message) {
      const lower = String(message || "").toLowerCase();
      const capacity = (lower.match(/(\d{2,4})\s*(people|personas|pax|guests)?/) || [])[1];
      const params = {
        q: (lower.match(/\b(ai|agents?|founders?|students?|grok|cursor|crypto|design|hackathons?|meetups?|london)\b/g) || []).join(" "),
        kind: /communit|comunidad/.test(lower) ? "community"
          : /venue|space|espacio|room|sala/.test(lower) ? "venue"
          : /event|hackathon|meetup|evento/.test(lower) ? "event" : "all",
        minCapacity: capacity ? Number(capacity) : 0,
        freeOnly: /free|gratis/.test(lower),
      };
      const aspect = /quiet|silent|silencio|noise|ruido/.test(lower)
        ? "noise"
        : /access|accesib|step-free/.test(lower) ? "accessibility" : null;
      const found = filter(params);
      const warnings = [];
      if (/today|tonight|tomorrow|thursday|jueves|next|próximo/.test(lower)) {
        warnings.push("Availability for that date is not documented. Ask the venue.");
      }
      if (fail === "grok") {
        warnings.unshift("Grok is unavailable. These are filter results, not an agent answer.");
        return wait({ mode: "filters", mock: true, understood: params, matches: found.matches, toConfirm: found.toConfirm, warnings: warnings, evidenceStatus: "not_requested" });
      }
      const ids = found.matches.concat(found.toConfirm).map(function (m) { return m.entity.id; });
      const evidence = aspect ? evidenceFor(ids, aspect) : { status: "not_requested", graph: null };
      if (evidence.status === "unavailable") warnings.push("Comment references are temporarily unavailable.");
      return wait({
        mode: "agent",
        mock: true,
        understood: Object.assign({ aspect: aspect }, params),
        matches: found.matches,
        toConfirm: found.toConfirm,
        warnings: warnings,
        evidenceStatus: evidence.status,
        evidenceGraph: evidence.graph,
      });
    },

    upcomingEvents: function (limit) {
      return wait(events.filter(function (e) { return e.upcoming; }).slice(0, limit || 6));
    },

    getEntity: function (id) {
      const entity = byId(id);
      if (!entity) return wait(null);
      const evidence = entity.kind === "venue" ? evidenceFor([id], null) : { status: "not_requested", graph: null };
      const related = entity.kind === "community" ? eventsOf(id) : [];
      return wait({
        entity: entity,
        evidenceStatus: evidence.status,
        evidenceGraph: evidence.graph,
        upcomingEvents: related.filter(function (e) { return e.upcoming; }),
        pastEventCount: related.filter(function (e) { return !e.upcoming; }).length,
      });
    },

    // Mock of POST /api/request-drafts. Returns text only; nothing is sent.
    draftRequest: function (id, requirements) {
      const entity = byId(id);
      if (!entity) return wait(null);
      const r = requirements || {};
      const lines = [
        "Hi " + (entity.leads ? entity.leads.join(" and ") : entity.name + " team") + ",",
        "",
        "We are planning " + (r.what || "a community event") + (r.people ? " for about " + r.people + " people" : "") + (r.when ? " on " + r.when : "") + ".",
        entity.kind === "venue"
          ? "Could you confirm availability, price and what the space includes?"
          : "Would " + entity.name + " be up for co-hosting?",
        "",
        "Thanks,",
        r.from || "[your name]",
      ];
      return wait({ draft: lines.join("\n"), sent: false, mock: true });
    },
  };
})();
