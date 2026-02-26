import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="UFO Tracker", page_icon="🛸", layout="wide")

st.title("🛸 UFO Sightings: ¿Estamos solos?")
st.markdown("Analizando miles de avistamientos oficiales reportados a la NUFORC.")

# 1. Cargar Datos
@st.cache_data # Para que no recargue el CSV cada vez que tocas un botón
def load_data():
    # Asegúrate de que el archivo se llame así y esté en la misma carpeta
    df = pd.read_csv("ufo_sighting_data.csv", low_memory=False)
    
    # Limpieza rápida: Convertir coordenadas a números y fechas a datetime
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df['date_time'] = pd.to_datetime(df['Date_time'], errors='coerce')
    df = df.dropna(subset=['latitude', 'longitude', 'date_time']) # Tiramos lo que está roto
    df['year'] = df['date_time'].dt.year
    return df

df = load_data()

# --- SIDEBAR (Filtros) ---
st.sidebar.header("Filtros Espaciales")
year_range = st.sidebar.slider("Selecciona el rango de años", 
                               int(df['year'].min()), int(df['year'].max()), (1990, 2014))

# Filtrar por forma del OVNI
shapes = st.sidebar.multiselect("Forma del objeto", options=df['UFO_shape'].unique(), default=['disk', 'light', 'triangle'])

# Aplicar filtros
df_filtered = df[(df['year'] >= year_range[0]) & 
                 (df['year'] <= year_range[1]) & 
                 (df['UFO_shape'].isin(shapes))]

# --- DASHBOARD ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Mapa de Avistamientos")
    # Mapa interactivo con Plotly
    fig_map = px.scatter_mapbox(df_filtered, lat="latitude", lon="longitude", 
                                hover_name="city", hover_data=["date_time", "description"],
                                color_discrete_sequence=["lime"], zoom=1, height=500)
    fig_map.update_layout(mapbox_style="carto-darkmatter") # Estilo oscuro tipo hacker
    st.plotly_chart(fig_map, use_container_width=True)

with col2:
    st.subheader("Top Formas")
    shape_counts = df_filtered['UFO_shape'].value_counts().head(10)
    st.bar_chart(shape_counts)

# Gráfico de línea temporal
st.subheader("Evolución de avistamientos en el tiempo")
yearly_counts = df_filtered.groupby('year').size().reset_index(name='counts')
fig_line = px.line(yearly_counts, x='year', y='counts', line_shape="spline", render_mode="svg")
st.plotly_chart(fig_line, use_container_width=True)

st.write(f"Mostrando {len(df_filtered)} avistamientos que coinciden con tu búsqueda.")