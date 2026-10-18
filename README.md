# Analizador de representación de datos

Aplicación web hecha con **Python 3.12 y Django** que relaciona tres temas del curso:
sistemas numéricos, codificación de caracteres (UTF-8) y ejecución en contenedores.

## Funcionalidades

**1. Conversión de números** (`/numero/`)
- Entrada: número + base de origen (2, 8, 10 o 16).
- Valida que los dígitos pertenezcan a la base y que el valor esté entre 0 y 65 535.
- Muestra decimal, binario (completado al siguiente límite de byte: 8, 16 bits…), octal y hexadecimal.
- Muestra bits significativos y bytes necesarios (el 0 cuenta como 1 bit y 1 byte).

**2. Análisis de caracteres** (`/texto/`)
- Texto de hasta 20 caracteres.
- Por cada carácter: carácter, código decimal, punto de código `U+XXXX`, hexadecimal y bytes UTF-8.
  Ejemplo: `ñ` → 241 · `U+00F1` · `0xF1` · `C3 B1` (2 bytes).

**Errores claros** para: entrada vacía, dígitos inválidos para la base (indica cuáles y cuáles se permiten),
valores negativos, valores fuera de rango y texto de más de 20 caracteres.

## Estructura

```
analizador/
├── manage.py
├── requirements.txt
├── Dockerfile
├── compose.yaml
├── config/                 # proyecto Django (settings, urls, wsgi)
└── analizador/             # aplicación
    ├── servicios.py        # lógica pura: conversión, validación, UTF-8
    ├── forms.py            # NumeroForm y TextoForm
    ├── views.py / urls.py
    ├── templates/analizador/index.html
    └── tests.py            # 15 pruebas automatizadas
```

La lógica vive en `servicios.py` (sin dependencia de Django), los formularios la llaman desde `clean()`
y las vistas solo renderizan. La aplicación no usa base de datos.

## Ejecución local (sin Docker)

```bash
python3.12 -m venv .venv
source .venv/bin/activate          # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
# abrir http://localhost:8000
```

## Pruebas automatizadas

```bash
python manage.py test -v 2
```

Hay 16 pruebas: conversiones válidas (decimal, hexadecimal en minúsculas, octal, binario),
ajuste a bytes (8 y 16 bits), el caso 0, dígitos inválidos por base, entrada vacía, negativos,
fuera de rango (65 536 y `10000` hex), texto vacío o de más de 20 caracteres, **UTF-8 de `ñ`
(`U+00F1`, `C3 B1`)** y pruebas de las vistas.

## Docker

### Construir y ejecutar con Compose (recomendado)

```bash
docker compose up --build -d      # construye y levanta en segundo plano
docker compose ps                 # estado y healthcheck
docker compose logs -f web        # registros
docker compose down               # detener y eliminar
```

Abrir <http://localhost:8000>. `compose.yaml` ya fija **`mem_limit: 256m`** y **`cpus: 1.0`**.

### Alternativa con `docker` directamente

```bash
docker build -t analizador-datos:1.0 .
docker run -d --name analizador-datos -p 8000:8000 \
  --memory=256m --memory-swap=256m --cpus=1 \
  analizador-datos:1.0
```

### Ejecutar las pruebas dentro del contenedor

```bash
docker compose run --rm web python manage.py test
```

### Evidencia de límites (`docker stats`)

Con el contenedor en ejecución:

```bash
docker stats analizador-datos --no-stream
docker inspect analizador-datos --format 'Memoria={{.HostConfig.Memory}} bytes  NanoCpus={{.HostConfig.NanoCpus}}'
```

Resultado esperado: la columna `MEM USAGE / LIMIT` muestra `… / 256MiB` y la inspección devuelve
`Memoria=268435456` y `NanoCpus=1000000000` (1 CPU). Guarde la captura o salida en
`evidencias/docker-stats.txt` (o `.png`).

> **Estado de la evidencia:** el archivo `evidencias/docker-stats.txt` debe generarse en su máquina
> con los comandos anteriores; este repositorio no incluye una salida inventada.

## Arquitectura de Von Neumann: recursos que usa la aplicación

| Componente | Uso en la aplicación |
|---|---|
| **CPU** (ALU + unidad de control) | Ejecuta la conversión entre bases y la codificación UTF-8. La ALU hace las divisiones/desplazamientos; la unidad de control recorre el ciclo captura-decodificación-ejecución del intérprete. Compose limita a 1 CPU. |
| **Memoria principal (RAM)** | Almacena *programa y datos* en el mismo espacio (idea central de Von Neumann): el intérprete de Python, el código de Django, y los números y cadenas en su representación binaria. Se limita a 256 MB. |
| **Almacenamiento secundario** | Guarda la imagen del contenedor y el código; se lee al arrancar. La app no escribe datos. |
| **Entrada/Salida** | Entrada: formularios HTTP (teclado → navegador → red). Salida: HTML renderizado. Pasa por la interfaz de red (puerto 8000). |
| **Bus** | Mueve instrucciones y datos entre CPU, RAM y E/S. |

Los valores ≤ 65 535 caben en 16 bits (2 bytes) y cada carácter ocupa 1 a 4 bytes en UTF-8:
la aplicación hace visible cómo un mismo dato (por ejemplo `ñ` = `0xF1` = `C3 B1`) cambia de
representación según el sistema numérico y la codificación.

## ¿Por qué el contenedor comparte el kernel del host?

Un contenedor **no es una máquina virtual**: no arranca su propio sistema operativo. Es un proceso
(o grupo de procesos) del host aislado mediante *namespaces* de Linux (PID, red, montajes, usuarios…)
y limitado mediante *cgroups* (memoria, CPU). Las llamadas al sistema de la aplicación
(`read`, `write`, `socket`, reserva de memoria…) las atiende el **mismo kernel** que usa el host.
La imagen solo aporta las bibliotecas y el sistema de archivos de espacio de usuario (Debian slim + Python).

Consecuencias: arranca en milisegundos, consume muy poco y es más ligero que una VM, pero el aislamiento
es más débil y el contenedor debe ser compatible con el kernel del host. En Windows y macOS, Docker
Desktop ejecuta una VM Linux ligera y es el kernel de esa VM el que se comparte. Los límites
`--memory=256m` y `--cpus=1` son precisamente *cgroups* del kernel compartido: si el proceso excede
los 256 MB, el kernel lo termina (OOM killer).

## Entrega

- **Repositorio:** `<pegue aquí el enlace de GitHub o Google Drive con acceso público>`
- **Video (máx. 2 min):** `<enlace>`. Guion sugerido (≈1:45):
  1. (0:00) `docker compose up --build -d` y abrir `http://localhost:8000`.
  2. (0:15) Conversión válida: `255` base 10 → binario `11111111`, hex `FF`, 8 bits / 1 byte.
  3. (0:30) Error de validación: `1012` base 2 → mensaje de dígito inválido.
  4. (0:45) Texto `año` → `ñ` = `U+00F1`, `C3 B1`.
  5. (1:05) `docker compose run --rm web python manage.py test`.
  6. (1:25) `docker stats analizador-datos --no-stream` mostrando el límite de 256 MiB.

## Correspondencia con la rúbrica

| Criterio | Dónde se cumple |
|---|---|
| Conversiones y ajuste a bytes | `servicios.py` (`convertir_numero`, `binario_ajustado`) |
| Análisis de caracteres y UTF-8 | `servicios.py` (`analizar_texto`), sección 2 de la página |
| Validación y mensajes de error | `ErrorValidacion` + `forms.py` |
| Estructura Django | `config/` + app `analizador` (forms, views, urls, templates) |
| Pruebas | `analizador/tests.py` |
| Docker y límites | `Dockerfile`, `compose.yaml` |
| README y evidencias | este archivo + `evidencias/` |
