# RAC — Running App Coach v0.1

Primera versión funcional del proyecto personal de running de Martín.

## Incluye

- Registro manual de entrenamientos.
- Selección y kilometraje de zapatillas.
- Botones separados para Sick Day, Día de estudio y descanso.
- Dashboard semanal.
- Reporte semanal determinista.
- Perfil/memoria estable de RAC.
- Exportación JSON y CSV.

## Ejecutar localmente

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Importante sobre los datos

Esta versión usa SQLite local para validar la app rápidamente. En Streamlit Community Cloud el almacenamiento local no tiene persistencia garantizada. La siguiente etapa será conectar Supabase y mantener SQLite solo para desarrollo/pruebas.

## Próximas etapas

1. Base persistente Supabase.
2. Importación de Adidas Running / Mi Fitness (.GPX, .JSON, .CSV o .FIT según exportación).
3. Sincronización resumida con LagartijApp.
4. Coach IA con memoria compacta y salida estructurada.
5. Reporte semanal generado por RAC.
