#!/usr/bin/env python3
"""Convierte normativa_full.txt a Articulado-Completo.md con wikilinks."""

import re

SRC = "/home/notbuc/.openclaw/workspace/POT-Revision-2025/normativa_full.txt"
DST = "/home/notbuc/.openclaw/workspace/Obsidian-POT/Articulado-Completo.md"

with open(SRC, "r", encoding="utf-8") as f:
    text = f.read()

# ── 1. Limpiar caracteres de control y páginas ────────────────────
text = re.sub(r'\f', '', text)           # form feeds
text = re.sub(r'\xa0', ' ', text)         # non-breaking spaces
text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)  # trailing whitespace

# ── 2. Estructurar encabezados ────────────────────────────────────
# CAPÍTULO X → ## Capítulo X
text = re.sub(r'^(CAP[ÍI]TULO\s+\d+)', r'## \1', text, flags=re.MULTILINE)

# Artículo X° → ### Artículo X
text = re.sub(r'^(Art[íi]culo\s+\d+[°º]?)', r'### \1', text, flags=re.MULTILINE)

# ── 3. Wikilinks a zonas existentes ───────────────────────────────
zrs = [
    'ZR01','ZR02','ZR03','ZR04','ZR05','ZR06','ZR07','ZR08','ZR09',
    'ZR10','ZR11','ZR12','ZR13','ZR14','ZR16','ZR17','ZR18','ZR19',
    'ZR20','ZR21','ZR22','ZR23','ZR24'
]
zes = [
    'ZE01','ZE02','ZE06','ZE07','ZE09','ZE13','ZE14','ZE16','ZE17','ZE18','ZE19','ZE20'
]
temas = {
    'Riesgo de Inundación': 'Riesgo-Inundacion',
    'municipio.*Paso de los Toros|Paso de los Toros.*municipio': 'Riesgo-Inundacion',
}

# ZR - con boundaries para no agarrar ZR15
for z in zrs:
    text = re.sub(rf'\b({z})\b', r'[[\1]]', text)

# ZE
for z in zes:
    text = re.sub(rf'\b({z})\b', r'[[\1]]', text)

# ZR15 no existe como página - dejar texto plano pero marcar
text = re.sub(r'\b(ZR15)\b', r'\1 (*zona no incluida en este índice*)', text)

# ── 4. Wikilinks a láminas que existen ────────────────────────────
text = re.sub(r'\bL[áa]mina\s+([14]0?)\b', r'[[Lamina-0\1|Lámina \1]]', text, flags=re.IGNORECASE)
text = re.sub(r'\bL[áa]mina\s+40\b', r'[[Lamina-40|Lámina 40]]', text, flags=re.IGNORECASE)
# otras láminas → link al índice general
text = re.sub(r'\bL[áa]mina\s+(\d+)\b', r'[[Laminas-MOC|Lámina \1]]', text, flags=re.IGNORECASE)

# ── 5. Links a temas ──────────────────────────────────────────────
text = re.sub(r'\bSistema de Espacios P[úu]blicos\b', '[[Espacios-Publicos|Sistema de Espacios Públicos]]', text)
text = re.sub(r'\bSistema Vial\b', '[[Sistema-Vial|Sistema Vial]]', text, flags=re.IGNORECASE)
text = re.sub(r'\bJerarquizaci[óo]n vial\b', '[[Sistema-Vial|Jerarquización vial]]', text, flags=re.IGNORECASE)
text = re.sub(r'\bRiesgo de Inundaci[óo]n\b', '[[Riesgo-Inundacion|Riesgo de Inundación]]', text, flags=re.IGNORECASE)
text = re.sub(r'\bCategorizaci[óo]n del suelo\b', '[[Categorizacion-Suelo|Categorización del suelo]]', text, flags=re.IGNORECASE)
text = re.sub(r'\bProyectos Estrat[ée]gicos\b', '[[Proyectos-Estrategicos|Proyectos Estratégicos]]', text, flags=re.IGNORECASE)
text = re.sub(r'\bDINAGUA\b', '[[Laminas-DINAGUA|DINAGUA]]', text)

# ── 6. Encabezado del documento ───────────────────────────────────
header = """# 📜 Articulado Completo — Memoria Normativa

> **Revisión del Plan Local de Ordenamiento Territorial y Desarrollo Sostenible de la ciudad de Tacuarembó y su microrregión**
> Documento de Avance — Marzo 2025

---

*Texto completo del articulado propuesto, con enlaces a las fichas de zonas y temas desarrollados en este sitio.*

→ [[POT-Tacuarembo-MOC|Volver al mapa de contenido]]

---

"""

# ── 7. Escribir ───────────────────────────────────────────────────
with open(DST, "w", encoding="utf-8") as f:
    f.write(header)
    f.write(text)

print(f"✅ Generado: {DST}")
print(f"   Líneas: {len(text.splitlines())}")
