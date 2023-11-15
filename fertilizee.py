import streamlit as st
import pandas as pd
import pydeck as pdk
import geopandas as gpd
import folium
from folium import Choropleth
import time
from streamlit_folium import folium_static
from math import radians, sin, cos, sqrt, atan2

st. set_page_config(layout="wide") 
red_icon = "🔴"
orange_icon = "🟠"
yellow_icon = "🟡"

st.title('Welcome to MANTAP Dashboard')

highlight = 'potensi distribusi pupuk, tingkat kesehatan tanah, dan kebutuhan pupuk'
st.markdown(f"Melalui peta interaktif yang disediakan, Anda dapat menjelajahi hubungan antara suplai pupuk dan kondisi lahan di beberapa wilayah kunci di Indonesia. Daerah yang memiliki produksi pupuk yang tinggi akan menjadi supplier bagi daerah-daerah yang memiliki demand. Visualisasi fokus pada **{highlight}** pada suatu wilayah. *Disclaimer : Dashboard juga masih dalam tahap awal, peta akan membutuhkan waktu untuk melakukan loading*")

left_column, right_column = st.columns(2)

with left_column:
    supply_chain = st.selectbox('Pick Supplier', ['All Chain', 'Aceh', 'Sumatera Selatan', 'Kalimantan Timur', 'Jawa Barat', 'Jawa Timur'])

with right_column:
    visualize_by = st.selectbox('Visualize by:', ['Soil index', 'Demand'])

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

def stroke_factory(val):
    # print(val)
    if val <= 100:
        return 75
    elif val <= 500:
        return 60
    elif val <= 1000:
        return 50
    elif val <= 2500:
        return 40
    elif val <= 5000:
        return 30
    elif val <= 10000:
        return 20
    else:
        return 10

def read_data_pdk():
    indo = gpd.read_file('FIX_INA_Pupuk.shp')
    supplier = list({'Aceh', 'Sumatera Selatan', 'Kalimantan Timur', 'Jawa Barat', 'Jawa Timur'})
    high = list({'Nusa Tenggara Timur', 'Jambi', 'Nusa Tenggara Barat', 'Bali', 'Sulawesi Selatan', 'Sulawesi Tengah', 'Jawa Tengah', 'Yogyakarta'})
    mid = list({'Gorontalo', 'Sulawesi Tenggara', 'Provinsi Riau', 'Sumatera Barat', 'Sulawesi Utara', 'Sumatera Utara', 'Kalimantan Barat', 'Banten', 'Maluku Utara', 'Maluku', 'Sulawesi Barat', 'Lampung', 'Bengkulu'})
    low = list({'Kepulauan Riau', 'Papua Barat', 'Kalimantan Utara', 'Bangka Belitung', 'DKI Jakarta', 'Kalimantan Selatan', 'Papua', 'Kalimantan Tengah'})

    indo_provinces = pd.read_csv('daftar_nama_daerah.csv')
    indo_provinces = indo_provinces.iloc[:33]

    kaltara_lng = float(indo.loc[indo.Provinsi == 'Kalimantan Utara'].geometry.centroid.x) 
    kaltara_lat = float(indo.loc[indo.Provinsi == 'Kalimantan Utara'].geometry.centroid.y)

    maluku_lng = float(indo_provinces.loc[indo_provinces.name == 'Provinsi Maluku'].longitude)
    maluku_lat = float(indo_provinces.loc[indo_provinces.name == 'Provinsi Maluku'].latitude)
    maltara_lng = float(indo_provinces.loc[indo_provinces.name == 'Provinsi Maluku Utara'].longitude)
    maltara_lat = float(indo_provinces.loc[indo_provinces.name == 'Provinsi Maluku Utara'].latitude)

    papua_lng = float(indo_provinces.loc[indo_provinces.name == 'Provinsi Papua'].longitude)
    papua_lat = float(indo_provinces.loc[indo_provinces.name == 'Provinsi Papua'].latitude)

    high_coords_lng, high_coords_lat = [], []
    for province in high:
        for idx in range(len(indo_provinces)):
            if province in indo_provinces.iloc[idx]['name']:
                high_coords_lng.append(indo_provinces.iloc[idx].longitude)
                high_coords_lat.append(indo_provinces.iloc[idx].latitude)

    mid_coords_lng, mid_coords_lat = [], []
    for province in mid:
        if province != 'Maluku' and province != 'Maluku Utara':
            for idx in range(len(indo_provinces)):
                if province in indo_provinces.iloc[idx]['name']:
                    mid_coords_lng.append(indo_provinces.iloc[idx].longitude)
                    mid_coords_lat.append(indo_provinces.iloc[idx].latitude)
        else:
            if province == 'Maluku':
                mid_coords_lng.append(maluku_lng)
                mid_coords_lat.append(maluku_lat)
            elif province == 'Maluku Utara':
                mid_coords_lng.append(maltara_lng)
                mid_coords_lat.append(maltara_lat)

    low_coords_lng, low_coords_lat = [], []
    for province in low:
        if province != 'Kalimantan Utara' and province != 'Papua':
            for idx in range(len(indo_provinces)):
                if province in indo_provinces.iloc[idx]['name']:
                    low_coords_lng.append(indo_provinces.iloc[idx].longitude)
                    low_coords_lat.append(indo_provinces.iloc[idx].latitude)
        else:
            if province == 'Kalimantan Utara':
                low_coords_lng.append(kaltara_lng)
                low_coords_lat.append(kaltara_lat)
            elif province == 'Papua':
                low_coords_lng.append(papua_lng)
                low_coords_lat.append(papua_lat)

    supp_lng, supp_lat = [], []
    for province in supplier:
        for idx in range(len(indo_provinces)):
            if province in indo_provinces.iloc[idx]['name']:
                supp_lng.append(indo_provinces.iloc[idx].longitude)
                supp_lat.append(indo_provinces.iloc[idx].latitude)

    list_of_gdf1, list_of_gdf2, list_of_gdf3= [], [], []
    df = None

    for i in range(len(supplier)):
        from_x = supp_lng[i]
        from_y = supp_lat[i]
                        
        to_coords_1, distances_1, stroke_1 = [], [], []
        for j in range(len(high)):
            lng = high_coords_lng[j]
            lat = high_coords_lat[j]
            to_coords_1.append([lng,lat])
            distances_1.append(int(haversine(from_y, from_x, lat, lng)))
            stroke_1.append(stroke_factory(distances_1[j]))

        list_of_gdf1.append(pd.DataFrame({
            'from' : supplier[i],
            'from_x' : from_x,
            'from_y' : from_y,
            'to' : high,
            'to_coords' : to_coords_1,
            'distance(km)' : distances_1,
            'stroke_val' : stroke_1,
        }))

        to_coords_2, distances_2, stroke_2 = [], [], []
        for j in range(len(mid)):
            lng = mid_coords_lng[j]
            lat = mid_coords_lat[j]
            to_coords_2.append([lng,lat])
            distances_2.append(int(haversine(from_y, from_x, lat, lng)))
            stroke_2.append(stroke_factory(distances_2[j]))


        list_of_gdf2.append(pd.DataFrame({
            'from' : supplier[i],
            'from_x' : from_x,
            'from_y' : from_y,
            'to' : mid,
            'to_coords' : to_coords_2,
            'distance(km)' : distances_2,
            'stroke_val' : stroke_2,
        }))

        to_coords_3, distances_3, stroke_3 = [], [], []
        for j in range(len(low)):
            lng = low_coords_lng[j]
            lat = low_coords_lat[j]
            to_coords_3.append([lng,lat])
            distances_3.append(int(haversine(from_y, from_x, lat, lng)))
            stroke_3.append(stroke_factory(distances_3[j]))

        list_of_gdf3.append(pd.DataFrame({
            'from' : supplier[i],
            'from_x' : from_x,
            'from_y' : from_y,
            'to' : low,
            'to_coords' : to_coords_3,
            'distance(km)' : distances_3,
            'stroke_val' : stroke_3,
        }))

    return (list_of_gdf1, list_of_gdf2, list_of_gdf3)

def load_all_chain(list_of_gdf):
    list_of_gdf1 = list_of_gdf[0]
    list_of_gdf2 = list_of_gdf[1]
    list_of_gdf3 = list_of_gdf[2]

    layers_1 = []
    for df in list_of_gdf1:
        layers_1.append(pdk.Layer(
            "ArcLayer",
            df,
            pickable=True,
            get_stroke_width='stroke_val',
            get_source_position= "[from_x, from_y]",
            get_target_position = "to_coords",
            get_tilt=15,
            get_source_color=[255,0,0],
            get_target_color=[255,0,0],
            auto_highlight=True
        ))

    layers_2 = []
    for df in list_of_gdf2:
        layers_2.append(pdk.Layer(
            "ArcLayer",
            df,
            pickable=True,
            get_stroke_width='stroke_val',
            get_source_position= "[from_x, from_y]",
            get_target_position = "to_coords",
            get_tilt=15,
            get_source_color=[255,122,0],
            get_target_color=[255,122,0],
            auto_highlight=True
        ))

    layers_3 = []
    for df in list_of_gdf3:
        layers_3.append(pdk.Layer(
            "ArcLayer",
            df,
            pickable=True,
            get_stroke_width='stroke_val',
            get_source_position= "[from_x, from_y]",
            get_target_position = "to_coords",
            get_tilt=15,
            get_source_color=[255,214,0],
            get_target_color=[255,214,0],
            auto_highlight=True
        ))

    layers = layers_1
    for el in layers_2:
        layers.append(el)
    for el in layers_3:
        layers.append(el)

    view_state = pdk.ViewState(latitude=0.7893, longitude=113.9213, zoom=4, bearing=20, pitch=100)

    r = pdk.Deck(
        layers= layers,
        initial_view_state=view_state,
        tooltip={"text": "{from} distribusi ke {to}"},
    )
    r.picking_radius = 10

    return r

def load_aceh(list_of_gdf):
    list_of_gdf1, list_of_gdf2, list_of_gdf3= list_of_gdf
    
    layer_1 = (pdk.Layer(
        "ArcLayer",
        list_of_gdf1[4],
        pickable=True,
        get_stroke_width='stroke_val',
        get_source_position= "[from_x, from_y]",
        get_target_position = "to_coords",
        get_tilt=15,
        get_source_color=[255,0,0],
        get_target_color=[255,0,0],
        auto_highlight=True
    ))

    layer_2 = (pdk.Layer(
        "ArcLayer",
        list_of_gdf2[4],
        pickable=True,
        get_stroke_width='stroke_val',
        get_source_position= "[from_x, from_y]",
        get_target_position = "to_coords",
        get_tilt=15,
        get_source_color=[255,122,0],
        get_target_color=[255,122,0],
        auto_highlight=True
    ))

    layer_3 = (pdk.Layer(
        "ArcLayer",
        list_of_gdf3[4],
        pickable=True,
        get_stroke_width='stroke_val',
        get_source_position= "[from_x, from_y]",
        get_target_position = "to_coords",
        get_tilt=15,
        get_source_color=[255,214,0],
        get_target_color=[255,214,0],
        auto_highlight=True
    ))

    view_state = pdk.ViewState(latitude=0.7893, longitude=113.9213, zoom=4, bearing=20, pitch=100)

    r = pdk.Deck(
        layers= [layer_1, layer_2, layer_3],
        initial_view_state=view_state,
        tooltip={"text": "{from} supply ke {to}"},
    )
    # print(r)
    r.picking_radius = 10

    return r

def load_sumsel(list_of_gdf):
    list_of_gdf1, list_of_gdf2, list_of_gdf3= list_of_gdf
    
    layer_1 = (pdk.Layer(
        "ArcLayer",
        list_of_gdf1[0],
        pickable=True,
        get_stroke_width='stroke_val',
        get_source_position= "[from_x, from_y]",
        get_target_position = "to_coords",
        get_tilt=15,
        get_source_color=[255,0,0],
        get_target_color=[255,0,0],
        auto_highlight=True
    ))

    layer_2 = (pdk.Layer(
        "ArcLayer",
        list_of_gdf2[0],
        pickable=True,
        get_stroke_width='stroke_val',
        get_source_position= "[from_x, from_y]",
        get_target_position = "to_coords",
        get_tilt=15,
        get_source_color=[255,122,0],
        get_target_color=[255,122,0],
        auto_highlight=True
    ))

    layer_3 = (pdk.Layer(
        "ArcLayer",
        list_of_gdf3[0],
        pickable=True,
        get_stroke_width='stroke_val',
        get_source_position= "[from_x, from_y]",
        get_target_position = "to_coords",
        get_tilt=15,
        get_source_color=[255,214,0],
        get_target_color=[255,214,0],
        auto_highlight=True
    ))

    view_state = pdk.ViewState(latitude=0.7893, longitude=113.9213, zoom=4, bearing=20, pitch=100)

    r = pdk.Deck(
        layers= [layer_1, layer_2, layer_3],
        initial_view_state=view_state,
        tooltip={"text": "{from} supply ke {to}"},
    )
    # print(r)
    r.picking_radius = 10

    return r

def load_jatim(list_of_gdf):
    list_of_gdf1, list_of_gdf2, list_of_gdf3= list_of_gdf
    
    layer_1 = (pdk.Layer(
        "ArcLayer",
        list_of_gdf1[1],
        pickable=True,
        get_stroke_width='stroke_val',
        get_source_position= "[from_x, from_y]",
        get_target_position = "to_coords",
        get_tilt=15,
        get_source_color=[255,0,0],
        get_target_color=[255,0,0],
        auto_highlight=True
    ))

    layer_2 = (pdk.Layer(
        "ArcLayer",
        list_of_gdf2[1],
        pickable=True,
        get_stroke_width='stroke_val',
        get_source_position= "[from_x, from_y]",
        get_target_position = "to_coords",
        get_tilt=15,
        get_source_color=[255,122,0],
        get_target_color=[255,122,0],
        auto_highlight=True
    ))

    layer_3 = (pdk.Layer(
        "ArcLayer",
        list_of_gdf3[1],
        pickable=True,
        get_stroke_width='stroke_val',
        get_source_position= "[from_x, from_y]",
        get_target_position = "to_coords",
        get_tilt=15,
        get_source_color=[255,214,0],
        get_target_color=[255,214,0],
        auto_highlight=True
    ))

    view_state = pdk.ViewState(latitude=0.7893, longitude=113.9213, zoom=4, bearing=20, pitch=100)

    r = pdk.Deck(
        layers= [layer_1, layer_2, layer_3],
        initial_view_state=view_state,
        tooltip={"text": "{from} supply ke {to}"},
    )
    # print(r)
    r.picking_radius = 10

    return r

def load_kaltim(list_of_gdf):
    list_of_gdf1, list_of_gdf2, list_of_gdf3= list_of_gdf
    
    layer_1 = (pdk.Layer(
        "ArcLayer",
        list_of_gdf1[2],
        pickable=True,
        get_stroke_width='stroke_val',
        get_source_position= "[from_x, from_y]",
        get_target_position = "to_coords",
        get_tilt=15,
        get_source_color=[255,0,0],
        get_target_color=[255,0,0],
        auto_highlight=True
    ))

    layer_2 = (pdk.Layer(
        "ArcLayer",
        list_of_gdf2[2],
        pickable=True,
        get_stroke_width='stroke_val',
        get_source_position= "[from_x, from_y]",
        get_target_position = "to_coords",
        get_tilt=15,
        get_source_color=[255,122,0],
        get_target_color=[255,122,0],
        auto_highlight=True
    ))

    layer_3 = (pdk.Layer(
        "ArcLayer",
        list_of_gdf3[2],
        pickable=True,
        get_stroke_width='stroke_val',
        get_source_position= "[from_x, from_y]",
        get_target_position = "to_coords",
        get_tilt=15,
        get_source_color=[255,214,0],
        get_target_color=[255,214,0],
        auto_highlight=True
    ))

    view_state = pdk.ViewState(latitude=0.7893, longitude=113.9213, zoom=4, bearing=20, pitch=100)

    r = pdk.Deck(
        layers= [layer_1, layer_2, layer_3],
        initial_view_state=view_state,
        tooltip={"text": "{from} supply ke {to}"},
    )
    # print(r)
    r.picking_radius = 10

    return r

def load_jabar(list_of_gdf):
    list_of_gdf1, list_of_gdf2, list_of_gdf3= list_of_gdf
    
    layer_1 = (pdk.Layer(
        "ArcLayer",
        list_of_gdf1[3],
        pickable=True,
        get_stroke_width='stroke_val',
        get_source_position= "[from_x, from_y]",
        get_target_position = "to_coords",
        get_tilt=15,
        get_source_color=[255,0,0],
        get_target_color=[255,0,0],
        auto_highlight=True
    ))

    layer_2 = (pdk.Layer(
        "ArcLayer",
        list_of_gdf2[3],
        pickable=True,
        get_stroke_width='stroke_val',
        get_source_position= "[from_x, from_y]",
        get_target_position = "to_coords",
        get_tilt=15,
        get_source_color=[255,122,0],
        get_target_color=[255,122,0],
        auto_highlight=True
    ))

    layer_3 = (pdk.Layer(
        "ArcLayer",
        list_of_gdf3[3],
        pickable=True,
        get_stroke_width='stroke_val',
        get_source_position= "[from_x, from_y]",
        get_target_position = "to_coords",
        get_tilt=15,
        get_source_color=[255,214,0],
        get_target_color=[255,214,0],
        auto_highlight=True
    ))

    view_state = pdk.ViewState(latitude=0.7893, longitude=113.9213, zoom=4, bearing=20, pitch=100)

    r = pdk.Deck(
        layers= [layer_1, layer_2, layer_3],
        initial_view_state=view_state,
        tooltip={"text": "{from} supply ke {to}"},
    )
    # print(r)
    r.picking_radius = 10

    return r

def demand_map():
    indo = gpd.read_file('FIX_INA_Pupuk.shp')
    pupuk = list(indo.Data_untuk)
    pupuk_conv = [float(x.replace('.', '').replace(',','.')) for x in pupuk]
    indo.Data_untuk = pupuk_conv

    m = folium.Map(location=[0.7893,113.9213], tiles = 'cartodbdark_matter', zoom_start=4)

    wilayah = indo[["Provinsi", "geometry"]]
    demand = indo.Data_untuk

    Choropleth(geo_data = wilayah.__geo_interface__,
           data = demand,
           key_on='feature.id',
           fill_color='OrRd',
           legend_name='Demand Pupuk',
           line_color = 'Red'
           ).add_to(m)
    
    folium.plugins.Fullscreen(
    position="topright",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True,
    ).add_to(m)

    return m
    
def soil_map():
    indo = gpd.read_file('FIX_INA_Pupuk.shp')
    pupuk = list(indo.Data_untuk)
    pupuk_conv = [float(x.replace('.', '').replace(',','.')) for x in pupuk]
    indo.Data_untuk = pupuk_conv

    m = folium.Map(location=[0.7893,113.9213], tiles = 'cartodbdark_matter', zoom_start=4)

    wilayah = indo[["Provinsi", "geometry"]]
    soil_index = indo.MEAN

    Choropleth(geo_data = wilayah.__geo_interface__,
           data = soil_index,
           key_on='feature.id',
           fill_color='Greens',
           legend_name='Soil index',
           line_color = 'Blue'
           ).add_to(m)
    
    folium.plugins.Fullscreen(
    position="topright",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True,
    ).add_to(m)

    return m

st.subheader('Map Fertilizer Potential Distribution')
# di col 3
st.markdown(f'{red_icon} High Potential' + '  ' + f'{orange_icon}Medium Potential' + '   ' + f'{yellow_icon} Low Potential')

if supply_chain:
    # st.text(read_data_pdk('All Chain'))
    if supply_chain == 'All Chain':
        with st.spinner('Under calculations...'):
            time.sleep(3)
            st.pydeck_chart(load_all_chain(read_data_pdk()))
    elif supply_chain == 'Aceh':
        with st.spinner('Under calculations...'):
            time.sleep(3)
            st.pydeck_chart(load_aceh(read_data_pdk()))
    elif supply_chain == 'Sumatera Selatan':
        with st.spinner('Under calculations...'):
            time.sleep(3)
            st.pydeck_chart(load_sumsel(read_data_pdk()))
    elif supply_chain == 'Kalimantan Timur':
        with st.spinner('Under calculations...'):
            time.sleep(3)
            st.pydeck_chart(load_kaltim(read_data_pdk()))
    elif supply_chain == 'Jawa Barat':
        with st.spinner('Under calculations...'):
            time.sleep(3)
            st.pydeck_chart(load_jabar(read_data_pdk()))
    elif supply_chain == 'Jawa Timur':
        with st.spinner('Loading PyDeck map...'):
            time.sleep(3)
            st.pydeck_chart(load_jatim(read_data_pdk()))
    else:
        st.text('Roti')

st.subheader('Soil Index & Fertilizer Demand Area')
st.markdown(f'Visualized By : {visualize_by}')
if visualize_by:
    if visualize_by == 'Demand':
        with st.spinner('Under calculations...'):
            time.sleep(3)
            folium_static(demand_map(), width = 1200)
    else:
        with st.spinner('Under calculations...'):
            time.sleep(3)
            folium_static(soil_map(), width = 1200)




