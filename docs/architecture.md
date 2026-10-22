# Arquitectura de venues y comunidades

Estado: diseño para implementar, 22 octubre 2026. Sponsors confirmados por el equipo: créditos de Grok, Supabase, Cognee y Notion. El acceso concreto y el hosting siguen pendientes. Este documento no acredita ninguna integración activa.

La web propia es la interfaz pública del producto. El equipo ha decidido prescindir de Notion; disponer de acceso al sponsor no obliga a integrarlo.

## Problema y uso

Cualquier visitante puede buscar comunidades y espacios en lenguaje natural. Solo los organizadores aprobados pueden mantener fichas. La demo central consiste en que dos organizadores añadan venues reales y un tercero encuentre uno y prepare una solicitud.

Ejemplo de consulta, no un resultado real: "Busco un espacio gratis para 80 personas cerca de Old Street el próximo jueves". La respuesta presenta coincidencias documentadas, fuentes y condiciones por confirmar. Tener horario de jueves no confirma disponibilidad para ese jueves.

El visitante puede escoger dos comunidades y continuar al escritorio actual para crear una página compartible. Las solicitudes son borradores para copiar. El envío requiere un flujo posterior explícito.

## Cómo funciona el prototipo actual

`data.js` contiene las comunidades con sus fuentes y el motor determinista de colaboración. Expone `window.SAME_ROOM`. `app.js` renderiza el escritorio de `index.html` y la página de `event.html`. Los borradores viven en `sessionStorage`; la página se comparte mediante parámetros de URL. No hay servidor de aplicación, login ni llamadas a sponsors.

`supabase/schema.sql` es un esquema de partida sin conexión demostrada. Incluye una política `anon insert events` que debe sustituirse antes de habilitar escrituras remotas. El esquema actual no cumple el modelo de organizadores aprobados.

## Forma elegida

Se conserva la web estática y se añaden páginas de descubrimiento y edición, una API de servidor y Supabase. Las rutas existentes siguen disponibles con `python3 -m http.server 4321`. Las funciones conectadas requieren además el servidor API, cuyo hosting se elige según el acceso del equipo.

- Web propia: catálogo, filtros, chat público, fichas, fuentes y formulario de organizador. Las fichas y páginas compartibles se consultan en esta web.
- Supabase: datos canónicos, autenticación, permisos por fila y búsquedas geográficas con PostGIS.
- Grok: interpreta la consulta y selecciona identificadores sobre resultados autorizados. Las claves permanecen en el servidor.

Grok usa herramientas de lectura como `searchVenues`, `searchCommunities` y `getPublicFacts`. La API valida filtros, límites, identificadores y revisiones. Las tarjetas muestran datos de la base, no afirmaciones factuales redactadas libremente por el modelo. Una cita válida por sí sola no demuestra que una frase sea verdadera.

Supabase también resuelve quién organizó cada evento y en qué espacio, mediante relaciones y procedencia. Este historial y sus citas no requieren Cognee. Si falla Grok, queda disponible la búsqueda por filtros, identificada como tal.

## Cognee como ampliación opcional

Cognee queda fuera de las dependencias del MVP. Las fichas actuales son breves y estructuradas; todavía no se ha demostrado un caso que necesite recuperación sobre textos desordenados.

Una ampliación acotada sería "Qué conviene preguntar antes de reservar". Después de buscar venues, recuperaría fragmentos de descripciones y notas reales de organizadores para sugerir preguntas específicas. Cada fragmento conservaría texto original, autor o procedencia, fecha y permiso de publicación en Supabase. Una experiencia pasada no se convertiría automáticamente en una característica permanente, precio o disponibilidad.

Solo se incorpora después de completar la demo principal, disponer de textos reales autorizados y comparar unas cinco consultas con Grok leyendo esos mismos textos directamente. Debe mostrar una mejora visible al recuperar evidencia pertinente. Con pocos documentos, la lectura directa puede bastar.

Estimación de esfuerzo adicional, no medición: 30–60 minutos para verificar acceso y probar recuperación; 4–8 horas-persona en total para una integración acotada, suponiendo catálogo y API operativos y un servicio Cognee accesible. Incluye ingestión, recuperación, bloque web, validación de fuentes y pruebas de fallo. Un despliegue propio quedaría fuera del alcance de esta hackathon. El coste monetario depende del plan, los créditos y el procesamiento; no está verificado.

Si se incorpora, Cognee devuelve contexto e identificadores de documentos. El servidor verifica revisión, visibilidad y respaldo del fragmento en Supabase antes de mostrarlo. La memoria se invalida al retirar o modificar una fuente. No decide permisos, precio ni disponibilidad. Si falla, se omite el bloque y funciona la búsqueda principal. No se envían contactos privados ni conversaciones sin autorización.

Los plugins de memoria de desarrollo instalados no integran la web. No se ha comprobado conectividad ni credenciales de la API. El MVP no requiere configurarlas.

## Datos y confianza

Los modelos y operaciones se definen en [el contrato](contracts.md). Cada dato público tiene procedencia y fecha de comprobación. Un valor ausente sigue siendo desconocido. El contacto público debe estar autorizado para publicación; los contactos privados viven en una tabla separada sin acceso desde el catálogo ni desde el agente.

Una relación comunidad–venue significa que existe evidencia de un evento allí. Una recomendación del agente no crea esa relación. El tamaño de comunidad tampoco se deduce de los asistentes de un evento.

El primer administrador aprueba manualmente a los organizadores iniciales. Un organizador puede avalar una solicitud de otro, pero el aval no concede permisos automáticamente. Las escrituras requieren aprobación vigente y permiso sobre la entidad concreta. Los clientes no pueden cambiar su propia aprobación ni sus asignaciones. Las ediciones usan una revisión esperada para detectar cambios simultáneos.

RLS se aplica también al acceso directo a Supabase. Las vistas públicas deben respetar RLS y los privilegios de sus tablas. La API de descubrimiento no usa credenciales privilegiadas. Antes del despliegue se prueba la matriz de acceso, incluidas las llamadas que evitan la interfaz.

Las URLs antiguas siguen siendo borradores compartidos; sus parámetros no prueban aprobación ni crean filas publicadas. Antes de introducir notas privadas, el editor debe advertir que el contenido de una URL se comparte con quien recibe el enlace.

## Módulos propuestos

Los archivos siguientes, salvo los del prototipo, todavía no existen:

- `discover.html`, `discover.js`, `organiser.html`, `organiser.js`: interfaz nueva. El responsable de web es el único que modifica `app.js` y `styles.css`.
- `api/`: entrada HTTP, consultas de catálogo, escritura autenticada y validación de contratos.
- `agent/`: interpretación con Grok y selección de hechos. Recuperación desde Cognee solo si se acepta la ampliación opcional. No escribe fichas ni envía mensajes.
- `supabase/migrations/`: cambios versionados, permisos y proyecciones públicas.
- `scripts/`: importación con procedencia.

`data.js` sigue siendo la fuente del roster del escritorio existente hasta que su lectura se migre expresamente. Se importa conservando los IDs. Para el catálogo conectado, manda Supabase. Una futura exportación offline debe generarse desde la base; no se mantiene manualmente otra copia editable.

## Decisión y alternativas

Se compararon dos propuestas independientes: extender la web estática con API y Supabase, o servir toda la aplicación desde Node con SQLite. Elegimos la primera porque conserva el recorrido existente y aprovecha el sponsor confirmado. La segunda requería almacenamiento persistente y una migración posterior de datos.

De la propuesta unificada tomamos revisiones de edición, operaciones idempotentes y distinción entre borrador y publicación. La revisión cruzada exigió aislar contactos privados y evitar que el modelo convierta una cita válida en una afirmación sin respaldo. Grok como agente de desarrollo estaba deshabilitado en el entorno; la comparación se hizo con Claude y Codex. Esto es independiente del acceso de la aplicación a los créditos de Grok.

Aceptamos desplegar una API además de la web estática. Evitamos por ahora microservicios y varios canales de chat. Primero se demuestra el chat web. Grok API y Grok Bot no son la misma integración; el segundo depende del acceso del evento.

## Eventos y siguientes entregas

El calendario del track sigue dentro del alcance, después del recorrido de venues. Primera fuente propuesta: Luma. Después, Devpost, BuilderBase y Meetup, con adaptadores separados, caché, fecha de última sincronización y deduplicación por proveedor e ID externo. Los snippets del brief son puntos de partida pendientes de comprobar, no integraciones probadas.

Se conservan ubicación, organizador y fuentes. El ranking muestra criterios y evidencia; no inventa calidad ni popularidad. Se etiquetan 30 eventos reales para evaluar el orden. El feed `.ics` usa UID estable, zona horaria y revisiones. Se compara con The Hack Collective si su calendario está disponible. Hack Radar requiere pedir acceso en la sala.

WhatsApp o Discord se añaden después mediante la misma API. Zero aparece en el brief, pero no está en la lista de acceso confirmada. El seguimiento inicial de solicitudes puede vivir en Supabase. No se afirma ninguna integración con Zero.

## Decisiones pendientes

- Proyecto Supabase compartido, acceso del equipo y hosting de API.
- Modelo Grok disponible y límites de los créditos.
- Si se aborda la ampliación de Cognee: acceso al servicio, textos autorizados y evaluación comparativa.
- Usuarios de GitHub para asignar los tres frentes. El repo es público; falta añadir una licencia abierta válida para la entrega.

No se comparten claves por chat, commits ni parámetros de URL. Se configuran en los secretos del despliegue.

## Referencias técnicas

- [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security) y [PostGIS](https://supabase.com/docs/guides/database/extensions/postgis).
- [Salidas estructuradas de Grok](https://docs.x.ai/developers/model-capabilities/text/structured-outputs).
- [API de Cognee](https://docs.cognee.ai/api-reference/introduction).
