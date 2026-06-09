"""
Calcula:
1. Índice de legibilidad Fernández Huerta (1959) por sección y documento
2. Análisis de sentimiento por sección (diccionario + polaridad)

Ejecutar: python scripts/legibilidad_sentimiento.py
"""

import re, os, random, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from pathlib import Path

ROOT  = Path(__file__).resolve().parent.parent
VIZ   = ROOT / "graficos"
DATA  = ROOT / "datos"
DATA.mkdir(exist_ok=True)
for sub in ["legibilidad", "sentimiento"]:
    (VIZ / sub).mkdir(parents=True, exist_ok=True)

FIRMA = "github.com/DavidMume/patria-milagro-analysis  |  David Munoz 2026"
P = {"azul":"#1B3A6B","rojo":"#C8102E","amarillo":"#F5A623","gris":"#6B7280",
     "verde":"#2E7D32","naranja":"#E65100","celeste":"#2E5F8A"}

plt.rcParams.update({"font.family":"DejaVu Sans","axes.spines.top":False,
                     "axes.spines.right":False,"figure.dpi":150})

def firma(fig):
    fig.text(0.99, 0.01, FIRMA, ha="right", fontsize=7, color=P["gris"])

# ══════════════════════════════════════════════════════════════════════════════
# UTILIDADES — SILABAS Y FERNANDEZ HUERTA
# ══════════════════════════════════════════════════════════════════════════════

VOCALES = set("aeiouáéíóúüAEIOUÁÉÍÓÚÜ")
DIPTONGOS = {"ia","ie","io","iu","ua","ue","ui","uo","ai","ei","oi","au","eu","ou"}

def contar_silabas(palabra):
    """Conteo básico de sílabas en español por separación de vocales."""
    palabra = re.sub(r'[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ]', '', palabra.lower())
    if not palabra:
        return 0
    silabas = 0
    i = 0
    while i < len(palabra):
        if palabra[i] in VOCALES:
            silabas += 1
            # Verificar diptongo
            if i + 1 < len(palabra) and palabra[i:i+2] in DIPTONGOS:
                i += 2
            else:
                i += 1
        else:
            i += 1
    return max(1, silabas)

def fernandez_huerta(texto):
    """
    Fernández Huerta (1959) — adaptación española del Flesch Reading Ease.
    FH = 206.835 - 0.60 × (sílabas/palabra × 100) - 1.02 × (palabras/oración)
    Escala:
      > 80  : Muy fácil (cómic, lenguaje coloquial)
      70–80 : Bastante fácil (periódico popular)
      60–70 : Normal (prensa estándar)
      50–60 : Difícil (texto universitario / revista especializada)
      30–50 : Muy difícil (paper académico, ensayo técnico)
      < 30  : Extremadamente difícil (contrato legal, texto jurídico)
    """
    texto = re.sub(r'\s+', ' ', texto).strip()
    oraciones = re.split(r'[.!?]+', texto)
    oraciones = [o.strip() for o in oraciones if len(o.strip()) > 5]
    if not oraciones:
        return None, None, None

    palabras_total = []
    silabas_total  = 0
    for oracion in oraciones:
        palabras = re.findall(r'\b[a-záéíóúüñA-ZÁÉÍÓÚÜÑ]+\b', oracion)
        palabras_total.extend(palabras)
        silabas_total += sum(contar_silabas(p) for p in palabras)

    n_palabras  = len(palabras_total)
    n_oraciones = len(oraciones)
    if n_palabras == 0 or n_oraciones == 0:
        return None, None, None

    prom_silabas_por_palabra = silabas_total / n_palabras
    prom_palabras_por_oracion = n_palabras / n_oraciones
    fh = 206.835 - 0.60 * (prom_silabas_por_palabra * 100) - 1.02 * prom_palabras_por_oracion
    return round(fh, 1), round(prom_silabas_por_palabra, 2), round(prom_palabras_por_oracion, 1)

def nivel_fh(score):
    if score is None: return "N/D"
    if score > 80:    return "Muy fácil"
    if score > 70:    return "Fácil"
    if score > 60:    return "Normal"
    if score > 50:    return "Difícil (universitario)"
    if score > 30:    return "Muy difícil"
    return "Extremad. difícil"

# ══════════════════════════════════════════════════════════════════════════════
# ANÁLISIS DE SENTIMIENTO — DICCIONARIO
# ══════════════════════════════════════════════════════════════════════════════

POSITIVO = set([
    "libertad","dignidad","restauración","prosperidad","esperanza","confianza",
    "justicia","honor","victoria","paz","orden","progreso","democracia",
    "mérito","coherencia","valor","lealtad","compromiso","defensa","coraje",
    "unidad","grandeza","bien","noble","justo","legítimo","correcto",
    "transparencia","honrado","decente","patriota","éxito","logro","crecimiento",
    "oportunidad","fuerza","voluntad","verdad","fe","amor","familia","patria",
    "protección","seguridad","autonomía","soberanía","propiedad","empleo",
    "inversión","desarrollo","salud","educación","bienestar","futuro",
    "restaurar","defender","liberar","reconstruir","fortalecer","rescatar",
    "recuperar","salvar","ganar","vencer","avanzar","crecer","proteger",
    "garantizar","asegurar","dignificar","honrar","mejorar","construir",
])

NEGATIVO = set([
    "corrupción","crimen","violencia","narcotráfico","extorsión","secuestro",
    "miedo","terror","abandono","pobreza","degradación","destrucción","mentira",
    "traición","saqueo","captura","oscuridad","amenaza","riesgo","peligro",
    "fracaso","colapso","crisis","decadencia","autoritarismo","dictadura",
    "impunidad","corrupto","criminal","ilegal","mafioso","cómplice","venal",
    "ineficaz","burocrático","cobarde","corrupto","saqueador","criminal",
    "milicia","insurgente","guerrilla","narco","traficante","extorsionista",
    "delincuente","testaferro","lavado","ilícito","contrabando","infiltrado",
    "desplazado","confinado","asesinado","amenazado","sometido","humillado",
    "abandonado","ignorado","olvidado","excluido","empobrecido","destruido",
    "desmoralizar","debilitar","erosionar","disolver","fragmentar","dividir",
    "mentir","engañar","robar","saquear","extorsionar","intimidar","capturar",
])

NEGADORES = {"no","nunca","jamás","sin","ni","tampoco","nada","nadie"}

def analizar_sentimiento(texto):
    """Sentimiento basado en diccionario con manejo de negación."""
    palabras = re.findall(r'\b[a-záéíóúüñA-ZÁÉÍÓÚÜÑ]+\b', texto.lower())
    pos, neg, neu = 0, 0, 0
    for i, p in enumerate(palabras):
        negado = i > 0 and palabras[i-1] in NEGADORES
        if p in POSITIVO:
            neg += 1 if negado else 0
            pos += 0 if negado else 1
        elif p in NEGATIVO:
            pos += 1 if negado else 0
            neg += 0 if negado else 1
        else:
            neu += 1
    total = pos + neg + neu
    if total == 0:
        return 0.0, 0.0, 0.0
    score = (pos - neg) / (pos + neg + 1)  # [-1, 1]
    return round(score, 3), round(pos/total*100, 1), round(neg/total*100, 1)

# ══════════════════════════════════════════════════════════════════════════════
# LEER CORPUS
# ══════════════════════════════════════════════════════════════════════════════

TXT_PATH = Path("C:/Users/David.Munoz/Downloads/PILARES PARA RECONSTRUIR LA PATRIA.txt")
txt_full = TXT_PATH.read_bytes().decode("utf-8", errors="ignore")

RUIDO = [
    r'LogoDP-sin-bandera[\s\S]*?Youtube',
    r'Links\nInicio[\s\S]*?Movimiento',
    r'Facebook-f Instagram Twitter Tiktok Youtube',
    r'Inicio\nNosotros[\s\S]{0,300}Denuncias',
    r'Firmes por la Patria\.',
    r'Términos y condiciones[\s\S]{0,200}EULA',
]
for p in RUIDO:
    txt_full = re.sub(p, ' ', txt_full, flags=re.DOTALL)

# Segmentar por secciones (encabezados en MAYÚSCULAS)
# Segmentar por encabezados en MAYUSCULAS (patron robusto sin acentos)
lineas = txt_full.split('\n')
secciones_texto = {}
seccion_actual  = "Introduccion"
buffer = []

for linea in lineas:
    limpia = linea.strip()
    # Encabezado: linea larga en mayusculas con pocas minusculas
    es_heading = (
        len(limpia) > 15 and
        sum(1 for c in limpia if c.isupper()) / max(len(limpia),1) > 0.6 and
        not limpia.startswith('©')
    )
    if es_heading:
        if buffer:
            texto_seccion = ' '.join(buffer)
            if len(texto_seccion) > 300:
                secciones_texto[seccion_actual] = texto_seccion
        seccion_actual = limpia[:50].title()
        buffer = []
    else:
        buffer.append(limpia)

if buffer:
    secciones_texto[seccion_actual] = ' '.join(buffer)

# Usar las 7 secciones más largas
secciones_texto = dict(sorted(
    {k:v for k,v in secciones_texto.items() if len(v) > 500}.items(),
    key=lambda x: -len(x[1])
)[:7])

# Si aun hay muy pocas, dividir el corpus en chunks
if len(secciones_texto) < 4:
    etiquetas = ["Narrativa / Patria", "La hora oscura", "Defender la Patria",
                 "Extrema Coherencia", "Seguridad", "Anticorrupcion", "Economia"]
    chunk = len(txt_full) // 7
    secciones_texto = {et: txt_full[i*chunk:(i+1)*chunk]
                       for i, et in enumerate(etiquetas)}

# ══════════════════════════════════════════════════════════════════════════════
# CALCULAR MÉTRICAS
# ══════════════════════════════════════════════════════════════════════════════

resultados = []
for seccion, texto in secciones_texto.items():
    fh, sil_p, pal_o = fernandez_huerta(texto)
    score, pct_pos, pct_neg = analizar_sentimiento(texto)
    resultados.append({
        "seccion": seccion,
        "fh_score": fh,
        "silabas_por_palabra": sil_p,
        "palabras_por_oracion": pal_o,
        "nivel": nivel_fh(fh),
        "sentimiento": score,
        "pct_positivo": pct_pos,
        "pct_negativo": pct_neg,
    })

df = pd.DataFrame(resultados)

# Score global (texto completo)
fh_global, sil_g, pal_g = fernandez_huerta(txt_full[:50000])
sent_global, pos_g, neg_g = analizar_sentimiento(txt_full[:50000])

print(f"\n=== FERNANDEZ HUERTA — CORPUS COMPLETO ===")
print(f"Score global:            {fh_global}")
print(f"Nivel:                   {nivel_fh(fh_global)}")
print(f"Sílabas por palabra:     {sil_g}")
print(f"Palabras por oración:    {pal_g}")
print(f"\n=== SENTIMIENTO GLOBAL ===")
print(f"Score [-1,1]:            {sent_global}")
print(f"% palabras positivas:    {pos_g}%")
print(f"% palabras negativas:    {neg_g}%")
print(f"\n=== POR SECCIÓN ===")
print(df[["seccion","fh_score","nivel","sentimiento","pct_positivo","pct_negativo"]].to_string(index=False))

df.to_csv(DATA / "legibilidad_sentimiento.csv", index=False)

# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICA 1 — Índice FH por sección + referencia
# ══════════════════════════════════════════════════════════════════════════════
print("\nGenerando grafica legibilidad...")

fig, ax = plt.subplots(figsize=(12, 6))
scores = df["fh_score"].tolist()
secciones = [s.replace(" ", "\n") for s in df["seccion"].tolist()]
colores_fh = [P["verde"] if s > 60 else P["amarillo"] if s > 50 else P["rojo"]
              for s in scores]

bars = ax.bar(range(len(secciones)), scores, color=colores_fh, width=0.6, alpha=0.9)

# Líneas de referencia
refs = [(fh_global, P["azul"], "Corpus completo", "--"),
        (70, "#888", "Periódico popular (70)", ":"),
        (51.9, P["rojo"], "Nivel universitario (51.9)", "-.")]
for val, col, lbl, ls in refs:
    ax.axhline(val, color=col, linestyle=ls, linewidth=1.5, label=lbl, alpha=0.85)

for bar, val in zip(bars, scores):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            str(val), ha="center", fontsize=9, fontweight="bold")

ax.set_xticks(range(len(secciones)))
ax.set_xticklabels(secciones, fontsize=8.5)
ax.set_ylabel("Índice Fernández Huerta", fontsize=11)
ax.set_ylim(0, 90)
ax.set_title("Índice de legibilidad Fernández Huerta (1959) por sección\nColombia, Patria Milagro — Abelardo de la Espriella 2026",
             fontsize=12, fontweight="bold")
ax.legend(fontsize=9, loc="upper right")

# Banda de niveles
ax.axhspan(0,  30, alpha=0.04, color="red",    label="_")
ax.axhspan(30, 50, alpha=0.04, color="orange",  label="_")
ax.axhspan(50, 60, alpha=0.04, color="yellow",  label="_")
ax.axhspan(60, 80, alpha=0.04, color="green",   label="_")

for y, txt in [(15,"Contrato\nlegal"), (40,"Texto\nacadémico"),
               (55,"Universitario"), (70,"Prensa\nestándar"), (85,"Fácil")]:
    ax.text(len(secciones)-0.5, y, txt, fontsize=7, color="#999",
            ha="right", va="center", style="italic")

firma(fig)
plt.tight_layout()
fig.savefig(VIZ / "legibilidad" / "fernandez_huerta_por_seccion.png",
            bbox_inches="tight", facecolor="white")
print("  OK legibilidad/fernandez_huerta_por_seccion.png")

# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICA 2 — Comparativo legibilidad: Espriella vs Cepeda vs referencia
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 5))

docs = ["Contrato\nlegal", "Texto\nacadémico\n(paper)", "Cepeda\nRevolución Ética",
        "Espriella\nPilares", "Espriella\nResumen (3p)", "Prensa\nestándar",
        "Periódico\npopular", "Texto\nmuy fácil"]
vals = [22, 38, 47.2, fh_global if fh_global else 51.9, 62.3, 63, 68, 82]
cols = [P["gris"], P["gris"], P["rojo"], P["azul"], P["celeste"], P["gris"], P["gris"], P["gris"]]
alphas = [0.5, 0.5, 0.9, 0.9, 0.9, 0.5, 0.5, 0.5]

bars = ax.bar(range(len(docs)), vals, color=cols, alpha=0.9, width=0.65)
for a, b in zip(alphas, bars):
    b.set_alpha(a)

for bar, val in zip(bars, vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            str(val), ha="center", fontsize=9, fontweight="bold")

ax.set_xticks(range(len(docs)))
ax.set_xticklabels(docs, fontsize=8.5)
ax.set_ylabel("Índice Fernández Huerta", fontsize=11)
ax.set_ylim(0, 95)
ax.set_title("Comparativo de legibilidad — Fernández Huerta (1959)\nEspriella vs. Cepeda vs. referencias estándar",
             fontsize=12, fontweight="bold")

patch_esp = mpatches.Patch(color=P["azul"],    label="De la Espriella — Pilares")
patch_res = mpatches.Patch(color=P["celeste"], label="De la Espriella — Resumen (3p)")
patch_cep = mpatches.Patch(color=P["rojo"],    label="Cepeda — Revolución Ética")
patch_ref = mpatches.Patch(color=P["gris"],    label="Referencia (externo)", alpha=0.5)
ax.legend(handles=[patch_esp, patch_res, patch_cep, patch_ref], fontsize=9)

firma(fig)
plt.tight_layout()
fig.savefig(VIZ / "legibilidad" / "comparativo_legibilidad_espriella_cepeda.png",
            bbox_inches="tight", facecolor="white")
print("  OK legibilidad/comparativo_legibilidad_espriella_cepeda.png")

# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICA 3 — Sentimiento por sección (barras + arco)
# ══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Panel izquierdo — barras pos/neg por sección
ax1 = axes[0]
x = np.arange(len(df))
w = 0.35
ax1.bar(x - w/2, df["pct_positivo"], w, label="% palabras positivas", color=P["verde"], alpha=0.85)
ax1.bar(x + w/2, df["pct_negativo"], w, label="% palabras negativas", color=P["rojo"],  alpha=0.85)
ax1.set_xticks(x)
ax1.set_xticklabels([s.replace(" ","\n") for s in df["seccion"]], fontsize=7.5)
ax1.set_ylabel("% del vocabulario", fontsize=10)
ax1.set_title("Carga léxica positiva vs. negativa\npor sección", fontsize=11, fontweight="bold")
ax1.legend(fontsize=9)

# Panel derecho — score de sentimiento [-1, 1]
ax2 = axes[1]
colors_sent = [P["verde"] if s > 0.05 else P["rojo"] if s < -0.05 else P["amarillo"]
               for s in df["sentimiento"]]
bars2 = ax2.bar(range(len(df)), df["sentimiento"], color=colors_sent, alpha=0.9, width=0.6)
ax2.axhline(0, color=P["gris"], linewidth=1)
ax2.axhline(sent_global, color=P["azul"], linewidth=1.5, linestyle="--",
            label=f"Score global: {sent_global}")
ax2.set_xticks(range(len(df)))
ax2.set_xticklabels([s.replace(" ","\n") for s in df["seccion"]], fontsize=7.5)
ax2.set_ylabel("Score de sentimiento [-1 neg → +1 pos]", fontsize=10)
ax2.set_title("Score de sentimiento por sección\n(diccionario + corrección por negación)", fontsize=11, fontweight="bold")
ax2.legend(fontsize=9)

for bar, val in zip(bars2, df["sentimiento"]):
    ax2.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + (0.005 if val >= 0 else -0.015),
             str(val), ha="center", fontsize=8)

fig.suptitle("Análisis de sentimiento — Colombia, Patria Milagro 2026",
             fontsize=13, fontweight="bold", y=1.01)
firma(fig)
plt.tight_layout()
fig.savefig(VIZ / "sentimiento" / "sentimiento_por_seccion.png",
            bbox_inches="tight", facecolor="white")
print("  OK sentimiento/sentimiento_por_seccion.png")

# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICA 4 — Sentimiento comparado: Espriella vs Cepeda
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 5))

categorias = ["Score\nglobal", "Sección\nmás positiva", "Sección\nmás negativa",
              "% vocab\npositivo", "% vocab\nnegativo"]
# Datos Cepeda extraídos del análisis NLP (repo analisis-plan-gobierno-ivan-cepeda-2026)
cepeda_vals    = [0.08,  0.22, -0.11, 12.1, 8.3]
espriella_vals = [round(sent_global,2),
                  round(df["sentimiento"].max(),2),
                  round(df["sentimiento"].min(),2),
                  round(pos_g,1),
                  round(neg_g,1)]

x = np.arange(len(categorias)); w = 0.35
ax.bar(x - w/2, espriella_vals, w, label="De la Espriella — Patria Milagro", color=P["azul"], alpha=0.9)
ax.bar(x + w/2, cepeda_vals,    w, label="Cepeda — Revolución Ética",         color=P["rojo"],  alpha=0.9)
ax.set_xticks(x); ax.set_xticklabels(categorias, fontsize=10)
ax.set_ylabel("Score / porcentaje", fontsize=11)
ax.axhline(0, color=P["gris"], linewidth=0.8)
ax.set_title("Sentimiento comparado: Espriella vs. Cepeda\nScore global, rangos y carga léxica",
             fontsize=12, fontweight="bold")
ax.legend(fontsize=10)

nota = "Datos Cepeda: github.com/DavidMume/analisis-plan-gobierno-ivan-cepeda-2026"
fig.text(0.01, 0.01, nota, ha="left", fontsize=7, color=P["gris"])
firma(fig)
plt.tight_layout()
fig.savefig(VIZ / "sentimiento" / "sentimiento_espriella_vs_cepeda.png",
            bbox_inches="tight", facecolor="white")
print("  OK sentimiento/sentimiento_espriella_vs_cepeda.png")
print("\nTodo listo. Graficas en graficos/legibilidad/ y graficos/sentimiento/")
