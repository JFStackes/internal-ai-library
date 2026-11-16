# Incorporar y actualizar componentes

La biblioteca prioriza componentes externos mantenidos. Antes de escribir una Skill o agente propio, busca alternativas oficiales y proyectos con licencia explícita. Skills.sh puede ayudar a descubrir candidatos, pero la aprobación debe basarse en los archivos y la licencia del repositorio de origen.

## Revisión de una fuente

1. Confirma que el repositorio existe, identifica su propietario, rama por defecto y commit completo, y registra la fecha de revisión y señales de mantenimiento. La popularidad no reemplaza la revisión.
2. Comprueba que la licencia permite el uso y la redistribución previstos. Conserva el texto original y los avisos aplicables; no deduzcas una licencia de un badge o de una fuente distinta.
3. Lee las instrucciones y todos los scripts que se incluirán. Revisa descargas, ejecución de comandos, acceso a secretos, escrituras, red, permisos y comandos destructivos. No ejecutes scripts para averiguar qué hacen.
4. Revisa referencias y dependencias. Incluye los archivos locales necesarios y documenta las herramientas externas que el componente espera. Descarta rutas que escapen del componente, enlaces inseguros y dependencias no justificadas.
5. Confirma la compatibilidad real: las Skills requieren `SKILL.md`; los agentes para otros clientes necesitan una adaptación explícita. Un README con una descripción de un agente no es una integración ejecutable.
6. Decide qué aporta frente a lo ya aprobado. Evita duplicar flujos, nombres de Skill o agentes. Documenta exclusiones y cobertura pendiente en [research.md](research.md).

Haz cualquier descarga temporal y revisión dentro de `.cache/` de este repositorio. Utiliza un commit inmutable, conserva los originales y nunca ejecutes el instalador de un repositorio externo durante esta revisión. No introduzcas credenciales de GitHub ni datos de producción.

## Incorporación

- Añade los metadatos y las licencias en `sources/`.
- Copia la carpeta completa de una Skill seleccionada a `skills/external/<id>/`, con sus referencias y scripts originales.
- Conserva agentes originales en `agents/upstream/`. Si es necesario, añade la adaptación compatible a `agents/codex/` y registra qué campos se han transformado u omitido.
- Registra en `catalog/` un identificador estable, tipo, nombre, ruta local, origen, commit completo, ruta de origen, licencia, categorías y decisión de revisión. Usa la estructura real de los registros existentes.
- Actualiza los registros de integridad con los archivos efectivamente aprobados. Un hash detecta cambios; no sustituye la revisión ni autentica por sí solo el origen.
- Añade el identificador a los perfiles apropiados y documenta requisitos o límites que afecten al operador.

Las adaptaciones de agentes mapean las instrucciones al campo `developer_instructions` del formato vigente. Conserva el nombre y la responsabilidad del agente existente. No añadas supuestas herramientas, credenciales, permisos elevados o modelos fijos por comodidad. Los agentes heredan la configuración y las herramientas de la sesión principal.

## Actualización controlada

`./scripts/library.sh check-updates` solo informa de diferencias con las referencias remotas. Para aprobar una actualización, compara el commit registrado con el candidato e inspecciona los cambios de instrucciones, scripts, licencias y dependencias. Repite la revisión mínima y registra el nuevo commit únicamente cuando corresponda incorporar el contenido.

Mantén el catálogo, los archivos originales, las adaptaciones y los hashes en el mismo cambio revisable. Si el origen cambia de licencia o desaparece, conserva la evidencia anterior y explica la decisión; no sustituyas silenciosamente la fuente. No uses ramas móviles como versión instalada.

## Validación antes de incorporar

```bash
./scripts/library.sh validate
python3 -m unittest discover -s tests -v
```

Después prueba el ciclo de instalación en un directorio desechable bajo `.cache/`: planificación con `--dry-run`, instalación, segunda instalación, verificación, actualización y desinstalación. Incluye conflictos con componentes ajenos y cambios locales. Si cambia el formato de Codex, consulta documentación oficial vigente y prueba `verify --codex` con un cliente compatible.

No afirmes que una integración autenticada funciona sin haberla probado con autorización y un entorno adecuado. Anota el resultado, versión del cliente y límites en [verification.md](verification.md). Mantén sincronizados [README.md](../README.md) y [README.es.md](README.es.md) cuando cambie el procedimiento del operador.

Una colección ampliada debe seguir siendo pequeña y útil: justifica nuevas dependencias, ejecutables o servidores. Los perfiles de instalación distribuyen archivos aprobados; no deben arrancar servidores, iniciar sesiones ni modificar infraestructura.

## Regenerar adaptadores e integridad

Tras completar la revisión y copiar los originales aprobados:

```bash
python3 scripts/prepare.py --reviewed
./scripts/library.sh validate
python3 -m unittest discover -s tests -v
```

`prepare.py` genera exclusivamente los adaptadores de `agents/codex/` y el inventario SHA-256; no descarga archivos, aprueba revisiones ni modifica los perfiles. `--reviewed` declara que ya has revisado los cambios: no es una auditoría automática. Añade el mapeo de Skills pertinentes en `LINKS` cuando incorpores otro agente. Los adaptadores conservan las instrucciones originales, añaden límites operativos comunes y el texto de licencia MIT, y omiten los campos upstream de modelo, esfuerzo y sandbox.

El inventario de integraciones MCP está separado en `catalog/integrations.json`; no mezcla servidores con componentes instalables ni incorpora conexiones en los perfiles. Una plantilla revisada y desactivada no equivale a un servidor probado.
