# Same Room

Mesa de collab para el [Grok Bot Community Engineering London Hackathon](https://luma.com/eveur09a) (hoy, 22 oct 2026, Expedite, 7 Lyric Square). Eliges dos comunidades de la sala y publicas la página del evento.

Repo: https://github.com/aleetreny/spaceXAI

## Arrancar

```bash
python3 -m http.server 4321
```

Abre http://127.0.0.1:4321

No hace falta Node. La página publicada es `event.html` con la pareja, la idea y las notas en la URL, así se puede enseñar sin backend.

## Demo de 3 minutos

1. La sala ya está cargada: las comunidades y los leads del listado de Luma. Outpost × Hackradar viene marcado.
2. Lee el motivo. Sale de descripciones públicas, no de una bio inventada.
3. Pulsa **Use this idea**. El título de la hoja cambia.
4. Si tienes una frase real de un miembro, pégala. Si no, deja el campo vacío: la página enseña preguntas, no citas falsas.
5. **Publish live page**. Esa es la URL que se enviaría a los dos leads, con la siguiente acción y las fuentes.

## Qué puntúa esto

| Criterio del jurado | Dónde está |
| --- | --- |
| Ejecución | La hoja y la página pública salen de la misma pareja, sin servidor. |
| Grok Bot y Cursor | El contexto del evento está en este repo (`data.js`, `AGENTS.md`) para que el agente no se lo invente. |
| Contexto de comunidad | Cada ficha cita una fuente. Lo que no está publicado se dice. |
| 10x–20x | De un hilo de mensajes a una página con hosts, fecha y siguiente acción, antes de salir del edificio. |
| Útil de verdad | Los nombres de la hoja son los leads que están en la sala. |
| Demo | Un clic, una URL, una hoja que se puede imprimir. |

## Horario

En Luma: puertas 18:00, kickoff 18:05, hacking 18:10, cena 18:15, **code freeze 21:50**, top 5 a las 22:20 (3 min), premios 22:45, cierre 23:00.

UK Hackathons y An Open Room adelantan el freeze a **21:15** y las demos a las 21:45. Confírmalo en la sala. El aviso también está en la cabecera de la app.

Equipos de hasta 5. Premios: 3 / 2 / 1 mes de Cursor Ultra por persona, más créditos de Supabase.

## Tracks

Se anuncian en la sala. El brief público pide tooling de comunidades: captación, collab entre comunidades, el event stack, activación a partir de lo que dicen los miembros, o una idea que llega a página publicada. Same Room cubre collab, event stack y un hueco honesto para la activación.

## Sponsors, sin fingir la integración

- **Supabase** (Isabelle Roser): esquema listo en `supabase/schema.sql`. Pégalo en el SQL editor cuando haya proyecto. La demo no depende de ello.
- **Cognee** (Veljko Kovac): el bloque "Memory used" de la página publicada es la memoria local, con cita. Ahí se sustituye por una query a Cognee cuando haya clave.
- **Zero** (Mariia Nedelkina, zero.inc): la "Next action" es la fila de CRM (a quién escribir y qué). No hay llamada a su API.
- **SpaceXAI / Grok Bot** y **Cursor**: el contexto estable está en `AGENTS.md` para que el agente siga construyendo sin inventar comunidades.

## Datos

Las fichas salen del listado de Luma de esta noche. El texto largo solo entra si hay una página pública que lo respalde (Outpost, Hackradar, Unicorn Mafia, Corgi, Kickstart, el cruce público de basedcollective). Zakee Abdi figura como lead adicional, sin comunidad asignada. Un agregador también nombra a Fergus McKenzie-Wilson en Unicorn Mafia; Luma solo lista a Charlie Cheesman, así que la ficha sigue a Luma.
