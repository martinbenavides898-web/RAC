# RAC 2.0 — Etapa 1: fecha y calendario

Este ZIP es un **parche de etapa 1** para aplicar sobre el repositorio RAC actual. No incluye cambios de métricas, seguridad, planificador, Coach IA, fueling, zapatillas, respaldo, GPX ni Google Drive.

## Fuente oficial consultada

La web oficial de Maratón de Santiago indica que el Itaú Maratón de Santiago se realizará el **domingo 16 de mayo de 2027**:

- https://maratondesantiago.cl/contacto/preguntas-frecuentes/
- Página principal: https://maratondesantiago.cl/

Fecha consultada: 17-10-2026.

## Archivos incluidos

- `ui/marathon.py`: versión completa de la página basada en el código auditado del repositorio, con fecha oficial, guardado explícito, zona horaria chilena y vista de fases.
- `rac_core/race_calendar.py`: funciones puras de calendario, zona horaria y fases; no necesita Streamlit ni Supabase.
- `tests/test_race_calendar.py`: pruebas unitarias de las funciones nuevas.

## Cómo aplicar

1. Descomprime el ZIP.
2. Copia `ui/marathon.py` sobre el archivo del mismo nombre en el repositorio.
3. Copia `rac_core/race_calendar.py` dentro de `rac_core/`.
4. Copia `tests/test_race_calendar.py` a `tests/` (crea la carpeta si no existe).
5. Haz commit en una rama de prueba o revisa el diff antes de fusionar.
6. Ejecuta las pruebas desde la raíz del repositorio:

   ```bash
   python -m unittest discover -s tests -v
   ```

7. Despliega y comprueba que la página abra, que muestre el 16/05/2027 como fecha oficial y que el botón «Guardar objetivo» persista la fecha seleccionada.

## Compatibilidad y datos

- Se conserva la clave existente de perfil `rac_2_marathon`; no hay migración SQL.
- Si Supabase ya tiene guardado `2027-04-18`, el parche **no lo sobrescribe silenciosamente**. La página avisa que era la fecha provisional anterior; selecciona `16/05/2027` y pulsa «Guardar objetivo».
- La fecha oficial se usa como valor por defecto solo cuando el perfil no contiene una fecha válida.
- El contador usa `America/Santiago` en lugar de la zona horaria del servidor.
- Las fases son solo un calendario visual. No se generan ni modifican entrenamientos en esta etapa.

## Estado de verificación

- Código escrito: sí.
- Pruebas unitarias: ejecutar el comando anterior; el resultado se reporta por separado en la conversación.
- Pruebas con Supabase real: no ejecutadas.
- Verificado en Streamlit Cloud: no ejecutado.
- No incluye credenciales ni secretos.
