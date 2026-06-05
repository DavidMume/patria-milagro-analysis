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

---

### Análisis de frecuencias

#### Vocabulario dominante del corpus

La nube de palabras y el ranking de unigramas son la primera radiografía del programa: revelan qué conceptos ocupa el candidato con más frecuencia y, por tanto, qué jerarquía de valores construye su lenguaje. En economía política, el vocabulario no es neutral — un programa que repite *billón* y *meta* 17 y 7 veces respectivamente tiene un perfil tecnocrático; uno que repite *pueblo*, *territorio* y *paz* tiene un perfil redistributivo y social.

El hallazgo más llamativo de Patria Milagro es que **el término más frecuente del programa lematizado es "billón"** (17 ocurrencias), seguido de "seguridad" (14) y "empleo" (11). El vocabulario dominante es económico-cuantitativo — billones, metas, reducciones, resultados — no ideológico ni moral. Contrasta directamente con el programa de Cepeda, donde el término más frecuente es "pueblo" y el vocabulario orbita alrededor de justicia, territorio y derechos.

![WordCloud](graficos/frecuencias/wordcloud.png)

![Top 40 unigrams](graficos/frecuencias/top40_unigrams.png)

---

#### Bigramas y trigramas — Las unidades de sentido reales

Los n-gramas son más informativos que los unigramas: revelan los marcos conceptuales compuestos que el candidato usa. "Reforma agraria" dice más que "reforma" sola; "sin subir impuestos" dice más que "impuestos". Los n-gramas se generan desde el **texto crudo del PDF** — no lematizado — para preservar las frases exactas del documento.

Los bigramas más frecuentes son: **"Plan Colombia"** (5), "empleo masivo" (3), "sin subir impuestos" (3), "bloque búsqueda" (3). La aparición de "Plan Colombia" como bigrama dominante es significativa: Espriella lo propone como política de seguridad a reinstaurar, nombrando explícitamente el modelo de los años 2000. "Bloque búsqueda" — el mecanismo de inteligencia que capturó a Pablo Escobar — aparece como referencia institucional dentro de la propuesta de seguridad.

![Top 25 bigramas](graficos/frecuencias/top25_bigrams.png)

![Top 20 trigramas](graficos/frecuencias/top20_trigrams.png)

---

#### Ley de Zipf — ¿es un texto lingüísticamente natural?

La ley de Zipf establece que en cualquier corpus lingüístico natural, la frecuencia de una palabra es inversamente proporcional a su rango: la palabra más frecuente aparece aproximadamente el doble de veces que la segunda, el triple que la tercera, y así sucesivamente. La pendiente de la recta en un gráfico log-log debe ser cercana a −1 para un texto natural.

La pendiente observada confirma que el programa sigue distribución de lenguaje natural. Esto es relevante como control metodológico: descarta que el documento sea una repetición mecánica de consignas o un texto generado artificialmente. También descarta el caso opuesto — un documento excesivamente diverso en vocabulario, que podría indicar texto compilado de múltiples fuentes sin coherencia temática.

![Zipf](graficos/frecuencias/zipf_law.png)

---

### Análisis temático

#### Distribución de tópicos LDA

El modelo LDA (*Latent Dirichlet Allocation*) identifica grupos de palabras que tienden a co-aparecer en el mismo contexto dentro del documento. No se le indica al modelo cuáles son los temas — los infiere del patrón de co-ocurrencia. Los 7 tópicos resultantes y su peso promedio revelan cuál es la arquitectura temática latente del programa.

El tópico de mayor peso en el modelo es **Economía y empresa**, seguido de **Seguridad y orden** e **Instituciones / República**. Esto confirma el hallazgo de frecuencias: el programa de Espriella es más un programa económico-institucional que un programa de seguridad puro, aunque la seguridad aparezca como el eje más visible en el discurso público.

![LDA](graficos/tematico/lda_topic_distribution.png)

---

#### ¿Dónde concentra su atención el documento?

Este heatmap muestra la intensidad de menciones de cada eje de política pública a lo largo del documento, dividido en secciones de páginas. Permite ver si el programa trata los temas de forma integrada o si los agrupa por capítulos.

![Heatmap temático](graficos/tematico/theme_heatmap.png)

---

#### Evolución temática a lo largo del programa

La línea temporal de menciones revela la arquitectura narrativa del documento: qué temas abren la discusión y cuáles aparecen solo al final. En el programa de Espriella, la economía domina la primera mitad del documento, mientras la seguridad y las instituciones aparecen de forma más transversal.

![Timeline temático](graficos/tematico/theme_mentions_timeline.png)

---

#### Peso relativo de cada eje de política

En términos absolutos, el conteo de menciones por eje confirma el perfil del programa: **Economía** (52 menciones de palabras clave), **Seguridad** (39), **Instituciones** (30) y **Anticorrupción** (27) concentran el 78% del corpus temático. Salud, campo, paz y energía quedan en un segundo plano comparativo. Desde una perspectiva de economía política, la jerarquía de menciones anticipa la jerarquía de prioridades presupuestales que el candidato establecería en gobierno.

![Totales temáticos](graficos/tematico/theme_totals.png)

---

#### Propuestas por área temática (clasificación manual)

Esta clasificación complementa el análisis NLP con una lectura cualitativa: cada propuesta identificada manualmente se asignó a un eje temático. La combinación de ambos métodos — cuantitativo y cualitativo — permite triangular los hallazgos.

![Propuestas por área](graficos/tematico/propuestas_por_area.png)

#### Distribución del corpus por tipo de enunciado

No todo el texto de un programa de gobierno es una propuesta. Esta clasificación separa los enunciados propositivos concretos de la narrativa motivacional, los diagnósticos, los marcos ideológicos y las promesas vagas. En el programa de Espriella predominan las propuestas concretas y los datos cuantitativos — una señal de que el documento está diseñado para comunicar gestión, no inspiración.

![Tipos de enunciado](graficos/tematico/tipos_enunciado.png)

---

### Análisis de sentimiento

El modelo de sentimiento usado es `robertuito-base-uncased-sentiment` de pysentimiento, entrenado en español latinoamericano. Analiza el tono de cada página como positivo, negativo o neutro. En economía política, el perfil de sentimiento revela si el programa construye su argumento desde el diagnóstico crítico (negativo) o desde la propuesta transformadora (positivo) — y en qué proporción.

#### Arco de sentimiento — página a página

El arco de sentimiento muestra que el programa de Espriella mantiene un tono predominantemente **positivo-propositivo** a lo largo de todo el documento. No hay picos de sentimiento negativo pronunciados, lo que es consistente con la ausencia de ataques nombrados a figuras políticas adversarias. El programa construye su argumento desde la propuesta, no desde la denuncia.

Esto contrasta con el patrón típico de programas de oposición en América Latina, donde el tono oscila entre diagnóstico crítico del gobierno saliente y propuesta alternativa. Espriella opta por no diagnosticar explícitamente el gobierno Petro como referente negativo en el documento formal.

![Arco de sentimiento](graficos/sentimiento/sentiment_arc.png)

#### Distribución global de sentimiento

![Distribución sentimiento](graficos/sentimiento/sentiment_distribution.png)

---

### Análisis semántico

#### Red de similitud semántica (Word2Vec)

El modelo Word2Vec aprende representaciones vectoriales de cada palabra a partir de su contexto de aparición en el documento. Dos palabras son semánticamente similares si tienden a aparecer en los mismos contextos. La red conecta palabras cuya similitud coseno supera el umbral definido; el tamaño de los nodos refleja su frecuencia.

En el espacio semántico de Patria Milagro, los conceptos más conectados son los del eje económico-fiscal: *billón*, *tributario*, *reducción*, *infraestructura*, *meta* forman un clúster denso. La **seguridad** conecta con *familia* y *empleo* — lo que revela que en el programa el orden público se conceptualiza no solo como control del crimen sino como condición para el desarrollo económico y la vida familiar. Esta es la diferencia conceptual clave con Cepeda, donde seguridad conecta semánticamente con *derechos humanos*, *verdad* y *conflicto*.

![Red semántica](graficos/semantica/semantic_network.png)

#### Embeddings de palabras (t-SNE)

La proyección t-SNE comprime los vectores de 100 dimensiones de Word2Vec a 2 dimensiones, agrupando palabras conceptualmente similares. Los clústeres visibles revelan las comunidades semánticas del documento: el eje económico (billones, inversión, fiscal, tributario), el eje de orden público (seguridad, crimen, fuerza, narco) y el eje institucional (república, constitución, estado, ley).

![t-SNE](graficos/semantica/tsne_embeddings.png)

---

### Análisis retórico y estructural

#### Distribución de longitud de oraciones

La longitud de las oraciones es uno de los indicadores más directos del estilo de comunicación política. Oraciones cortas comunican certeza, urgencia y accesibilidad; oraciones largas son típicas de textos jurídicos, académicos o deliberadamente complejos.

El programa de Espriella tiene una longitud media de **12.5 palabras por oración** y una mediana de **10 palabras** — el 72.7% de las oraciones tiene menos de 15 palabras. Esto lo convierte en el programa más legible de los analizados, muy por debajo de las 25.8 palabras por oración de Cepeda. El máximo es de 67 palabras, correspondiente a una tabla de cifras fiscales, no a un párrafo narrativo. El formato es el de una presentación ejecutiva: bullets, cifras, verbos de acción.

| Indicador | Espriella | Cepeda |
|---|---|---|
| Índice Fernández Huerta | 45.0/100 | 51.9/100 |
| Palabras por oración | 12.5 | 25.8 |
| Sílabas por palabra | 2.52 | 2.14 |
| TTR (riqueza léxica) | 0.569 | 0.148 |
| MTLD | 285.5 | 366.7 |

El TTR de 0.569 en 21 páginas es muy alto — indica variedad léxica notable para el tamaño del corpus. El MTLD de 285.5 es sólido. Estos indicadores sugieren un documento que no repite fórmulas, sino que introduce vocabulario técnico diverso por cada eje temático.

![Longitud oraciones](graficos/estructura/sentence_length_hist.png)

---

#### Iniciadores de oración más frecuentes

Las palabras con las que el candidato inicia sus oraciones revelan su modo de razonamiento político. Los iniciadores más frecuentes en Patria Milagro son términos de acción directa y categorización — "Creación de", "Reducción del", "Plan de", "Sistema de" — lo que confirma el registro ejecutivo del documento: no argumenta ni narra, enumera medidas.

![Iniciadores](graficos/estructura/sentence_starters.png)

---

#### Densidad de palabras por página

El mapa de calor de densidad muestra cuántas palabras contiene cada página. Las páginas más densas corresponden a los pilares de seguridad y economía, que incluyen tablas de cifras y listas de propuestas. Las páginas menos densas son las de marcos ideológicos (Brújula Moral, Principios Innegociables), que usan diseño visual con texto fragmentado. Esta distribución confirma que el documento mezcla dos géneros: comunicación política de campaña y propuesta técnica de gobierno.

![Densidad heatmap](graficos/estructura/density_heatmap.png)

---

#### ¿A quién nombra el programa? (Entidades nombradas — NER)

El análisis de reconocimiento de entidades nombradas (NER) revela qué organizaciones, instituciones y lugares menciona explícitamente el programa. En economía política institucional, **el conjunto de actores que el candidato nombra define el espacio de coaliciones que imagina para gobernar**: las instituciones que fortalecerá, las que reformará y las que ignorará.

![NER org](graficos/estructura/ner_org.png)

![NER loc](graficos/estructura/ner_loc.png)

#### Red de co-ocurrencia de entidades

Cuando dos entidades aparecen en la misma página, probablemente tienen una relación funcional en el programa. La red de co-ocurrencia revela qué organizaciones e instituciones el candidato conceptualiza juntas — y, por tanto, qué arquitectura institucional imagina.

![NER red](graficos/estructura/ner_cooccurrence_network.png)

---

#### Verificabilidad de las 30 cifras extraídas

El programa de Espriella incluye cifras concretas — una de sus marcas distintivas frente a otros candidatos. La pregunta relevante de economía política no es si las cifras existen, sino si son verificables: si tienen fuente explícita, si son consistentes con datos oficiales (DIAN, DNP, Banco de la República, UNODC) y si la metodología para alcanzarlas está descrita.

![Verificabilidad](graficos/estructura/verificabilidad_cifras.png)

#### Densidad programática por documento — ¿dónde están las propuestas?

Esta comparación entre documentos muestra qué proporción de cada texto corresponde a propuestas concretas versus narrativa e ideología. El hallazgo central: **el programa formal de 21 páginas tiene la mayor densidad propositiva**, seguido de la propuesta territorial del Valle del Cauca. Los Pilares Fundacionales son casi exclusivamente narrativa ideológica. La crítica de que el programa "cabe en tres páginas" confunde el resumen ejecutivo con el programa completo.

![Densidad por fuente](graficos/estructura/densidad_por_fuente.png)

---

### Figuras políticas mencionadas

El análisis busca menciones explícitas a Gustavo Petro y Álvaro Uribe Vélez — las dos figuras que en el programa de Cepeda suman 495 menciones y estructuran toda su narrativa política.

El resultado es inequívoco: **el programa formal de Espriella no menciona a ninguna figura política adversaria por nombre**. Ni "Petro", ni "Uribe", ni ningún otro político colombiano aparece en el documento. El adversario de Espriella es abstracto — la corrupción, el crimen, la burocracia, el modelo económico "equivocado" — en lugar de personal. Esta es una decisión retórica consciente que distingue su documento de todos los programas de oposición analizados: el ataque se hace a un sistema, no a una persona.

En contraste:

| Figura | Espriella (21 págs.) | Cepeda (433 págs.) |
|---|---|---|
| Gustavo Petro | **0** | 274 |
| Álvaro Uribe Vélez | **0** | 221 |

Los gráficos muestran cero actividad, lo que en sí mismo es el hallazgo más relevante de esta sección.

![Menciones por página](graficos/figuras_politicas/menciones_por_pagina.png)

![Tono del contexto](graficos/figuras_politicas/tono_contexto_figuras.png)

---

### Análisis comparativo: Espriella vs. Cepeda

#### Distribución temática comparada

Este gráfico contrasta el porcentaje del espacio programático dedicado a cada eje de política en ambos candidatos. El contraste más marcado: Espriella dedica el doble de espacio relativo a seguridad (28% vs. 8% de Cepeda), mientras Cepeda dedica más del triple a justicia social (18% vs. 5% de Espriella) y al doble a paz y conflicto (12% vs. 4%). La distribución temática no es solo un indicador de prioridades — es el mapa de las coaliciones que cada candidato necesita para gobernar.

![Comparativo temático](graficos/comparativo/espriella_vs_cepeda_tematico.png)

---

#### Composición del discurso: ¿propositivo o confrontacional?

Ambos candidatos producen más propuestas concretas que ataques políticos. La diferencia está en el margen: Espriella tiene proporcionalmente más narrativa motivacional (31% vs. 20% de Cepeda), mientras Cepeda tiene más ataques políticos explícitos (14% vs. 10% de Espriella). Pero dado que el corpus de Cepeda es 20 veces más grande, el volumen absoluto de ataques de Cepeda es sustancialmente mayor.

![Tono comparado](graficos/comparativo/tono_espriella_vs_cepeda.png)

---

#### Cobertura temática: resumen ejecutivo vs. pilares completos

Este gráfico responde directamente a la crítica de que el programa "cabe en tres páginas": el resumen ejecutivo cubre todos los temas pero con profundidad mínima, mientras los pilares temáticos completos desarrollan cada uno en detalle. La brecha más grande está en seguridad y economía — exactamente los ejes que más propuestas concretas tienen en el programa completo.

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
