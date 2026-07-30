# RAC — Running App Coach v0.3

RAC es una aplicación personal de running construida con Streamlit, Supabase y un coach IA opcional.

## v0.3

- Perfil estructurado y editable.
- Memorias seleccionadas, con activación/desactivación manual.
- Coach IA para entrenamiento, semana y preguntas.
- Contexto compacto: perfil + memorias activas + últimos 14 días.
- Caché en Supabase: si los datos no cambian, reutiliza el análisis y no cobra otra llamada.
- No guarda prompts completos ni conversaciones infinitas.
- La API se llama con `store=False`; la memoria oficial vive en Supabase.
- Seguimiento de tokens acumulados.

## Orden de instalación

1. Ejecutar `supabase_v0_3.sql` en Supabase SQL Editor.
2. Subir los archivos al repositorio RAC.
3. Mantener los secretos Supabase existentes.
4. Agregar en Streamlit Secrets:

```toml
[openai]
api_key = "TU_API_KEY"
model = "gpt-5-mini"
```

La clave nunca debe subirse a GitHub.
