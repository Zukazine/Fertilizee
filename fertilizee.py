import streamlit as st
import pandas as pd
import pydeck as pdk
import folium
import time

# Data contoh
data = {
    'Province': ['Aceh', 'Sumatera Selatan', 'Kalimantan Timur', 'Jawa Barat', 'Jawa Timur'],
    'Soil_index': [50, 60, 70, 55, 45],
    'Demand': [1000, 1500, 800, 1200, 900]
}

df = pd.DataFrame(data)

# Judul dan Deskripsi
st.title('Fertilizer and Indonesian Land')

description = "This web app visualizes fertilizer data across different supply chains in Indonesia."
st.markdown(f"**{description}**")

# Container untuk layout kolom
left_column, right_column = st.columns(2)

# Select box untuk Supply Chain dan Visualize by
with left_column:
    supply_chain = st.selectbox('Pick Supply Chain', ['All Chain', 'Aceh', 'Sumatera Selatan', 'Kalimantan Timur', 'Jawa Barat', 'Jawa Timur'])

with right_column:
    visualize_by = st.selectbox('Visualize by:', ['Soil index', 'Demand'])

# Container untuk map PyDeck dan Folium
map_column_1, map_column_2 = st.columns(2)

# Fungsi untuk membuat peta PyDeck
def create_pydeck_map(dataframe, color_column):
    view_state = pdk.ViewState(latitude=-2.5, longitude=118, zoom=5)
    layer = pdk.Layer(
        'GeoJsonLayer',
        data={'type': 'FeatureCollection', 'features': []},
        opacity=0.8,
        get_fill_color=f'[{color_column}, 0, 255, 200]',
        pickable=True,
        auto_highlight=True
    )

    deck = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9', initial_view_state=view_state, layers=[layer])
    return deck

# Fungsi untuk membuat peta Choropleth Folium
def create_folium_map(dataframe, color_column):
    m = folium.Map(location=[-2.5, 118], zoom_start=5, tiles='CartoDB positron')

    # Logic untuk menambahkan Choropleth
    # (Gunakan logika sesuai dengan kebutuhan dan data yang ada)
    folium.Choropleth(
        geo_data='indonesia.geojson',  # GeoJSON untuk peta Indonesia
        data=dataframe,
        columns=['Province', color_column],
        key_on='feature.properties.name',
        fill_color='YlGnBu',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=color_column
    ).add_to(m)

    return m

# Logic untuk tampilan interaktif dengan spinner saat peta sedang dimuat
if visualize_by and supply_chain:
    if visualize_by == 'Soil index':
        with map_column_1:
            st.subheader('Map with PyDeck')
            pydeck_placeholder = st.empty()
            with st.spinner('Loading PyDeck map...'):
                time.sleep(3)  # Contoh delay untuk simulasi loading
                pydeck_placeholder.pydeck_chart(create_pydeck_map(df, 'Soil_index'))
    elif visualize_by == 'Demand':
        with map_column_2:
            st.subheader('Choropleth Map with Folium')
            folium_placeholder = st.empty()
            with st.spinner('Loading Folium map...'):
                time.sleep(3)  # Contoh delay untuk simulasi loading
                folium_placeholder.pyplot(create_folium_map(df, 'Demand'))