#!/usr/bin/env python3
"""
Análisis NLP completo del programa de gobierno de Abelardo de la Espriella
Colombia, Patria Milagro — Elecciones 2026-2030.
Replicación exacta de la metodología usada para el análisis de Iván Cepeda.
"""

import os, sys, re, json, warnings, subprocess
warnings.filterwarnings("ignore")

ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_PATH = os.path.join(ROOT, "sources", "pdfs", "f04_programa_oficial.pdf")
DATOS   = os.path.join(ROOT, "datos")
GFX     = os.path.join(ROOT, "graficos")

for sub in ["frecuencias", "tematico", "sentimiento", "semantica",
            "estructura", "figuras_politicas"]:
    os.makedirs(os.path.join(GFX, sub), exist_ok=True)
os.makedirs(DATOS, exist_ok=True)

FIRMA = "github.com/DavidMume/patria-milagro-analysis  |  David Muñoz · 2026"

def gfx(carpeta, nombre):
    return os.path.join(GFX, carpeta, nombre)

def datos(nombre):
    return os.path.join(DATOS, nombre)

# ─── auto-install ─────────────────────────────────────────────────────────────
def ensure(pkg, imp=None):
    try: __import__(imp or pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

for p, i in [
    ("pymupdf","fitz"), ("nltk",None), ("spacy",None),
    ("scikit-learn","sklearn"), ("gensim",None), ("wordcloud",None),
    ("matplotlib",None), ("seaborn",None), ("networkx",None),
    ("pyLDAvis","pyLDAvis"), ("pysentimiento",None), ("lexicalrichness",None),
]:
    ensure(p, i)

# ─── imports ──────────────────────────────────────────────────────────────────
import fitz
import nltk
import spacy
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
import networkx as nx
from collections import Counter
from itertools import combinations

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from wordcloud import WordCloud

from gensim.models import Word2Vec
from gensim.models.coherencemodel import CoherenceModel
from gensim import corpora

try:
    import pyLDAvis
    import pyLDAvis.lda_model as pyLDAvis_sklearn
    HAS_PYLDAVIS = True
except Exception:
    HAS_PYLDAVIS = False

try:
    from pysentimiento import create_analyzer
    HAS_PYSENTIMIENTO = True
except Exception:
    HAS_PYSENTIMIENTO = False

try:
    from lexicalrichness import LexicalRichness
    HAS_LR = True
except Exception:
    HAS_LR = False

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
})

def firma(fig):
    fig.text(0.99, 0.01, FIRMA, ha="right", fontsize=7, color="#6B7280")

# ─── NLTK ─────────────────────────────────────────────────────────────────────
for res in ["stopwords", "punkt", "punkt_tab"]:
    try:
        nltk.data.find(f"tokenizers/{res}" if "punkt" in res else f"corpora/{res}")
    except LookupError:
        nltk.download(res, quiet=True)

from nltk.corpus import stopwords as nltk_sw
from nltk.util import ngrams as nltk_ngrams

# ─── spaCy ────────────────────────────────────────────────────────────────────
try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "es_core_news_sm", "-q"])
    nlp = spacy.load("es_core_news_sm")

# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("SECCIÓN 1 — EXTRACCIÓN Y LIMPIEZA DE TEXTO")
print("═"*60)

doc_pdf   = fitz.open(PDF_PATH)
pages_raw = [page.get_text("text") for page in doc_pdf]
full_raw  = "\n".join(pages_raw)
print(f"Páginas extraídas: {len(pages_raw)}")

with open(datos("raw_text.txt"), "w", encoding="utf-8") as f:
    f.write(full_raw)

base_sw = set(nltk_sw.words("spanish"))
custom_sw = {
    "así","más","será","solo","puede","debe","cada","través","mediante",
    "tanto","bien","hacer","tener","parte","también","sino","ante","desde",
    "hacia","entre","sobre","donde","cual","cuales","este","esta","estos",
    "estas","ese","esa","esos","esas","uno","una","unos","unas","ser",
    "estar","haber","hay","han","son","sus","del","las","los","les","nos",
    "como","pero","para","por","con","sin","todo","todos","toda","todas",
    "mismo","misma","mismos","mismas","muy","cuando","quien","quienes",
    "que","qué","donde","cómo","porque","si","ya","aún","sólo",
    "colombiano","colombiana","colombianos","colombianas","gobierno",
    "nacional","país","público","pública","años","año","mil","millones",
    "deben","hacer","abelardo","espriella","candidato","patria","milagro",
    "propone","propuesta","propuestas","nuestro","nuestros","nuestra",
}
STOPWORDS = base_sw | custom_sw

def clean_text(t):
    t = re.sub(r"http\S+|www\S+", " ", t)
    t = re.sub(r"[0-9]+", " ", t)
    t = re.sub(r"[^\w\sáéíóúüñÁÉÍÓÚÜÑ]", " ", t)
    return re.sub(r"\s+", " ", t).strip().lower()

pages_clean  = [clean_text(p) for p in pages_raw]
nlp.max_length = 2_000_000

pages_tokens = []
for pg in pages_clean:
    doc_sp = nlp(pg[:100_000])
    tokens = [
        t.lemma_ for t in doc_sp
        if t.is_alpha and t.lemma_.lower() not in STOPWORDS and len(t.lemma_) > 2
    ]
    pages_tokens.append(tokens)

all_tokens   = [t for pg in pages_tokens for t in pg]
total_words  = len(all_tokens)
unique_words = len(set(all_tokens))
print(f"Tokens limpios: {total_words:,}  |  únicos: {unique_words:,}")
print(f"Promedio por página: {total_words/max(len(pages_tokens),1):.1f}")

clean_corpus = " ".join(all_tokens)
with open(datos("clean_tokens.txt"), "w", encoding="utf-8") as f:
    f.write(clean_corpus)

# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("SECCIÓN 2 — ANÁLISIS DE FRECUENCIAS")
print("═"*60)

freq = Counter(all_tokens)

# ── Wordcloud ──────────────────────────────────────────────────────────────
print("Generando wordcloud…")
import random
PALETTE = ["#0A1F44","#1B2A6B","#8B0000","#A30000","#1C3A5E",
           "#2C3E6B","#C8102E","#0D1B3E","#5C0A0A"]

def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return random.choice(PALETTE)

wc = WordCloud(
    width=1600, height=800, background_color="white",
    color_func=color_func, max_words=150,
    prefer_horizontal=0.75, collocations=False,
).generate_from_frequencies(freq)

fig, ax = plt.subplots(figsize=(14, 7))
ax.imshow(wc, interpolation="bilinear")
ax.axis("off")
ax.set_title("Términos más frecuentes — Colombia, Patria Milagro\nAbelardo de la Espriella 2026",
             fontsize=14, fontweight="bold")
firma(fig)
fig.savefig(gfx("frecuencias","wordcloud.png"), bbox_inches="tight", facecolor="white")
plt.close()
print("  Guardado: wordcloud.png")

# ── helper hbar ───────────────────────────────────────────────────────────
def hbar(data, title, path, color="steelblue"):
    labels, values = zip(*data)
    fig, ax = plt.subplots(figsize=(12, max(6, len(labels)*0.38)))
    bars = ax.barh(range(len(labels)), values, color=color)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlabel("Frecuencia")
    for bar, v in zip(bars, values):
        ax.text(bar.get_width()+0.3, bar.get_y()+bar.get_height()/2,
                str(v), va="center", fontsize=8)
    firma(fig)
    plt.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  Guardado: {os.path.basename(path)}")

# ── Top 40 unigramas ──────────────────────────────────────────────────────
top40 = freq.most_common(40)
hbar(top40[::-1],
     "Top 40 términos más frecuentes\nColombia, Patria Milagro — Espriella 2026",
     gfx("frecuencias","top40_unigrams.png"),
     color="#1B3A6B")

# ── Bigramas (texto crudo, no lematizado) ─────────────────────────────────
raw_words_all = []
for pg in pages_raw:
    words = re.findall(r"\b[a-záéíóúüñ]{3,}\b", pg.lower())
    sw_set = STOPWORDS
    raw_words_all.extend([w for w in words if w not in sw_set])

bg_freq = Counter(nltk_ngrams(raw_words_all, 2)).most_common(25)
hbar([(" ".join(b), c) for b, c in bg_freq][::-1],
     "Top 25 bigramas — Patria Milagro",
     gfx("frecuencias","top25_bigrams.png"),
     color="#C8102E")

tg_freq = Counter(nltk_ngrams(raw_words_all, 3)).most_common(20)
hbar([(" ".join(t), c) for t, c in tg_freq][::-1],
     "Top 20 trigramas — Patria Milagro",
     gfx("frecuencias","top20_trigrams.png"),
     color="#2E7D32")

qg_freq = Counter(nltk_ngrams(raw_words_all, 4)).most_common(10)
hbar([(" ".join(q), c) for q, c in qg_freq][::-1],
     "Top 10 cuadrigramas — Patria Milagro",
     gfx("frecuencias","top10_quadgrams.png"),
     color="#6A0DAD")

# ── Ley de Zipf ───────────────────────────────────────────────────────────
print("Graficando ley de Zipf…")
ranks  = np.arange(1, len(freq)+1)
counts = np.array([c for _, c in freq.most_common()])
fig, ax = plt.subplots(figsize=(8, 5))
ax.loglog(ranks, counts, "b.", markersize=2, alpha=0.6)
fit_n = min(300, len(ranks))
if fit_n > 2:
    m, b = np.polyfit(np.log(ranks[:fit_n]), np.log(counts[:fit_n]), 1)
    ax.loglog(ranks[:fit_n], np.exp(b)*ranks[:fit_n]**m, "r-",
              label=f"pendiente={m:.2f}", linewidth=1.5)
ax.set_xlabel("Rango (log)")
ax.set_ylabel("Frecuencia (log)")
ax.set_title("Ley de Zipf — Patria Milagro", fontsize=12, fontweight="bold")
ax.legend()
firma(fig)
plt.tight_layout()
fig.savefig(gfx("frecuencias","zipf_law.png"), bbox_inches="tight", facecolor="white")
plt.close()
print("  Guardado: zipf_law.png")

# ── Riqueza léxica ────────────────────────────────────────────────────────
if HAS_LR and len(clean_corpus.split()) >= 100:
    try:
        lex  = LexicalRichness(clean_corpus)
        ttr  = lex.ttr
        mtld = None
        try: mtld = lex.mtld(threshold=0.72)
        except Exception: pass
        print(f"TTR: {ttr:.4f}  MTLD: {mtld}")
        with open(datos("lexical_richness.txt"), "w") as f:
            f.write(f"TTR: {ttr:.4f}\nMTLD: {mtld}\n")
    except Exception as e:
        print(f"  Riqueza léxica omitida: {e}")

# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("SECCIÓN 3 — MODELADO DE TÓPICOS (LDA)")
print("═"*60)

page_docs = [" ".join(toks) for toks in pages_tokens if len(toks) > 5]
N_TOPICS  = min(7, max(2, len(page_docs) // 2))

TOPIC_LABELS = {
    0: "Seguridad y orden",
    1: "Anticorrupción",
    2: "Economía y empresa",
    3: "Instituciones / República",
    4: "Salud y bienestar",
    5: "Campo y territorio",
    6: "Energía y recursos",
}

cv  = CountVectorizer(max_df=0.95, min_df=1, max_features=3000)
dtm = cv.fit_transform(page_docs)
lda = LatentDirichletAllocation(n_components=N_TOPICS, random_state=42,
                                max_iter=30, learning_method="batch")
lda.fit(dtm)

feature_names = cv.get_feature_names_out()
lda_topic_words = {}
print("Tópicos LDA:")
for i, comp in enumerate(lda.components_):
    top15 = [feature_names[j] for j in comp.argsort()[-15:][::-1]]
    lda_topic_words[i] = top15
    print(f"  {TOPIC_LABELS.get(i,f'T{i}')}: {', '.join(top15[:8])}")

lda_dist  = lda.transform(dtm)
topic_avgs = lda_dist.mean(axis=0)
fig, ax = plt.subplots(figsize=(11, 5))
colors = cm.tab10(np.linspace(0, 1, N_TOPICS))
ax.bar([TOPIC_LABELS.get(i, f"T{i}") for i in range(N_TOPICS)],
       topic_avgs, color=colors)
ax.set_title("Distribución de tópicos LDA — Patria Milagro", fontsize=12, fontweight="bold")
ax.set_ylabel("Peso promedio")
plt.xticks(rotation=20, ha="right")
firma(fig)
plt.tight_layout()
fig.savefig(gfx("tematico","lda_topic_distribution.png"), bbox_inches="tight", facecolor="white")
plt.close()
print("  Guardado: lda_topic_distribution.png")

if HAS_PYLDAVIS:
    try:
        panel = pyLDAvis_sklearn.prepare(lda, dtm, cv, mds="mmds")
        pyLDAvis.save_html(panel, gfx("tematico","lda_interactive.html"))
        print("  Guardado: lda_interactive.html")
    except Exception as e:
        print(f"  pyLDAvis omitido: {e}")

# ── NMF ────────────────────────────────────────────────────────────────────
tfidf_v = TfidfVectorizer(max_df=0.95, min_df=1, max_features=3000)
tfidf_m = tfidf_v.fit_transform(page_docs)
nmf = NMF(n_components=N_TOPICS, random_state=42, max_iter=400)
nmf.fit(tfidf_m)

# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("SECCIÓN 4 — ANÁLISIS DE SENTIMIENTO")
print("═"*60)

if HAS_PYSENTIMIENTO:
    print("Cargando analizador (robertuito)…")
    try:
        sent_analyzer = create_analyzer(task="sentiment", lang="es")

        page_sentiments = []
        for pg in pages_raw:
            chunk = pg[:512].strip()
            if len(chunk) < 20:
                page_sentiments.append({"pos": 0, "neg": 0, "neu": 1})
                continue
            try:
                res = sent_analyzer.predict(chunk)
                s   = res.probas
                page_sentiments.append({"pos": s.get("POS",0),
                                         "neg": s.get("NEG",0),
                                         "neu": s.get("NEU",0)})
            except Exception:
                page_sentiments.append({"pos": 0, "neg": 0, "neu": 1})

        idx_pages = list(range(1, len(page_sentiments)+1))
        pos = [s["pos"] for s in page_sentiments]
        neg = [s["neg"] for s in page_sentiments]
        neu = [s["neu"] for s in page_sentiments]

        fig, ax = plt.subplots(figsize=(13, 5))
        ax.plot(idx_pages, pos, color="#27ae60", label="Positivo",  linewidth=1.5)
        ax.plot(idx_pages, neg, color="#c0392b", label="Negativo",  linewidth=1.5)
        ax.plot(idx_pages, neu, color="#7f8c8d", label="Neutro",    linewidth=1, alpha=0.5)
        ax.set_xlabel("Página")
        ax.set_ylabel("Score")
        ax.set_title("Arco de sentimiento — Patria Milagro\n¿Propositivo o confrontacional?",
                     fontsize=12, fontweight="bold")
        ax.legend()
        firma(fig)
        plt.tight_layout()
        fig.savefig(gfx("sentimiento","sentiment_arc.png"), bbox_inches="tight", facecolor="white")
        plt.close()
        print("  Guardado: sentiment_arc.png")

        overall = {"Positivo": np.mean(pos), "Negativo": np.mean(neg), "Neutro": np.mean(neu)}
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(overall.keys(), overall.values(),
               color=["#27ae60","#c0392b","#95a5a6"])
        ax.set_title("Distribución global de sentimiento\nPatria Milagro",
                     fontsize=12, fontweight="bold")
        ax.set_ylabel("Score promedio")
        firma(fig)
        plt.tight_layout()
        fig.savefig(gfx("sentimiento","sentiment_distribution.png"), bbox_inches="tight", facecolor="white")
        plt.close()
        print("  Guardado: sentiment_distribution.png")

        # Párrafos más positivos / negativos
        paras, ps_pos, ps_neg = [], [], []
        for pg in pages_raw:
            for para in pg.split("\n\n"):
                para = para.strip()
                if len(para) > 60:
                    try:
                        res = sent_analyzer.predict(para[:512])
                        paras.append(para)
                        ps_pos.append(res.probas.get("POS", 0))
                        ps_neg.append(res.probas.get("NEG", 0))
                    except Exception:
                        pass

        with open(datos("top_paragraphs.txt"), "w", encoding="utf-8") as f:
            f.write("=== TOP 5 PÁRRAFOS MÁS POSITIVOS ===\n\n")
            for idx in np.argsort(ps_pos)[-5:][::-1]:
                f.write(f"[{ps_pos[idx]:.3f}]\n{paras[idx]}\n\n")
            f.write("=== TOP 5 PÁRRAFOS MÁS NEGATIVOS ===\n\n")
            for idx in np.argsort(ps_neg)[-5:][::-1]:
                f.write(f"[{ps_neg[idx]:.3f}]\n{paras[idx]}\n\n")
        print("  Guardado: top_paragraphs.txt")

    except Exception as e:
        print(f"  Sentimiento omitido: {e}")
else:
    print("  pysentimiento no disponible")

# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("SECCIÓN 5 — ANÁLISIS SEMÁNTICO (Word2Vec)")
print("═"*60)

sentences = [pg for pg in pages_tokens if len(pg) > 3]
print(f"Entrenando Word2Vec sobre {len(sentences)} documentos…")
w2v = Word2Vec(sentences=sentences, vector_size=100, window=5,
               min_count=1, workers=4, epochs=40, seed=42)

KEY_TERMS = ["seguridad","corrupción","estado","nación","economía",
             "campo","salud","educación"]

sim_results = {}
with open(datos("word2vec_similarities.txt"), "w", encoding="utf-8") as f:
    for term in KEY_TERMS:
        vocab = w2v.wv.key_to_index
        matched = term if term in vocab else None
        if matched is None:
            for w in vocab:
                if w.startswith(term[:4]):
                    matched = w; break
        if matched:
            similar = w2v.wv.most_similar(matched, topn=10)
            sim_results[term] = similar
            f.write(f"\nTop similares a '{term}' (match: '{matched}'):\n")
            for w, s in similar:
                f.write(f"  {w}: {s:.3f}\n")
            print(f"  {term}: {[w for w,_ in similar[:5]]}")
        else:
            f.write(f"\n'{term}' no está en el vocabulario\n")

# ── Red semántica ──────────────────────────────────────────────────────────
# Con corpus pequeño las similitudes se comprimen en un rango estrecho; en
# lugar de un umbral fijo se toman las top-N aristas por peso para mantener
# la red legible independientemente del tamaño del corpus.
print("Construyendo red semántica…")
TOP_WORDS = 60   # vocabulario considerado
TOP_EDGES = 50   # aristas a mostrar

# Solo palabras >= 4 chars para evitar abreviaturas cortadas
all_kw = [w for w in w2v.wv.key_to_index.keys() if len(w) >= 4][:TOP_WORDS]
all_edges = []
for i, w1 in enumerate(all_kw):
    for w2 in all_kw[i+1:]:
        try:
            sim = float(w2v.wv.similarity(w1, w2))
            all_edges.append((sim, w1, w2))
        except Exception:
            pass

all_edges.sort(reverse=True)
G = nx.Graph()
for sim, w1, w2 in all_edges[:TOP_EDGES]:
    G.add_edge(w1, w2, weight=sim)

if G.number_of_nodes() > 0:
    freq_map = Counter(all_tokens)
    node_sizes = [max(200, freq_map.get(n, 1) * 120) for n in G.nodes()]
    fig, ax = plt.subplots(figsize=(13, 9))
    pos = nx.spring_layout(G, seed=42, k=1.8)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes,
                           node_color="#1B3A6B", alpha=0.85)
    # Labels desplazados arriba del nodo para no solaparse
    label_pos = {k: (v[0], v[1] + 0.04) for k, v in pos.items()}
    nx.draw_networkx_labels(G, label_pos, ax=ax, font_size=8,
                            font_color="#1B3A6B", font_weight="bold")
    weights = [G[u][v]["weight"] for u, v in G.edges()]
    w_min, w_max = min(weights), max(weights)
    widths = [0.8 + 2.5 * (w - w_min) / max(w_max - w_min, 1e-6) for w in weights]
    nx.draw_networkx_edges(G, pos, ax=ax, width=widths,
                           edge_color="#C8102E", alpha=0.35)
    ax.set_title(f"Red de similitud semántica — top {TOP_EDGES} conexiones\nPatria Milagro",
                 fontsize=12, fontweight="bold")
    ax.axis("off")
    firma(fig)
    plt.tight_layout()
    fig.savefig(gfx("semantica","semantic_network.png"), bbox_inches="tight", facecolor="white")
    plt.close()
    print("  Guardado: semantic_network.png")

# ── t-SNE ──────────────────────────────────────────────────────────────────
# Usar solo las palabras más frecuentes (>=4 chars) para evitar tokens
# raros que generan clusters aislados; etiquetar solo las top-30 por
# frecuencia para que el gráfico respire.
freq_sorted = [w for w, _ in Counter(all_tokens).most_common()
               if len(w) >= 4 and w in w2v.wv.key_to_index]
vocab_words  = freq_sorted[:60]   # puntos en el gráfico
label_words  = set(freq_sorted[:30])  # solo estos llevan etiqueta

if len(vocab_words) >= 10:
    vectors = np.array([w2v.wv[w] for w in vocab_words])
    try:
        from sklearn.manifold import TSNE
        perp = min(20, len(vocab_words) - 1)
        tsne = TSNE(n_components=2, random_state=42, perplexity=perp,
                    n_iter=1000)
        coords = tsne.fit_transform(vectors)

        fig, ax = plt.subplots(figsize=(13, 9))
        # Puntos: más grandes para las palabras etiquetadas
        sizes  = [80 if w in label_words else 20 for w in vocab_words]
        alphas = [0.9 if w in label_words else 0.35 for w in vocab_words]
        for (x, y), s, a in zip(coords, sizes, alphas):
            ax.scatter(x, y, s=s, alpha=a, color="#1B3A6B", linewidths=0)

        # Etiquetas solo en las top-30, con fondo blanco para legibilidad
        for i, word in enumerate(vocab_words):
            if word in label_words:
                ax.annotate(
                    word, (coords[i, 0], coords[i, 1]),
                    fontsize=8, fontweight="bold", color="#1B3A6B",
                    xytext=(4, 4), textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white",
                              ec="none", alpha=0.7),
                )

        ax.set_title("Embeddings de palabras (t-SNE)\nPatria Milagro — top 60 términos, etiquetas top 30",
                     fontsize=12, fontweight="bold")
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        firma(fig)
        plt.tight_layout()
        fig.savefig(gfx("semantica","tsne_embeddings.png"), bbox_inches="tight", facecolor="white")
        plt.close()
        print("  Guardado: tsne_embeddings.png")
    except Exception as e:
        print(f"  t-SNE omitido: {e}")

# ── KWIC ──────────────────────────────────────────────────────────────────
with open(datos("kwic.txt"), "w", encoding="utf-8") as f:
    for term in KEY_TERMS:
        f.write(f"\n=== KWIC: '{term}' ===\n")
        count = 0
        for pg in pages_raw:
            for sent in re.split(r'[.!?]', pg):
                if term in sent.lower() and count < 5:
                    f.write(f"  ...{sent.strip()[:200]}...\n")
                    count += 1
                if count >= 5: break
print("  Guardado: kwic.txt")

# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("SECCIÓN 6 — ANÁLISIS ESTRUCTURAL Y RETÓRICO")
print("═"*60)

sentences_raw = []
for pg in pages_raw:
    for sent in re.split(r'[.!?]', pg):
        sent = sent.strip()
        if len(sent) > 10:
            sentences_raw.append(sent)

sent_lengths = [len(s.split()) for s in sentences_raw]
word_lengths  = [len(w) for pg in pages_raw for w in pg.split() if w.isalpha()]
avg_sent = np.mean(sent_lengths) if sent_lengths else 0
avg_word = np.mean(word_lengths) if word_lengths else 0
print(f"Longitud media oración: {avg_sent:.1f} palabras")
print(f"Longitud media palabra: {avg_word:.1f} caracteres")

def count_syllables_es(word):
    word = word.lower()
    vowels     = "aeiouáéíóúü"
    diphthongs = {"ai","au","ei","eu","oi","ou","ia","ie","io","iu","ua","ue","ui","uo"}
    count, i = 0, 0
    while i < len(word):
        if word[i] in vowels:
            if i+1 < len(word) and word[i:i+2] in diphthongs:
                count += 1; i += 2
            else:
                count += 1; i += 1
        else:
            i += 1
    return max(1, count)

all_words_raw  = [w for pg in pages_raw for w in pg.split() if w.isalpha()]
total_sents_raw = max(len(sentences_raw), 1)
total_syl      = sum(count_syllables_es(w) for w in all_words_raw)
ppo = len(all_words_raw) / total_sents_raw
psp = total_syl / max(len(all_words_raw), 1)
fh  = 206.84 - 1.02*ppo - 60*psp
print(f"Índice Fernández Huerta: {fh:.1f}/100  (pal/orac={ppo:.1f}, síl/pal={psp:.2f})")

with open(datos("readability.txt"), "w") as f:
    f.write("LEGIBILIDAD — Fernández Huerta (1959)\n")
    f.write("206.84 - 1.02*(pal/orac) - 60*(síl/pal)\n")
    f.write("Escala: 0-30 muy difícil | 30-50 difícil | 50-60 algo difícil | 60-70 normal\n\n")
    f.write(f"Índice:                {fh:.1f}/100\n")
    f.write(f"Palabras por oración:  {ppo:.1f}\n")
    f.write(f"Sílabas por palabra:   {psp:.2f}\n")
    f.write(f"Long. media oración:   {avg_sent:.1f} palabras\n")
    f.write(f"Long. media palabra:   {avg_word:.1f} caracteres\n")

# ── Histograma longitud de oraciones ─────────────────────────────────────
if sent_lengths:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(sent_lengths, bins=min(40, len(sent_lengths)//2+1),
            color="#1B3A6B", edgecolor="white", alpha=0.85)
    ax.axvline(avg_sent, color="#C8102E", linestyle="--", linewidth=2,
               label=f"Media = {avg_sent:.1f} palabras")
    ax.set_xlabel("Palabras por oración")
    ax.set_ylabel("Frecuencia")
    ax.set_title("Distribución de longitud de oraciones\nPatria Milagro — Abelardo de la Espriella 2026",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=10)
    firma(fig)
    plt.tight_layout()
    fig.savefig(gfx("estructura","sentence_length_hist.png"), bbox_inches="tight", facecolor="white")
    plt.close()
    print("  Guardado: sentence_length_hist.png")

# ── Iniciadores de oración ─────────────────────────────────────────────────
starters = []
for s in sentences_raw:
    words = s.split()
    if len(words) >= 2:
        starters.append(" ".join(words[:2]).lower())
starter_top = Counter(starters).most_common(20)
if starter_top:
    hbar(starter_top[::-1],
         "Top 20 iniciadores de oración — Patria Milagro",
         gfx("estructura","sentence_starters.png"),
         color="#2E7D32")

# ── Heatmap densidad de palabras por página ────────────────────────────────
wpp = [len(pg.split()) for pg in pages_raw]
if len(wpp) > 1:
    side = int(np.ceil(np.sqrt(len(wpp))))
    pad  = side*side - len(wpp)
    hm   = np.array(wpp + [0]*pad).reshape(side, side)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(hm, ax=ax, cmap="YlOrRd", linewidths=0.5,
                annot=True, fmt="d", annot_kws={"size": 8},
                cbar_kws={"label":"Palabras por página"})
    ax.set_title("Densidad de palabras por página — Patria Milagro",
                 fontsize=12, fontweight="bold")
    firma(fig)
    plt.tight_layout()
    fig.savefig(gfx("estructura","density_heatmap.png"), bbox_inches="tight", facecolor="white")
    plt.close()
    print("  Guardado: density_heatmap.png")

# ── NER ────────────────────────────────────────────────────────────────────
print("Ejecutando NER…")
ner_ents = {"PERSON": [], "ORG": [], "GPE": [], "LOC": []}
ner_doc  = nlp(full_raw[:500_000])
for ent in ner_doc.ents:
    if ent.label_ in ner_ents:
        ner_ents[ent.label_].append(ent.text.strip())

for etype, entities in ner_ents.items():
    cnt = Counter(entities).most_common(20)
    if cnt:
        label_map = {"PERSON":"personas","ORG":"organizaciones",
                     "GPE":"lugares/países","LOC":"lugares"}
        hbar(cnt[::-1],
             f"Top entidades — {label_map.get(etype, etype)}\nPatria Milagro",
             gfx("estructura", f"ner_{etype.lower()}.png"),
             color="#2E5F8A")
        print(f"  {etype}: {[e for e,_ in cnt[:5]]}")

# ── Red de co-ocurrencia NER ───────────────────────────────────────────────
ner_G = nx.Graph()
for pg in pages_raw:
    pg_doc  = nlp(pg[:5000])
    pg_ents = [e.text.strip() for e in pg_doc.ents
               if e.label_ in ("PERSON","ORG","GPE") and len(e.text) > 3]
    for e1, e2 in combinations(set(pg_ents), 2):
        if ner_G.has_edge(e1, e2):
            ner_G[e1][e2]["weight"] += 1
        else:
            ner_G.add_edge(e1, e2, weight=1)

edges_top = sorted(ner_G.edges(data=True), key=lambda x: x[2]["weight"], reverse=True)[:60]
ner_sub = nx.Graph()
for u, v, d in edges_top:
    ner_sub.add_edge(u, v, weight=d["weight"])

if ner_sub.number_of_nodes() > 0:
    fig, ax = plt.subplots(figsize=(14, 10))
    pos_n   = nx.spring_layout(ner_sub, seed=42)
    weights = [ner_sub[u][v]["weight"] for u, v in ner_sub.edges()]
    nx.draw_networkx(ner_sub, pos_n, ax=ax, node_size=40, font_size=6,
                     width=[w*0.4 for w in weights], alpha=0.8, with_labels=True)
    ax.set_title("Red de co-ocurrencia de entidades — Patria Milagro",
                 fontsize=12, fontweight="bold")
    ax.axis("off")
    firma(fig)
    plt.tight_layout()
    fig.savefig(gfx("estructura","ner_cooccurrence_network.png"), bbox_inches="tight", facecolor="white")
    plt.close()
    print("  Guardado: ner_cooccurrence_network.png")

# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("SECCIÓN 7 — ANÁLISIS TEMÁTICO PROFUNDO")
print("═"*60)

# Diccionarios ajustados al perfil ideológico de Espriella
THEMATIC_DICTS = {
    "Seguridad": [
        "seguridad","crimen","delincuencia","policía","ejército","fuerza",
        "narcotráfico","droga","coca","cultivo","ilícito","delito","homicidio",
        "extorsión","secuestro","banda","criminal","narco","fumigación",
        "erradicación","prisionero","carcel","penitenciario","orden","autoridad",
    ],
    "Anticorrupción": [
        "corrupción","corrupto","anticorrupción","transparencia","fiscal",
        "contrabando","lavado","testaferro","extinción","dominio","dian",
        "peculado","soborno","mermelada","burocracia","malversación",
        "secop","licitación","contrato","auditoría","rendición",
    ],
    "Economía": [
        "economía","económico","empleo","trabajo","inversión","empresa",
        "industria","exportación","importación","pib","crecimiento","mercado",
        "tributario","impuesto","ingreso","salario","deuda","presupuesto",
        "finanza","banco","crédito","inflación","competitividad","arancelario",
    ],
    "Instituciones": [
        "república","constitución","estado","democracia","institución",
        "poder","derecho","judicial","legislativo","ejecutivo","soberanía",
        "libertad","ciudadano","voto","elección","partido","reforma",
        "magistrado","corte","tribunal","fiscal","procuraduría",
    ],
    "Salud": [
        "salud","hospital","médico","enfermedad","atención","seguro",
        "eps","sistema","cobertura","vacuna","medicamento","nutrición",
        "mortalidad","mental","clínica","farmacéutico","urgencias",
    ],
    "Campo y agro": [
        "campo","rural","campesino","tierra","agroindustria","agricultor",
        "cosecha","ganadería","minifundio","hectárea","finca","alimento",
        "soberanía alimentaria","producción agrícola","subsidio","comunidad rural",
    ],
    "Energía y minería": [
        "petróleo","energía","minería","ecopetrol","gas","electricidad",
        "renovable","carbón","recurso","exportación energética","oleoducto",
        "transición energética","nuclear","termoeléctrica","hidroeléctrica",
    ],
    "Paz y conflicto": [
        "paz","conflicto","guerrilla","farc","eln","negociación","cese",
        "armisticio","desmovilización","reintegración","zonas","excombatiente",
        "paramilitarismo","víctima","desplazado","masacre","verdad","memoria",
    ],
}

theme_counts = {t: [] for t in THEMATIC_DICTS}
for pg in pages_raw:
    pg_lower = pg.lower()
    for theme, kws in THEMATIC_DICTS.items():
        theme_counts[theme].append(sum(pg_lower.count(kw) for kw in kws))

theme_df = pd.DataFrame(theme_counts)
theme_df.index.name = "pagina"
theme_df.to_csv(datos("theme_counts_per_page.csv"))

# ── Línea temporal ─────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(15, 7))
colors = cm.tab10(np.linspace(0, 1, len(THEMATIC_DICTS)))
for (theme, counts), color in zip(theme_counts.items(), colors):
    smoothed = pd.Series(counts).rolling(3, min_periods=1).mean()
    ax.plot(range(1, len(counts)+1), smoothed, label=theme, color=color, linewidth=1.8)
ax.set_xlabel("Página")
ax.set_ylabel("Menciones (media móvil 3 páginas)")
ax.set_title("Evolución temática a lo largo del programa\nColombia, Patria Milagro — Espriella 2026",
             fontsize=13, fontweight="bold")
ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
firma(fig)
plt.tight_layout()
fig.savefig(gfx("tematico","theme_mentions_timeline.png"), bbox_inches="tight", facecolor="white")
plt.close()
print("  Guardado: theme_mentions_timeline.png")

# ── Totales por tema ──────────────────────────────────────────────────────
theme_totals = {t: sum(c) for t, c in theme_counts.items()}
sorted_t     = sorted(theme_totals.items(), key=lambda x: x[1], reverse=True)
fig, ax = plt.subplots(figsize=(11, 5))
ax.bar([t for t, _ in sorted_t], [v for _, v in sorted_t],
       color=cm.tab10(np.linspace(0, 1, len(sorted_t))))
ax.set_title("Menciones totales por eje temático — Patria Milagro",
             fontsize=12, fontweight="bold")
ax.set_ylabel("Menciones totales")
plt.xticks(rotation=20, ha="right")
firma(fig)
plt.tight_layout()
fig.savefig(gfx("tematico","theme_totals.png"), bbox_inches="tight", facecolor="white")
plt.close()
print("  Guardado: theme_totals.png")

# ── Heatmap temático por secciones ────────────────────────────────────────
n_pags = len(pages_raw)
bucket = max(1, n_pags // 5)
n_bucks = max(1, n_pags // bucket)
hm_data = {}
for theme in THEMATIC_DICTS:
    row = []
    for i in range(n_bucks):
        row.append(sum(theme_counts[theme][i*bucket:(i+1)*bucket]))
    hm_data[theme] = row

hm_df = pd.DataFrame(hm_data).T
hm_df.columns = [f"p{i*bucket+1}-{min((i+1)*bucket, n_pags)}" for i in range(n_bucks)]
fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(hm_df, ax=ax, cmap="YlOrRd", linewidths=0.5,
            annot=True, fmt="d", annot_kws={"size": 8})
ax.set_title("Intensidad temática por sección del documento — Patria Milagro",
             fontsize=12, fontweight="bold")
firma(fig)
plt.tight_layout()
fig.savefig(gfx("tematico","theme_heatmap.png"), bbox_inches="tight", facecolor="white")
plt.close()
print("  Guardado: theme_heatmap.png")

# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("SECCIÓN 8 — FIGURAS POLÍTICAS MENCIONADAS")
print("═"*60)

PATRONES = {
    "Gustavo Petro": [
        r"\bpetro\b", r"gustavo\s+petro", r"gobierno\s+petro",
        r"presidente\s+petro", r"petrismo", r"petroísta[s]?",
        r"petro\s+urrego",
    ],
    "Álvaro Uribe": [
        r"\buribe\b", r"álvaro\s+uribe", r"alvaro\s+uribe",
        r"uribe\s+v[eé]lez", r"\buribismo\b", r"\buribista[s]?\b",
        r"expresidente\s+uribe",
    ],
}

def buscar_menciones(pages, patrones):
    res = {fig: [] for fig in patrones}
    for i, pg in enumerate(pages):
        pg_lower = pg.lower()
        for figura, pats in patrones.items():
            for pat in pats:
                for m in re.finditer(pat, pg_lower):
                    start = max(0, m.start()-150)
                    end   = min(len(pg), m.end()+150)
                    frag  = pg[start:end].replace("\n"," ").strip()
                    res[figura].append({"pagina": i+1, "match": m.group(), "contexto": frag})
    return res

menciones = buscar_menciones(pages_raw, PATRONES)
print("\nMENCIONES:")
for fig, hits in menciones.items():
    pags = set(h["pagina"] for h in hits)
    print(f"  {fig}: {len(hits)} menciones en {len(pags)} páginas")

# ── Barras por página ──────────────────────────────────────────────────────
fig_ctr = {fig: Counter(h["pagina"] for h in hits) for fig, hits in menciones.items()}
all_p   = list(range(1, len(pages_raw)+1))

figs_list = list(PATRONES.keys())
colors_f  = ["#2980b9", "#c0392b"]

fig_m, axes = plt.subplots(len(figs_list), 1, figsize=(14, 5*len(figs_list)), sharex=True)
if len(figs_list) == 1: axes = [axes]
fig_m.suptitle("Menciones por página\nPrograma de Gobierno — Abelardo de la Espriella 2026",
               fontsize=13, fontweight="bold")
for ax_i, (figura, color) in zip(axes, zip(figs_list, colors_f)):
    vals = [fig_ctr[figura].get(p, 0) for p in all_p]
    ax_i.bar(all_p, vals, color=color, width=1.0, alpha=0.85)
    ax_i.set_title(figura, fontsize=11, color=color, fontweight="bold")
    ax_i.set_ylabel("Menciones/pág", fontsize=9)
    ax_i.set_ylim(0, max(max(vals, default=0)+1, 2))
axes[-1].set_xlabel("Página", fontsize=10)
plt.tight_layout()
fig_m.savefig(gfx("figuras_politicas","menciones_por_pagina.png"), bbox_inches="tight", facecolor="white")
plt.close()
print("  Guardado: menciones_por_pagina.png")

# ── Timeline superpuesto ──────────────────────────────────────────────────
window = max(2, len(pages_raw)//8)
fig, ax = plt.subplots(figsize=(14, 5))
for figura, color in zip(figs_list, colors_f):
    vals     = [fig_ctr[figura].get(p, 0) for p in all_p]
    smoothed = pd.Series(vals).rolling(window, min_periods=1).mean()
    ax.fill_between(all_p, smoothed, alpha=0.25, color=color)
    ax.plot(all_p, smoothed, color=color, linewidth=2, label=figura)
ax.set_xlabel("Página"); ax.set_ylabel(f"Menciones (media móvil {window} pág.)")
ax.set_title("Intensidad de menciones a lo largo del documento\nPatria Milagro",
             fontsize=12, fontweight="bold")
ax.legend(fontsize=10)
firma(fig)
plt.tight_layout()
fig.savefig(gfx("figuras_politicas","menciones_comparado_timeline.png"), bbox_inches="tight", facecolor="white")
plt.close()
print("  Guardado: menciones_comparado_timeline.png")

# ── Pie proporción ─────────────────────────────────────────────────────────
totales_fig = {fig: len(hits) for fig, hits in menciones.items()}
if sum(totales_fig.values()) > 0:
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(totales_fig.values(), labels=totales_fig.keys(),
           colors=colors_f[:len(figs_list)],
           autopct="%1.1f%%", startangle=90,
           textprops={"fontsize":11},
           wedgeprops={"linewidth":2,"edgecolor":"white"})
    ax.set_title("Proporción de menciones totales\nPatria Milagro", fontsize=12, fontweight="bold")
    firma(fig)
    plt.tight_layout()
    fig.savefig(gfx("figuras_politicas","menciones_proporcion.png"), bbox_inches="tight", facecolor="white")
    plt.close()
    print("  Guardado: menciones_proporcion.png")

# ── Tono del contexto ──────────────────────────────────────────────────────
NEG_WORDS = {
    "corrupción","crimen","criminal","muerte","víctima","violencia","impunidad",
    "engaño","mentira","traición","narcotráfico","robo","saqueo","represión",
    "autoritarismo","dictadura","fraude","ilegal","ilegítimo","guerra","terror",
    "desastre","caos","fracaso","derrumbe","desgobierno","pobreza","miseria",
}
POS_WORDS = {
    "paz","reforma","progreso","desarrollo","democracia","libertad","esperanza",
    "cambio","transformación","bienestar","derecho","construcción","futuro",
    "restauración","seguridad","crecimiento","éxito","patria","nación","pueblo",
}

def analizar_tono(hits):
    neg, pos, neu = 0, 0, 0
    for h in hits:
        ctx_words = set(re.findall(r"\b\w+\b", h["contexto"].lower()))
        n = len(ctx_words & NEG_WORDS)
        p = len(ctx_words & POS_WORDS)
        if n > p: neg += 1
        elif p > n: pos += 1
        else: neu += 1
    return {"negativo": neg, "positivo": pos, "neutro": neu}

ctx_results = {fig: analizar_tono(hits) for fig, hits in menciones.items()}

if len(figs_list) >= 1:
    n_plots = min(len(figs_list), 2)
    fig_t, axes_t = plt.subplots(1, n_plots, figsize=(6*n_plots, 5))
    if n_plots == 1: axes_t = [axes_t]
    fig_t.suptitle("Tono del contexto de cada mención\nPatria Milagro",
                   fontsize=12, fontweight="bold")
    for ax_i, (figura, color) in zip(axes_t, zip(figs_list[:n_plots], colors_f)):
        ctx = ctx_results[figura]
        cats = ["Negativo","Positivo","Neutro"]
        vals = [ctx["negativo"], ctx["positivo"], ctx["neutro"]]
        ax_i.bar(cats, vals, color=["#e74c3c","#27ae60","#95a5a6"], edgecolor="white")
        for bar_i, v in zip(ax_i.containers[0], vals):
            ax_i.text(bar_i.get_x()+bar_i.get_width()/2, bar_i.get_height()+0.1,
                      str(v), ha="center", fontsize=11, fontweight="bold")
        ax_i.set_title(figura, fontsize=10, color=color, fontweight="bold")
        ax_i.set_ylabel("N° menciones")
    plt.tight_layout()
    fig_t.savefig(gfx("figuras_politicas","tono_contexto_figuras.png"), bbox_inches="tight", facecolor="white")
    plt.close()
    print("  Guardado: tono_contexto_figuras.png")

# ── Palabras en contexto ───────────────────────────────────────────────────
def palabras_contexto(hits, excluir, topn=20):
    SW_CTX = STOPWORDS | set(excluir.lower().split())
    words  = []
    for h in hits:
        ws = re.findall(r"\b[a-záéíóúüñ]{4,}\b", h["contexto"].lower())
        words.extend([w for w in ws if w not in SW_CTX])
    return Counter(words).most_common(topn)

n_plots = min(len(figs_list), 2)
fig_p, axes_p = plt.subplots(1, n_plots, figsize=(9*n_plots, 7))
if n_plots == 1: axes_p = [axes_p]
fig_p.suptitle("Vocabulario que rodea cada mención\nPatria Milagro",
               fontsize=12, fontweight="bold")
for ax_i, (figura, color) in zip(axes_p, zip(figs_list[:n_plots], colors_f)):
    ctx_w = palabras_contexto(menciones[figura], figura)
    if ctx_w:
        labels_w, vals_w = zip(*ctx_w)
        ax_i.barh(range(len(labels_w)), vals_w, color=color, alpha=0.8)
        ax_i.set_yticks(range(len(labels_w)))
        ax_i.set_yticklabels(labels_w, fontsize=9)
        ax_i.invert_yaxis()
        ax_i.set_title(f"Contexto de {figura}", fontsize=10, fontweight="bold")
        ax_i.set_xlabel("Frecuencia")
plt.tight_layout()
fig_p.savefig(gfx("figuras_politicas","palabras_contexto_figuras.png"), bbox_inches="tight", facecolor="white")
plt.close()
print("  Guardado: palabras_contexto_figuras.png")

# ── Exportar citas ─────────────────────────────────────────────────────────
with open(datos("citas_figuras_politicas.txt"), "w", encoding="utf-8") as f:
    for figura, hits in menciones.items():
        f.write("\n" + "="*70 + "\n")
        f.write(f"  {figura.upper()} — {len(hits)} menciones\n")
        f.write("="*70 + "\n\n")
        seen = set()
        for h in hits:
            if h["pagina"] not in seen:
                seen.add(h["pagina"])
                f.write(f"[Pág. {h['pagina']}] ...{h['contexto']}...\n\n")
print("  Guardado: citas_figuras_politicas.txt")

# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("ANÁLISIS COMPLETO")
print("═"*60)
total_files = 0
for carpeta in ["frecuencias","tematico","sentimiento","semantica","estructura","figuras_politicas"]:
    path = os.path.join(GFX, carpeta)
    files = os.listdir(path)
    print(f"  graficos/{carpeta}/  →  {len(files)} archivos")
    total_files += len(files)
print(f"\nTotal gráficos: {total_files}")
print(f"Datos en: {DATOS}/")
