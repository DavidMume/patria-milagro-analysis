# Colombia, Patria Milagro — Análisis político-económico
### Programa de gobierno de Abelardo de la Espriella · Elecciones Colombia 2026

> **Economía Política · Procesamiento de Lenguaje Natural · Análisis de Discurso**
> David Muñoz · 2026

---

## ¿Por qué este análisis?

La crítica más repetida al programa de De la Espriella es que "cabe en tres páginas". Este proyecto demuestra que esa lectura es incompleta: el documento de tres páginas es una pieza de comunicación política, no el programa. El proyecto programático real se distribuye en al menos cinco capas documentales con distinto nivel de abstracción y densidad técnica.

El análisis aplica herramientas de economía política y NLP para responder: **¿qué propone realmente el candidato, cómo lo dice y qué revela su lenguaje sobre sus prioridades?**

Como análisis complementario, los hallazgos se contrastan con el estudio del programa de Iván Cepeda disponible en [analisis-plan-gobierno-ivan-cepeda-2026](https://github.com/DavidMume/analisis-plan-gobierno-ivan-cepeda-2026).

---

## Estructura del repositorio

```
patria-milagro-analysis/
├── sources/
│   ├── 00_fuentes_inventario.csv   # 20 fuentes documentales
│   └── pdfs/                       # PDFs descargados (no versionados)
├── datos/                          # Outputs textuales y CSV del análisis NLP
├── docs/                           # Metodología, notas, glosario
├── scripts/
│   ├── generar_graficos.py         # Gráficos comparativos (hardcoded)
│   └── analyze_espriella.py        # Análisis NLP completo desde PDF
├── notebooks/                      # Análisis paso a paso en Jupyter
└── graficos/
    ├── frecuencias/   # WordCloud, top-40, bigramas, trigramas, Zipf
    ├── tematico/      # LDA, heatmap temático, evolución por sección
    ├── sentimiento/   # Arco de sentimiento, distribución global
    ├── semantica/     # Red semántica Word2Vec, t-SNE embeddings
    ├── estructura/    # NER, densidad, longitud de oraciones
    ├── figuras_politicas/  # Menciones a figuras políticas
    └── comparativo/   # Espriella vs. Cepeda
```

---

## Fuentes documentales analizadas

| ID | Documento | Tipo | Páginas |
|---|---|---|---|
| F01 | Primeras 13 propuestas (Propuestas del Tigre) | Resumen ejecutivo | ~3 |
| F02 | Pilares para reconstruir la Patria Milagro (web) | Programa temático | — |
| F03 | Pilares Fundacionales | Marco ideológico | 14 |
| F04 | Programa de gobierno oficial | Documento formal | 29 |
| F05 | El Milagro del Valle del Cauca | Propuesta territorial | 47 |

Ver inventario completo en [`sources/00_fuentes_inventario.csv`](sources/00_fuentes_inventario.csv) (20 fuentes).

---

## Principales hallazgos

### El programa es, ante todo, un proyecto de seguridad y restauración institucional

El análisis de frecuencias y la clasificación temática revelan que **seguridad y anticorrupción concentran el 42% de las propuestas concretas**. El vocabulario dominante — *patria, nación, restauración, República, Constitución* — no es tecnocrático ni redistributivo: es moral y político. Contrasta con el programa de Cepeda, donde el eje central es redistribución y justicia social.

### El resumen ejecutivo no representa el programa completo

El documento de tres páginas menciona los temas pero no los desarrolla. El pilar de seguridad, por ejemplo, incluye una doctrina completa con diez nuevas cárceles, un nuevo cuerpo penitenciario, fumigación aérea desde el día uno y comandos conjuntos por región — nada de eso aparece en el resumen.

### El programa formal no nombra adversarios

A diferencia del programa de Iván Cepeda — donde Uribe Vélez (221 menciones) y Petro (274 menciones) aparecen como referencias explícitas — el documento formal de Espriella **no menciona ninguna figura política adversaria por nombre**. El adversario es abstracto: la corrupción, el crimen, la burocracia. Esta es una decisión retórica consciente: propone un programa de gobierno sin personalizar el ataque político.

### Legibilidad: documento técnico, no populista

El índice Fernández Huerta es **45.0/100** (nivel: difícil / universitario), con **12.5 palabras por oración** — significativamente más corto que el programa de Cepeda (25.8 palabras/oración). Las oraciones cortas reflejan el formato de bullet points y propuestas concretas que domina el documento.

---

## Visualizaciones

### Frecuencias

#### WordCloud — Vocabulario dominante del corpus
![WordCloud](graficos/frecuencias/wordcloud.png)

#### Top 40 términos más frecuentes (lematizados)
![Top 40 unigrams](graficos/frecuencias/top40_unigrams.png)

#### Top 25 bigramas
![Top 25 bigramas](graficos/frecuencias/top25_bigrams.png)

#### Top 20 trigramas
![Top 20 trigramas](graficos/frecuencias/top20_trigrams.png)

#### Ley de Zipf — ¿es un texto lingüísticamente natural?
![Zipf](graficos/frecuencias/zipf_law.png)

---

### Análisis temático (NLP)

#### Distribución de tópicos LDA
![LDA](graficos/tematico/lda_topic_distribution.png)

#### Evolución temática a lo largo del programa
![Timeline temático](graficos/tematico/theme_mentions_timeline.png)

#### Peso relativo de cada eje de política
![Totales temáticos](graficos/tematico/theme_totals.png)

#### Intensidad temática por sección del documento (heatmap)
![Heatmap temático](graficos/tematico/theme_heatmap.png)

#### Propuestas por área temática (clasificación manual)
![Propuestas por área](graficos/tematico/propuestas_por_area.png)

#### Distribución del corpus por tipo de enunciado
![Tipos de enunciado](graficos/tematico/tipos_enunciado.png)

---

### Análisis de sentimiento

#### Arco de sentimiento — ¿propositivo o confrontacional?
![Arco de sentimiento](graficos/sentimiento/sentiment_arc.png)

#### Distribución global de sentimiento
![Distribución sentimiento](graficos/sentimiento/sentiment_distribution.png)

---

### Análisis semántico

#### Red de similitud semántica (Word2Vec)
![Red semántica](graficos/semantica/semantic_network.png)

#### Embeddings de palabras (t-SNE)
![t-SNE](graficos/semantica/tsne_embeddings.png)

---

### Análisis retórico y estructural

#### Distribución de longitud de oraciones
![Longitud oraciones](graficos/estructura/sentence_length_hist.png)

#### Iniciadores de oración más frecuentes
![Iniciadores](graficos/estructura/sentence_starters.png)

#### Densidad de palabras por página
![Densidad heatmap](graficos/estructura/density_heatmap.png)

#### Entidades nombradas — organizaciones
![NER org](graficos/estructura/ner_org.png)

#### Entidades nombradas — lugares
![NER loc](graficos/estructura/ner_loc.png)

#### Red de co-ocurrencia de entidades
![NER red](graficos/estructura/ner_cooccurrence_network.png)

#### Verificabilidad de las 30 cifras extraídas
![Verificabilidad](graficos/estructura/verificabilidad_cifras.png)

#### Densidad programática por documento — ¿dónde están las propuestas concretas?
![Densidad por fuente](graficos/estructura/densidad_por_fuente.png)

---

### Figuras políticas mencionadas

> **Nota:** El documento formal analizado (programa de gobierno, 21 págs.) no nombra adversarios políticos explícitamente. A diferencia del programa de Cepeda — que menciona a Uribe Vélez 221 veces y a Petro 274 veces — Espriella abstrae el adversario como concepto ("la corrupción", "el crimen") en lugar de personalizarlo.

![Menciones por página](graficos/figuras_politicas/menciones_por_pagina.png)
![Timeline comparado](graficos/figuras_politicas/menciones_comparado_timeline.png)
![Tono del contexto](graficos/figuras_politicas/tono_contexto_figuras.png)

---

### Análisis comparativo: Espriella vs. Cepeda

#### Distribución temática comparada
![Comparativo temático](graficos/comparativo/espriella_vs_cepeda_tematico.png)

#### Tono del discurso: propositivo vs. confrontacional
![Tono comparado](graficos/comparativo/tono_espriella_vs_cepeda.png)

#### Cobertura temática: resumen ejecutivo vs. pilares completos
![Cobertura](graficos/comparativo/cobertura_resumen_vs_pilares.png)

---

## Metodología

| Sección | Método | Pregunta que responde |
|---|---|---|
| 1. Extracción y limpieza | PyMuPDF, spaCy, NLTK | ¿Cuál es el corpus real del documento? |
| 2. Análisis de frecuencias | N-gramas, WordCloud, Zipf | ¿Qué conceptos dominan el discurso? |
| 3. Modelado de tópicos | LDA + NMF (7 tópicos) | ¿Cuáles son los ejes temáticos del programa? |
| 4. Análisis de sentimiento | BERT en español (robertuito) | ¿El tono es propositivo o confrontacional? |
| 5. Análisis semántico | Word2Vec, redes de similitud | ¿Cómo se relacionan conceptualmente los temas? |
| 6. Análisis retórico | NER, densidad, legibilidad | ¿A quién nombra, cómo escribe, qué tan complejo es? |
| 7. Inmersión temática | Diccionarios por eje de política | ¿Cuánto espacio le dedica a cada eje? |
| 8. Figuras políticas | Regex, análisis de contexto | ¿A quién menciona y en qué tono? |

Ver metodología completa en [`docs/metodologia.md`](docs/metodologia.md).

## Reproducibilidad

```bash
git clone https://github.com/DavidMume/patria-milagro-analysis.git
cd patria-milagro-analysis

pip install pymupdf nltk spacy scikit-learn gensim wordcloud matplotlib \
            seaborn networkx pyLDAvis pysentimiento lexicalrichness

python -m spacy download es_core_news_sm

# Colocar el PDF del programa en sources/pdfs/f04_programa_oficial.pdf
python scripts/analyze_espriella.py
```

## Estado del proyecto

- [x] Inventario de fuentes (20 documentos)
- [x] Metodología y glosario
- [x] Extracción de cifras (30 cifras, con nivel de verificabilidad)
- [x] Comparación resumen ejecutivo vs. pilares
- [x] Análisis NLP completo (análisis de frecuencias, LDA, sentimiento, Word2Vec, NER, legibilidad)
- [x] Análisis comparativo Espriella vs. Cepeda
- [x] Script reproducible `analyze_espriella.py`
- [ ] Artículo de opinión — versión final
