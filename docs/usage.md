# Instalación y uso

Los comandos se ejecutan desde la raíz de la biblioteca. Necesitas Bash y Python 3.11 o posterior; las comprobaciones con Codex requieren un cliente local compatible. La colección se copia desde archivos versionados: instalar no descarga ni ejecuta herramientas de terceros.

## Elegir alcance y componentes

```bash
./scripts/library.sh list
./scripts/library.sh validate
mkdir -p .cache/demo
./scripts/library.sh install --scope project --target .cache/demo --profile wordpress --dry-run
./scripts/library.sh install --scope project --target .cache/demo --profile wordpress
```

`--scope project --target DIRECTORIO` instala Skills en `DIRECTORIO/.agents/skills/`, agentes en `DIRECTORIO/.codex/agents/` y registra la propiedad en `DIRECTORIO/.codex/internal-ai-library.json`. Utiliza rutas absolutas al trabajar con destinos de otros proyectos y autoriza ese alcance antes de ejecutarlo. Los ejemplos de esta documentación permanecen dentro de la biblioteca.

Los perfiles disponibles son `sysadmin`, `devops`, `development`, `wordpress`, `microsoft365`, `security` y `full`. Consulta sus archivos en `profiles/` para ver la selección exacta. Los perfiles pueden compartir componentes; no es necesario duplicarlos para reutilizarlos.

Para instalar componentes individuales, utiliza identificadores de `list`:

```bash
./scripts/library.sh install --scope project --target .cache/demo \
  --component wp-wpcli-and-ops --component agent-wordpress-master --dry-run
```

También existe `--scope global`. Úsalo solo cuando quieras afectar a todas tus sesiones locales: las Skills van a `~/.agents/skills/` y los agentes y el registro a `$CODEX_HOME`, por defecto `~/.codex`. El alcance global no se utilizó durante la configuración inicial. No necesitas editar tu configuración global para probar esta biblioteca.

## Verificar el descubrimiento

```bash
./scripts/library.sh verify --scope project --target .cache/demo --profile wordpress
./scripts/library.sh verify --scope project --target .cache/demo --profile wordpress --codex
```

La primera comprobación verifica los archivos instalados y su integridad. La opción `--codex` consulta el descubrimiento de Skills mediante el cliente local en un entorno aislado y sin solicitudes a un modelo. Esta prueba confirma lo que devuelve el cliente para las Skills; no ejecuta flujos de agentes ni autentica servidores MCP. Consulta los resultados y límites en [verification.md](verification.md).

Abre Codex desde `.cache/demo`. En CLI e IDE puedes utilizar `/skills` o escribir `$` para seleccionar una Skill. Codex también puede activarla cuando la descripción coincide con tu tarea. Si no aparece una instalación reciente, reinicia el cliente; comprueba también si la Skill está deshabilitada por configuración o por políticas administradas. La ruta y el comportamiento están documentados por [OpenAI](https://developers.openai.com/codex/skills).

### Codex no está en el PATH

Si aparecen `PASS` para los archivos y después falta el ejecutable, la instalación ha pasado su validación local. `UNCHANGED` significa que los componentes ya estaban instalados y coinciden con el catálogo. El error solo afecta al descubrimiento adicional solicitado con `--codex`.

Puedes comprobar los archivos sin el cliente:

```bash
./scripts/library.sh verify --scope project --target .cache/demo --profile sysadmin
```

Para comprobar el descubrimiento, indica un ejecutable de confianza ya disponible, sin instalar nada globalmente:

```bash
./scripts/library.sh verify --scope project --target .cache/demo --profile sysadmin \
  --codex --codex-bin /ruta/absoluta/a/codex
```

También puedes definir `CODEX_BIN` para ese comando. La opción `--codex-bin` tiene prioridad sobre esa variable y, si ninguna está definida, se busca `codex` en `PATH`. Una ruta explícita incorrecta produce un error: no se ejecuta automáticamente otro binario ni se buscan copias por el disco. Se admiten rutas con espacios si las entrecomillas. Si el cliente no existe, omite `--codex` hasta disponer de uno; la biblioteca no instala el cliente ni modifica tu `PATH`.

## Delegar en agentes especializados

Pide la delegación de forma expresa y acota la responsabilidad. Los agentes instalados son roles reales adaptados al formato independiente de Codex. Heredan las Skills disponibles, los permisos y los servidores MCP de la sesión principal; instalar un agente no añade herramientas ni inicia tareas por sí solo.

| Agente | Responsabilidad |
| --- | --- |
| `windows-infra-admin` | Diagnóstico y administración de infraestructura Windows |
| `devops-engineer` | Contenedores, automatización e integración y entrega continua |
| `fullstack-developer` | Desarrollo y diagnóstico de aplicaciones frontend y backend |
| `security-auditor` | Revisión de seguridad y hallazgos basados en evidencias |
| `incident-responder` | Recogida de evidencias, triaje y coordinación de incidentes |
| `wordpress-master` | Desarrollo y diagnóstico de WordPress |
| `m365-admin` | Administración y diagnóstico de Microsoft 365 |

Codex delega cuando se lo pides o cuando una instrucción aplicable solicita delegación; la disponibilidad depende del cliente y de sus políticas. Las instrucciones pueden restringir el comportamiento, pero los agentes heredan el aislamiento de la sesión. Consulta la [documentación oficial de subagentes](https://developers.openai.com/codex/agent-configuration/subagents).

## Ejemplos de trabajo

**SysAdmin, sin cambios en el servidor:**

> Utiliza `$sysadmin-diagnose` para analizar estos registros de Linux. Identifica las causas probables y propón comandos de diagnóstico de solo lectura. No conectes a servidores ni ejecutes reparaciones. Devuelve evidencias y los datos que faltan.

Para infraestructura Windows, puedes añadir: «Delega el análisis de estos eventos en `windows-infra-admin`; limita la tarea a los registros que te proporciono». La colección no presupone acceso SSH, PowerShell remoto ni credenciales.

**WordPress, diagnóstico con WP-CLI:**

> Delega en `wordpress-master` la revisión de este proyecto. Utiliza `$wp-project-triage` y `$wp-wpcli-and-ops` cuando corresponda. Empieza por identificar la instalación y prepara comprobaciones de solo lectura. No actualices plugins, cambies opciones ni escribas en la base de datos sin autorización.

Las Skills de bloques, plugins, REST API y rendimiento complementan este flujo. Los originales seleccionados apuntan a WordPress 7.0 o posterior: comprueba la versión del proyecto. Algunos ejemplos de origen usan rutas `skills/<nombre>`; resuelve los scripts desde la carpeta real instalada en `.agents/skills/<nombre>`. WP-CLI y una instalación accesible de WordPress son dependencias del entorno de trabajo. Incluso las consultas de WP-CLI pueden cargar código de plugins: ejecútalas únicamente en instalaciones de confianza y con autorización.

**Microsoft 365, revisión de permisos:**

> Delega en `m365-admin` el diseño de una auditoría de permisos de este tenant. Utiliza `$clim365` si está disponible. Propón comandos de solo lectura, los ámbitos mínimos y los datos necesarios. No inicies sesión, concedas consentimiento ni modifiques usuarios, licencias o permisos.

La Skill aporta conocimiento de CLI for Microsoft 365. Las consultas reales requieren su instalación, autenticación autorizada y los permisos necesarios. No hay credenciales ni tenant preconfigurado.

## Actualizar sin perder cambios locales

```bash
./scripts/library.sh check-updates
./scripts/library.sh update --scope project --target .cache/demo --profile wordpress --dry-run
./scripts/library.sh update --scope project --target .cache/demo --profile wordpress
./scripts/library.sh verify --scope project --target .cache/demo --profile wordpress
```

`check-updates` consulta las referencias remotas y muestra si existen nuevos commits; no los descarga como componentes aprobados. `update` aplica únicamente las versiones que ya están revisadas y presentes en el catálogo local. Para actualizar el catálogo sigue [contributing.md](contributing.md).

Si existe un destino ajeno a la biblioteca o un archivo administrado ha cambiado, detente y conserva tus cambios antes de resolver el conflicto. No borres el registro de propiedad ni alteres hashes para eludir las comprobaciones. Si necesitas una variante permanente, mantenla como componente distinto y registra su procedencia.

## Desinstalar

```bash
./scripts/library.sh uninstall --scope project --target .cache/demo --profile wordpress --dry-run
./scripts/library.sh uninstall --scope project --target .cache/demo --profile wordpress
```

Solo se retiran componentes seleccionados que pertenezcan a esta biblioteca y sigan sin cambios. Las configuraciones de usuario, credenciales y conexiones MCP tienen un ciclo independiente y no se eliminan mediante este comando.

## Límites de compatibilidad de los originales

Los archivos externos se conservan para mantener su trazabilidad. Consulta `review.notes` en `catalog/components.json` antes de ejecutar sus scripts:

- Los flujos de Superpowers pueden mencionar `superpowers:nombre`; en Codex, selecciona la Skill instalada con ese nombre sin prefijo. Sus hooks y bootstrap no están instalados.
- `ansible-ops` referencia un ejemplo `examples/nginx-role` ausente en el commit original; utiliza las referencias incluidas. No se ejecuta ningún playbook al instalar.
- `sharp-edges` puede mencionar un agente opcional de su plugin original que no forma parte de esta colección. Los campos `allowed-tools` no configuran permisos en Codex.
- El recolector de `supply-chain-risk-auditor` usa red, puede leer autenticación de GitHub y escribe cachés e informes. Revisa el código y autoriza la divulgación de nombres de paquetes antes de utilizarlo.
- La guía de `mcp-builder` puede usarse desde Codex; su evaluador opcional usa la API de Anthropic y puede invocar herramientas MCP o generar costes. El instalador no lo ejecuta ni lo necesita.
- Los ayudantes Docker pueden construir imágenes; las Skills SysAdmin y de Microsoft 365 incluyen operaciones que escriben. La revisión inicial no autoriza su ejecución sobre sistemas reales.

La cobertura inicial no constituye una suite completa de Proxmox, backups, almacenamiento, Kubernetes, Terraform o SEO. [research.md](research.md) identifica las limitaciones y decisiones de selección.

## MCP y resolución de problemas

Las recetas en `integrations/mcp/` se configuran aparte. Revisa dependencias, versión fijada, transporte y exposición de herramientas antes de activarlas. La instalación de un perfil no configura un MCP ni inicia un proceso. No guardes tokens en TOML; usa referencias al entorno o autenticación interactiva compatible. La [configuración oficial de MCP](https://developers.openai.com/codex/mcp) explica cómo inspeccionar y autorizar conexiones.

Si falla `validate`, resuelve primero el archivo, metadato o hash indicado. Si falla `verify`, revisa el alcance y destino elegidos y el registro de instalación. Si el cliente rechaza agentes, comprueba que tu versión admite TOML independientes con `name`, `description` y `developer_instructions`; no copies formatos de otros clientes a `.codex/agents/`. Los fallos de autenticación, herramientas ausentes y permisos remotos se resuelven en el entorno de trabajo y no mediante reinstalaciones forzadas.

Ejecuta un solo instalador por destino y evita editar los componentes mientras se instalan o actualizan. Las operaciones comprueban conflictos antes de escribir y recuperan las copias anteriores si se produce una excepción de copia. No hay bloqueo entre procesos ni recuperación automática ante una interrupción del sistema. Si una operación se interrumpe, conserva el directorio afectado y el registro para reconciliarlos manualmente. Las carpetas vacías de instalación y el registro vacío pueden permanecer tras desinstalar.
