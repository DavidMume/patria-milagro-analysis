# Colombia, Patria Milagro — Análisis político-económico del programa de Abelardo de la Espriella

Repositorio de análisis documental del programa de gobierno del candidato presidencial Abelardo de la Espriella para las elecciones colombianas de 2026.

## Hipótesis central

El documento de tres páginas (*Primeras 13 propuestas para reconstruir la Patria Milagro*) es una pieza de comunicación política, no el programa completo. El proyecto programático real debe reconstruirse a partir de los Pilares Fundacionales, los documentos temáticos, los discursos y las propuestas territoriales — un corpus de más de 300 páginas distribuidas en el sitio [defensoresdelapatria.com](https://defensoresdelapatria.com/colombia-patria-milagro/).

## Estructura del repositorio

```
patria-milagro-analysis/
├── sources/          # Inventario de fuentes y textos extraídos (sin PDFs)
├── data/
│   ├── raw/          # Textos crudos normalizados
│   └── processed/    # Corpus limpio, lematizado y clasificado
├── docs/             # Metodología, notas, glosario
├── notebooks/        # Análisis en Jupyter
├── outputs/          # Matrices de propuestas y cifras
├── visualizations/   # Gráficos y wordclouds
└── article/          # Borrador y versión final del artículo de opinión
```

## Fuentes documentales

| ID | Documento | Tipo | URL |
|---|---|---|---|
| F01 | Primeras 13 propuestas (Propuestas del Tigre) | Resumen ejecutivo | [enlace](https://defensoresdelapatria.com/wp-content/uploads/2026/04/PROPUESTAS-DEL-TIGRE.pdf) |
| F02 | Pilares para reconstruir la Patria Milagro | Programa temático (web) | [enlace](https://defensoresdelapatria.com/colombia-patria-milagro/) |
| F03 | Pilares Fundacionales | Marco ideológico | [enlace](https://defensoresdelapatria.com/wp-content/uploads/2026/04/PILARES-FUNDACIONALES.pdf) |
| F04 | Programa de gobierno oficial | Documento formal | PDF registrado |
| F05 | El Milagro del Valle del Cauca | Propuesta territorial | [enlace](https://defensoresdelapatria.com/wp-content/uploads/2026/04/EL-MILAGRO-DEL-VALLE-DEL-CAUCA-PRIMERAS-PROPUESTAS-PARA-LOS-VALLECAUCANOS_compressed.pdf) |
| F06 | Discurso constitución / Bogotá | Discurso político | PDF |

## Metodología

Ver [`docs/metodologia.md`](docs/metodologia.md) para el protocolo completo de limpieza, clasificación y análisis NLP.

## Áreas temáticas analizadas

- Democracia e instituciones
- Seguridad y control territorial
- Anticorrupción
- Economía y modelo de desarrollo
- Política fiscal
- Energía y minería
- Salud
- Educación
- Campo y agro
- Mujeres y cuidado
- Cultura
- Medio ambiente
- Bienestar animal
- Valle del Cauca / propuestas territoriales

## Visualizaciones

| Gráfica | Descripción |
|---|---|
| ![Tipos de enunciado](visualizations/01_tipos_enunciado.png) | Distribución del corpus por tipo: narrativa, propuesta, diagnóstico, etc. |
| ![Propuestas por área](visualizations/02_propuestas_por_area.png) | Densidad programática por área temática |
| ![Verificabilidad](visualizations/03_verificabilidad_cifras.png) | Qué porcentaje de las cifras citadas son verificables |
| ![Cobertura](visualizations/04_cobertura_resumen_vs_pilares.png) | Comparación de cobertura: resumen ejecutivo vs. pilares completos |
| ![Cifras por área](visualizations/05_cifras_por_area.png) | Distribución de cifras extraídas por área temática |
| ![WordCloud](visualizations/06_wordcloud_corpus.png) | Términos más frecuentes del corpus completo |

> Las visualizaciones se generan ejecutando `notebooks/03_visualizaciones.ipynb`

## Estado del proyecto

- [x] Inventario de fuentes
- [x] Metodología de análisis
- [x] Estructura del repositorio
- [ ] Limpieza y segmentación del corpus
- [ ] Clasificación de enunciados
- [ ] Lematización con spaCy
- [ ] Matriz de propuestas
- [ ] Análisis TF-IDF por área temática
- [ ] Artículo de opinión

## Requisitos

```bash
pip install spacy pandas openpyxl scikit-learn matplotlib wordcloud
python -m spacy download es_core_news_lg
```

## Autor

Análisis desarrollado con fines académicos y periodísticos. Fecha de inicio: junio 2026.
