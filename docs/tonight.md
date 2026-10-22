# Plan para el freeze de esta noche

Escrito a las 20:42. Freeze: 21:50 según Luma, 21:15 según UK Hackathons y An Open Room. Confirmadlo en la sala y planificad para 21:15.

`architecture.md`, `contracts.md` y `team-plan.md` son la hoja de ruta para después del hackathon. Esta noche no se construye auth, RLS, moderación, revisiones, Cognee ni migraciones. En la demo se presentan como siguiente paso, no como integraciones.

## Qué se enseña

1. El desk actual: dos comunidades, página publicada. Ya funciona.
2. `discover.html`: unos pocos venues reales con fuente, filtrables sin servidor.
3. Si da tiempo y la clave de xAI funciona: una caja de texto que manda la consulta a Grok y muestra las tarjetas que devuelve, construidas desde `venues.js`.

Si a las 21:05 el paso 3 no funciona, se quita del HTML y se enseñan 1 y 2.

## Reparto

Ramas con estos nombres exactos para que pase `scripts/check_scope.py`. En T3, poned el nombre de rama al crear el worktree; las ramas `t3/...` no pasan el check.

| Rol | Rama | Archivos | Entrega |
| --- | --- | --- | --- |
| Data | `feature/catalog-data` | `venues.js`, `api/ask.js`, `vercel.json` | Venues y endpoint |
| Agente | `feature/discovery-agent` | `agent/ask.js` | Prompt y validación de Grok |
| Web | `feature/catalog-ui` | `discover.html`, `discover.js`, `event.html`, `app.js`, `styles.css` | Página de búsqueda y arreglo de notas |

## Contrato

`venues.js`, mismo patrón que `data.js`. Solo venues con página pública. Un campo sin fuente se omite, no se rellena.

```js
window.SAME_ROOM_VENUES = [
  {
    id: "slug",
    name: "…",
    area: "…",            // barrio, solo si la fuente lo dice
    capacity: null,       // número solo si la fuente lo dice
    pricing: "unknown",   // unknown | on_request | free | paid
    url: "https://…",
    source: "…",          // de dónde sale cada dato
  },
];
```

`agent/ask.js` exporta una función pura, sin red salvo la llamada a Grok:

```js
export async function ask({ message, venues, apiKey }) {
  // -> { ids: ["slug", ...], note: "…" }
  // ids filtrados contra venues; los desconocidos se descartan.
  // note: una frase; no afirma disponibilidad ni precio.
}
```

`api/ask.js` (función de Vercel) lee `XAI_API_KEY` del entorno, importa `venues.js` y `agent/ask.js`, y responde `POST { message }` con `{ ids, note }`. La clave nunca va al navegador.

`discover.js` pinta las tarjetas desde `venues.js` con los `ids`, no desde el texto de Grok. `pricing: unknown` se muestra como "Precio por confirmar"; nunca hay disponibilidad.

## Arreglo en `event.html` (web)

El parámetro `notes` de la URL se muestra como "What members actually said", y cualquiera puede escribir esa URL. Cambiad el título a "Pasted on the desk — not verified".

## Horas

- 20:55: data sube `venues.js`. Web ya puede pintar.
- 21:05: decidir si Grok entra o no.
- 21:10: merge a `main`, probar en `python3 -m http.server 4321` y en el deploy.
