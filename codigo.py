from copyreg import pickle
from tkinter.messagebox import NO
from tokenize import group
from click import option
import pydeck as pdk
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_icon=":thumbs_up:",
    layout="wide",
)

@st.cache
def carga_data():
    return pd.read_excel("encuestaMP.xlsx", header=0)

#se lee la info de manera óptima
mp =  carga_data()

st.header("Desafío tres")
st.info("#### Top 3 de sectores en la comuna")

################################################################
col_bar, col_pie, col_table = st.columns(3, gap="large")
#Agrupar los datos en base a la columna donde están el uso actual
#Se gnera la serie de la agrupación usando "Size()"
sector = mp.groupby(["SEC_PR"]).size()
#Se ordena de mayor a menor, gracias al uso del parámetro "ascending="
sector.sort_values(axis="index", ascending=False, inplace=True)
#Ya se pueden obtener los 3 primeros registros
top3=sector[0:3]

def formato_porciento(dato: float):
    return f"{round(dato, ndigits=2)}%"

with col_bar:
    bar= plt.figure()
    top3.plot.bar(
        title="Predios en la comuna de María Pinto",
        label="Total de Puntos",
        xlabel="Sector Comuna",
        ylabel="Cantidad de Predios",
        color="lightblue",
        grid=True,
    ).plot()
    st.pyplot(bar)

with col_pie:
    pie = plt.figure()
    top3.plot.pie(
        y="index",
        title="Predios en la comuna de María Pinto",
        legend=None,
        autopct=formato_porciento
    ).plot()
    st.pyplot(pie)

with col_table:
    line= plt.figure()
    top3.plot.line(
        title="Predios en la comuna de María Pinto",
        label="Total de Puntos",
        xlabel="Sector Comuna",
        ylabel="Cantidad de Predios",
        color="lightblue",
        grid=True
    ).plot()
    st.pyplot(line)

##############################################################
st.info("#### Agrupación por sector del predio en la comuna")

col_sel, col_map = st.columns([1,2])

#Crear grupos por cantidad de puntos
group_10= sector.apply(lambda x: x if x <= 10 else None).dropna(axis=0)
group_30= sector.apply(lambda x: x if x > 10 and x <=30 else None).dropna(axis=0)
group_max= sector.apply(lambda x: x if x > 30 else None).dropna(axis=0)

with col_sel:
    sector_agrupado = st.multiselect(
        label="Filtrar por grupos de Comuna",
        options=["Menos de 10 Puntos", "11 a 30 Puntos", "Más de 30 Puntos"],
        help="Selecciona la agrupación a mostrar",
        default=[]
    )

filtrar = []

if "Menos de 10 Puntos" in sector_agrupado:
    filtrar = filtrar + group_10.index.tolist()

if "11 a 30 Puntos" in sector_agrupado:
    filtrar = filtrar + group_30.index.tolist()

if "Más de 30 Puntos" in sector_agrupado:
    filtrar = filtrar + group_max.index.tolist()

#Obtener parte de la info
geo_puntos_comuna = mp[ ["SEC_PR", "AR_APR", "R_TC", "USO_PR_ACTUAL", "X", "Y"]].rename(columns={
    "SEC_PR": "Sector_predio",
    "USO_PR_ACTUAL": "Uso_actual_predio",
    "Y": "Latitud",
    "X": "Longitud"
})
geo_puntos_comuna.dropna(subset=["Sector_predio"], inplace=True)
geo_data = geo_puntos_comuna

#Aplicar filtro de comuna
if filtrar:
    geo_data = geo_puntos_comuna.query("Sector_predio == @filtrar")

#Obtener el punto promedio entre todas las georreferencias
avg_lat =np.median(geo_data["Latitud"])
avg_lng =np.median(geo_data["Longitud"])

puntos_mapa = pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
        latitude=avg_lat,
        longitude=avg_lng,
        zoom=10,
        min_zoom=10,
        max_zoom=15,
        pitch=20,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=geo_data,
            pickable=True,
            auto_highlight=True,
            get_position= '[Longitud, Latitud]',
            filled=True,
            opacity=1,
            radius_scale=10,
            radius_min_pixels=2,
            #radius_max_pixels=10,
            #line_idth_min_pixels=0.01,
        ),
    ],    
    tooltip={
        "html": "<b>Sector comuna: </b> {Sector_predio} <br/>"
                "<b>Uso actual del predio: </b> {Uso_actual_predio} <br/>"
                "<b>Posee riego tecnificado: </b> {R_TC} <br/>"
                "<b>Tiene acceso a Agua de Riego o APR en este Predio: </b> {AR_APR} <br/>"
                "<b>Georreferencia (Lat, Lng): </b> [{Latitud}, {Longitud}] <br/>"
    }
)



with col_map:
    st.write(puntos_mapa)
