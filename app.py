import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Dashboard de Matrículas - UCMC",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PALETA DE COLORES SOLICITADA
COLOR_PRINCIPAL = "#CB7087"
COLOR_SECUNDARIO = "#EDBECA"
COLOR_TERCIARIO = "#FFD6DC"
COLOR_FONDO = "#FFF1E4"
PALETA = [COLOR_PRINCIPAL, COLOR_SECUNDARIO, COLOR_TERCIARIO, COLOR_FONDO]

# ESTILOS CSS PERSONALIZADOS
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {COLOR_FONDO};
        }}
        [data-testid="stSidebar"] {{
            background-color: {COLOR_TERCIARIO};
            border-right: 2px solid {COLOR_PRINCIPAL};
        }}
        h1, h2, h3 {{
            color: {COLOR_PRINCIPAL} !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: {COLOR_SECUNDARIO};
            border-radius: 8px 8px 0px 0px;
            padding: 10px 16px;
            color: #2B2B2B;
            font-weight: 600;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {COLOR_PRINCIPAL} !important;
            color: #FFFFFF !important;
        }}
        .resena-box {{
            background-color: #FFFFFF;
            border-left: 5px solid {COLOR_PRINCIPAL};
            padding: 16px;
            border-radius: 6px;
            margin-top: 15px;
            box-shadow: 0 2px 6px rgba(203, 112, 135, 0.15);
            color: #333333;
            font-size: 15px;
        }}
    </style>
""", unsafe_allow_html=True)

# 2. CARGA Y LIMPIEZA DE DATOS
@st.cache_data
def cargar_datos():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(
        base_dir,
        "database",
        "Valor_de_Matricula_-_Programas_Universidad_Colegio_Mayor_de_Cundinamarca_20261126.csv",
    )
    df = pd.read_csv(ruta)
    df.columns = df.columns.str.strip()
    
    # Mapeo flexible para asegurar coincidencia exacta con los nombres solicitados
    col_map = {}
    for col in df.columns:
        c_upper = col.upper()
        if "PROGRAMA" in c_upper:
            col_map[col] = "PROGRAMA"
        elif "MAXIMO" in c_upper or "MÁXIMO" in c_upper:
            col_map[col] = "NIVEL DE INGRESO MAXIMO"
        elif "NIVEL DE INGRESO" in c_upper:
            col_map[col] = "NIVEL DE INGRESOS"
        elif "MATRICULA" in c_upper or "MATRÍCULA" in c_upper:
            col_map[col] = "VALOR DE MATRICULA"
        elif "SMLMV" in c_upper:
            col_map[col] = "Valor en SMLMV"
            
    df = df.rename(columns=col_map)
    
    # Limpieza de columnas numéricas, sin depender del tipo interno de pandas
    if "VALOR DE MATRICULA" in df.columns:
        df["VALOR DE MATRICULA"] = (
            df["VALOR DE MATRICULA"]
            .astype(str)
            .str.replace(r"[$\s]", "", regex=True)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        df["VALOR DE MATRICULA"] = pd.to_numeric(
            df["VALOR DE MATRICULA"], errors="coerce"
        )

    if "Valor en SMLMV" in df.columns:
        df["Valor en SMLMV"] = (
            df["Valor en SMLMV"]
            .astype(str)
            .str.extract(r"([0-9]+(?:[,.][0-9]+)?)", expand=False)
            .str.replace(",", ".", regex=False)
        )
        df["Valor en SMLMV"] = pd.to_numeric(
            df["Valor en SMLMV"], errors="coerce"
        )
            
    return df

try:
    df_original = cargar_datos()
except FileNotFoundError:
    st.error('❌ No se encontró el archivo en la ruta: `"database\\Valor_de_Matricula_-_Programas_Universidad_Colegio_Mayor_de_Cundinamarca_20261126.csv"`. Verifica la carpeta.')
    st.stop()

# 3. PANEL IZQUIERDO: FILTROS ENCADENADOS EN EL ORDEN SOLICITADO
st.sidebar.markdown("## 🔍 Filtros Encadenados")
st.sidebar.caption("Cada filtro actualiza dinámicamente las opciones disponibles de los siguientes.")

categorias_ordenadas = [
    "PROGRAMA",
    "NIVEL DE INGRESOS",
    "NIVEL DE INGRESO MAXIMO",
    "VALOR DE MATRICULA",
    "Valor en SMLMV"
]

df_filtrado = df_original.copy()

for cat in categorias_ordenadas:
    if cat in df_filtrado.columns:
        opciones_disponibles = sorted(df_filtrado[cat].dropna().unique().tolist())
        seleccion = st.sidebar.multiselect(
            label=f"📌 {cat}",
            options=opciones_disponibles,
            default=[],
            placeholder="Seleccionar..."
        )
        # Encadenamiento: se filtra inmediatamente para restringir el siguiente control
        if seleccion:
            df_filtrado = df_filtrado[df_filtrado[cat].isin(seleccion)]

st.sidebar.markdown("---")
st.sidebar.metric(label="Registros Filtrados", value=f"{len(df_filtrado)} / {len(df_original)}")

# 4. CUERPO PRINCIPAL Y ÚNICA TABLA OCULTA POR DEFECTO
st.title("🎓 Dashboard de Valores de Matrícula - UCMC")
st.markdown("Análisis interactivo por programa académico, rangos de ingreso y costos de matrícula.")

with st.expander("📋 Ver Tabla Única de Datos (Clic para desplegar)", expanded=False):
    st.dataframe(df_filtrado, width="stretch", hide_index=True)

st.markdown("---")

# Función para uniformar el diseño visual de los gráficos
def estilizar_grafico(fig):
    fig.update_layout(
        plot_bgcolor="rgba(255, 255, 255, 0.9)",
        paper_bgcolor="rgba(255, 255, 255, 0.9)",
        font=dict(color="#2B2B2B", family="Segoe UI"),
        title_font=dict(size=18, color=COLOR_PRINCIPAL),
        margin=dict(l=30, r=30, t=55, b=30),
        hoverlabel=dict(bgcolor=COLOR_FONDO, font_size=13, font_color="#2B2B2B")
    )
    return fig

# 5. PESTAÑAS POR CADA CATEGORÍA CON SU GRÁFICO Y RESEÑA
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1️⃣ PROGRAMA",
    "2️⃣ NIVEL DE INGRESOS",
    "3️⃣ NIVEL DE INGRESO MAXIMO",
    "4️⃣ VALOR DE MATRICULA",
    "5️⃣ Valor en SMLMV"
])

# --- PESTAÑA 1: PROGRAMA ---
with tab1:
    st.subheader("Análisis por Programa Académico")
    if not df_filtrado.empty and "PROGRAMA" in df_filtrado.columns:
        df_prog = (
            df_filtrado.groupby("PROGRAMA", as_index=False)["VALOR DE MATRICULA"]
            .mean()
            .sort_values(by="VALOR DE MATRICULA", ascending=True)
        )
        fig1 = px.bar(
            df_prog,
            x="VALOR DE MATRICULA",
            y="PROGRAMA",
            orientation="h",
            text_auto="$.2s",
            color="VALOR DE MATRICULA",
            color_continuous_scale=[COLOR_TERCIARIO, COLOR_SECUNDARIO, COLOR_PRINCIPAL],
            title="Promedio del Valor de Matrícula por Programa"
        )
        fig1.update_layout(height=max(450, len(df_prog) * 28), coloraxis_showscale=False)
        st.plotly_chart(estilizar_grafico(fig1), width="stretch")
        
        st.markdown("""
        <div class="resena-box">
            <strong>📌 Reseña - PROGRAMA:</strong><br>
            Esta categoría agrupa los diferentes programas académicos ofertados por la institución. 
            El gráfico permite comparar el valor promedio de matrícula entre carreras y evaluar cómo varía la estructura de costos según la selección de filtros.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No hay datos disponibles para mostrar con los filtros seleccionados.")

# --- PESTAÑA 2: NIVEL DE INGRESOS ---
with tab2:
    st.subheader("Distribución por Nivel de Ingresos")
    if not df_filtrado.empty and "NIVEL DE INGRESOS" in df_filtrado.columns:
        df_ni = df_filtrado["NIVEL DE INGRESOS"].value_counts().reset_index()
        df_ni.columns = ["NIVEL DE INGRESOS", "Registros"]
        
        fig2 = px.pie(
            df_ni,
            names="NIVEL DE INGRESOS",
            values="Registros",
            hole=0.45,
            color_discrete_sequence=[COLOR_PRINCIPAL, COLOR_SECUNDARIO, COLOR_TERCIARIO, "#B55A71", "#F4D1DA"],
            title="Participación Porcentual por Nivel de Ingresos"
        )
        fig2.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color="#FFFFFF", width=2))
        )
        st.plotly_chart(estilizar_grafico(fig2), width="stretch")
        
        st.markdown("""
        <div class="resena-box">
            <strong>📌 Reseña - NIVEL DE INGRESOS:</strong><br>
            Clasifica los estratos o rangos socioeconómicos base declarados por los aspirantes o estudiantes. 
            Permite visualizar la distribución de la población según su capacidad económica inicial para la liquidación de matrícula.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No hay datos disponibles para mostrar con los filtros seleccionados.")

# --- PESTAÑA 3: NIVEL DE INGRESO MAXIMO ---
with tab3:
    st.subheader("Frecuencia por Nivel de Ingreso Máximo")
    if not df_filtrado.empty and "NIVEL DE INGRESO MAXIMO" in df_filtrado.columns:
        df_max = df_filtrado["NIVEL DE INGRESO MAXIMO"].value_counts().reset_index()
        df_max.columns = ["NIVEL DE INGRESO MAXIMO", "Cantidad"]
        
        fig3 = px.bar(
            df_max,
            x="NIVEL DE INGRESO MAXIMO",
            y="Cantidad",
            text="Cantidad",
            color="NIVEL DE INGRESO MAXIMO",
            color_discrete_sequence=[COLOR_PRINCIPAL, COLOR_SECUNDARIO, COLOR_TERCIARIO],
            title="Distribución de Registros por Tope Máximo de Ingresos"
        )
        fig3.update_traces(textposition="outside", marker_line_color=COLOR_PRINCIPAL, marker_line_width=1.5)
        fig3.update_layout(showlegend=False)
        st.plotly_chart(estilizar_grafico(fig3), width="stretch")
        
        st.markdown("""
        <div class="resena-box">
            <strong>📌 Reseña - NIVEL DE INGRESO MAXIMO:</strong><br>
            Indica el umbral superior de ingresos establecido dentro de cada categoría tarifaria. 
            Facilita identificar los límites máximos de capacidad económica bajo los cuales se asignan las tarifas diferenciales en la universidad.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No hay datos disponibles para mostrar con los filtros seleccionados.")

# --- PESTAÑA 4: VALOR DE MATRICULA ---
with tab4:
    st.subheader("Distribución del Valor de Matrícula ($ COP)")
    if not df_filtrado.empty and "VALOR DE MATRICULA" in df_filtrado.columns:
        fig4 = px.histogram(
            df_filtrado,
            x="VALOR DE MATRICULA",
            nbins=20,
            marginal="box",
            color_discrete_sequence=[COLOR_PRINCIPAL],
            title="Distribución y Dispersión del Valor de Matrícula en Pesos"
        )
        fig4.update_traces(marker_line_color="#FFFFFF", marker_line_width=1.2)
        st.plotly_chart(estilizar_grafico(fig4), width="stretch")
        
        st.markdown("""
        <div class="resena-box">
            <strong>📌 Reseña - VALOR DE MATRICULA:</strong><br>
            Representa el monto monetario exacto liquidado por concepto de derechos académicos. 
            La combinación del histograma y el diagrama de caja superior permite observar tanto la frecuencia de cada rango de precios como su mediana y valores extremos.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No hay datos disponibles para mostrar con los filtros seleccionados.")

# --- PESTAÑA 5: VALOR EN SMLMV ---
with tab5:
    st.subheader("Análisis del Valor en SMLMV")
    if not df_filtrado.empty and "Valor en SMLMV" in df_filtrado.columns:
        eje_x = "NIVEL DE INGRESOS" if "NIVEL DE INGRESOS" in df_filtrado.columns else None
        fig5 = px.box(
            df_filtrado,
            x=eje_x,
            y="Valor en SMLMV",
            color=eje_x,
            points="all",
            color_discrete_sequence=[COLOR_PRINCIPAL, COLOR_SECUNDARIO, COLOR_TERCIARIO],
            title="Comportamiento del Valor de Matrícula expresado en SMLMV"
        )
        fig5.update_layout(showlegend=False)
        st.plotly_chart(estilizar_grafico(fig5), width="stretch")
        
        st.markdown("""
        <div class="resena-box">
            <strong>📌 Reseña - Valor en SMLMV:</strong><br>
            Expresa el costo de la matrícula en unidades de Salarios Mínimos Legales Mensuales Vigentes (SMLMV). 
            Esta estandarización permite analizar la carga financiera relativa de la matrícula frente al salario mínimo legal independientemente del año de vigencia.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No hay datos disponibles para mostrar con los filtros seleccionados.")

import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Dashboard Relacional de Matrículas - UCMC",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PALETA DE COLORES SOLICITADA
COLOR_PRINCIPAL = "#CB7087"
COLOR_SECUNDARIO = "#EDBECA"
COLOR_TERCIARIO = "#FFD6DC"
COLOR_FONDO = "#FFF1E4"
PALETA = [COLOR_PRINCIPAL, COLOR_SECUNDARIO, COLOR_TERCIARIO, "#B55A71", "#E295A8", "#F4D1DA"]

# ESTILOS CSS PERSONALIZADOS
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {COLOR_FONDO};
        }}
        [data-testid="stSidebar"] {{
            background-color: {COLOR_TERCIARIO};
            border-right: 2px solid {COLOR_PRINCIPAL};
        }}
        h1, h2, h3 {{
            color: {COLOR_PRINCIPAL} !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: {COLOR_SECUNDARIO};
            border-radius: 8px 8px 0px 0px;
            padding: 10px 16px;
            color: #2B2B2B;
            font-weight: 600;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {COLOR_PRINCIPAL} !important;
            color: #FFFFFF !important;
        }}
        .resena-box {{
            background-color: #FFFFFF;
            border-left: 5px solid {COLOR_PRINCIPAL};
            padding: 16px;
            border-radius: 6px;
            margin-top: 15px;
            box-shadow: 0 2px 6px rgba(203, 112, 135, 0.15);
            color: #333333;
            font-size: 15px;
        }}
    </style>
""", unsafe_allow_html=True)

# 2. CARGA Y LIMPIEZA DE DATOS
@st.cache_data
def cargar_datos():
    ruta = os.path.join("database", "Valor_de_Matricula_-_Programas_Universidad_Colegio_Mayor_de_Cundinamarca_20261126.csv")
    df = pd.read_csv(ruta)
    df.columns = df.columns.str.strip()
    
    # Mapeo flexible para asegurar coincidencia exacta con los nombres de columnas
    col_map = {}
    for col in df.columns:
        c_upper = col.upper()
        if "PROGRAMA" in c_upper:
            col_map[col] = "PROGRAMA"
        elif "MAXIMO" in c_upper or "MÁXIMO" in c_upper:
            col_map[col] = "NIVEL DE INGRESO MAXIMO"
        elif "NIVEL DE INGRESO" in c_upper:
            col_map[col] = "NIVEL DE INGRESOS"
        elif "MATRICULA" in c_upper or "MATRÍCULA" in c_upper:
            col_map[col] = "VALOR DE MATRICULA"
        elif "SMLMV" in c_upper:
            col_map[col] = "Valor en SMLMV"
            
    df = df.rename(columns=col_map)
    
    # Limpieza de columnas numéricas si vienen formateadas como texto
    for num_col in ["VALOR DE MATRICULA", "Valor en SMLMV"]:
        if num_col in df.columns and df[num_col].dtype == 'object':
            df[num_col] = (
                df[num_col]
                .astype(str)
                .str.replace(r'[$\s]', '', regex=True)
                .str.replace('.', '', regex=False)
                .str.replace(',', '.', regex=False)
            )
            df[num_col] = pd.to_numeric(df[num_col], errors='coerce')
            
    return df

try:
    df_original = cargar_datos()
except FileNotFoundError:
    st.error('❌ No se encontró el archivo en la ruta: `"database\\Valor_de_Matricula_-_Programas_Universidad_Colegio_Mayor_de_Cundinamarca_20261126.csv"`. Verifica la carpeta.')
    st.stop()

# 3. PANEL IZQUIERDO: FILTROS ENCADENADOS
st.sidebar.markdown("## 🔍 Filtros Encadenados")
st.sidebar.caption("Cada filtro actualiza dinámicamente las opciones disponibles de los siguientes.")

categorias_ordenadas = [
    "PROGRAMA",
    "NIVEL DE INGRESOS",
    "NIVEL DE INGRESO MAXIMO",
    "VALOR DE MATRICULA",
    "Valor en SMLMV"
]

df_filtrado = df_original.copy()

for cat in categorias_ordenadas:
    if cat in df_filtrado.columns:
        opciones_disponibles = sorted(df_filtrado[cat].dropna().unique().tolist())
        seleccion = st.sidebar.multiselect(
            label=f"📌 {cat}",
            options=opciones_disponibles,
            default=[],
            placeholder="Seleccionar..."
        )
        if seleccion:
            df_filtrado = df_filtrado[df_filtrado[cat].isin(seleccion)]

st.sidebar.markdown("---")
st.sidebar.metric(label="Registros Filtrados", value=f"{len(df_filtrado)} / {len(df_original)}")

# 4. CUERPO PRINCIPAL Y ÚNICA TABLA OCULTA POR DEFECTO
st.title("🎓 Análisis Multivariable por Programa - UCMC")
st.markdown("Explora las relaciones entre los programas académicos, los rangos de ingreso y los costos de matrícula.")

with st.expander("📋 Ver Tabla Única de Datos (Clic para desplegar)", expanded=False):
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

st.markdown("---")

# Función para uniformar el diseño visual de los gráficos
def estilizar_grafico(fig, altura=520):
    fig.update_layout(
        height=altura,
        plot_bgcolor="rgba(255, 255, 255, 0.92)",
        paper_bgcolor="rgba(255, 255, 255, 0.92)",
        font=dict(color="#2B2B2B", family="Segoe UI"),
        title_font=dict(size=18, color=COLOR_PRINCIPAL),
        margin=dict(l=30, r=30, t=60, b=40),
        hoverlabel=dict(bgcolor=COLOR_FONDO, font_size=13, font_color="#2B2B2B"),
        legend=dict(title_font_color=COLOR_PRINCIPAL, bgcolor="rgba(255,255,255,0.7)")
    )
    return fig

# 5. PESTAÑAS POR CADA GRUPO DE CATEGORÍAS SOLICITADO
tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Programa vs Nivel de Ingresos",
    "2️⃣ Programa vs Nivel Ingreso Máximo",
    "3️⃣ Programa vs Valor de Matrícula",
    "4️⃣ Programa vs Valor en SMLMV"
])

# --- PESTAÑA 1: [PROGRAMA, NIVEL DE INGRESOS] ---
with tab1:
    st.subheader("Relación: Programa vs. Nivel de Ingresos")
    if not df_filtrado.empty and {"PROGRAMA", "NIVEL DE INGRESOS"}.issubset(df_filtrado.columns):
        df_g1 = (
            df_filtrado.groupby(["PROGRAMA", "NIVEL DE INGRESOS"], as_index=False)
            .size()
            .rename(columns={"size": "Cantidad"})
        )
        altura_dinamica = max(480, df_g1["PROGRAMA"].nunique() * 28)
        
        fig1 = px.bar(
            df_g1,
            x="Cantidad",
            y="PROGRAMA",
            color="NIVEL DE INGRESOS",
            orientation="h",
            barmode="stack",
            text="Cantidad",
            color_discrete_sequence=PALETA,
            title="Composición de Niveles de Ingreso por Programa Académico"
        )
        fig1.update_traces(textposition="inside", marker_line_color="#FFFFFF", marker_line_width=1)
        st.plotly_chart(estilizar_grafico(fig1, altura_dinamica), use_container_width=True)
        
        st.markdown("""
        <div class="resena-box">
            <strong>📌 Reseña - Programa y Nivel de Ingresos:</strong><br>
            Este gráfico de barras apiladas permite visualizar cómo se distribuyen los diferentes niveles de ingreso socioeconómico al interior de cada programa académico. 
            Facilita identificar qué carreras concentran mayor diversidad de rangos de ingreso o presentan predominio de un estrato tarifario específico.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No hay datos disponibles para cruzar Programa y Nivel de Ingresos con los filtros actuales.")

# --- PESTAÑA 2: [PROGRAMA, NIVEL DE INGRESO MAXIMO] ---
with tab2:
    st.subheader("Relación: Programa vs. Nivel de Ingreso Máximo")
    if not df_filtrado.empty and {"PROGRAMA", "NIVEL DE INGRESO MAXIMO"}.issubset(df_filtrado.columns):
        df_g2 = (
            df_filtrado.groupby(["PROGRAMA", "NIVEL DE INGRESO MAXIMO"], as_index=False)
            .size()
            .rename(columns={"size": "Frecuencia"})
        )
        altura_dinamica = max(480, df_g2["PROGRAMA"].nunique() * 28)
        
        fig2 = px.density_heatmap(
            df_g2,
            x="NIVEL DE INGRESO MAXIMO",
            y="PROGRAMA",
            z="Frecuencia",
            text_auto=True,
            color_continuous_scale=[COLOR_FONDO, COLOR_TERCIARIO, COLOR_SECUNDARIO, COLOR_PRINCIPAL],
            title="Mapa de Calor: Concentración de Topes Máximos de Ingreso por Programa"
        )
        fig2.update_layout(coloraxis_colorbar=dict(title="Registros"))
        st.plotly_chart(estilizar_grafico(fig2, altura_dinamica), use_container_width=True)
        
        st.markdown("""
        <div class="resena-box">
            <strong>📌 Reseña - Programa y Nivel de Ingreso Máximo:</strong><br>
            El mapa de calor cruza cada carrera con los límites máximos de ingresos declarados, resaltando en tonos más intensos las combinaciones con mayor frecuencia. 
            Permite detectar rápidamente los techos financieros más habituales por programa académico para la liquidación de matrículas.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No hay datos disponibles para cruzar Programa y Nivel de Ingreso Máximo con los filtros actuales.")

# --- PESTAÑA 3: [PROGRAMA, VALOR DE MATRICULA] ---
with tab3:
    st.subheader("Relación: Programa vs. Valor de Matrícula ($ COP)")
    if not df_filtrado.empty and {"PROGRAMA", "VALOR DE MATRICULA"}.issubset(df_filtrado.columns):
        df_g3 = (
            df_filtrado.groupby("PROGRAMA", as_index=False)["VALOR DE MATRICULA"]
            .agg(Promedio="mean", Minimo="min", Maximo="max")
            .sort_values(by="Promedio", ascending=True)
        )
        altura_dinamica = max(480, len(df_g3) * 30)
        
        fig3 = px.bar(
            df_g3,
            x="Promedio",
            y="PROGRAMA",
            orientation="h",
            text_auto="$.2s",
            color="Promedio",
            hover_data={"Minimo": ":$,.0f", "Promedio": ":$,.0f", "Maximo": ":$,.0f"},
            color_continuous_scale=[COLOR_TERCIARIO, COLOR_SECUNDARIO, COLOR_PRINCIPAL],
            title="Valor Promedio de Matrícula por Programa (con Rango Mínimo y Máximo en Tooltip)"
        )
        fig3.update_traces(textposition="outside", marker_line_color=COLOR_PRINCIPAL, marker_line_width=1)
        fig3.update_layout(coloraxis_showscale=False)
        st.plotly_chart(estilizar_grafico(fig3, altura_dinamica), use_container_width=True)
        
        st.markdown("""
        <div class="resena-box">
            <strong>📌 Reseña - Programa y Valor de Matrícula:</strong><br>
            Compara el costo promedio en pesos colombianos (COP) de la matrícula entre todos los programas académicos seleccionados. 
            Al pasar el cursor sobre cada barra se detallan además los valores mínimo y máximo registrados, mostrando la amplitud tarifaria de cada carrera.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No hay datos disponibles para cruzar Programa y Valor de Matrícula con los filtros actuales.")

# --- PESTAÑA 4: [PROGRAMA, VALOR DEL SEMESTRE EN SMLMV] ---
with tab4:
    st.subheader("Relación: Programa vs. Valor del Semestre en SMLMV")
    if not df_filtrado.empty and {"PROGRAMA", "Valor en SMLMV"}.issubset(df_filtrado.columns):
        # Ordenar programas por su mediana en SMLMV para una lectura limpia
        orden_programas = (
            df_filtrado.groupby("PROGRAMA")["Valor en SMLMV"]
            .median()
            .sort_values(ascending=True)
            .index.tolist()
        )
        altura_dinamica = max(500, len(orden_programas) * 30)
        
        fig4 = px.box(
            df_filtrado,
            x="Valor en SMLMV",
            y="PROGRAMA",
            orientation="h",
            category_orders={"PROGRAMA": orden_programas},
            points="all",
            color_discrete_sequence=[COLOR_PRINCIPAL],
            title="Dispersión y Mediana del Valor en SMLMV por Programa Académico"
        )
        fig4.update_traces(
            fillcolor=COLOR_SECUNDARIO,
            line=dict(color=COLOR_PRINCIPAL, width=2),
            marker=dict(color=COLOR_PRINCIPAL, size=6, opacity=0.75)
        )
        st.plotly_chart(estilizar_grafico(fig4, altura_dinamica), use_container_width=True)
        
        st.markdown("""
        <div class="resena-box">
            <strong>📌 Reseña - Programa y Valor en SMLMV:</strong><br>
            Este diagrama de cajas y puntos (Boxplot) ilustra la distribución del costo de matrícula expresado en Salarios Mínimos Legales Mensuales Vigentes (SMLMV) para cada programa. 
            Permite identificar la mediana, los cuartiles y cada tarifa escalonada individual, facilitando la comparación del esfuerzo económico relativo entre carreras.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No hay datos disponibles para cruzar Programa y Valor en SMLMV con los filtros actuales.")
