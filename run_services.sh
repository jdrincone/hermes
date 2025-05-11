#!/bin/bash

# Matar cualquier proceso de Streamlit existente
pkill -f streamlit

# Iniciar la aplicación principal en el puerto 8501
streamlit run app.py --server.port 8501 &

# Esperar 2 segundos para asegurar que el primer servicio se inicie
sleep 2

# Iniciar la visualización de datos en el puerto 8502
streamlit run view_data.py --server.port 8502 &

# Mantener el script corriendo
wait 