# Resultados de verificación / Verification record

Fecha: **2026-11-16**, zona del usuario Europe/Madrid. Entorno: Linux, Bash, Python **3.14.10**, Git **2.56.0**, Codex CLI **0.169.0-alpha.11.1**. Requisito de Python declarado: **3.11+** por `tomllib`; no se ha ejecutado la suite en todas esas versiones ni en macOS/Windows.

## PASS

- **Fuentes:** investigados los doce repositorios solicitados y Skills.sh. Nueve fuentes suministran 20 Skills y siete agentes originales; hay metadatos y decisiones para las doce. Se conservan las licencias y los commits completos. El servidor MCP PnP tiene un catálogo y una plantilla separados.
- **Originales:** 150 archivos originales contrastados con sus hashes de objetos Git (`SHA-1(blob <length> + NUL + contenido)`) y modos ejecutables del árbol de los commits fijados. Los 19 archivos `UPSTREAM_LICENSE.txt` añadidos al empaquetado se identifican por separado. La comprobación inicial utilizó los árboles obtenidos de la API; la validación normal es local por SHA-256.
- **Integridad:** `./scripts/library.sh validate` comprueba 27 componentes, 199 archivos bloqueados por SHA-256, metadatos de origen, nombres únicos, siete perfiles y formato TOML de plantillas MCP desactivadas. Las Skills usan `SKILL.md` y los siete adaptadores de agentes usan únicamente `name`, `description`, `developer_instructions`.
- **Instalador:** `python3 -m unittest discover -s tests -v`: **20 pruebas satisfactorias**. Cubren todos los perfiles y el ciclo instalación/repetición/verificación/actualización/desinstalación; actualización a contenido revisado distinto; conflictos de nombres/rutas; cambios locales, incluso carpetas vacías; enlaces simbólicos; selección desconocida; alcance obligatorio; registro manipulado; fallo de copia con recuperación; integridad alterada; uso del CLI desde otro directorio y planificación sin escrituras. La resolución de rutas globales se comprobó con rutas simuladas, sin instalar en el directorio personal.
- **Codex real, Skills:** instalación `full` en `.cache/demo`, verificación de archivos y consulta RPC `initialize` + `skills/list` mediante el app-server del cliente instalado. Codex devolvió las **20 Skills** seleccionadas y ningún error de análisis. No se solicitó inferencia a un modelo. `CODEX_HOME`, cachés, estado y temporales de esta comprobación se aislaron dentro del repositorio.
- **Actualizaciones:** `./scripts/library.sh check-updates` consultó `git ls-remote ... HEAD` para las nueve fuentes incorporadas. Sus referencias coincidían con los commits fijados al ejecutar la prueba; no descargó ni aprobó versiones nuevas.
- **Sintaxis:** `bash -n scripts/library.sh` y compilación sintáctica de los módulos Python propios.

## Límites: NOT RUN / no confirmado

- **Ejecución de agentes:** se validaron estáticamente los siete adaptadores contra el formato oficial. No se ha lanzado una tarea de modelo ni demostrado ejecución delegada de cada rol. La consulta `skills/list` enumera Skills, no agentes. Una inspección de `debug prompt-input` no enumeró los roles personalizados y no se toma como evidencia de reconocimiento de agentes.
- **MCP autenticado y servicios:** no se instalaron paquetes, iniciaron servidores ni probaron logins, Microsoft Graph, tenants Microsoft 365, WordPress, Docker, Ansible, SSH, infraestructura o producción. Las plantillas MCP pasan validación de formato y permanecen desactivadas.
- **Scripts externos:** revisión estática de instrucciones y código incorporado; no se ejecutaron ayudantes upstream, instaladores remotos ni evaluaciones de pago.
- **Configuración personal:** la prueba de descubrimiento aísla la configuración personal. No demuestra que las mismas Skills estén habilitadas en todas las sesiones del operador o por sus políticas administradas; usa `/skills` en la sesión real para comprobarlo.
- **Plataformas:** no se probó instalación global real, Windows nativo ni macOS. El punto de entrada Bash está orientado a Linux/macOS/WSL; no se declara validación en plataformas no usadas.
- **Seguridad:** revisión mínima por versión, no auditoría completa ni garantía. Los hashes detectan cambios respecto al inventario aprobado; no sustituyen la revisión ni autentican por sí mismos a un publicador. No se admite ejecución concurrente del instalador sobre un mismo destino.

## Reproducir sin salir del repositorio

```bash
./scripts/library.sh validate
python3 -m unittest discover -s tests -v
mkdir -p .cache/demo
./scripts/library.sh install --scope project --target .cache/demo --profile full --dry-run
./scripts/library.sh install --scope project --target .cache/demo --profile full
./scripts/library.sh verify --scope project --target .cache/demo --profile full --codex
./scripts/library.sh update --scope project --target .cache/demo --profile full
./scripts/library.sh uninstall --scope project --target .cache/demo --profile full --dry-run
```

Se inicializó Git localmente en la rama `main`. No se ha creado remoto, commit ni push, y no se ha configurado el acceso privado en un proveedor de alojamiento. Todos los artefactos y pruebas se mantuvieron en este repositorio. `.cache/`, instalaciones de prueba, bytecode y archivos de entorno están excluidos de Git.

## English summary

Twenty installer regression tests passed. All 150 original upstream files matched their pinned Git blobs; 199 curated files are checked by SHA-256. The actual local Codex app-server discovered all 20 installed Skills without a model call. Seven agent adapters pass static format checks, but delegated execution and agent runtime discovery were not demonstrated. Authenticated MCP connections, production systems, global installation and other operating systems were not tested. No remote push, credential storage or third-party script execution occurred.

## Corrección de ejecutable fuera de PATH — 2026-11-16

Se reprodujo el caso en que los archivos instalados pasan `verify`, pero el descubrimiento solicitado con `--codex` no encuentra el ejecutable en la terminal. Se añadió `--codex-bin` y la variable `CODEX_BIN`, con precedencia opción > variable > `PATH`. El error mantiene código de salida 1 e indica explícitamente que la comprobación local pasó y el descubrimiento quedó `NOT RUN`.

**PASS:** suite ampliada a **29 pruebas**, incluidos ausencia del cliente, rutas con espacios/relativas, precedencia, ruta explícita inválida, uso incorrecto de la opción y conservación del registro de instalación al fallar el descubrimiento. Validación de catálogo e integridad satisfactoria. La comprobación real `verify --scope project --target .cache/demo --profile sysadmin --codex --codex-bin <ejecutable>` pasó con el binario ya disponible en la extensión local de VS Code: **7 componentes verificados y 4 Skills reconocidas**. No se instaló un cliente, modificó `PATH` ni ejecutó una tarea de modelo.
