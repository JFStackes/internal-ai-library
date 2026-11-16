# Revisión de fuentes / Source review

Revisión: **16 de noviembre de 2026**. La selección inicial contiene **20 Skills y 7 agentes**, todos externos. El catálogo autoritativo es [`catalog/components.json`](../catalog/components.json); cada componente identifica el repositorio, commit completo y ruta original. `sources/<owner>--<repo>/metadata.json` conserva la evidencia de existencia, rama, actividad, licencia y decisión. Las fechas siguientes describen el commit fijado, no garantizan mantenimiento futuro.

## Fuentes prioritarias investigadas

| Fuente | Commit fijado | Fecha del commit UTC | Licencia verificada | Decisión |
|---|---|---|---|---|
| [Hassanzadeh-sd/ansible-ops-toolkit](https://github.com/Hassanzadeh-sd/ansible-ops-toolkit) | [c9389dc0c219](https://github.com/Hassanzadeh-sd/ansible-ops-toolkit/commit/c9389dc0c219544fae5fd93b812b600903faf49c) | 2026-06-29 | MIT | selected |
| [HermeticOrmus/linux-sysadmin-skills](https://github.com/HermeticOrmus/linux-sysadmin-skills) | [358769e5e431](https://github.com/HermeticOrmus/linux-sysadmin-skills/commit/358769e5e43197609b093a354f182cc6ad1118c2) | 2026-05-25 | MIT | selected |
| [VoltAgent/awesome-codex-subagents](https://github.com/VoltAgent/awesome-codex-subagents) | [9abe3279a0aa](https://github.com/VoltAgent/awesome-codex-subagents/commit/9abe3279a0aa4ee518381af800ca1062398f5433) | 2026-11-02 | MIT | selected |
| [WordPress/agent-skills](https://github.com/WordPress/agent-skills) | [7374e6f1c913](https://github.com/WordPress/agent-skills/commit/7374e6f1c913b3b02b25465d266d9c0e0a04fc96) | 2026-11-05 | GPL-2.0-or-later | selected |
| [anthropics/skills](https://github.com/anthropics/skills) | [e4bb5d960d87](https://github.com/anthropics/skills/commit/e4bb5d960d87126ff3b3a8af1a104b7db67560ba) | 2026-11-16 | mixed / per-skill | selected |
| [docker/skills](https://github.com/docker/skills) | [a65ae5b65d22](https://github.com/docker/skills/commit/a65ae5b65d22f0613375d6c3e5ea8bb287698cc0) | 2026-11-13 | Apache-2.0 | selected |
| [microsoft/skills](https://github.com/microsoft/skills) | [f03ec5392f7a](https://github.com/microsoft/skills/commit/f03ec5392f7a0f3aca12af47477e92f1edf7b44c) | 2026-11-13 | MIT | reviewed-not-selected |
| [obra/superpowers](https://github.com/obra/superpowers) | [22f0b463e7a5](https://github.com/obra/superpowers/commit/22f0b463e7a5e579904dd6211a520321035526f7) | 2026-11-03 | MIT | selected |
| [pnp/cli-microsoft365](https://github.com/pnp/cli-microsoft365) | [945ca0d61729](https://github.com/pnp/cli-microsoft365/commit/945ca0d61729c2022780d12f0380e5ac4d882151) | 2026-11-16 | MIT | selected |
| [pnp/cli-microsoft365-mcp-server](https://github.com/pnp/cli-microsoft365-mcp-server) | [38ed9902e363](https://github.com/pnp/cli-microsoft365-mcp-server/commit/38ed9902e36378c3e0404366e44d57e1df3807b4) | 2026-11-07 | MIT | integration-candidate |
| [trailofbits/skills](https://github.com/trailofbits/skills) | [149d7b21f406](https://github.com/trailofbits/skills/commit/149d7b21f4067765b82e67029730b42d228ef4b4) | 2026-11-12 | CC-BY-SA-4.0 | selected |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | [1a2c79d4e6c4](https://github.com/vercel-labs/agent-skills/commit/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62) | 2026-10-27 | unlicensed | excluded |

Todos los repositorios existen y estaban sin archivar al consultar la API de GitHub. Se contrastaron existencia con el conector GitHub y metadatos/commit/árbol con la API pública. El conector no devolvía licencia ni fecha de push; se completaron con esa API. Se descargaron archivos individuales mediante URLs raw fijadas al commit, sin ejecutar instaladores, hooks ni scripts de terceros.

### Decisiones de selección

- **WordPress**: fuente oficial; seis Skills de triage, WP-CLI/operaciones, REST, plugins, bloques Gutenberg y rendimiento. `LICENSE` expresa GPL versión 2 o posterior, aunque GitHub la clasifique como `NOASSERTION`; se conserva literalmente. Los scripts de inspección se revisaron por operaciones de fichero y ejecución de procesos. Los inspectores que llaman `wp` pueden cargar código de plugins de la instalación consultada: usar solamente proyectos de confianza y autorizados.
- **Docker**: tres Skills oficiales para Compose, builds y operaciones destructivas. Apache-2.0. El helper Compose usa `docker compose config --quiet`; el helper build construye realmente una imagen. Ninguno se ejecutó durante la importación.
- **Superpowers**: MIT; se incorporan debugging, TDD y verificación. Se excluyen hooks, bootstrap y el conjunto completo de orquestación para evitar duplicidad y dependencia de otras plataformas. Las referencias `superpowers:<nombre>` son referencias al flujo con ese nombre, no comandos nativos de Codex.
- **Linux SysAdmin**: MIT; tres runbooks comunitarios, breves, para Debian/Ubuntu. La última modificación fijada es de mayo; su cobertura es más limitada que una suite oficial de administración. Monitorización es explícitamente de lectura; diagnóstico y rendimiento exigen confirmar cambios. No se presenta esta fuente como una colección madura y completa de todos los sistemas Linux.
- **Ansible Ops**: MIT; versión upstream 0.1.0 con cinco archivos. Revisadas convenciones FQCN, idempotencia, `no_log`, comprobación y diff. El texto upstream menciona `examples/nginx-role/`, que no existe en el árbol del commit seleccionado; se conserva el original y se documenta esa limitación, sin fabricar el ejemplo. Las referencias reales sí están incluidas.
- **Trail of Bits**: CC-BY-SA-4.0; se conservan atribución y licencia. `sharp-edges` aporta revisión de APIs y configuración segura. `supply-chain-risk-auditor` aporta análisis de manifiestos npm/PyPI/Go con metadatos públicos; su código usa caché local y puede consultar registries/OSV/GitHub/Scorecard, leer la credencial de `gh` y ejecutar `pip-audit --no-deps --disable-pip` si está disponible. La importación no ejecuta nada de ello. Su uso exige revisar destinos y qué nombres de dependencias pueden salir por red; las cachés e informes pueden contener información privada del proyecto. `allowed-tools` de otras plataformas no es un control de permisos en Codex.
- **Anthropic**: el repositorio tiene licencias por Skill; **solo** `mcp-builder`, con `LICENSE.txt` Apache-2.0, está aprobado. La guía para diseño de servidores MCP es reutilizable desde Codex. El harness opcional de evaluación Python usa la API de Anthropic y llama herramientas del servidor objetivo; puede generar costes o cambios según sus herramientas. No es parte necesaria de instalar/usar la guía ni se ha probado ejecutándolo.
- **VoltAgent**: siete agentes nativos TOML reales, MIT: administración Windows, DevOps, fullstack, auditoría de seguridad, incidentes, WordPress y Microsoft 365. Los archivos reales usan `developer_instructions`; el ejemplo del README upstream mostraba otra estructura. Los originales se mantienen; los adaptadores de la biblioteca añaden normas comunes y eliminan preferencias upstream de modelo, esfuerzo y sandbox para heredar la sesión del operador.
- **PnP CLI for Microsoft 365**: MIT; `clim365` y su índice cubren Entra, Exchange/Outlook, SharePoint, Teams, OneDrive, licencias y auditoría mediante una CLI real. La Skill exige verificar opciones con `--help`. Instalarla no instala `m365`, no autentica y no concede acceso a ningún tenant. Los ejemplos de escritura no constituyen autorización para ejecutarlos.
- **PnP MCP**: servidor real, MIT y activo; candidato de integración separado, no una Skill ni un subagente. La configuración/documentación de integración está en `integrations/`; no se ha instalado ni conectado a Microsoft 365.
- **Microsoft Skills**: fuente real, MIT y activa. Se inspeccionó el inventario y los candidatos `microsoft-docs` y `entra-app-registration`. Predominan Azure/SDK y flujos con herramientas MCP/Copilot. La primera colección ya cubre administración Microsoft 365 con PnP; no se añade otra Skill con `context: fork` o herramientas que podrían no estar disponibles. Puede incorporarse una Skill concreta tras revisar su directorio y dependencias.
- **Vercel Labs**: el repositorio existe y está activo, pero en el commit consultado no se encontró `LICENSE` de repositorio ni por Skill, y la API devuelve licencia nula. Se excluye de la redistribución hasta verificar una concesión explícita. Popularidad y disponibilidad pública no sustituyen una licencia.

### Skills.sh y otras fuentes

Se consultó [Skills.sh](https://www.skills.sh/) como índice de descubrimiento y se leyó su [ficha de WordPress wp-env](https://www.skills.sh/wordpress/agent-skills/wp-env), que remite a la fuente WordPress oficial. No se tomaron cifras de instalaciones ni badges de auditoría como garantía de seguridad y no se ejecutó su comando `npx skills add`. El origen de los archivos sigue siendo GitHub a commit fijo, no una copia intermediaria del índice.

La documentación oficial vigente de OpenAI determina el formato de instalación; véase [Skills](https://developers.openai.com/codex/skills) y [Subagents](https://developers.openai.com/codex/agent-configuration/subagents). La documentación de cada proyecto determina sus requisitos operativos. El sello de aprobación de esta biblioteca significa revisión mínima concreta de esta versión, no auditoría integral o garantía del proveedor.

## Compatibilidad y límites prácticos

Las Skills siguen el formato `SKILL.md` con `name` y `description` en frontmatter. Se conservan directorios completos y originales para no romper referencias locales. Como única adición de empaquetado, cada Skill sin licencia local recibe `UPSTREAM_LICENSE.txt`, copia literal de la licencia del repositorio; `packaging_additions` registra esa procedencia y hash. Los archivos originales upstream permanecen intactos. Campos heredados como `allowed-tools` y `context` no crean permisos ni delegación en Codex. Las instrucciones de terceros siempre se subordinan al usuario y a la política de la sesión.

Las Skills WordPress incluyen ejemplos con rutas `skills/<nombre>/scripts/...` que reflejan su repositorio original. En una instalación Codex, resolver la ruta absoluta al directorio instalado (`.agents/skills/<nombre>` o `~/.agents/skills/<nombre>`) antes de ejecutar el helper, manteniendo el directorio de trabajo del proyecto inspeccionado. No ejecutar literalmente una ruta upstream suponiendo que existe en cualquier proyecto. Los requisitos WordPress 7.0+/PHP, Node, WP-CLI, Docker/Compose y `m365` son dependencias operativas separadas, que la biblioteca no instala.

`sharp-edges` menciona un agente opcional del plugin upstream (`sharp-edges-analyzer`) no incluido. La Skill contiene el flujo completo para uso directo; ese nombre no se registra como agente Codex. Los agentes incluidos no obtienen acceso automático a herramientas, credenciales, red, PowerShell o sistemas remotos por el mero hecho de tener una especialidad.

## Cobertura pendiente

| Área | Estado inicial y ampliación útil |
|---|---|
| Linux | Diagnóstico, monitorización y rendimiento Debian/Ubuntu; faltan runbooks específicos revisados de almacenamiento, backups/restauración y SSH. |
| Windows Server | Agente real con AD/DNS/DHCP/GPO y orientación PowerShell; sin Skill operativa Windows específica ni pruebas en Windows. |
| Proxmox | Sin candidato específico aprobado en las fuentes prioritarias; no se inventa una Skill. |
| Kubernetes, Terraform, Traefik, CI/CD | Agente DevOps general y Docker/Ansible; faltan Skills dedicadas revisadas. No se importa toda la colección de agentes para rellenar categorías. |
| Desarrollo | Debugging, TDD, validación y agente fullstack; sin batería dedicada por lenguaje/framework. |
| WordPress | Bloques, plugins, REST, WP-CLI y rendimiento; sin Skill de temas/SEO especializada en esta primera selección. |
| Microsoft 365 | PnP CLI + agente especializado; Graph/PowerShell se eligen cuando el usuario los solicita y requieren herramientas/permisos separados. |
| IA/automatización | Diseño de MCP reutilizable; sin candidato n8n específico revisado ni aplicación LLM instalada. |

## Alcance de las comprobaciones

La importación comprobó archivos y modos contra el árbol Git de cada commit, licencias y estructura; se revisaron instrucciones y entradas/salidas relevantes de scripts seleccionados. No se ejecutaron scripts upstream ni se probaron servicios externos, WordPress, Microsoft 365, Docker, infraestructura o APIs de pago. Las pruebas del instalador y reconocimiento de Codex las documenta el informe de validación de la biblioteca, diferenciando validación estática y ejecución real.

## English summary

All twelve requested repositories were found and reviewed at immutable commits. This first release vendors twenty complete Skill directories and seven original TOML agent definitions, preserving third-party files and license notices. Vercel is excluded because an explicit license was not found at the reviewed commit. Microsoft Skills remains a reviewed future source; PnP CLI provides the initial M365 administration workflow. Skills.sh was used for discovery only.

The approval covers static, version-specific review; it does not imply comprehensive security certification. No third-party helper, tenant operation, production change, authentication or paid evaluation was executed. WordPress path examples require resolving installed Skill locations. Anthropic's optional MCP evaluation harness uses its own API, and the supply-chain collector may query public registries using dependency metadata. Dedicated Proxmox, backup/restore, n8n, Traefik, Kubernetes and Terraform workflows remain explicitly unfilled until suitable components receive review.
