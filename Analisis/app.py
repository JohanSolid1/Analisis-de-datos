import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Dashboard Avanzado de Datos Públicos",
    page_icon="📊",
    layout="wide"
)

st.title("Análisis de Datos Públicos: Portal Datos.gob.cl")
st.write("Esta aplicación web interactiva consume información en tiempo real desde la API oficial de datos abiertos de Chile.")

# URL base de la API
API_URL = "https://datos.gob.cl/api/3/action/package_list"

@st.cache_data
def load_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("result", [])
        else:
            st.error(f"Error al conectar con la API: Código {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Ocurrió un error en la conexión: {e}")
        return []

# 1. Extracción de datos
raw_datasets = load_data(API_URL)

if raw_datasets:
    # 2. Procesamiento de datos con Pandas
    df_datasets = pd.DataFrame({
        "ID_Dataset": range(1, len(raw_datasets) + 1),
        "Nombre_Identificador": raw_datasets
    })
    
    # Lógica de categorización mejorada
    def categorizar_fuente(nombre):
        nombre = nombre.lower()

        # 1. Transporte y Obras Públicas
        if any(k in nombre for k in ["transporte", "subtel", "vias", "transantiago", "mop", "vivienda", "serviu", "infraestructura"]):
            return "Transporte y Urbanismo"
        # 2. Salud
        elif any(k in nombre for k in ["salud", "minsal", "hospital", "fonasa", "medica", "isp", "sanitario"]):
            return "Salud Pública"
        # 3. Educación y Cultura
        elif any(k in nombre for k in ["educacion", "mineduc", "beca", "colegio", "escuela", "cultura", "patrimonio", "conicyt", "anid"]):
            return "Educación y Cultura"
        # 4. Medio Ambiente y Energía
        elif any(k in nombre for k in ["ambiente", "mma", "contaminacion", "residuos", "clima", "energia", "cne", "agua", "sustentable"]):
            return "Medio Ambiente y Energía"
        # 5. Gestión Comunal y Municipal
        elif any(k in nombre for k in ["municipalidad", "muni", "comuna", "local", "valparaiso", "santiago", "región", "subdere"]):
            return "Gestión Municipal y Regional"
        # 6. Economía, Finanzas y Comercio
        elif any(k in nombre for k in ["economia", "hacienda", "sii", "cmf", "comercio", "pyme", "aduanas", "tesoreria", "banco"]):
            return "Economía y Finanzas"
        # 7. Justicia, Seguridad y Defensa
        elif any(k in nombre for k in ["justicia", "seguridad", "carabineros", "pdi", "defensa", "gendarmeria", "legal", "delito"]):
            return "Seguridad y Justicia"
        # 8. Desarrollo Social, Trabajo y Subsidios
        elif any(k in nombre for k in ["social", "mideso", "trabajo", "sence", "empleo", "subsidio", "bono", "transferencias", "fondos", "postulacion"]):
            return "Desarrollo Social y Laboral"
        # 9. Agricultura, Minería y Pesca
        elif any(k in nombre for k in ["agricultura", "mineria", "sernageomin", "indap", "pesca", "sernapesca", "conaf"]):
            return "Recursos Naturales y Agro"
        else:
            return "Trámites e Información General"

    df_datasets["Categoría"] = df_datasets["Nombre_Identificador"].apply(categorizar_fuente)
    
    # Contar la cantidad de palabras separadas por guiones en el identificador
    df_datasets["Cantidad_Palabras"] = df_datasets["Nombre_Identificador"].apply(lambda x: len(x.split("-")))

    # 3. Componentes Interactivos (Barra Lateral)
    st.sidebar.header("Filtros de Búsqueda")
    categorias_disponibles = ["Todas"] + list(df_datasets["Categoría"].unique())
    categoria_seleccionada = st.sidebar.selectbox("Selecciona una categoría institucional:", categorias_disponibles)

    # Aplicar filtro dinámico
    if categoria_seleccionada != "Todas":
        df_filtrado = df_datasets[df_datasets["Categoría"] == categoria_seleccionada]
    else:
        df_filtrado = df_datasets

    # Despliegue de métricas clave en la cabecera
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Datasets Analizados", len(df_datasets))
    with col2:
        st.metric("Datasets en Filtro Actual", len(df_filtrado))
    with col3:
        # CORRECCIÓN AQUÍ: Usamos Cantidad_Palabras en lugar del largo de caracteres que daba error
        st.metric("Promedio Palabras por Nombre", f"{round(df_filtrado['Cantidad_Palabras'].mean(), 1)} pal.")

    # Mostrar tabla de datos procesados
    st.subheader("Vista de Datos Procesados")
    st.dataframe(df_filtrado, use_container_width=True)

    # 4. Sección de Visualización Avanzada mediante Pestañas (Tabs)
    st.subheader("Visualización Analítica del Conjunto de Datos")
    tab1, tab2, tab3 = st.tabs(["Distribución Institucional", "Análisis de Frecuencia de Palabras", "Análisis de Estructura de Nombres"])

    # PESTAÑA 1: Gráfico de Barras por Categoría (Mejorado)
    # PESTAÑA 1: Gráfico de Barras por Categoría (Optimizado sin el outlier)
    with tab1:
        st.write("#### Distribución de Recursos de Información por Categoría")
        
        # 1. Obtener el conteo total de todas las categorías
        conteo_completo = df_filtrado["Categoría"].value_counts()
        
        # 2. Guardar el valor de Trámites de forma independiente para mostrarlo en texto
        total_tramites = conteo_completo.get("Trámites e Información General", 0)
        
        # 3. Filtrar el conteo para EXCLUIR la barra gigante del gráfico
        conteo_grafico = conteo_completo.drop(labels=["Trámites e Información General"], errors="ignore").sort_values(ascending=True)
        
        # 4. Renderizar el gráfico limpio
        if not conteo_grafico.empty:
            fig1, ax1 = plt.subplots(figsize=(10, 4))
            conteo_grafico.plot(kind="barh", ax=ax1, color="#2b5c8f")
            ax1.set_xlabel("Cantidad de Datasets")
            ax1.set_ylabel("Categorías")
            plt.tight_layout()
            st.pyplot(fig1)
        else:
            st.info("No hay categorías institucionales adicionales para mostrar con el filtro seleccionado.")
        
        # 5. Apartado especial abajo del gráfico para mostrar el dato aislado de forma limpia
        st.markdown("---")
        st.write("#### Volumen de Información General Aislada")
        st.info(
            f"**Nota de Análisis:** Para mantener la legibilidad de las métricas sectoriales, se ha excluido del gráfico "
            f"la categoría principal. Actualmente, existen **{total_tramites:,} datasets** clasificados bajo "
            f"**Trámites e Información General**, los cuales corresponden a normativas estandarizadas, índices globales "
            f"y documentación pública general de la nación."
        )

    # PESTAÑA 2: Top 10 Palabras Clave (Uso analítico de Strings)
    with tab2:
        st.write("#### Top 10 Palabras Clave más Comunes en los Identificadores")
        st.info("Este gráfico procesa el texto eliminando conectores comunes para identificar las temáticas estatales predominantes.")
        
        # Unir todos los nombres, separar por guiones y limpiar conectores comunes de nombres de datasets chilenos
        todas_las_palabras = "-".join(df_filtrado["Nombre_Identificador"].tolist()).split("-")
        conectores_a_excluir = {"de", "del", "la", "el", "en", "para", "los", "las", "un", "una", "ano", "mes", "al", "con", "a"}
        palabras_limpias = [p for p in todas_las_palabras if p.lower() not in conectores_a_excluir and len(p) > 2]
        
        # Contar frecuencias y tomar las 10 más comunes
        frecuencia_palabras = Counter(palabras_limpias).most_common(10)
        
        if frecuencia_palabras:
            df_palabras = pd.DataFrame(frecuencia_palabras, columns=["Palabra", "Frecuencia"])
            
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            ax2.bar(df_palabras["Palabra"], df_palabras["Frecuencia"], color="#e07a5f")
            ax2.set_ylabel("Número de Apariciones")
            ax2.set_xlabel("Términos Detectados")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig2)
        else:
            st.write("No hay suficientes palabras para generar el análisis.")

   # PESTAÑA 3: Top 10 Instituciones Proveedoras de Datos
    with tab3:
        st.write("#### Top 10 Organismos Públicos Líderes en Datos Abiertos")
        st.info("Este análisis identifica las instituciones del Estado que registran el mayor volumen de datasets publicados en el portal nacional.")
        
        # Extraemos la primera palabra de cada identificador (sigla institucional o término raíz)
        instituciones = df_filtrado["Nombre_Identificador"].apply(lambda x: x.split("-")[0] if "-" in x else x)
        instituciones_limpias = [inst for inst in instituciones if not inst.isdigit() and len(inst) > 2]
        
        conteo_instituciones = Counter(instituciones_limpias).most_common(10)
        
        if conteo_instituciones:
            df_inst = pd.DataFrame(conteo_instituciones, columns=["Institución/Sigla", "Cantidad de Datasets"])
            df_inst = df_inst.sort_values(by="Cantidad de Datasets", ascending=True)
            
            fig3, ax3 = plt.subplots(figsize=(10, 4))
            ax3.barh(df_inst["Institución/Sigla"], df_inst["Cantidad de Datasets"], color="#81b29a")
            ax3.set_xlabel("Cantidad de Datasets Publicados")
            ax3.set_ylabel("Sigla Institucional / Término Raíz")
            plt.tight_layout()
            st.pyplot(fig3)
            
            # Tabla de apoyo resumida abajo del gráfico
            st.write("**Detalle de registros por entidad:**")
            st.dataframe(df_inst.sort_values(by="Cantidad de Datasets", ascending=False), use_container_width=True)
            
            # GLOSARIO MEJORADO CON TODOS LOS TÉRMINOS DETECTADOS EN TU IMAGEN
            st.markdown("---")
            st.write("📖 **Diccionario Analítico y Glosario de Conceptos Encontrados:**")
            
            glosario_maestro = {
                "ejecucion": "**EJECUCION:** Clasificación correspondiente a los informes de **Ejecución Presupuestaria** mensuales y trimestrales. Representa el control de gastos públicos e inversiones reales realizados por ministerios y municipalidades en Chile.",
                "ley": "**LEY:** Documentación referente a cuerpos legales, normativas específicas y el cumplimiento activo de la **Ley de Transparencia (Ley N° 20.285)**, la cual exige registrar públicamente los actos y resoluciones del Estado.",
                "permisos": "**PERMISOS:** Bases de datos asociadas a autorizaciones comerciales, ambientales, sanitarias y de edificación otorgadas por los distintos organismos gubernamentales y direcciones de obras.",
                "permiso": "**PERMISO:** (Variante de Permisos) Centrado principalmente en registros de patentes comerciales locales, derechos de agua, o autorizaciones territoriales específicas.",
                "organizaciones": "**ORGANIZACIONES:** Datasets que catastran entidades de la sociedad civil, juntas de vecinos, uniones comunales, clubes deportivos o agrupaciones comunitarias registradas ante el Ministerio de fe pública.",
                "finanzas": "**FINANZAS:** Reportes contables oficiales, balances financieros del sector público, estados de cuentas institucionales y transferencias monetarias interbancarias del tesoro público.",
                "cuadro": "**CUADRO:** Término técnico utilizado en la nomenclatura de datos para clasificar matrices estadísticas, cuadros de mando de indicadores de gestión, o tabulados analíticos consolidados por departamentos de estudios.",
                "https": "**HTTPS / HTTP (Prefijo Tecnológico):** Indica que la institución configuró el identificador del recurso utilizando la URL completa de su servidor web o repositorio API remoto en lugar de una sigla simple.",
                "aeronaves": "**AERONAVES:** Registros, bitácoras y hojas técnicas provistas por la **Dirección General de Aeronáutica Civil (DGAC)** sobre aeronavegación civil y comercial en Chile.",
                "patentes": "**PATENTES:** Datos sobre el parque automotriz comunal (permisos de circulación) o registros de propiedad industrial administrados por INAPI.",
                "mop": "**MOP:** Ministerio de Obras Públicas. Infraestructura vial, portuaria, aeroportuaria y recursos hidráulicos.",
                "subtel": "**SUBTEL:** Subsecretaría de Telecomunicaciones. Conectividad, telecomunicaciones y espectro radial.",
                "minsal": "**MINSAL:** Ministerio de Salud. Políticas sanitarias, control epidemiológico y datos de la red de hospitales públicos.",
                "subdere": "**SUBDERE:** Subsecretaría de Desarrollo Regional. Gestión de fondos presupuestarios para el desarrollo de las regiones de Chile.",
                "muni": "**MUNI / MUNICIPALIDAD:** Administraciones locales y municipalidades a nivel comunal.",
                "daem": "**DAEM:** Dirección de Administración de Educación Municipal. Datos de gestión de escuelas y liceos públicos comunales."
            }
            
            with st.expander("Haz clic aquí para ver el significado técnico de las palabras en el gráfico"):
                st.markdown("A continuación se desglosan los enunciados y acrónimos detectados dinámicamente en el top actual:")
                
                # Buscamos qué términos del Top 10 están en nuestro glosario maestro
                terminos_en_grafico = df_inst["Institución/Sigla"].tolist()
                
                for termino in terminos_en_grafico:
                    t_lower = termino.lower()
                    if t_lower in glosario_maestro:
                        st.markdown(f"* {glosario_maestro[t_lower]}")
                
                st.markdown("""
                * ⚙️ **Otros términos/Códigos:** Cualquier concepto o palabra adicional no listada explícitamente representa un identificador técnico interno o la raíz del nombre de un archivo plano (`.csv` o `.json`) indexado directamente por los administradores informáticos de las bases de datos del Estado.
                """)
        else:
            st.write("No hay suficientes identificadores institucionales para generar la métrica.")

else:
    st.warning("No se pudieron recuperar datos de la API en este momento.")