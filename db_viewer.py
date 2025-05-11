import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Visor de Base de Datos",
    page_icon="🗄️",
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

def get_table_names():
    conn = sqlite3.connect('hermes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return [table[0] for table in tables]

def get_table_data(table_name):
    conn = sqlite3.connect('hermes.db')
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

def main():
    st.title("🗄️ Visor de Base de Datos")
    
    # Obtener lista de tablas
    tables = get_table_names()
    
    if not tables:
        st.error("No se encontraron tablas en la base de datos.")
        return
    
    # Selector de tabla
    selected_table = st.sidebar.selectbox(
        "Seleccione una tabla",
        tables
    )
    
    if selected_table:
        # Obtener datos de la tabla seleccionada
        df = get_table_data(selected_table)
        
        # Mostrar información de la tabla
        st.subheader(f"Tabla: {selected_table}")
        st.write(f"Total de registros: {len(df)}")
        
        # Mostrar datos
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # Opción para descargar datos
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Descargar Datos",
            csv,
            f"{selected_table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv",
            key='download-csv'
        )
        
        # Mostrar esquema de la tabla
        st.subheader("Esquema de la Tabla")
        conn = sqlite3.connect('hermes.db')
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({selected_table})")
        columns = cursor.fetchall()
        conn.close()
        
        # Crear DataFrame con la información del esquema
        schema_df = pd.DataFrame(columns, columns=['cid', 'name', 'type', 'notnull', 'dflt_value', 'pk'])
        st.dataframe(
            schema_df,
            use_container_width=True,
            hide_index=True
        )

if __name__ == "__main__":
    main() 