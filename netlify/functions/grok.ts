const MODEL = "grok-4.7";
const MAX_BODY = 32_000;
const MAX_MESSAGES = 8;
const MAX_CONTENT = 4_000;
const MAX_COMPLETION_TOKENS = 600;

type ChatMessage = {
  role: "system" | "user" | "assistant";
  content: string;
};

declare const Netlify: {
  env: { get(name: string): string | undefined };
};

function json(status: number, body: unknown) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

function readKey() {
  if (typeof Netlify === "undefined" || !Netlify.env) return "";
  return String(Netlify.env.get("XAI_API_KEY") || "").trim();
}

function parseMessages(body: unknown): ChatMessage[] | null {
  if (!body || typeof body !== "object") return null;
  const messages = (body as { messages?: unknown }).messages;
  if (!Array.isArray(messages) || messages.length === 0 || messages.length > MAX_MESSAGES) {
    return null;
  }
  const clean: ChatMessage[] = [];
  for (const item of messages) {
    if (!item || typeof item !== "object") return null;
    const role = (item as { role?: unknown }).role;
    const content = (item as { content?: unknown }).content;
    if (role !== "system" && role !== "user" && role !== "assistant") return null;
    if (typeof content !== "string" || !content.trim() || content.length > MAX_CONTENT) return null;
    clean.push({ role, content });
  }
  return clean;
}

export default async (req: Request) => {
  if (req.method !== "POST") return json(405, { error: "Method not allowed" });

  const key = readKey();
  if (!key) return json(503, { error: "XAI_API_KEY is not set on the server." });

  let raw = "";
  try {
    raw = await req.text();
  } catch {
    return json(400, { error: "Expected JSON with a messages array." });
  }
  if (raw.length > MAX_BODY) return json(413, { error: "Body too large." });

  let payload: unknown;
  try {
    payload = JSON.parse(raw);
  } catch {
    return json(400, { error: "Expected JSON with a messages array." });
  }

  const messages = parseMessages(payload);
  if (!messages) {
    return json(400, { error: "messages must be 1–8 objects with role and content." });
  }

  let upstream: Response;
  try {
    upstream = await fetch("https://api.x.ai/v1/chat/completions", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        authorization: `Bearer ${key}`,
      },
      body: JSON.stringify({
        model: MODEL,
        messages,
        stream: false,
        max_completion_tokens: MAX_COMPLETION_TOKENS,
      }),
    });
  } catch {
    return json(502, { error: "Grok did not respond." });
  }

  const text = await upstream.text();
  return new Response(text, {
    status: upstream.status,
    headers: {
      "content-type": upstream.headers.get("content-type") || "application/json; charset=utf-8",
    },
  });
};

export const config = {
  path: "/api/grok",
  method: ["POST"],
};
