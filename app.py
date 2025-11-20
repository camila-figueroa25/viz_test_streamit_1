import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# 1. CARGA DE DATOS
# -------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("owid-co2-data.csv")

    # Nos quedamos con columnas clave
    cols = [
        "country",
        "iso_code",
        "year",
        "co2",              # emisiones totales (millones de toneladas)
        "co2_per_capita"    # emisiones per cápita
    ]
    df = df[cols]

    # Filtramos solo códigos ISO3 válidos (para el mapa)
    df = df[df["iso_code"].notna()]
    df = df[df["iso_code"].str.len() == 3]

    return df

df = load_data()

# Lista de países "normales" (sacamos agregados tipo World)
country_list = sorted(
    df[
        (~df["country"].isin(["World"])) &
        (df["iso_code"].notna())
    ]["country"].unique()
)

# -------------------------
# 2. CONFIGURACIÓN APP
# -------------------------

st.set_page_config(page_title="Emisiones de CO₂ — Our World in Data", layout="wide")
st.title("🌍 Explorador de emisiones de CO₂ (Our World in Data)")

st.markdown(
    """
    Esta app recrea y adapta visualizaciones de  
    [Our World in Data — CO₂ Emissions](https://ourworldindata.org/co2-emissions).

    - Puedes **elegir el año**.
    - Puedes **seleccionar países**.
    - Puedes cambiar el **tipo de métrica** (totales vs per cápita).
    - El **mismo año** controla el mapa, el ranking y la vista de detalle.
    """
)

# -------------------------
# 3. SIDEBAR — CONTROLES COMPARTIDOS
# -------------------------

st.sidebar.header("Controles")

# 3.1 Año (estado compartido)
min_year = int(df["year"].min())
max_year = int(df["year"].max())

year_selected = st.sidebar.slider(
    "Selecciona el año",
    min_value=min_year,
    max_value=max_year,
    value=max_year,
    step=1
)

# 3.2 Países
countries_selected = st.sidebar.multiselect(
    "Selecciona uno o más países",
    options=country_list,
    default=["Chile", "United States", "China"]
)

# 3.3 Tipo de métrica / modo de visualización
metric_label = st.sidebar.selectbox(
    "Tipo de métrica",
    options=[
        "Emisiones totales de CO₂",
        "Emisiones de CO₂ per cápita"
    ]
)

# Mapeo de etiqueta → columna del dataset
if metric_label == "Emisiones totales de CO₂":
    metric_col = "co2"
    metric_units = "millones de toneladas"
else:
    metric_col = "co2_per_capita"
    metric_units = "toneladas por persona"


# -------------------------
# 4. FILTRAR DATA SEGÚN CONTROLES (ESTADO COMPARTIDO)
# -------------------------

# Filtramos por año (para mapa + ranking)
df_year = df[df["year"] == year_selected]

# Si el usuario no selecciona países, interpretamos "todos"
if countries_selected:
    df_year_countries = df_year[df_year["country"].isin(countries_selected)]
else:
    df_year_countries = df_year.copy()

# También creamos un dataset para series de tiempo (solo filtramos países)
if countries_selected:
    df_time = df[df["country"].isin(countries_selected)]
else:
    df_time = df.copy()

# -------------------------
# 5. LAYOUT PRINCIPAL (TRES GRÁFICOS)
# -------------------------

col1, col2 = st.columns([2, 1])

# ========= 5.1 MAPA MUNDIAL =========
with col1:
    st.subheader(f"Mapa mundial — {metric_label.lower()} ({year_selected})")

    if df_year[metric_col].dropna().empty:
        st.warning(f"No hay datos de **{metric_label.lower()}** para el año {year_selected}.")
    else:
        fig_map = px.choropleth(
            df_year,
            locations="iso_code",
            color=metric_col,
            hover_name="country",
            color_continuous_scale="OrRd",
            projection="natural earth",
            labels={metric_col: metric_label},
            title=None
        )

        fig_map.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_colorbar=dict(
                title=metric_col,
                ticks="outside"
            )
        )

        st.plotly_chart(fig_map, use_container_width=True)

# ========= 5.2 RANKING (BARRAS) =========
with col2:
    st.subheader(f"Top países — {metric_label.lower()} ({year_selected})")

    df_rank = (
        df_year_countries[["country", metric_col]]
        .dropna()
        .sort_values(metric_col, ascending=False)
        .head(10)
    )

    if df_rank.empty:
        st.info("No hay datos para los países seleccionados en este año.")
    else:
        fig_bar = px.bar(
            df_rank,
            x=metric_col,
            y="country",
            orientation="h",
            labels={
                "country": "País",
                metric_col: metric_label
            }
        )
        fig_bar.update_layout(margin=dict(l=0, r=0, t=20, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

# ========= 5.3 SERIE DE TIEMPO (MISMO ESTADO COMPARTIDO) =========

st.subheader(f"Evolución temporal — {metric_label.lower()}")

df_time_metric = df_time[df_time[metric_col].notna()]

if df_time_metric.empty:
    st.info("No hay datos históricos suficientes para la combinación de países y métrica seleccionada.")
else:
    fig_line = px.line(
        df_time_metric,
        x="year",
        y=metric_col,
        color="country",
        labels={
            "year": "Año",
            metric_col: f"{metric_label} ({metric_units})",
            "country": "País"
        }
    )

    # Línea vertical para marcar el año seleccionado (estado compartido)
    fig_line.add_vline(
        x=year_selected,
        line_width=2,
        line_dash="dash",
        line_color="gray"
    )

    fig_line.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig_line, use_container_width=True)

st.markdown(
    f"""
    🔄 **Estado compartido:**  
    - El **año seleccionado ({year_selected})** controla el **mapa** y el **ranking de barras**.  
    - El **mismo año** se destaca en la **serie temporal** con una línea vertical.  
    - El **conjunto de países** y el **tipo de métrica** afectan a los **tres gráficos**.
    """
)
with st.expander("Información sobre los datos y decisiones de diseño"):
    st.markdown(
    """
    ### Datasets utilizados
    - **OWID CO₂ Emissions Dataset**  
      Tabla con emisiones totales y per cápita por país y año.  
      Variables: `co2`, `co2_per_capita`, `year`, `iso_code`.  
      Fuente: Our World in Data.

    ### Unidades y período
    - **CO₂ total:** millones de toneladas/año  
    - **CO₂ per cápita:** toneladas por persona/año  
    - Período aprox.: 1750 al 2022, esto varia según país

    ### Decisiones de diseño
    **1. Mapa choropleth (color → magnitud)**  
    Basado en las recomendaciones de la clase:  
    - Posición = canal más preciso para datos espaciales  
    - Color secuencial = magnitud (evitamos áreas y ángulos por baja precisión)  
    - Permite comparar patrones espaciales de emisiones.

    **2. Ranking con barras horizontales**  
    - Longitud = canal altamente preciso para comparación  
    - Mejor lectura de nombres de países  
    - Evita confusión de tonalidades similares.

    **3. Serie temporal alineada con el año elegido**  
    - Atributo secuencial → posición horizontal  
    - Mismo año marcado en mapa, barras y serie → estado compartido.

    ### Limitaciones
    - Países con años sin datos o con series incompletas  
    - Cambios históricos en fronteras  
    - Per cápita y totales no son comparables directamente  
    - Colores no representan exactitud puntual sino rangos  
    """
    )


