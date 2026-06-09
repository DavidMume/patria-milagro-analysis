"""
lematizar_pdfs.py
=================
Extrae texto de los PDFs del programa de gobierno, limpia el contenido,
lematiza con spaCy y guarda archivos planos listos para NLP.

Salidas por cada PDF:
  data/raw/      <nombre>_raw.txt          texto extraido tal cual
  data/processed/<nombre>_limpio.txt       texto limpio (sin ruido)
  data/processed/<nombre>_lematizado.txt   texto lematizado plano
  data/processed/<nombre>_corpus.csv       tabla: pagina | parrafo | original | limpio | lemas | tokens | n_tokens

Uso:
    python scripts/lematizar_pdfs.py

Requisitos:
    pip install pymupdf spacy pandas
    python -m spacy download es_core_news_sm   (ya instalado)
    # Para mejor precision:
    python -m spacy download es_core_news_lg
"""

import re
import sys
import csv
from pathlib import Path

import fitz          # PyMuPDF
import pandas as pd
import spacy

# ── configuracion ─────────────────────────────────────────────────────────────
DESCARGAS = Path("C:/Users/David.Munoz/Downloads")

PDFS = [
    ("F03", "PILARES-FUNDACIONALES.pdf"),
    ("F04", "programa_de_gobierno_Abelardo_de_la_Espriella.pdf"),
    ("F05", "EL-MILAGRO-DEL-VALLE-DEL-CAUCA-PRIMERAS-PROPUESTAS-PARA-LOS-VALLECAUCANOS_compressed.pdf"),
    ("F01", "PROPUESTAS-DEL-TIGRE.pdf"),
]

ROOT      = Path(__file__).resolve().parent.parent
RAW_DIR   = ROOT / "data" / "raw"
PROC_DIR  = ROOT / "data" / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)

# ── cargar modelo spacy ───────────────────────────────────────────────────────
MODEL = "es_core_news_lg"
try:
    nlp = spacy.load(MODEL)
    print(f"Modelo cargado: {MODEL}")
except OSError:
    MODEL = "es_core_news_sm"
    nlp = spacy.load(MODEL)
    print(f"Modelo cargado: {MODEL} (instala es_core_news_lg para mayor precision)")

nlp.max_length = 2_000_000

# ── stopwords y ruido ─────────────────────────────────────────────────────────
STOP_EXTRA = {
    "sr", "sra", "ing", "dr", "dra", "etc", "vs", "art", "num",
    "pag", "cap", "fig", "ver", "ref", "eds", "col",
}

PATRONES_RUIDO = [
    r"©\s*\d{4}.*",
    r"Todos los derechos reservados.*",
    r"www\.\S+",
    r"http\S+",
    r"\d+\s*/\s*\d+",       # numeracion de pagina tipo 3/29
    r"^\s*\d+\s*$",         # lineas solo con numero
    r"Página \d+",
    r"^[-–—_]{3,}$",        # lineas de separacion
]

def limpiar_linea(linea: str) -> str:
    for patron in PATRONES_RUIDO:
        linea = re.sub(patron, "", linea, flags=re.IGNORECASE)
    linea = re.sub(r"\s{2,}", " ", linea)
    return linea.strip()

def extraer_parrafos(pdf_path: Path) -> list[dict]:
    """Extrae texto pagina a pagina y segmenta en parrafos."""
    doc = fitz.open(pdf_path)
    parrafos = []
    for num_pag, pag in enumerate(doc, start=1):
        texto_pag = pag.get_text("text")
        bloques = texto_pag.split("\n\n")
        for bloque in bloques:
            lineas = [limpiar_linea(l) for l in bloque.split("\n")]
            texto = " ".join(l for l in lineas if l)
            texto = re.sub(r"\s{2,}", " ", texto).strip()
            if len(texto) > 40:          # descartar fragmentos muy cortos
                parrafos.append({"pagina": num_pag, "texto_original": texto})
    doc.close()
    return parrafos

# ── lematizacion ─────────────────────────────────────────────────────────────
POS_UTILES = {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}

def lematizar(texto: str) -> tuple[str, str, int]:
    """
    Retorna (texto_lematizado_completo, solo_lemas_utiles, n_tokens).
    texto_lematizado_completo: todos los tokens con su lema (preserva estructura)
    solo_lemas_utiles: solo sustantivos, verbos, adjetivos y adverbios
    """
    # spaCy tiene limite de longitud por doc; procesar en chunks si es necesario
    if len(texto) > 100_000:
        chunks = [texto[i:i+90_000] for i in range(0, len(texto), 90_000)]
        docs = list(nlp.pipe(chunks))
    else:
        docs = [nlp(texto)]

    lemas_full  = []
    lemas_utiles = []
    n_tokens = 0

    for doc in docs:
        for token in doc:
            n_tokens += 1
            if not token.is_space:
                lemas_full.append(token.lemma_.lower())
            if (token.pos_ in POS_UTILES
                    and not token.is_stop
                    and not token.is_punct
                    and token.lemma_ not in STOP_EXTRA
                    and len(token.lemma_) > 2):
                lemas_utiles.append(token.lemma_.lower())

    return " ".join(lemas_full), " ".join(lemas_utiles), n_tokens


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

resumen_global = []

for fid, nombre_pdf in PDFS:
    pdf_path = DESCARGAS / nombre_pdf
    if not pdf_path.exists():
        print(f"  [!] No encontrado: {pdf_path}")
        continue

    slug = re.sub(r"[^a-z0-9]", "_", nombre_pdf.lower().replace(".pdf", ""))[:40]
    print(f"\n{'='*60}")
    print(f"Procesando [{fid}]: {nombre_pdf}")
    print(f"{'='*60}")

    # 1. Extraccion ─────────────────────────────────────────────────────────
    print("  [1/4] Extrayendo texto del PDF...")
    parrafos = extraer_parrafos(pdf_path)
    texto_raw = "\n\n".join(p["texto_original"] for p in parrafos)
    (RAW_DIR / f"{slug}_raw.txt").write_text(texto_raw, encoding="utf-8")
    print(f"        {len(parrafos)} parrafos extraidos")

    # 2. Limpieza ligera adicional ───────────────────────────────────────────
    print("  [2/4] Limpiando texto...")
    for p in parrafos:
        t = p["texto_original"]
        t = re.sub(r"[^\w\s.,;:!?()\"'\-áéíóúüñÁÉÍÓÚÜÑ]", " ", t)
        t = re.sub(r"\s{2,}", " ", t).strip()
        p["texto_limpio"] = t
    texto_limpio = "\n\n".join(p["texto_limpio"] for p in parrafos)
    (PROC_DIR / f"{slug}_limpio.txt").write_text(texto_limpio, encoding="utf-8")

    # 3. Lematizacion ────────────────────────────────────────────────────────
    print("  [3/4] Lematizando (esto puede tardar unos segundos)...")
    for p in parrafos:
        lemas_full, lemas_utiles, n_tok = lematizar(p["texto_limpio"])
        p["lemas_completos"] = lemas_full
        p["lemas_utiles"]    = lemas_utiles
        p["n_tokens"]        = n_tok

    texto_lematizado = "\n\n".join(p["lemas_utiles"] for p in parrafos)
    (PROC_DIR / f"{slug}_lematizado.txt").write_text(texto_lematizado, encoding="utf-8")

    # 4. CSV ─────────────────────────────────────────────────────────────────
    print("  [4/4] Guardando CSV...")
    df = pd.DataFrame([{
        "fuente_id":       fid,
        "archivo":         nombre_pdf,
        "pagina":          p["pagina"],
        "texto_original":  p["texto_original"],
        "texto_limpio":    p["texto_limpio"],
        "lemas_completos": p["lemas_completos"],
        "lemas_utiles":    p["lemas_utiles"],
        "n_tokens":        p["n_tokens"],
    } for p in parrafos])
    csv_path = PROC_DIR / f"{slug}_corpus.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")  # utf-8-sig para Excel

    # Estadisticas
    total_tokens  = df["n_tokens"].sum()
    total_parrafs = len(df)
    vocab_size    = len(set(" ".join(df["lemas_utiles"]).split()))
    print(f"\n  Resumen [{fid}]:")
    print(f"    Paginas procesadas : {df['pagina'].max()}")
    print(f"    Parrafos           : {total_parrafs}")
    print(f"    Tokens totales     : {total_tokens:,}")
    print(f"    Vocabulario unico  : {vocab_size:,} lemas")
    print(f"    CSV guardado en    : {csv_path.name}")

    resumen_global.append({
        "fuente_id":   fid,
        "archivo":     nombre_pdf,
        "paginas":     int(df["pagina"].max()),
        "parrafos":    total_parrafs,
        "tokens":      int(total_tokens),
        "vocab_unico": vocab_size,
    })

# ── resumen final ─────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("RESUMEN FINAL")
print(f"{'='*60}")
df_resumen = pd.DataFrame(resumen_global)
print(df_resumen.to_string(index=False))
df_resumen.to_csv(PROC_DIR / "resumen_corpus.csv", index=False, encoding="utf-8-sig")

print(f"\nArchivos generados en:")
print(f"  data/raw/       — textos crudos extraidos del PDF")
print(f"  data/processed/ — textos limpios, lematizados y CSV por documento")
print(f"\nPara mayor precision en lematizacion, instala el modelo grande:")
print(f"  python -m spacy download es_core_news_lg")
