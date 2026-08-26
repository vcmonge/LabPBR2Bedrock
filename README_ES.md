# LabPBR2Bedrock

[![English](https://img.shields.io/badge/lang-English-blue)](README.md)

**LabPBR to Bedrock Converter**

LabPBR2Bedrock es una aplicación de escritorio para convertir texturas PBR de Minecraft Java en formato LabPBR al formato PBR compatible con Minecraft Bedrock.

## Captura de pantalla

![LabPBR2Bedrock](https://ik.imagekit.io/dmNtb25nZQ/LabPBR2Bedrock/LabPBR2Bedrock.webp?updatedAt=1787277920137)

Convierte:

- Mapas specular `*_s.png` en mapas MER `*_mer.png`.
- Mapas specular con subsurface scattering (SSS) en mapas MERS `*_mers.tga` cuando se activa esa opción (La opción se habilita al detectarse SSS en la textura de entrada).
- Mapas normales `*_n` en mapas `*_normal.png`.
- Opcionalmente, genera archivos `*.texture_set.json` para Minecraft Bedrock.

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

## Requisitos

- Windows 10 u 11.
- Python 3.14.

## Instalación

Abre PowerShell en la carpeta del proyecto y elige uno de estos métodos.

### Con Python Launcher

Si instalaste Python desde python.org y tienes disponible Python Launcher (`py`), ejecuta:

```powershell
py -3.14 -m venv .venv

.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Con uv

Como alternativa, si tienes [uv](https://docs.astral.sh/uv/getting-started/installation/) instalado, ejecuta:

```powershell
uv venv --python 3.14 .venv

uv pip install -r requirements.txt
```

`uv` puede descargar Python 3.14 automáticamente si no lo encuentra instalado. Ambos métodos crean el entorno virtual `.venv` e instalan PySide6, Pillow y NumPy.

## Ejecutar la aplicación

### Opción 1: doble clic

Haz doble clic en `run.bat`.

El script localiza automáticamente `app.py` y el entorno `.venv` con respecto a su propia ubicación. No inicia la aplicación si el entorno virtual no existe.

### Opción 2: PowerShell

```powershell
.\.venv\Scripts\python.exe app.py
```

## Uso

1. Arrastra archivos o carpetas al recuadro principal, o usa `Browse files...`.
2. Activa `Generate JSON` si necesitas archivos `*.texture_set.json`.
3. Si la entrada contiene SSS y quieres conservarlo, activa `SSS`.
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

- **SSS:** se habilita cuando un mapa specular contiene subsurface scattering. Al activarlo, las texturas que realmente tienen SSS se guardan como MERS TGA y, si se genera JSON, usan el formato `1.21.30`, las demás conservan el formato MER PNG.
- **POM:** se habilita cuando un normal map contiene altura en su canal alfa.
- **Generate JSON:** crea un `*.texture_set.json` por cada nombre base convertido. Las imagenes con SSS usa el formato `1.21.30`, el resto usa `1.16.100`.

## Carpeta de salida

La carpeta elegida con `Change...` se recuerda entre ejecuciones. La preferencia guardada tiene prioridad sobre `--output-dir`.

## Notas

- Los archivos originales de entrada no se modifican ni se eliminan.

## Agradecimientos

La lógica de conversión de LabPBR a PBR de Bedrock en `mer_converter.py` y `normal_converter.py` se adaptó a partir de partes de [JE2BE Resource Pack Converter](https://github.com/Seraphic-Studio/JE2BE-Resource-Pack-Converter), desarrollado por el equipo de JE2BE.

Desde entonces, la implementación de este proyecto se ha modificado y ampliado considerablemente.

JE2BE Resource Pack Converter está publicado bajo la licencia MIT.
Consulta `THIRD_PARTY_LICENSES.md` para ver el aviso de copyright y la licencia originales.
