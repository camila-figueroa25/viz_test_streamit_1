import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# 1. CARGA DE DATOS
# -------------------------

@st.cache_data
def load_data():
    csv_path = "emissions_per_country/annual-co2-emissions-per-country.csv"
    df = pd.read_csv(csv_path)

    # Renombrar columnas para trabajar más fácil
    df = df.rename(columns={"Entity": "country", "Code": "code", "Year": "year"})
    df["code"] = df["code"].str.upper()

    # Filtrar códigos ISO3 válidos
    df = df[df["code"].str.len() == 3]

    # Detectar la columna de emisiones (la que no es country, code ni year)
    value_col = [c for c in df.columns if c not in ["country", "code", "year"]][0]
    df = df.rename(columns={value_col: "co2"})

    return df


df = load_data()

# -------------------------
# 2. CONFIGURACIÓN DE PÁGINA
# -------------------------

st.set_page_config(
    page_title="Mapa CO₂ por país (Streamlit Cloud)",
    layout="wide"
)

st.title("🌍 Emisiones de CO₂ por país")
st.markdown(
    """
    Esta app muestra un **mapa mundial** con las emisiones anuales de CO₂ por país,
    usando únicamente el archivo CSV (sin GeoPandas ni shapefiles, para que funcione en Streamlit Cloud).

    - Usa el **slider de año** en la barra lateral para cambiar la visualización.  
    - Los países coloreados tienen datos de emisiones para ese año.  
    - Los países sin datos quedan con el color de fondo (efecto similar a “gris”).
    """
)

# -------------------------
# 3. SIDEBAR (CONTROLES)
# -------------------------

st.sidebar.header("Controles")

years = sorted(df["year"].unique())
min_year = int(min(years))
max_year = int(max(years))

year_selected = st.sidebar.slider(
    "Selecciona el año",
    min_value=min_year,
    max_value=max_year,
    value=max_year,
    step=1
)

st.sidebar.markdown(
    """
    **Nota:**  
    Streamlit Cloud no soporta GeoPandas ni shapefiles.  
    Por eso, el mapa usa un choropleth de Plotly basado en los códigos ISO3:

    - País coloreado → hay dato de CO₂.  
    - País sin color → no hay dato en el CSV para ese año.
    """
)

# -------------------------
# 4. FILTRAR DATA POR AÑO
# -------------------------

df_year = df[df["year"] == year_selected]

if df_year.empty:
    st.warning(f"No hay datos de CO₂ para el año {year_selected}.")
else:
    # -------------------------
    # 5. MAPA CON PLOTLY
    # -------------------------

    fig = px.choropleth(
        df_year,
        locations="code",           # códigos ISO3
        color="co2",                # variable a colorear
        hover_name="country",       # nombre que aparece al pasar el mouse
        color_continuous_scale="OrRd",
        projection="natural earth",
        title=f"Emisiones de CO₂ por país — {year_selected}"
    )

    # Ajustes estéticos
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        coloraxis_colorbar=dict(
            title="CO₂",
            ticks="outside"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # 6. TABLA RESUMEN
    # -------------------------

    st.subheader("Top 10 países emisores en el año seleccionado")
    top10 = (
        df_year[["country", "co2"]]
        .sort_values("co2", ascending=False)
        .reset_index(drop=True)
        .head(10)
    )
    st.dataframe(top10)


