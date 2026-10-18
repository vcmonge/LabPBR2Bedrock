# LabPBR2Bedrock

[![English](https://img.shields.io/badge/lang-English-blue)](README.md)

**LabPBR to Bedrock Converter**

LabPBR2Bedrock es una aplicación de escritorio para convertir texturas PBR de Minecraft Java en formato LabPBR al formato PBR compatible con Minecraft Bedrock.

## Captura de pantalla

![LabPBR2Bedrock](https://ik.imagekit.io/dmNtb25nZQ/LabPBR2Bedrock/LabPBR2Bedrockv3.webp?updatedAt=1789529312137)

Convierte:

- Mapas specular `*_s.png` en mapas MER `*_mer.png`.
- Mapas specular en mapas MERS cuando se selecciona el formato `1.21.30`: `*_mers.tga` para texturas cuyo SSS se empaqueta (`SSS` activado y SSS real presente) y `*_mers.png` sin alfa para el resto. Ambas opciones siempre se pueden seleccionar, aunque ninguna entrada tenga SSS.
- Mapas normales `*_n` en mapas `*_normal.png`.
- Opcionalmente, genera archivos `*.texture_set.json` para Minecraft Bedrock.

## Requisitos

- Windows 10 u 11.
- Python 3.14 (la instalación automática lo descarga si no está disponible).

## Instalación

### Instalación automática (recomendada)

Haz doble clic en `windows_setup.bat`. El script:

1. Instala [uv](https://docs.astral.sh/uv/) si no está disponible.
2. Descarga Python 3.14 con `uv` si no está instalado.
3. Crea el entorno virtual `.venv`, o lo recrea si está incompleto o usa otra versión de Python.
4. Instala las dependencias de `requirements.txt` y verifica que se puedan importar.

Al terminar, inicia la aplicación con `run.bat`. Puedes volver a ejecutar la instalación sin riesgo: solo repite los pasos que falten.

### Instalación manual

Si prefieres instalar todo por tu cuenta, elige uno de estos métodos. Ejecuta los comandos en PowerShell desde la carpeta del proyecto.

#### Opción A: Python desde python.org

1. Descarga e instala Python 3.14 desde [python.org](https://www.python.org/downloads/windows/). Asegúrate de incluir Python Launcher (`py`) en la instalación.
2. Abre una nueva ventana de PowerShell y confirma que Python 3.14 está disponible:

   ```powershell
   py -3.14 --version
   ```

3. Crea el entorno virtual e instala las dependencias:

   ```powershell
   py -3.14 -m venv .venv

   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

#### Opción B: uv

1. Instala [uv](https://docs.astral.sh/uv/getting-started/installation/) :

   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. Abre una nueva ventana de PowerShell y confirma que uv está disponible:

   ```powershell
   uv --version
   ```

3. Descarga Python 3.14 si aún no lo tienes:

   ```powershell
   uv python install 3.14
   ```

4. Crea el entorno virtual e instala las dependencias:

   ```powershell
   uv venv --python 3.14 .venv

   uv pip install -r requirements.txt
   ```

#### Verificar la instalación

Ambos métodos crean el entorno virtual `.venv` e instalan PySide6, Pillow y NumPy. Para confirmar que las dependencias están disponibles, ejecuta:

```powershell
.\.venv\Scripts\python.exe -c "import PySide6, PIL, numpy"
```

Si el comando termina sin errores, inicia la aplicación con `run.bat`.

## Ejecutar la aplicación

### Opción 1: doble clic

Haz doble clic en `run.bat`.

El script localiza automáticamente `app.py` y el entorno `.venv` con respecto a su propia ubicación. No inicia la aplicación si el entorno virtual no existe; en ese caso, ejecuta primero `windows_setup.bat`.

### Opción 2: PowerShell

```powershell
.\.venv\Scripts\python.exe app.py
```

## Uso

1. Arrastra archivos o carpetas al recuadro principal, o usa `Browse files...`.
2. Activa `Generate JSON` si necesitas archivos `*.texture_set.json`.
3. Selecciona `1.21.30` para generar texture sets MERS y activa `SSS` si además quieres empaquetar el SSS real de las texturas.
4. Si un normal map contiene información de altura y quieres conservarla, activa `POM`.
5. Selecciona la carpeta de salida con `Change...` si es necesario.
6. Presiona `Process images`.

Al terminar, la consola muestra los archivos convertidos, ignorados y los errores del lote. El botón `Clear` vacía las entradas pendientes y la consola.

## Archivos compatibles

La aplicación acepta únicamente imágenes PNG y TGA. Los sufijos no distinguen entre mayúsculas y minúsculas:

```text
stone_s.png
stone_n.png
stone_normal.png
```

Los archivos que no siguen esos patrones se muestran como ignorados. Si existen `stone_n` y `stone_normal` para la misma textura, se usa `stone_n`.

## Opciones PBR

- **SSS:** empaqueta el SSS de LabPBR en el canal alfa de MERS. Los valores de SSS (66–255) se copian directamente, sin reescalar; 0–65 (porosidad y 0 % de SSS) pasan a 0. MER no tiene canal de SSS, así que activar `SSS` selecciona `1.21.30` y elegir `1.16.100` desactiva `SSS`; desactivar `SSS` conserva `1.21.30`. Ambas opciones siempre se pueden elegir y se conservan tras procesar y tras `Clear`. Elegir el `format_version` correcto queda a cargo del usuario. Con `1.21.30`, las texturas con SSS tras la exclusión con metalness producen un `*_mers.tga` RGBA de 32 bits si `SSS` está activado; el resto (incluidas todas si `SSS` está desactivado) producen un `*_mers.png` RGB sin canal alfa. Cuando el texture set declara MERS pero la textura no tiene canal alfa, Vibrant Visuals no aplica ningún fallback y toma SSS = 255 (máximo) en todos los píxeles. Bedrock conserva el mayor entre metalness y SSS por píxel; un empate favorece SSS.
- **POM:** se habilita cuando un normal map contiene altura en su canal alfa. Al activarlo, esa altura se copia al canal Blue de `*_normal.png` para BetterRTX 1.5. RTX y Vibrant Visuals oficiales tratan Blue como el componente Z del normal; deja POM desactivado para reconstruir Z.
- **Generate JSON:** crea un `*.texture_set.json` por cada nombre base convertido. Todos los texture sets usan el formato seleccionado: `1.21.30` apunta a `*_mers` y `1.16.100` a `*_mer`, incluidos los nombres base que solo tienen normal.

## Carpeta de salida

La carpeta elegida con `Change...` se recuerda entre ejecuciones. La preferencia guardada tiene prioridad sobre `--output-dir`.

## Ejemplo

Archivos de entrada:

```text
stone_s.png
stone_n.png
```

Archivos de salida:

```text
stone_mer.png
stone_normal.png
stone.texture_set.json (opcional)
```

Los mapas specular y normal que comparten nombre base se procesan como una sola textura y generan un único JSON. También se admiten mapas sin pareja. Por ejemplo:

Entrada:

```text
stone_s.png
dirt_n.png
cherry_leaves_s.png
```
Salida:

```text
stone_mer.png
dirt_normal.png
cherry_leaves.tga

# (Si se activó la opción de "Generate JSON")
stone.texture_set.json
dirt.texture_set.json
cherry_leaves.texture_set.json
```

## Notas

- Los archivos originales de entrada no se modifican ni se eliminan.

## Agradecimientos

La lógica de conversión de LabPBR a PBR de Bedrock en `mer_converter.py` y `normal_converter.py` se adaptó a partir de partes de [JE2BE Resource Pack Converter](https://github.com/Seraphic-Studio/JE2BE-Resource-Pack-Converter), desarrollado por el equipo de JE2BE.

Desde entonces, la implementación de este proyecto se ha modificado y ampliado considerablemente.

JE2BE Resource Pack Converter está publicado bajo la licencia MIT.
Consulta `THIRD_PARTY_LICENSES.md` para ver el aviso de copyright y la licencia originales.
