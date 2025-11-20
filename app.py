#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import geopandas as gpd
import pandas as pd
import plotly.express as px


# In[ ]:


# cargar shapefile natural earth
shp_path = '50m_cultural/ne_50m_admin_0_countries.shp'
world = gpd.read_file(shp_path)

# estandarizar columna iso3
world = world.rename(columns={'ISO_A3': 'code'})
world['code'] = world['code'].str.upper()

# cargar emisiones
df = pd.read_csv('emissions_per_country/annual-co2-emissions-per-country.csv')
df = df.rename(columns={'Entity': 'country', 'Code': 'code', 'Year': 'year'})
df['code'] = df['code'].str.upper()

# filtrar a códigos iso válidos
df = df[df['code'].str.len() == 3]

# quedarnos con la columna de emisiones
value_col = [c for c in df.columns if c not in ['country', 'code', 'year']]
df = df.rename(columns={value_col[0]: 'co2'})
df


# In[ ]:


# maestro de países: una sola fila por code, como base para todos los años
world_master = (
    world[['code', 'NAME', 'geometry']]
    .drop_duplicates(subset=['code'])
    .rename(columns={'NAME': 'country'})
    .set_index('code')
)

# geojson fijo indexado por code (iso3)
geojson_world = world_master['geometry'].__geo_interface__
geojson_world


# In[ ]:


world_master.crs


# In[ ]:


def make_co2_map(df_co2, year):
    # emisiones del año seleccionado, agregadas por país
    co2_year = (
        df_co2[df_co2['year'] == year][['code', 'co2']]
        .groupby('code', as_index=False)
        .agg({'co2': 'sum'})
        .set_index('code')
    )

    # unir al maestro: aquí nunca se pierden países
    world_y = world_master.join(co2_year, how='left')

    # países con dato vs sin dato
    g_with = world_y[world_y['co2'].notna()].reset_index()
    g_no = world_y[world_y['co2'].isna()].reset_index()

    # capa 1: países con dato → escala continua
    fig = px.choropleth(
        g_with,
        geojson=geojson_world,
        locations='code',            # usa el iso3
        color='co2',
        hover_name='country',
        projection='natural earth',
        color_continuous_scale='Reds'
    )

    # capa 2: países sin dato → gris, sin leyenda
    fig_grey = px.choropleth(
        g_no,
        geojson=geojson_world,
        locations='code',
        color_discrete_sequence=['#d0d0d0'],
        hover_name='country',
        projection='natural earth'
    )

    for trace in fig_grey.data:
        trace.showlegend = False
        fig.add_trace(trace)

    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(
        title_text=f'CO₂ emissions by country in {year}',
        title_x=0.5,
        width=900,
        height=600
    )

    return fig


# In[ ]:


fig_1751 = make_co2_map(df, 1751)
fig_1751.show()

fig_1851 = make_co2_map(df, 1851)
fig_1851.show()

fig_1951 = make_co2_map(df, 1951)
fig_1951.show()

fig_2024 = make_co2_map(df, 2024)
fig_2024.show()

