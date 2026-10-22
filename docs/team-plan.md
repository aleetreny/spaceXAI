# Trabajo entre tres personas y sus agentes

Este plan prepara tareas para GitHub. Los responsables personales se asignan cuando el equipo facilite sus usuarios. Cada persona trabaja con su agente en una rama y checkout propios, desde el mismo commit base.

## Primera entrega compartida

Lean [la arquitectura](architecture.md), [el contrato](contracts.md) y `AGENTS.md`. Conviertan los objetos del contrato en ejemplos verificables con datos reales y fuentes. Resuelvan cambios del contrato antes de que cada rama implemente una forma distinta.

El primer recorrido es añadir dos venues reales, consultarlos sin cuenta, mostrar fuentes y preparar una solicitud. El calendario agregado y `.ics` siguen después. El aviso de freeze 21:50 frente a 21:15 permanece visible.

## Persona A: web y experiencia

Rama propuesta: `feature/catalog-ui`. Archivos propios: `discover.*`, `organiser.*`, `styles.css` y cambios de integración en `app.js`, `index.html` y `event.html`.

Prompt para su agente:

> Lee AGENTS.md y docs/. Implementa el catálogo público, el chat web y la edición de fichas según contracts.md. Conserva el recorrido de dos comunidades a página compartible. Usa solo datos con fuente; muestra estados vacíos y errores de conexión. Si usas respuestas de prueba, no las presentes como datos reales. Separa disponibilidad confirmada de horarios y precio desconocido de gratis. No añadas claves al cliente. Coordina cualquier cambio de contrato mediante la PR. No cambies SQL ni la implementación del agente.

Se acepta cuando un visitante busca, abre fuentes y llega al borrador; un organizador ve sus formularios autorizados. La web permite aportar comentarios y muestra fragmentos, fechas, contradicciones y referencias del subgrafo recuperado, con estados sin evidencia o servicio no disponible. En móvil se puede completar el recorrido. El escritorio original y su aviso de horario siguen funcionando.

## Persona B: base de datos, permisos y API

Rama propuesta: `feature/catalog-data`. Archivos propios: `supabase/`, `api/`, importación en `scripts/` y configuración del despliegue API.

Prompt para su agente:

> Lee AGENTS.md y docs/. Implementa el contrato sobre Supabase con datos reales, PostGIS y autorización por entidad. Conserva los IDs de comunidades. Reemplaza la política de escritura anónima antes de habilitar la base. Aísla los contactos privados de la proyección pública y del agente. Implementa comentarios con autoría, permiso de publicación y moderación, además de revisiones de edición, creación idempotente y trabajos de indexación por comentario y revisión. Entrega pruebas de acceso directo para visitante, usuario pendiente, editor propio, editor ajeno y administrador. Documenta cómo arrancar y desplegar la API. No cambies la UI ni agent/.

Se acepta cuando dos organizadores aprobados guardan venues con fuentes y un tercero los consulta. Las llamadas directas no permiten autoaprobarse, editar entidades ajenas ni obtener contactos privados. Repetir una importación o publicación no duplica registros.

## Persona C: agente y evaluación

Rama propuesta: `feature/discovery-agent`. Archivos propios: `agent/` y evaluación del agente.

Prompt para su agente:

> Lee AGENTS.md y docs/. Implementa un servicio invocable por api/ que interprete consultas con Grok y consulte el catálogo público y sus relaciones en Supabase. Devuelve el contrato de DiscoveryResult y valida IDs, revisiones y visibilidad. Integra Cognee como grafo de comentarios sobre venues y comunidades mediante searchCommentEvidence. Indexa solo comentarios publicados y devuelve un subgrafo acotado con fragmentos originales y revisiones verificadas en Supabase. Conserva evidencia contradictoria y separa experiencias subjetivas de los datos confirmados. Si falla Cognee, conserva la búsqueda estructurada y declara que las referencias no están disponibles. No permitas que el modelo escriba fichas, conceda permisos, reserve o envíe mensajes. Las razones factuales salen de campos canónicos y plantillas. Prueba consultas sin resultados, fechas ambiguas, precio desconocido, disponibilidad ausente y caídas de proveedor. Sin proveedor, devuelve búsqueda por filtros identificada. No cambies la UI ni las políticas SQL.

Se acepta cuando consultas de venues y comunidades devuelven entidades reales y fuentes. Una instrucción maliciosa en una ficha no cambia permisos ni activa herramientas no autorizadas. El contexto enviado a Grok excluye contactos privados. Las bajas y revisiones se respetan en cada consulta.

Esta persona entrega el grafo de comentarios descrito en architecture.md con textos reales autorizados. Prueba búsqueda por ruido en venues y por actividades en comunidades, evidencia contradictoria, ausencia de comentarios, modificación y retirada de fuentes, y caída del servicio. Compara la recuperación con Grok leyendo esos mismos textos. El catálogo debe funcionar aunque el grafo esté indisponible.

## Integración y revisión

1. La persona B fija la forma ejecutable del contrato y el arranque de API en una PR pequeña. Las demás ramas desarrollan contra ese contrato mientras se completa la infraestructura.
2. Cada persona abre una PR con alcance, instrucciones de arranque y evidencia del recorrido que funciona. Otra persona revisa antes de integrar.
3. La persona A conecta la web con API. La persona B conecta `api/` con el servicio de `agent/` entregado por C. Se verifica búsqueda con y sin proveedores.
4. El equipo ejecuta la demo con dos venues reales y tres organizadores. La solicitud se copia como borrador; no se afirma que fue enviada.
5. Después se integran eventos, ranking con razones e `.ics`. Se actualiza README para distinguir funciones activas de pendientes.

Los agentes no editan la misma rama ni comparten archivos de secretos. Cada PR declara cambios de contratos. El repositorio debe tener licencia MIT, Apache-2.0 o AGPL-3.0 antes de entregarlo. No hay una licencia todavía; el equipo debe elegirla y comprobar derechos sobre el contenido importado.

## Evidencia para cerrar la demo

- Enlaces de las dos fichas reales y sus fuentes, introducidas por organizadores aprobados.
- Consulta pública que devuelve esas fichas con condiciones por confirmar.
- Rechazo de escritura sin aprobación y de edición ajena, también por acceso directo.
- Respuesta del agente sin entidades ni hechos inventados; fuente visible en cada tarjeta.
- Comentarios reales de venues y comunidades recuperados a través de Cognee, con subgrafo y fragmentos comprobables.
- Retirada de un comentario que impide recuperar su evidencia, y búsqueda estructurada operativa con Cognee caído.
- Captura de un contexto del modelo que no contiene contactos privados.
- Recorrido original de comunidades a página compartible conservado.
- Para la entrega completa del track: importación viva, ranking explicado y suscripción `.ics` comprobada.
