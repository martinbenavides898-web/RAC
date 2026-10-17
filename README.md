# RAC — Running App Coach v0.3.1 · Gemini

RAC es una aplicación personal de running construida con Streamlit, Supabase y Gemini.

## v0.3.1

- Gemini reemplaza a OpenAI como motor del Coach IA.
- Modelo inicial: `gemini-2.5-flash-lite`.
- Salidas estructuradas mediante Pydantic.
- Perfil, memorias y últimos 14 días se envían como contexto compacto.
- Los análisis se reutilizan desde Supabase si los datos no cambiaron.
- No se guarda una conversación infinita: la memoria oficial vive en Supabase.
- Seguimiento de tokens procesados.

## Instalación

1. Mantener las tablas de Supabase creadas para RAC v0.3.
2. Subir estos archivos al repositorio RAC.
3. Mantener el bloque `[supabase]` existente en Streamlit Secrets.
4. Crear una API key en Google AI Studio y agregar:

```toml
[gemini]
api_key = "TU_API_KEY"
model = "gemini-2.5-flash-lite"
```

La clave nunca debe subirse a GitHub.

## Privacidad

En el nivel gratuito de Gemini, Google puede usar el contenido enviado para mejorar sus productos. RAC reduce lo enviado a un contexto deportivo compacto, pero no se deben escribir identificadores personales innecesarios ni información clínica sensible en las notas.


## Google Drive (OAuth 2.0)

La pantalla de respaldo usa OAuth 2.0 con un `refresh_token`; no se admiten credenciales de cuenta de servicio en esta implementación. Configura los secretos del servidor, nunca los subas al repositorio:

```toml
[gdrive]
client_id = "TU_CLIENT_ID"
client_secret = "TU_CLIENT_SECRET"
refresh_token = "TU_REFRESH_TOKEN"
root_folder_id = "ID_CARPETA_PADRE_OPCIONAL"
```

La verificación compara el SHA-256 del archivo descargado desde Drive con el archivo enviado y valida también el hash del contenido del respaldo. Ejecuta `supabase_v0_3.sql` en el SQL Editor de Supabase para crear las tablas de memoria, análisis y registro de respaldos.
