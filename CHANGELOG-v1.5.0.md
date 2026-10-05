# LinguaAI Coach v1.5.0 - Traducción libre con Azure Translator

## Cambios

- Se separó el proveedor del Tutor (`AI_PROVIDER`) del proveedor del Traductor (`TRANSLATION_PROVIDER`).
- Nuevo proveedor `azure_translator` para traducir texto libre entre español, inglés y serbio.
- Serbio de salida usa alfabeto latino por defecto (`sr-Latn`).
- Entrada serbia detecta cirílico y usa `sr-Cyrl` cuando corresponde.
- Se mantienen `rule_based` y `openai_compatible` como alternativas.
- Nuevas variables: `AZURE_TRANSLATOR_KEY`, `AZURE_TRANSLATOR_REGION` y `AZURE_TRANSLATOR_ENDPOINT`.
- Se conserva el Tutor en modo gratuito `rule_based` aunque el traductor use Azure.
- `render.yaml` conserva la configuración de staging validada en Render (Python 3.11, Node 20 y API pública para el frontend).

## Nota

No se incluyen credenciales. Las claves de Azure deben configurarse como variables de entorno privadas en Render y nunca subirse a GitHub.
