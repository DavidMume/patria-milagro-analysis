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
├── sources/          # Inventario de 20 fuentes documentales (CSV)
├── data/
│   ├── raw/          # Textos crudos (no incluidos — ver .gitignore)
│   └── processed/    # Corpus limpio, lematizado y clasificado
├── docs/             # Metodología, notas, glosario
├── scripts/          # Script Python para generar gráficos
├── notebooks/        # Análisis paso a paso en Jupyter
├── outputs/          # Matrices de propuestas y cifras (CSV/MD)
└── graficos/
    ├── frecuencias/  # WordCloud, top unigrams
    ├── tematico/     # Propuestas por área, tipos de enunciado
    ├── estructura/   # Verificabilidad, densidad por fuente
    └── comparativo/  # Espriella vs. Cepeda
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

---

## Visualizaciones

### Frecuencias

#### WordCloud — Vocabulario dominante del corpus
![WordCloud](graficos/frecuencias/wordcloud.png)

#### Top 40 términos más frecuentes (lematizados)
![Top 40 unigrams](graficos/frecuencias/top40_unigrams.png)

---

### Análisis temático

#### Propuestas por área temática
![Propuestas por área](graficos/tematico/propuestas_por_area.png)

#### Distribución del corpus por tipo de enunciado
![Tipos de enunciado](graficos/tematico/tipos_enunciado.png)

---

### Estructura del programa

#### Verificabilidad de las 30 cifras extraídas
![Verificabilidad](graficos/estructura/verificabilidad_cifras.png)

#### Densidad programática por documento — ¿dónde están las propuestas concretas?
![Densidad por fuente](graficos/estructura/densidad_por_fuente.png)

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

| Paso | Método | Pregunta que responde |
|---|---|---|
| 1. Inventario de fuentes | Clasificación manual | ¿Cuáles son los documentos del programa? |
| 2. Limpieza y segmentación | Regex, spaCy | ¿Cuál es el corpus real? |
| 3. Clasificación de enunciados | Reglas + anotación | ¿Qué tipo de texto domina? |
| 4. Análisis de frecuencias | N-gramas, WordCloud | ¿Qué conceptos dominan el discurso? |
| 5. Análisis temático | Diccionarios por eje | ¿Cuánto espacio le dedica a cada área? |
| 6. Extracción de cifras | Regex + verificación | ¿Qué datos son verificables? |
| 7. Análisis comparativo | Contraste con Cepeda | ¿Qué diferencia a ambos programas? |

Ver metodología completa en [`docs/metodologia.md`](docs/metodologia.md).

## Requisitos

```bash
pip install spacy pandas matplotlib wordcloud openpyxl scikit-learn
python -m spacy download es_core_news_lg
python scripts/generar_graficos.py
```

## Estado del proyecto

- [x] Inventario de fuentes (20 documentos)
- [x] Metodología y glosario
- [x] Extracción de cifras (30 cifras, con nivel de verificabilidad)
- [x] Comparación resumen ejecutivo vs. pilares
- [x] Visualizaciones (9 gráficos)
- [x] Análisis comparativo Espriella vs. Cepeda
- [ ] Corpus limpio y lematizado (requiere archivos en data/raw/)
- [ ] Clasificación automática de enunciados
- [ ] Artículo de opinión — versión final
