# Metodología de análisis

## 1. Hipótesis de trabajo

El documento de tres páginas (*Primeras 13 propuestas*) es una pieza de comunicación política, no el programa completo. El programa real se distribuye en cinco capas documentales:

| Capa | Documento | Función |
|---|---|---|
| Narrativa/ideológica | Pilares Fundacionales, "Firmes por la Patria", "Extrema Coherencia" | Legitimación del proyecto, marco moral |
| Diagnóstico político | "La hora oscura de la Patria", "Defender la Patria para salvarla" | Definición del enemigo, urgencia histórica |
| Programática general | Pilares temáticos (seguridad, anticorrupción, salud, economía…) | Propuestas detalladas por sector |
| Territorial | El Milagro del Valle del Cauca | Adaptación regional |
| Resumen ejecutivo | PROPUESTAS-DEL-TIGRE.pdf | Pieza de campaña para público general |

---

## 2. Protocolo de limpieza de textos

### 2.1 Eliminación de ruido estructural

Los archivos TXT extraídos del sitio contienen elementos de navegación repetidos. Patrones a eliminar:

```
LogoDP-sin-bandera / Inicio / Nosotros / Noticias / Tienda / Descargas...
© 2026 Defensores de la Patria, All Rights Reserved – Powered By Strategee Group
Links / Inicio / Nosotros / Noticias / Contáctanos...
```

### 2.2 Segmentación

- **Unidad primaria:** párrafo (separado por `\n\n`)
- **Unidad secundaria:** sección (encabezado en MAYÚSCULAS SOSTENIDAS)

### 2.3 Clasificación por tipo de enunciado

| Etiqueta | Descripción | Ejemplo |
|---|---|---|
| `DIAGNÓSTICO` | Describe el problema actual | *"Colombia ha llegado a 330.000 hectáreas de coca"* |
| `PROPUESTA` | Acción concreta prometida | *"Crearé un Bloque de Búsqueda contra la Corrupción"* |
| `CIFRA` | Dato cuantificable | *"$137,65 billones en riesgo por corrupción"* |
| `NARRATIVA` | Retórica, apelación emocional | *"La Patria nos está llamando porque está herida"* |
| `ATAQUE_POLÍTICO` | Crítica explícita a adversarios | *"Petro, el Pacto Histórico e Iván Cepeda…"* |
| `PROMESA_VAGA` | Intención sin mecanismo | *"haremos una transformación estructural"* |
| `MARCO_IDEOLÓGICO` | Definición de valores/visión | *"Extrema Coherencia", "bien común"* |

---

## 3. Normalización de términos

| Variante en texto | Término normalizado |
|---|---|
| Patria Milagro / patria / Patria | patria_milagro |
| Fuerza Pública / Fuerzas Armadas / Ejército / Policía | fuerza_publica |
| Pacto Histórico / gobierno actual / Petro / extrema izquierda | gobierno_petro |
| Constituyente / asamblea constituyente | constituyente |
| Extinción de dominio / extinción de dominio exprés | extincion_dominio |
| blockchain / registros inmutables / contratos inteligentes | blockchain_gobierno |
| los nunca / ciudadano honrado / colombiano de bien | los_nunca |

---

## 4. Pipeline NLP

```python
import spacy
import re
import pandas as pd

nlp = spacy.load("es_core_news_lg")

PATRONES_RUIDO = [
    r'LogoDP-sin-bandera.*?Youtube\n',
    r'Links\nInicio.*?Únete al Movimiento\n',
    r'© \d{4} Defensores.*?\n',
]

PATRON_CIFRA = r'\$[\d\.,]+ (billones|millones)|[\d\.,]+ (hectáreas|casos|municipios|%)'

TIPOS_ENUNCIADO = [
    'DIAGNÓSTICO', 'PROPUESTA', 'CIFRA',
    'NARRATIVA', 'ATAQUE_POLÍTICO',
    'PROMESA_VAGA', 'MARCO_IDEOLÓGICO'
]

def limpiar(texto):
    for patron in PATRONES_RUIDO:
        texto = re.sub(patron, '', texto, flags=re.DOTALL)
    return texto.strip()

def lematizar(texto):
    doc = nlp(texto)
    return ' '.join([t.lemma_ for t in doc if not t.is_stop and not t.is_punct])
```

---

## 5. Campos del CSV procesado

```
id | fuente | seccion | parrafo | tipo_enunciado | area_tematica |
subtema | cifra_detectada | entidades_nombradas | lemmatized |
keywords_tfidf | tono_estimado | verificable
```

---

## 6. Limitaciones

- Los PDFs no se incluyen en el repositorio por derechos de autor.
- El scrape del sitio web puede estar incompleto (algunas páginas devolvieron error 403).
- La clasificación de enunciados es manual en una primera fase; puede introducir sesgo del analista.
- Las cifras citadas en los documentos no siempre tienen fuente explícita verificable.
