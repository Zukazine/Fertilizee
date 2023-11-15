import streamlit as st
import pandas as pd
import pydeck as pdk
import folium
import time

st.title('Fertilizer and Indonesian Land')

st.markdown("Melalui peta interaktif yang disediakan, Anda dapat menjelajahi hubungan antara suplai pupuk dan kondisi lahan di beberapa wilayah kunci di Indonesia. Dengan pemilihan berbagai rantai pasokan dan fokus pada indikator tanah atau demand.")

left_column, right_column = st.columns(2)

with left_column:
    supply_chain = st.selectbox('Pick Supply Chain', ['All Chain', 'Aceh', 'Sumatera Selatan', 'Kalimantan Timur', 'Jawa Barat', 'Jawa Timur'])

with right_column:
    visualize_by = st.selectbox('Visualize by:', ['Soil index', 'Demand'])

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

st.subheader('Map with PyDeck')
pydeck_placeholder = st.pydeck_chart(pdk.Deck())
# path_to_html = 'prior_arc.html'
# st.components.v1.html(open(path_to_html, 'r').read(), width=704, height=500)



