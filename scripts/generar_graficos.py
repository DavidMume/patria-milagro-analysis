"""
Genera todos los gráficos del análisis de Colombia, Patria Milagro.
Ejecutar desde la raíz del repositorio: python scripts/generar_graficos.py
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIZ  = os.path.join(ROOT, "graficos")
os.makedirs(VIZ, exist_ok=True)
for sub in ["frecuencias", "tematico", "comparativo", "estructura"]:
    os.makedirs(os.path.join(VIZ, sub), exist_ok=True)

# ── paleta ─────────────────────────────────────────────────────────────────────
P = {
    "azul":    "#1B3A6B",
    "rojo":    "#C8102E",
    "amarillo":"#F5A623",
    "gris":    "#6B7280",
    "verde":   "#2E7D32",
    "celeste": "#2E5F8A",
    "claro":   "#F3F4F6",
}
FIRMA = "github.com/DavidMume/patria-milagro-analysis  |  David Muñoz · 2026"

plt.rcParams.update({
    "font.family":        "DejaVu Sans",
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "figure.dpi":         150,
    "axes.titlepad":      14,
})

def firma(fig):
    fig.text(0.99, 0.01, FIRMA, ha="right", fontsize=7, color=P["gris"])

def guardar(fig, carpeta, nombre):
    path = os.path.join(VIZ, carpeta, nombre)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    print(f"  OK  {path}")
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# 1. FRECUENCIAS — WordCloud
# ══════════════════════════════════════════════════════════════════════════════
print("\n[1] WordCloud …")
try:
    from wordcloud import WordCloud

    freq = {
        "patria": 180, "Colombia": 160, "nación": 120, "seguridad": 95,
        "corrupción": 88, "Estado": 85, "crimen": 80, "gobierno": 78,
        "República": 72, "democracia": 68, "Constitución": 65, "libertad": 60,
        "fuerza pública": 55, "territorios": 52, "ciudadano": 50, "familia": 48,
        "restauración": 45, "economía": 44, "narcotráfico": 42, "extorsión": 40,
        "verdad": 38, "salud": 36, "campo": 35, "autoridad": 34, "principios": 32,
        "dignidad": 30, "bien común": 28, "Ecopetrol": 26, "fiscal": 25,
        "minería": 24, "educación": 23, "mujeres": 22, "energía": 21,
        "anticorrupción": 20, "los nunca": 18, "blockchain": 15,
        "Constituyente": 14, "milicianización": 13, "veteranos": 12,
        "campesino": 20, "inversión": 18, "empleo": 16, "vivienda": 14,
    }

    # Colores oscuros legibles sobre fondo blanco — sin amarillos ni verdes claros
    COLORES_WC = [
        "#1B3A6B",  # azul oscuro
        "#C8102E",  # rojo
        "#2E5F8A",  # azul medio
        "#7B1D1D",  # rojo oscuro
        "#0D2B4E",  # azul muy oscuro
        "#8B0000",  # dark red
        "#1A4A7A",  # azul acero
        "#3B0A0A",  # granate
        "#2C4770",  # azul pizarra
        "#6B0F0F",  # rojo vino
    ]

    import random
    def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        return random.choice(COLORES_WC)

    wc = WordCloud(
        width=1400, height=700, background_color="white",
        color_func=color_func, max_words=60,
        prefer_horizontal=0.85, min_font_size=10,
    ).generate_from_frequencies(freq)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Términos más frecuentes — Colombia, Patria Milagro",
                 fontsize=14, fontweight="bold")
    firma(fig)
    guardar(fig, "frecuencias", "wordcloud.png")
except ImportError:
    print("  ⚠  wordcloud no instalado — omitiendo")


# ══════════════════════════════════════════════════════════════════════════════
# 2. FRECUENCIAS — Top 40 unigrams (estimado del corpus)
# ══════════════════════════════════════════════════════════════════════════════
print("[2] Top 40 unigrams …")
unigrams = [
    ("patria", 180), ("colombia", 160), ("nacion", 120), ("seguridad", 95),
    ("corrupcion", 88), ("estado", 85), ("crimen", 80), ("gobierno", 78),
    ("republica", 72), ("democracia", 68), ("constitucion", 65), ("libertad", 60),
    ("territorio", 55), ("ciudadano", 50), ("familia", 48), ("restauracion", 45),
    ("economia", 44), ("narcotrafico", 42), ("extorsion", 40), ("verdad", 38),
    ("salud", 36), ("campo", 35), ("autoridad", 34), ("principios", 32),
    ("dignidad", 30), ("bien", 28), ("ecopetrol", 26), ("fiscal", 25),
    ("mineria", 24), ("educacion", 23), ("mujeres", 22), ("energia", 21),
    ("anticorrupcion", 20), ("campesino", 20), ("inversion", 18),
    ("nunca", 18), ("empleo", 16), ("vivienda", 14), ("constituye", 13), ("reforma", 12),
]
labels = [u[0] for u in unigrams]
vals   = [u[1] for u in unigrams]
colores_uni = [P["rojo"] if v >= 80 else P["azul"] if v >= 40 else P["gris"] for v in vals]

fig, ax = plt.subplots(figsize=(11, 12))
bars = ax.barh(labels[::-1], vals[::-1], color=colores_uni[::-1], height=0.7)
ax.set_xlabel("Frecuencia estimada en el corpus", fontsize=11)
ax.set_title("Top 40 términos más frecuentes\nColombia, Patria Milagro — Abelardo de la Espriella 2026",
             fontsize=13, fontweight="bold")
for bar, v in zip(bars, vals[::-1]):
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
            str(v), va="center", fontsize=8, color=P["gris"])
firma(fig)
plt.tight_layout()
guardar(fig, "frecuencias", "top40_unigrams.png")


# ══════════════════════════════════════════════════════════════════════════════
# 3. TEMÁTICO — Propuestas por área
# ══════════════════════════════════════════════════════════════════════════════
print("[3] Propuestas por área …")
areas = {
    "Seguridad y control territorial": 24,
    "Anticorrupción": 18,
    "Economía y modelo de desarrollo": 14,
    "Campo y agro": 10,
    "Salud": 9,
    "Energía y minería": 8,
    "Educación": 6,
    "Mujeres y cuidado": 5,
    "Democracia e instituciones": 4,
    "Cultura": 2,
    "Medio ambiente": 2,
    "Bienestar animal": 1,
}
etiquetas = list(areas.keys())
valores   = list(areas.values())
col_areas = [P["rojo"] if v >= 18 else P["azul"] if v >= 8 else
             P["celeste"] if v >= 4 else P["gris"] for v in valores]

fig, ax = plt.subplots(figsize=(10, 7))
bars = ax.barh(range(len(etiquetas)), valores, color=col_areas, height=0.65)
ax.set_yticks(range(len(etiquetas)))
ax.set_yticklabels(etiquetas, fontsize=10)
ax.set_xlabel("Número de propuestas identificadas", fontsize=11)
ax.set_title("Propuestas por área temática\nColombia, Patria Milagro",
             fontsize=13, fontweight="bold")
for bar, v in zip(bars, valores):
    ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
            str(v), va="center", fontsize=9)
firma(fig)
plt.tight_layout()
guardar(fig, "tematico", "propuestas_por_area.png")


# ══════════════════════════════════════════════════════════════════════════════
# 4. TEMÁTICO — Distribución tipos de enunciado
# ══════════════════════════════════════════════════════════════════════════════
print("[4] Tipos de enunciado …")
tipos = {
    "Narrativa / retórica": 31,
    "Propuesta concreta": 27,
    "Diagnóstico": 18,
    "Ataque político": 10,
    "Marco ideológico": 8,
    "Cifra / dato": 4,
    "Promesa vaga": 2,
}
col_tipos = [P["gris"], P["azul"], P["celeste"], P["rojo"],
             P["amarillo"], P["verde"], "#9B2335"]

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.barh(list(tipos.keys()), list(tipos.values()), color=col_tipos, height=0.6)
for bar, v in zip(bars, tipos.values()):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f"{v}%", va="center", fontsize=10)
ax.set_xlabel("Porcentaje del corpus (%)", fontsize=11)
ax.set_title("Distribución del corpus por tipo de enunciado\nColombia, Patria Milagro",
             fontsize=13, fontweight="bold")
ax.set_xlim(0, 40)
firma(fig)
plt.tight_layout()
guardar(fig, "tematico", "tipos_enunciado.png")


# ══════════════════════════════════════════════════════════════════════════════
# 5. ESTRUCTURA — Verificabilidad de cifras
# ══════════════════════════════════════════════════════════════════════════════
print("[5] Verificabilidad …")
verif = {"Verificable\nexternal.": 12, "Parcialmente\nverificable": 13, "Sin fuente\nexplícita": 5}
col_v = [P["verde"], P["amarillo"], P["rojo"]]

fig, ax = plt.subplots(figsize=(6, 6))
wedges, texts, autotexts = ax.pie(
    verif.values(), labels=verif.keys(), colors=col_v,
    autopct="%1.0f%%", startangle=140, pctdistance=0.72,
    wedgeprops={"linewidth": 2, "edgecolor": "white"},
)
for t in autotexts:
    t.set_fontsize(13); t.set_fontweight("bold"); t.set_color("white")
ax.set_title("Verificabilidad de las 30 cifras extraídas\ndel corpus programático",
             fontsize=12, fontweight="bold")
firma(fig)
plt.tight_layout()
guardar(fig, "estructura", "verificabilidad_cifras.png")


# ══════════════════════════════════════════════════════════════════════════════
# 6. COMPARATIVO — Cobertura temática: resumen vs. pilares
# ══════════════════════════════════════════════════════════════════════════════
print("[6] Cobertura resumen vs. pilares …")
temas_cob = ["Seguridad", "Anticorrupción", "Economía", "Salud", "Campo",
             "Energía", "Educación", "Mujeres", "Democracia", "Cultura",
             "Medio\nAmbiente", "Marco\nideológico"]
resumen_val = [2, 2, 3, 2, 2, 2, 2, 2, 1, 1, 1, 0]
pilares_val = [5, 5, 4, 4, 4, 4, 3, 3, 3, 2, 2, 5]
x = np.arange(len(temas_cob)); w = 0.38

fig, ax = plt.subplots(figsize=(13, 6))
b1 = ax.bar(x - w/2, resumen_val, w, label="Resumen ejecutivo (3 págs.)",
            color=P["amarillo"], alpha=0.9)
b2 = ax.bar(x + w/2, pilares_val, w, label="Pilares completos",
            color=P["azul"], alpha=0.9)
ax.set_xticks(x); ax.set_xticklabels(temas_cob, fontsize=9)
ax.set_ylabel("Profundidad de cobertura (0–5)", fontsize=11)
ytick_labels = ["Ausente", "Mencionado", "Resumido", "Desarrollado", "Extenso", "Central"]
ax.set_yticks(range(6)); ax.set_yticklabels(ytick_labels, fontsize=9)
ax.set_title("Cobertura temática: Resumen ejecutivo vs. Pilares completos\nColombia, Patria Milagro — Abelardo de la Espriella 2026",
             fontsize=12, fontweight="bold")
ax.legend(fontsize=10); ax.set_ylim(0, 6)
firma(fig)
plt.tight_layout()
guardar(fig, "comparativo", "cobertura_resumen_vs_pilares.png")


# ══════════════════════════════════════════════════════════════════════════════
# 7. COMPARATIVO — Espriella vs. Cepeda: distribución temática
# ══════════════════════════════════════════════════════════════════════════════
print("[7] Comparativo Espriella vs. Cepeda …")

ejes = ["Seguridad", "Economía\nfiscal", "Instituciones\n/democracia",
        "Salud", "Campo\n/agro", "Educación", "Justicia\nsocial",
        "Paz\n/conflicto", "Género", "Medio\nambiente"]

espriella = [28, 18, 12,  9, 10,  6,  5,  4,  5,  3]
cepeda    = [ 8, 12, 14, 10,  8,  9, 18, 12,  6,  3]

x = np.arange(len(ejes)); w = 0.38

fig, ax = plt.subplots(figsize=(13, 6))
ax.bar(x - w/2, espriella, w, label="De la Espriella — Patria Milagro",
       color=P["azul"], alpha=0.9)
ax.bar(x + w/2, cepeda, w, label="Cepeda — Revolución Ética",
       color=P["rojo"], alpha=0.9)

ax.set_xticks(x); ax.set_xticklabels(ejes, fontsize=9)
ax.set_ylabel("% del espacio programático dedicado al eje", fontsize=11)
ax.set_title("Distribución temática comparada\nEspriella (Patria Milagro) vs. Cepeda (Revolución Ética) — 2026",
             fontsize=12, fontweight="bold")
ax.legend(fontsize=10)

nota = ("Nota: datos de Cepeda extraídos del análisis NLP disponible en\n"
        "github.com/DavidMume/analisis-plan-gobierno-ivan-cepeda-2026")
fig.text(0.01, 0.01, nota, ha="left", fontsize=7, color=P["gris"])
firma(fig)
plt.tight_layout()
guardar(fig, "comparativo", "espriella_vs_cepeda_tematico.png")


# ══════════════════════════════════════════════════════════════════════════════
# 8. COMPARATIVO — Tono del discurso: propositivo vs. confrontacional
# ══════════════════════════════════════════════════════════════════════════════
print("[8] Tono del discurso comparado …")

categorias = ["Propuesta\nconcreta", "Diagnóstico\nneutro", "Narrativa\nmotivacional",
              "Ataque\npolítico", "Marco\nideológico", "Promesa\nvaga"]
esp_pct   = [27, 18, 31, 10, 8, 6]
cep_pct   = [32, 22, 20, 14, 7, 5]

x = np.arange(len(categorias)); w = 0.38

fig, ax = plt.subplots(figsize=(11, 5))
ax.bar(x - w/2, esp_pct, w, label="De la Espriella", color=P["azul"], alpha=0.9)
ax.bar(x + w/2, cep_pct, w, label="Cepeda",          color=P["rojo"], alpha=0.9)
ax.set_xticks(x); ax.set_xticklabels(categorias, fontsize=9)
ax.set_ylabel("% del corpus", fontsize=11)
ax.set_title("Composición del discurso: tipos de enunciado comparados\nEspriella vs. Cepeda — 2026",
             fontsize=12, fontweight="bold")
ax.legend(fontsize=10)
nota = "Datos Cepeda: github.com/DavidMume/analisis-plan-gobierno-ivan-cepeda-2026"
fig.text(0.01, 0.01, nota, ha="left", fontsize=7, color=P["gris"])
firma(fig)
plt.tight_layout()
guardar(fig, "comparativo", "tono_espriella_vs_cepeda.png")


# ══════════════════════════════════════════════════════════════════════════════
# 9. ESTRUCTURA — Densidad programática por fuente
# ══════════════════════════════════════════════════════════════════════════════
print("[9] Densidad programática por fuente …")

fuentes = ["Pilares\ntemáticos\n(web)", "Programa\noficial\n(29 págs.)",
           "Valle\ndel Cauca\n(47 págs.)", "Pilares\nFundacionales\n(14 págs.)",
           "Resumen\nejecutivo\n(3 págs.)"]
propuestas_concretas = [38, 25, 18, 2, 12]
narrativa_ideologia  = [30, 20, 15, 55, 25]

x = np.arange(len(fuentes)); w = 0.38

fig, ax = plt.subplots(figsize=(11, 5))
ax.bar(x - w/2, propuestas_concretas, w, label="Propuestas concretas (%)", color=P["azul"])
ax.bar(x + w/2, narrativa_ideologia,  w, label="Narrativa / ideología (%)", color=P["amarillo"])
ax.set_xticks(x); ax.set_xticklabels(fuentes, fontsize=9)
ax.set_ylabel("% del contenido del documento", fontsize=11)
ax.set_title("Densidad programática por documento\n¿Dónde están las propuestas concretas?",
             fontsize=12, fontweight="bold")
ax.legend(fontsize=10)
firma(fig)
plt.tight_layout()
guardar(fig, "estructura", "densidad_por_fuente.png")


print("\nTodos los graficos generados en /graficos/")
