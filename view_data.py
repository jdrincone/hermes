import streamlit as st
import pandas as pd
from database import get_db
from models import User, ProductionOrder, QualityForm, ProductionForm
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    page_title="Visualización de Datos",
    page_icon="📊",
    layout="wide"
)

# Estilos personalizados
st.markdown("""
    <style>
    .stButton>button {
        background-color: #1A494C;
        color: white;
    }
    .stButton>button:hover {
        background-color: #94AF92;
        color: white;
    }
    .stSelectbox, .stNumberInput {
        background-color: #E6ECD8;
    }
    .stTextInput>div>div>input {
        background-color: #E6ECD8;
    }
    .stCheckbox>div {
        background-color: #E6ECD8;
    }
    .stRadio>div {
        background-color: #E6ECD8;
    }
    .stSuccess {
        background-color: #94AF92;
        color: white;
    }
    .stError {
        background-color: #1A494C;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

def get_quality_data():
    db = next(get_db())
    quality_forms = db.query(QualityForm).all()
    
    data = []
    for form in quality_forms:
        order = db.query(ProductionOrder).filter(ProductionOrder.id == form.production_order_id).first()
        user = db.query(User).filter(User.id == form.user_id).first()
        
        data.append({
            'ID': form.id,
            'Orden de Producción': order.order_number if order else 'N/A',
            'Usuario': user.username if user else 'N/A',
            'Apariencia': form.apariencia,
            'Color': form.color,
            'Olor': form.olor,
            'Humedad (%)': form.humedad,
            'Proteína (%)': form.proteina,
            'Grasa (%)': form.grasa,
            'Fibra (%)': form.fibra,
            'Cenizas (%)': form.cenizas,
            'Fecha de Creación': form.created_at
        })
    
    return pd.DataFrame(data)

def get_production_data():
    db = next(get_db())
    production_forms = db.query(ProductionForm).all()
    
    data = []
    for form in production_forms:
        order = db.query(ProductionOrder).filter(ProductionOrder.id == form.production_order_id).first()
        user = db.query(User).filter(User.id == form.user_id).first()
        
        data.append({
            'ID': form.id,
            'Orden de Producción': order.order_number if order else 'N/A',
            'Usuario': user.username if user else 'N/A',
            'Dieta': form.dieta,
            'Molienda': form.molienda,
            'Durabilidad': form.durabilidad,
            'Dureza': form.dureza,
            'Temperatura (°C)': form.temperatura,
            'Pelletizadora': form.peletizadora,
            'Fecha de Creación': form.created_at
        })
    
    return pd.DataFrame(data)

def get_combined_data():
    quality_df = get_quality_data()
    production_df = get_production_data()
    
    if quality_df.empty or production_df.empty:
        return pd.DataFrame()
    
    # Obtener órdenes que están en ambos conjuntos
    common_orders = set(quality_df['Orden de Producción']).intersection(set(production_df['Orden de Producción']))
    
    # Filtrar los DataFrames para incluir solo las órdenes comunes
    quality_filtered = quality_df[quality_df['Orden de Producción'].isin(common_orders)]
    production_filtered = production_df[production_df['Orden de Producción'].isin(common_orders)]
    
    # Renombrar columnas para evitar duplicados
    quality_filtered = quality_filtered.add_prefix('Calidad_')
    production_filtered = production_filtered.add_prefix('Producción_')
    
    # Unir los DataFrames usando la orden de producción
    combined_df = pd.merge(
        quality_filtered,
        production_filtered,
        left_on='Calidad_Orden de Producción',
        right_on='Producción_Orden de Producción',
        how='inner'
    )
    
    # Renombrar la columna de orden de producción
    combined_df = combined_df.rename(columns={'Calidad_Orden de Producción': 'Orden de Producción'})
    
    # Eliminar la columna duplicada
    combined_df = combined_df.drop('Producción_Orden de Producción', axis=1)
    
    return combined_df

def main():
    st.title("📊 Visualización de Datos")
    
    # Selector de tipo de datos
    data_type = st.sidebar.selectbox(
        "Seleccione el tipo de datos a visualizar",
        ["Formularios de Calidad", "Formularios de Producción", "Órdenes Completas"]
    )
    
    # Filtros
    st.sidebar.subheader("Filtros")
    
    if data_type == "Formularios de Calidad":
        df = get_quality_data()
        
        # Filtros específicos para calidad
        if not df.empty:
            order_filter = st.sidebar.multiselect(
                "Filtrar por Orden de Producción",
                options=sorted(df['Orden de Producción'].unique())
            )
            
            user_filter = st.sidebar.multiselect(
                "Filtrar por Usuario",
                options=sorted(df['Usuario'].unique())
            )
            
            # Convertir fechas a datetime si son strings
            if isinstance(df['Fecha de Creación'].iloc[0], str):
                df['Fecha de Creación'] = pd.to_datetime(df['Fecha de Creación'])
            
            min_date = df['Fecha de Creación'].min().date()
            max_date = df['Fecha de Creación'].max().date()
            
            date_range = st.sidebar.date_input(
                "Rango de Fechas",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            # Aplicar filtros
            if order_filter:
                df = df[df['Orden de Producción'].isin(order_filter)]
            if user_filter:
                df = df[df['Usuario'].isin(user_filter)]
            if date_range:
                start_date = pd.to_datetime(date_range[0])
                end_date = pd.to_datetime(date_range[1]) + timedelta(days=1)
                df = df[(df['Fecha de Creación'] >= start_date) & 
                       (df['Fecha de Creación'] < end_date)]
    
    elif data_type == "Formularios de Producción":
        df = get_production_data()
        
        # Filtros específicos para producción
        if not df.empty:
            order_filter = st.sidebar.multiselect(
                "Filtrar por Orden de Producción",
                options=sorted(df['Orden de Producción'].unique())
            )
            
            user_filter = st.sidebar.multiselect(
                "Filtrar por Usuario",
                options=sorted(df['Usuario'].unique())
            )
            
            dieta_filter = st.sidebar.multiselect(
                "Filtrar por Dieta",
                options=sorted(df['Dieta'].unique())
            )
            
            # Convertir fechas a datetime si son strings
            if isinstance(df['Fecha de Creación'].iloc[0], str):
                df['Fecha de Creación'] = pd.to_datetime(df['Fecha de Creación'])
            
            min_date = df['Fecha de Creación'].min().date()
            max_date = df['Fecha de Creación'].max().date()
            
            date_range = st.sidebar.date_input(
                "Rango de Fechas",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            # Aplicar filtros
            if order_filter:
                df = df[df['Orden de Producción'].isin(order_filter)]
            if user_filter:
                df = df[df['Usuario'].isin(user_filter)]
            if dieta_filter:
                df = df[df['Dieta'].isin(dieta_filter)]
            if date_range:
                start_date = pd.to_datetime(date_range[0])
                end_date = pd.to_datetime(date_range[1]) + timedelta(days=1)
                df = df[(df['Fecha de Creación'] >= start_date) & 
                       (df['Fecha de Creación'] < end_date)]
    
    else:  # Órdenes Completas
        df = get_combined_data()
        
        # Filtros para órdenes completas
        if not df.empty:
            order_filter = st.sidebar.multiselect(
                "Filtrar por Orden de Producción",
                options=sorted(df['Orden de Producción'].unique())
            )
            
            user_filter = st.sidebar.multiselect(
                "Filtrar por Usuario",
                options=sorted(df['Calidad_Usuario'].unique())
            )
            
            dieta_filter = st.sidebar.multiselect(
                "Filtrar por Dieta",
                options=sorted(df['Producción_Dieta'].unique())
            )
            
            # Convertir fechas a datetime si son strings
            if isinstance(df['Calidad_Fecha de Creación'].iloc[0], str):
                df['Calidad_Fecha de Creación'] = pd.to_datetime(df['Calidad_Fecha de Creación'])
                df['Producción_Fecha de Creación'] = pd.to_datetime(df['Producción_Fecha de Creación'])
            
            min_date = min(df['Calidad_Fecha de Creación'].min(), df['Producción_Fecha de Creación'].min()).date()
            max_date = max(df['Calidad_Fecha de Creación'].max(), df['Producción_Fecha de Creación'].max()).date()
            
            date_range = st.sidebar.date_input(
                "Rango de Fechas",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            # Aplicar filtros
            if order_filter:
                df = df[df['Orden de Producción'].isin(order_filter)]
            if user_filter:
                df = df[df['Calidad_Usuario'].isin(user_filter)]
            if dieta_filter:
                df = df[df['Producción_Dieta'].isin(dieta_filter)]
            if date_range:
                start_date = pd.to_datetime(date_range[0])
                end_date = pd.to_datetime(date_range[1]) + timedelta(days=1)
                df = df[
                    ((df['Calidad_Fecha de Creación'] >= start_date) & 
                     (df['Calidad_Fecha de Creación'] < end_date)) |
                    ((df['Producción_Fecha de Creación'] >= start_date) & 
                     (df['Producción_Fecha de Creación'] < end_date))
                ]
    
    # Mostrar datos
    if not df.empty:
        # Convertir fechas a string para mostrar
        if data_type == "Órdenes Completas":
            df['Calidad_Fecha de Creación'] = df['Calidad_Fecha de Creación'].dt.strftime('%Y-%m-%d %H:%M:%S')
            df['Producción_Fecha de Creación'] = df['Producción_Fecha de Creación'].dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            df['Fecha de Creación'] = df['Fecha de Creación'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # Estadísticas básicas
        st.subheader("📈 Estadísticas")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total de Registros", len(df))
        
        with col2:
            st.metric("Última Actualización", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Opción para descargar datos
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Descargar Datos",
            csv,
            f"{data_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.info("No hay datos disponibles para mostrar.")

if __name__ == "__main__":
    main() 