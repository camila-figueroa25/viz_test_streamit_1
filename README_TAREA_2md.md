# Visualizador Interactivo de Emisiones de CO₂  
App desarrollada en **Streamlit** para recrear y adaptar visualizaciones del portal  https://vizteststreamit1-ynesl2i3n7qlaiwuvle4vd.streamlit.app/
**Our World in Data — CO₂ Emissions**: https://ourworldindata.org/co2-emissions

El proyecto permite explorar emisiones de CO₂ por país, año y métrica, combinando  
visualización geográfica, comparaciones de ranking y tendencias temporales.

---

## Datasets utilizados

1. **OWID CO₂ Emissions Dataset**  
   - Archivo: `owid-co2-data.csv`  
   - Fuente: Our World in Data  
   - Variables principales:
     - `year`: año
     - `country`: país
     - `iso_code`: código ISO3
     - `co2`: emisiones totales (millones de toneladas)
     - `co2_per_capita`: emisiones per cápita (toneladas por persona)

---

## Funcionalidades interactivas de la app

La aplicación incluye:

### **Controles en sidebar**
- Selector de **año** (controla mapa, ranking y series temporal)
- Selector de **países** (uno o múltiples)
- Selector de **métrica**:
  - Emisiones totales de CO₂
  - Emisiones per cápita

### **Visualizaciones incluidas**
1. **Mapa choropleth mundial**  
   - Colorea países según la métrica seleccionada  
   - Basado en códigos ISO3  
   - Proyección *Natural Earth*

2. **Ranking de países (Top 10)**  
   - Barras horizontales para comparación clara

3. **Serie temporal multipaís**  
   - Evolución de la métrica a lo largo del tiempo  
   - Línea vertical marca el año seleccionado (estado compartido entre gráficos)

4. **Panel informativo**  
   - Dataset  
   - Unidades  
   - Decisiones de diseño 
   - Limitaciones de la data

---

## Decisiones de diseño 

### **1. Uso de mapa choropleth con escala secuencial**
- Basado en los principios de **marcas y canales** (pág. 25–33).  
- El mapa utiliza **posición** como canal principal, el más efectivo para datos espaciales.  
- El color secuencial usa **luminancia y saturación** para representar magnitud,  
  como recomienda la clase para atributos cuantitativos continuos.  
- Se evita el uso de **áreas o tamaños de burbujas**, que el documento identifica como  
  canales de baja precisión para comparar magnitudes (pág. 32–33).

### **2. Ranking con barras horizontales**
- Elegimos **barras** porque la clase establece que **longitud** es uno de los canales  
  más precisos para comparación cuantitativa (pág. 29).  
- Las barras horizontales facilitan la lectura de países con nombres largos.  
- Este tipo de gráfico corresponde a la operación de **ranking** presentada en la clase (pág. 17).

### **3. Serie temporal con eje X secuencial**
- El documento indica que el **tiempo es un atributo secuencial** y debe representarse  
  mediante posición en un eje continuo (pág. 14–15).  
- La línea vertical que marca el año seleccionado introduce **saliencia controlada**,  
  reforzando el estado compartido entre gráficos.

---

## Limitaciones del dataset

- Algunos países no tienen datos en los primeros años (antes de 1950).  
- Países creados recientemente (ej: Sudán del Sur) tienen series cortas.  
- Cambios en fronteras históricas no están reflejados en todos los períodos.  
- Datos per cápita y totales **no son comparables directamente** entre sí.  
- El mapa puede inducir una falsa sensación de precisión en países pequeños  
  debido a problemas clásicos de choropleths.

---

