# Proyecto: Publicidad Allegro RJ PL

Este proyecto automatiza el proceso de carga y procesamiento de datos publicitarios de **Allegro** en una base de datos MySQL.  
Convierte un archivo Excel exportado desde Allegro en CSV, lo carga en una tabla temporal y ejecuta una serie de scripts SQL para actualizar la información final.

---

## 📂 Estructura del proyecto

```
.
├── .env_sample                # Archivo de ejemplo con variables de entorno
├── .gitignore                 # Configuración de gitignore
├── Pasos/                     # Contiene los scripts SQL en orden de ejecución
│   ├── paso1_allegro_rj_pl.sql
│   ├── paso2_allegro_rj_pl.sql
│   ├── paso3_allegro_rj_pl.sql
│   ├── paso4_allegro_rj_pl.sql
├── Archivos/                  # Carpeta donde se coloca el archivo Excel y CSV temporal
│   ├── .gitkeep
│   └── rj_allegro_pl.xlsx     # Archivo Excel exportado desde Allegro
├── SQL_Seller.py              # Script principal en Python
```

---

## ⚙️ Requisitos

- Python **3.8+**
- MySQL con `local_infile` habilitado
- Librerías de Python:
  - `pandas`
  - `mysql-connector-python`
  - `python-dotenv`
  - `openpyxl` (para leer archivos Excel)
- Archivo `.env` con las variables:
  ```env
  MYSQL_HOST=localhost
  MYSQL_USER=usuario
  MYSQL_PASSWORD=contraseña
  MYSQL_DATABASE=nombre_bd
  ```

---

## 🚀 Ejecución del proceso

Para la ejecución de este proceso:

1. **Generar el archivo XLSX desde Allegro** (reporte RJ PL).
2. **Renombrar** el archivo a:
   ```
   rj_allegro_pl.xlsx
   ```
3. **Colocar el archivo** dentro de la carpeta:
   ```
   Archivos/
   ```
4. **Ejecutar el script**:
   ```bash
   python SQL_Seller.py
   ```

---

## 🛠️ Funcionalidad del script

El script realiza los siguientes pasos:

1. **Leer los scripts SQL** desde la carpeta `Pasos/`.
2. **Convertir el archivo Excel en CSV** (ajustando formato de fechas y separador `;`).
3. **Cargar el CSV a MySQL** en una tabla temporal (`t_temp_rj_allegro_pl`).
4. **Actualizar columnas auxiliares** (`divisa`, `indice`).
5. **Ejecutar los pasos SQL 2, 3 y 4** para procesar la información final.
6. **Limpiar la carpeta `Archivos`** dejando solo `.gitkeep`.

---

## 📌 Notas

- El archivo CSV se genera con terminador de línea `LF` para compatibilidad con sistemas Linux.
- Si el comando `LOAD DATA LOCAL INFILE` falla, verificar:
  - Que MySQL tenga `local_infile=1` habilitado.
  - Que el usuario tenga permisos para `LOCAL`.
- Los warnings de `openpyxl` sobre *default style* son inofensivos y no afectan la ejecución.

---

## 📄 Licencia

Este proyecto es de uso interno y no cuenta con una licencia de distribución pública.
