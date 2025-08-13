#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# Limitar threads
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"]      = "1"
os.environ["MKL_NUM_THREADS"]      = "1"
os.environ["NUMEXPR_NUM_THREADS"]  = "1"

from pathlib import Path
from datetime import datetime
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

# ------------------------------------------------------------
# Configuración base: usar automáticamente la carpeta del repo
# (la carpeta donde está este .py tras hacer git clone).
# Busca 'Pasos' y 'Archivos' desde el directorio del script
# hacia arriba (por si el script vive en /scripts).
# ------------------------------------------------------------
load_dotenv()

THIS_DIR = Path(__file__).resolve().parent

def find_repo_base(start: Path) -> Path:
    candidates = [start] + list(start.parents)
    for base in candidates:
        pasos = base / "Pasos"
        archivos = base / "Archivos"
        if pasos.is_dir() and archivos.is_dir():
            return base
    # Si no existen, usamos el directorio del script como base
    return start

BASE_DIR = find_repo_base(THIS_DIR)
PASOS_DIR = BASE_DIR / "Pasos"
ARCHIVOS_DIR = BASE_DIR / "Archivos"

# Rutas de archivos
SQL1 = PASOS_DIR / "paso1_allegro_rj_pl.sql"
SQL2 = PASOS_DIR / "paso2_allegro_rj_pl.sql"
SQL3 = PASOS_DIR / "paso3_allegro_rj_pl.sql"
SQL4 = PASOS_DIR / "paso4_allegro_rj_pl.sql"

XLSX_IN = ARCHIVOS_DIR / "rj_allegro_pl.xlsx"
CSV_OUT = ARCHIVOS_DIR / "rj_allegro_pl.csv"

def read_sql(path: Path) -> str:
    with path.open("r", encoding="utf-8") as f:
        return f.read()

def convertir_fecha_ddmmyyyy_to_yyyymmdd(s: str) -> str:
    # 'dd-mm-YYYY' -> 'YYYY-mm-dd'
    dt = datetime.strptime(s, "%d-%m-%Y")
    return dt.strftime("%Y-%m-%d")

def mysql_connect():
    cnx = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        allow_local_infile=True,
    )
    return cnx, cnx.cursor()

def main():
    # 1) Leer SQL
    paso1 = read_sql(SQL1)
    paso2 = read_sql(SQL2)
    paso3 = read_sql(SQL3)
    paso4 = read_sql(SQL4)

    # 2) Excel -> CSV (ajustar columna fecha en índice 13)
    print("[INFO] Convirtiendo Excel a CSV...")
    df = pd.read_excel(XLSX_IN)
    df.iloc[:, 13] = df.iloc[:, 13].astype(str).apply(convertir_fecha_ddmmyyyy_to_yyyymmdd)

    # Usar LF para compatibilidad Linux
    # (cambio aquí: lineterminator en lugar de line_terminator)
    df.to_csv(CSV_OUT, sep=";", index=False, lineterminator="\n")

    # 3) MySQL
    print("[INFO] Conectando a MySQL...")
    cnx, cursor = mysql_connect()
    try:
        print("[INFO] Ejecutando paso 1...")
        cursor.execute(paso1)
        cnx.commit()

        print("[INFO] Cargando CSV a tabla temporal...")
        csv_for_mysql = str(CSV_OUT.as_posix())
        load_stmt = (
            "LOAD DATA LOW_PRIORITY LOCAL INFILE %(csv)s "
            "REPLACE INTO TABLE `campaigns1`.`t_temp_rj_allegro_pl` "
            "CHARACTER SET utf8 "
            "FIELDS TERMINATED BY ';' "
            "LINES TERMINATED BY '\n' "
            "IGNORE 1 LINES "
            "(`nombre_campana`, `ad_group`, `oferta`, `id_producto`, `impresiones`, `clics`, `interes`, "
            "`cpc`, `ctr`, `costo`, `retorno_inversion`, `pedidos`, `ventas`, `fecha`, `fecha_add`, `fecha_update`);"
        )
        cursor.execute(load_stmt, {"csv": csv_for_mysql})
        cnx.commit()

        print("[INFO] Actualizando columnas auxiliares...")
        cursor.execute("UPDATE t_temp_rj_allegro_pl SET divisa = 'PLN';")
        cursor.execute("UPDATE t_temp_rj_allegro_pl SET indice = CONCAT(nombre_campana, ad_group, oferta, fecha);")
        cnx.commit()

        print("[INFO] Ejecutando paso 2...")
        cursor.execute(paso2); cnx.commit()

        print("[INFO] Ejecutando paso 3...")
        cursor.execute(paso3); cnx.commit()

        print("[INFO] Ejecutando paso 4...")
        cursor.execute(paso4); cnx.commit()

        print("[OK] Proceso Allegro RJ PL finalizado.")

    finally:
        print("[INFO] Cerrando conexión MySQL...")
        try:
            cursor.close()
        except Exception:
            pass
        try:
            cnx.close()
        except Exception:
            pass

    # 4) Limpiar carpeta 'Archivos' (mantener .gitkeep)
    print("[INFO] Limpiando carpeta de archivos...")
    kept = 0
    removed = 0
    for item in ARCHIVOS_DIR.iterdir():
        if item.is_file() and item.name.lower() != ".gitkeep":
            try:
                item.unlink()
                removed += 1
            except Exception as e:
                print(f"[WARN] No se pudo eliminar {item.name}: {e}")
        else:
            kept += 1
    print(f"[INFO] Limpieza completada. Eliminados: {removed}, Conservados (incl. .gitkeep): {kept}")

if __name__ == "__main__":
    main()
