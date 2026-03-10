import pandas as pd
import json
import re

archivo = "datos/productos.xlsx"

df = pd.read_excel(archivo)

# Limpiar nombres de columnas
df.columns = [str(col).strip().upper() for col in df.columns]

print("Columnas detectadas:", list(df.columns))

def limpiar(texto):
    t = str(texto if pd.notna(texto) else "").strip()
    t = t.replace("\n", " ").replace("\r", " ")
    t = re.sub(r"\s+", " ", t)
    return t

def buscar_columna(posibles):
    for posible in posibles:
        posible = posible.upper().strip()
        if posible in df.columns:
            return posible
    return None

def interpretar_vida_util(texto, dias_fallback=None):
    texto = limpiar(texto).upper()

    if "MES" in texto:
        n = re.search(r"\d+", texto)
        return (int(n.group()), "meses") if n else (None, None)

    if "AÑO" in texto or "ANO" in texto:
        n = re.search(r"\d+", texto)
        return (int(n.group()) * 12, "meses") if n else (None, None)

    if "DIA" in texto:
        n = re.search(r"\d+", texto)
        return (int(n.group()), "dias") if n else (None, None)

    if pd.notna(dias_fallback):
        try:
            return int(dias_fallback), "dias"
        except:
            return None, None

    return None, None

# Detectar columnas reales
col_codigo = buscar_columna(["CODIGO", "CÓDIGO", "CODE"])
col_nombre = buscar_columna(["NOMBRE", "NOMBRE DEL PRODUCTO", "PRODUCTO", "DESCRIPCION", "DESCRIPCIÓN"])
col_vida = buscar_columna(["VIDA_UTIL", "VIDA UTIL", "VIDA ÚTIL"])
col_dias = buscar_columna(["DIAS", "DÍAS"])

if not col_codigo:
    raise ValueError(f"No se encontró columna de código. Columnas disponibles: {list(df.columns)}")

if not col_nombre:
    raise ValueError(f"No se encontró columna de nombre. Columnas disponibles: {list(df.columns)}")

if not col_vida and not col_dias:
    raise ValueError(f"No se encontró columna de vida útil ni de días. Columnas disponibles: {list(df.columns)}")

materiales = {}

for _, row in df.iterrows():
    codigo = limpiar(row[col_codigo])
    nombre = limpiar(row[col_nombre])

    vida_texto = row[col_vida] if col_vida else ""
    dias_fallback = row[col_dias] if col_dias else None

    vida, unidad = interpretar_vida_util(vida_texto, dias_fallback)

    if codigo and nombre and vida and unidad:
        materiales[codigo] = {
            "nombre": nombre,
            "vidaUtil": vida,
            "unidadVidaUtil": unidad
        }

with open("materiales.json", "w", encoding="utf-8") as f:
    json.dump(materiales, f, ensure_ascii=False, indent=2)

with open("materiales.js", "w", encoding="utf-8") as f:
    f.write("window.MATERIALES = ")
    json.dump(materiales, f, ensure_ascii=False, indent=2)
    f.write(";\nwindow.materiales = window.MATERIALES;\n")

print(f"Archivos generados correctamente. Total materiales: {len(materiales)}")
