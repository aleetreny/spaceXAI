# Contrato de catálogo y agente

Estado: especificación conceptual v0 para coordinar implementación. No es una API desplegada. Los ejemplos describen consultas, no venues ni testimonios reales.

## Uso antes de implementación

Operaciones públicas propuestas:

```text
GET /api/discover?q=...&kind=venue|community|all&cursor=...
POST /api/ask { message, timezone: "Europe/London" }
POST /api/request-drafts { entityId, requirements }
```

`discover` busca con filtros y paginación. `ask` interpreta lenguaje natural y llama a la misma búsqueda. `request-drafts` devuelve texto sin guardar ni enviar. La hora actual la aporta el servidor. Una fecha ambigua devuelve una aclaración y no una disponibilidad supuesta.

Operaciones autenticadas propuestas:

```text
POST /api/venues { fields, sources, operationId }
PATCH /api/venues/:id { fields, sources, expectedRevision }
PATCH /api/communities/:id { fields, sources, expectedRevision }
POST /api/collaborations { communityIds, venueId?, proposal, operationId }
```

Crear o editar requiere organizador aprobado y permiso sobre la entidad. La asignación inicial la realiza una operación de confianza, nunca un campo controlado por el cliente. `operationId` es único por actor y operación. Repetir el mismo cuerpo devuelve el mismo resultado; reutilizar la clave con otro cuerpo produce conflicto. Una revisión antigua devuelve conflicto sin sobrescribir.

## Forma de los datos

Las firmas son pseudocódigo, no tipos compilados:

```text
Source = { id, label, url?, checkedAt, contributedBy? }
Fact = { id, entityId, field, value, sourceId, revision }
Pricing = unknown | on_request | free{conditions} | paid{amount?, currency?, conditions}
Availability = unknown | confirmed{startsAt, endsAt, sourceId, checkedAt}
Venue = { id, name, location?, capacity?, av?, openingHours?, pricing,
          availability[], publicContactUrl?, factIds[], revision }
Community = { id, name, audience?, size?, activities?, publicContactUrl?,
              factIds[], revision }
HostedAt = { communityId, venueId, eventId?, sourceId }
Match = { entityId, kind, factIds[], reasonCodes[], unknownFields[], revision }
DiscoveryResult = { mode: agent|filters, matches[], sources[], nextCursor?,
                    clarification?, warnings[],
                    evidenceStatus: available|no_evidence|not_requested|unavailable,
                    evidenceGraph? }
```

Cada campo factual publicado debe poder enlazarse con un `Fact` y su fuente. Un campo sin fuente queda ausente. Los contactos privados no forman parte de estos objetos. Las cantidades no se extraen de textos que describen otra métrica.

`reasonCodes` pertenece a un conjunto cerrado: `capacity_match`, `area_match`, `topic_match`, `documented_free_terms`, `documented_host_relation`. La API verifica cada código contra los hechos actuales. El modelo propone IDs; el servidor comprueba que existan y sean públicos. Las tarjetas leen los valores canónicos y construyen las explicaciones mediante plantillas.

`pricing=on_request` no satisface un filtro estricto de gratis. Un venue de precio desconocido puede aparecer aparte como alternativa por confirmar. Sin evidencia de disponibilidad del intervalo solicitado, la tarjeta dice "por confirmar", incluso cuando encaja en los horarios habituales.

## Almacenamiento propuesto

Supabase contiene `venues`, `communities`, `facts`, `sources`, `hosted_at`, `venue_availability`, `organisers`, `entity_editors`, `vouches` y `audit_log`. Los contactos privados van en una tabla separada y restringida. Las publicaciones persistidas se distinguen de los borradores de URL existentes.

Los nombres son propuestas para la primera migración, no tablas ya creadas. `communities` y `events` existentes requieren una migración compatible; no se descartan sus IDs ni su contenido.

La ingestión identifica registros por `(provider, external_id)` y conserva la procedencia. Una repetición actualiza el registro en vez de duplicarlo. El MVP consulta el historial mediante relaciones en Supabase, sin depender de Cognee.

## Contrato del grafo de comentarios

Operaciones autenticadas propuestas:

```text
POST /api/comments { entityId, body, sourceId, experiencedAt?, operationId }
PATCH /api/comments/:id { body, expectedRevision }
POST /api/comments/:id/moderation { decision, expectedRevision }
```

Un organizador aprobado aporta y edita sus comentarios; no puede hacerse pasar por otro autor ni publicar o moderar por su cuenta. El moderador autoriza publicación o retirada. Un comentario puede referirse a un venue o comunidad ajena sin conceder permisos de edición sobre su ficha. La indexación solo consume comentarios publicados y autorizados para uso público.

Contrato conceptual de lectura e indexación, no funciones ya implementadas:

```text
Comment = { id, entityId, body, sourceId, experiencedAt?, createdAt,
            publicationStatus: pending|published|withdrawn, revision }
EvidenceReference = { commentId, revision, sourceId, excerpt, experiencedAt? }
EvidenceNode = { id, kind: venue|community|comment|aspect, label }
EvidenceEdge = { from, to, relation: about|mentions,
                 interpretation?: favorable|unfavorable|mixed|unclear,
                 references[] }
EvidenceGraph = { nodes[], edges[] }
searchCommentEvidence({ candidateIds?, entityKind, aspect, query, limit })
  -> { status: available|no_evidence|unavailable, graph: EvidenceGraph }
indexPublishedComment(commentId, revision) -> processing|indexed|failed
```

`evidenceStatus` informa si la búsqueda se realizó, no tuvo evidencia, no se solicitó o falló. `evidenceGraph` solo contiene nodos y relaciones autorizados para la consulta. Las interpretaciones extraídas se muestran como tales, no como hechos confirmados ni como una medida objetiva de silencio.

Supabase añade `comments` y trabajos de indexación al modelo propuesto. Guarda autoría y moderación fuera de la proyección pública del agente; la autoría solo se expone con permiso. La identidad para idempotencia del trabajo es comentario y revisión. Cada fragmento debe existir en el original vigente y respaldar la relación mostrada. Si no se puede comprobar, se descarta. La API aplica visibilidad y revisión antes de devolver cualquier nodo o relación, incluidos los conectados indirectamente. Las relaciones sin evidencia válida se excluyen.

Los comentarios contradictorios conservan sus referencias, fechas y contexto. `no_evidence` no se convierte en una valoración negativa. El grafo no cambia capacidad, precio, disponibilidad ni permisos. Al retirar un comentario se bloquea inmediatamente su recuperación pública y se programa la limpieza del grafo.

## Matriz mínima de acceso

- Visitante: lee fichas publicadas y usa el chat. No escribe ni lee contactos privados.
- Usuario autenticado sin aprobación: mismo catálogo público; puede solicitar aprobación.
- Organizador aprobado: edita sus entidades asignadas. No cambia aprobación ni asignaciones propias.
- Administrador: aprueba, revoca y asigna editores con registro de auditoría.
- Agente: solo lee la proyección pública. No dispone de credenciales administrativas.

La autorización vive en la base y en las entradas de servidor. Ocultar botones no concede protección. La ruta pública valida tamaños, paginación y frecuencia para limitar consumo de créditos.
