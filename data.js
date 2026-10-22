/* Public facts checked 22 Oct 2026. Do not extend a bio to fill a gap. */
(function () {
  const communities = [
    {
      id: "unicorn-mafia",
      name: "Unicorn Mafia",
      leads: ["Charlie Cheesman"],
      focus: "Developer community of 1,000+ engineers across the EU and US.",
      tags: ["engineers", "hackathons", "europe"],
      url: "https://www.charliecheesman.net/about/",
      source: "charliecheesman.net/about",
    },
    {
      id: "basedcollective",
      name: "basedcollective",
      leads: ["Fatema Al Khalifa"],
      focus:
        "The listed lead has hosted in London with Corgi and previously organised with Unicorn Mafia.",
      tags: ["london", "events"],
      url: "",
      source: "Luma listing, plus Fatema Al Khalifa's public post on 25 Aug 2026",
    },
    {
      id: "kickstart-global",
      name: "Kickstart Global",
      leads: ["Ilya Vencjuns"],
      focus:
        "Described publicly as the UK’s largest cross-university incubator, with 100+ startups built and £33M+ raised.",
      tags: ["students", "startups", "universities"],
      url: "",
      source:
        "Lead from the Luma listing. Incubator description from Claudia Maggi's public profile of her Kickstart fellowship.",
    },
    {
      id: "hackradar",
      name: "Hackradar",
      leads: ["Keanu Czirjak"],
      focus:
        "Hackathons, CTFs and internships in one feed, pulled from group chats, Luma calendars and Discords.",
      tags: ["hackathons", "students", "discovery", "events"],
      url: "https://hackradar.tech/",
      source: "hackradar.tech",
    },
    {
      id: "ai-agents-lab",
      name: "AI Agents Lab",
      leads: ["May Yu", "Minghan Xiao"],
      focus: "Community partner tonight. No public one-line beyond the name and the leads.",
      tags: [],
      url: "",
      source: "Luma listing for this hackathon",
    },
    {
      id: "corgi",
      name: "Corgi Community",
      leads: ["Claudia Maggi"],
      focus: "London community, cafe launch, partnerships and events for Corgi.",
      tags: ["london", "events", "partnerships"],
      url: "",
      source: "Claudia Maggi's public role: Community Lead at Corgi",
    },
    {
      id: "night-office",
      name: "Night Office",
      leads: ["Oli Kingshott", "Shreyas Raghu"],
      focus: "Community partner tonight. No public one-line checked for this page.",
      tags: [],
      url: "",
      source: "Luma listing for this hackathon",
    },
    {
      id: "hack-collective",
      name: "The Hack Collective",
      leads: ["Louis Le"],
      focus: "Louis Le is listed as lead, and as a host of tonight’s hackathon.",
      tags: ["hackathons", "events"],
      url: "https://luma.com/eveur09a",
      source: "SpaceXAI community calendar and the Luma listing",
    },
    {
      id: "united-italian-societies",
      name: "United Italian Societies",
      leads: ["Umberto Belluzzo"],
      focus: "Community partner tonight, led by Umberto Belluzzo.",
      tags: [],
      url: "",
      source: "Luma listing for this hackathon",
    },
    {
      id: "outpost",
      name: "Outpost",
      leads: ["Andy Tyler", "Oscar Falemara"],
      focus:
        "Community for founders, engineers and operators: high-signal events, hackathons, dinners and shared spaces.",
      tags: ["founders", "engineers", "operators", "hackathons", "events"],
      url: "https://outpostcrew.co",
      source: "Outpost’s own description on the Daytona HackSprint Luma page",
    },
    {
      id: "ai-pilled",
      name: "AI Pilled",
      leads: ["Nuan Zhang", "Yiran Qin"],
      focus: "Community partner tonight. No public one-line checked for this page.",
      tags: [],
      url: "",
      source: "Luma listing for this hackathon",
    },
  ];

  const pairs = {
    "hackradar|outpost":
      "Outpost already runs the high-signal rooms. Hackradar already watches the hackathons everyone else hears about late. The next event can be on the feed before the group chats fill up.",
    "kickstart-global|unicorn-mafia":
      "Unicorn Mafia is a large engineer community. Kickstart turns student teams into companies. The collab is a room where those teams meet engineers who have shipped.",
    "outpost|unicorn-mafia":
      "A large engineer community and a smaller crew of founders and operators. One event can use both lists instead of two separate invites.",
    "hackradar|kickstart-global":
      "Kickstart’s teams need the next hackathon. Hackradar already collects them. The event is that filter, in person.",
    "basedcollective|corgi":
      "These leads have already shared a London event. This page is the next one, with the run of show written down.",
    "basedcollective|unicorn-mafia":
      "The listed leads already sit across both rooms. Fatema has organised with Unicorn Mafia and with Corgi. The page makes the next overlap explicit.",
    "hack-collective|hackradar":
      "Louis Le is hosting tonight with Keanu Czirjak. Hackradar is Keanu’s feed. The collab page is the artefact of a room they are already in.",
  };

  const ideas = {
    "hackradar|outpost":
      "Put the next high-signal hackathon on the feed before it sells out",
    "kickstart-global|unicorn-mafia":
      "An evening where Kickstart teams meet Unicorn Mafia engineers",
    "basedcollective|corgi": "The next London night, written down this time",
  };

  const questions = {
    hackathons: "Which hackathon did people almost skip, and what made them come?",
    students: "Who would a member bring if the next one was obviously for them?",
    founders: "Which room last month was worth leaving the company for?",
    events: "What did people stay for after the programme ended?",
    engineers: "What did members ask for that never became an event?",
    discovery: "Which event did members hear about only after it sold out?",
    startups: "Which intro last month turned into work, and which was noise?",
    operators: "What broke last time the two communities shared a room?",
    partnerships: "Which partner would the members actually notice?",
    london: "Which weeknight can both communities actually fill?",
  };

  const gathers = new Set(["students", "discovery", "universities"]);
  const hosts = new Set(["events", "hackathons", "founders", "operators"]);

  function byId(id) {
    return communities.find((community) => community.id === id) || null;
  }

  function key(a, b) {
    return [a.id, b.id].sort().join("|");
  }

  function shared(left, right) {
    const rightSet = new Set(right);
    return left.filter((tag) => rightSet.has(tag));
  }

  function reasonFor(a, b) {
    const written = pairs[key(a, b)];
    if (written) return written;
    const overlap = shared(a.tags, b.tags);
    if (overlap.length) {
      return "Shared ground: " + overlap.join(", ") + ". The page is that overlap, with a date on it.";
    }
    const aGathers = a.tags.some((tag) => gathers.has(tag));
    const bGathers = b.tags.some((tag) => gathers.has(tag));
    const aHosts = a.tags.some((tag) => hosts.has(tag));
    const bHosts = b.tags.some((tag) => hosts.has(tag));
    if ((aGathers && bHosts) || (bGathers && aHosts)) {
      return "One side already gathers people. The other already runs rooms. The page is the collab, not another group chat.";
    }
    return "Both leads are in this room tonight. Public pages don’t show a programme overlap yet, so the case is that they are here.";
  }

  function questionsFor(a, b) {
    const overlap = shared(a.tags, b.tags);
    const rest = a.tags.concat(b.tags).filter(function (tag) {
      return overlap.indexOf(tag) === -1;
    });
    const tags = Array.from(new Set(overlap.concat(rest)));
    const lines = [];
    tags.forEach((tag) => {
      if (questions[tag] && lines.length < 3) lines.push(questions[tag]);
    });
    if (!lines.length) {
      lines.push("What did members ask for the last time these two communities were in the same week?");
    }
    return lines;
  }

  function joinNames(names) {
    if (names.length <= 1) return names.join("");
    if (names.length === 2) return names[0] + " and " + names[1];
    return names.slice(0, -1).join(", ") + ", and " + names[names.length - 1];
  }

  function invitesFor(a, b) {
    const tags = a.tags.concat(b.tags);
    return communities
      .filter(function (community) {
        return community.id !== a.id && community.id !== b.id;
      })
      .map(function (community) {
        return { community: community, overlap: shared(community.tags, tags) };
      })
      .sort(function (left, right) {
        if (right.overlap.length !== left.overlap.length) {
          return right.overlap.length - left.overlap.length;
        }
        return left.community.name.localeCompare(right.community.name);
      })
      .slice(0, 5);
  }

  function draft(a, b, idea) {
    const title = idea.trim() || a.name + " × " + b.name;
    const leads = a.leads.concat(b.leads);
    return {
      title,
      reason: reasonFor(a, b),
      questions: questionsFor(a, b),
      invites: invitesFor(a, b),
      suggestion: ideas[key(a, b)] || a.name + " × " + b.name + ": one night, one page",
      nextAction:
        "Send this page to " +
        joinNames(leads) +
        ". Agree a date before you leave Lyric Square.",
      hosts: leads,
      sources: [
        { name: a.name, source: a.source, url: a.url },
        { name: b.name, source: b.source, url: b.url },
      ],
    };
  }

  window.SAME_ROOM = {
    communities,
    byId,
    draft,
    extraLead: "Zakee Abdi",
    eventUrl: "https://luma.com/eveur09a",
    repoUrl: "https://github.com/aleetreny/spaceXAI",
  };
})();
