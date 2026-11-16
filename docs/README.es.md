# Internal AI Library

[Read in English](../README.md)

Biblioteca privada y versionada de Skills externas, agentes especializados y recetas de integración MCP para OpenAI Codex. Los componentes se seleccionan y revisan antes de incorporarlos; se conservan los archivos originales, las licencias y la trazabilidad hasta commits inmutables.

La colección cubre SysAdmin, DevOps, desarrollo, WordPress, Microsoft 365, seguridad e IA y automatización cuando existen componentes adecuados. La [investigación y las decisiones de selección](research.md) registran cobertura y exclusiones. Instalar un perfil no inicia servidores MCP ni modifica infraestructura.

## Requisitos

- Bash, Python 3.11 o posterior y Git.
- Un cliente local reciente de Codex para descubrir componentes y ejecutar la comprobación opcional con el cliente.
- Linux, macOS o WSL para el punto de entrada Bash. La instalación nativa en Windows no está verificada.

La instalación y la validación local usan la colección incluida y no necesitan red. Consultar actualizaciones y conectar servidores MCP requiere acceso a red. Cada Skill puede necesitar herramientas adicionales; consulta sus instrucciones antes de utilizarla.

## Primer uso dentro de este repositorio

```bash
./scripts/library.sh list
./scripts/library.sh validate
mkdir -p .cache/demo
./scripts/library.sh install --scope project --target .cache/demo --profile sysadmin --dry-run
./scripts/library.sh install --scope project --target .cache/demo --profile sysadmin
./scripts/library.sh verify --scope project --target .cache/demo --profile sysadmin
./scripts/library.sh verify --scope project --target .cache/demo --profile sysadmin --codex
```

Abre Codex desde el directorio de destino. Utiliza `/skills` o `$nombre-de-la-skill` en CLI o IDE. Pide expresamente que delegue una tarea acotada en un agente instalado. El cliente debe soportar el formato actual de agentes independientes; los permisos, la autenticación y las herramientas disponibles siguen dependiendo de la sesión principal.

`verify` comprueba los archivos sin necesitar un ejecutable de Codex. La opción `--codex` exige además encontrar `codex` en el `PATH` de tu terminal. Si está en otra ubicación, utiliza `verify ... --codex --codex-bin /ruta/absoluta/a/codex`, o define `CODEX_BIN`. El orden es `--codex-bin`, `CODEX_BIN` y finalmente `codex` en `PATH`. Si falta el ejecutable, la comprobación de archivos sigue siendo válida, pero el descubrimiento solicitado falla indicando `NOT RUN`; no se reinstala nada. Consulta la [solución de problemas](usage.md#codex-no-está-en-el-path).

## Perfiles y componentes individuales

Perfiles disponibles: `sysadmin`, `devops`, `development`, `wordpress`, `microsoft365`, `security` y `full`. Los componentes de IA y automatización forman parte de los perfiles pertinentes y de `full`. Consulta `profiles/` y `list` antes de elegir `full`, que puede añadir bastante contexto de Skills.

Selecciona componentes individuales repitiendo `--component ID` en lugar de `--profile NOMBRE`; `list` muestra los identificadores. La instalación por proyecto escribe únicamente debajo del destino elegido. La instalación global está disponible mediante `--scope global` explícito; no es necesaria para el ejemplo y no se realizó durante la configuración del repositorio.

| Componente | Ubicación por proyecto | Ubicación global |
| --- | --- | --- |
| Skills | `.agents/skills/<nombre-de-skill>/` | `~/.agents/skills/<nombre-de-skill>/` |
| Agentes personalizados | `.codex/agents/<agente>.toml` | `$CODEX_HOME/agents/`, por defecto `~/.codex/agents/` |
| Registro de instalación | `.codex/internal-ai-library.json` | `$CODEX_HOME/internal-ai-library.json` |

Las instalaciones existentes ajenas a la biblioteca están protegidas. Actualizar o desinstalar exige un registro de propiedad y que el contenido instalado siga sin modificaciones. Resuelve los cambios locales de forma deliberada; no hay una opción para forzar la sobrescritura.

## Mantener una instalación

```bash
# Consulta commits remotos; no aprueba ni instala código nuevo.
./scripts/library.sh check-updates

# Aplica versiones ya revisadas e incorporadas a esta biblioteca.
./scripts/library.sh update --scope project --target .cache/demo --profile sysadmin --dry-run
./scripts/library.sh update --scope project --target .cache/demo --profile sysadmin

# Retira solo los componentes seleccionados, propios y sin cambios locales.
./scripts/library.sh uninstall --scope project --target .cache/demo --profile sysadmin --dry-run
./scripts/library.sh uninstall --scope project --target .cache/demo --profile sysadmin
```

Consulta [instalación y uso](usage.md) para los procedimientos y ejemplos, [incorporación y revisión de actualizaciones](contributing.md) para ampliar las fuentes y [arquitectura](architecture.md) para las responsabilidades de cada capa. Las plantillas MCP están separadas en `integrations/mcp/`; revisa su documentación antes de activar una conexión.

## Validación y seguridad

```bash
python3 -m unittest discover -s tests -v
./scripts/library.sh validate
```

Los [resultados de verificación](verification.md) distinguen comprobaciones estáticas, descubrimiento aislado con Codex e integraciones autenticadas sin probar. Validar el formato no demuestra que el flujo de una Skill o un servidor remoto funcione en tu entorno.

No guardes secretos en este repositorio. Revisa los scripts externos antes de ejecutarlos, prioriza diagnósticos de solo lectura, limita los permisos y exige autorización expresa antes de operaciones destructivas. Las instrucciones describen el comportamiento; los permisos de herramientas y el aislamiento se configuran por separado.

Cada componente externo conserva su licencia. Revisa `catalog/`, `sources/` y los archivos de licencia originales antes de redistribuir o adaptar contenido; la aprobación representa una revisión acotada, no una garantía de seguridad.
