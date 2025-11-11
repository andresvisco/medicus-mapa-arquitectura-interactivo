# 🏥 MEDICUS - Mapa de Arquitectura GCP Interactivo

Sistema completo de visualización de arquitectura Google Cloud Platform con dos aplicaciones especializadas.

## 🎯 Arquitectura del Sistema

### 📊 **app.py** - Aplicación de Visualización (Pública)
- 📁 **Solo modo cache**: No requiere credenciales GCP
- 🔄 **Nodos colapsables**: Click para expandir/contraer categorías  
- 🎨 **Visualización interactiva**: Arrastra, zoom, y explora
- ⚡ **Acceso rápido**: Carga instantánea desde archivos locales
- 🌐 **Lista para Streamlit Cloud**: Sin dependencias de GCP

### 🌐 **app_download.py** - Aplicación de Descarga (Privada)
- 🔑 **Con autenticación GCP**: Para administradores únicamente
- 📡 **Conexión directa a APIs**: Obtiene datos frescos
- 💾 **Generación de cache**: Crea archivos JSON optimizados
- 🛠️ **Gestión completa**: Descarga, valida y guarda datos

## 🚀 Guía de Uso

### Método Rápido (Script Automatizado)
```bash
# Usar el script interactivo
./run.sh
```

### Método Manual

#### 1. 📡 Descargar Datos (Solo Administrador)
```bash
# Instalar dependencias completas
pip install -r requirements_download.txt

# Autenticar con GCP
gcloud auth application-default login

# Ejecutar aplicación de descarga
streamlit run app_download.py
```

#### 2. 📊 Visualizar Datos (Público)
```bash
# Instalar dependencias mínimas
pip install -r requirements.txt

# Ejecutar aplicación de visualización
streamlit run app.py
```

### 3. 🔄 Flujo de Trabajo Completo
1. **Admin**: Ejecuta `app_download.py` para actualizar datos
2. **Admin**: Copia archivos JSON generados
3. **Usuarios**: Usan `app.py` para visualizar sin credenciales

## 📁 Estructura de archivos

```
gcp_cache/
├── proyecto1_gcp_data.json
├── proyecto2_gcp_data.json
└── ...
```

## 🌐 Despliegue en Streamlit Cloud

Esta versión está optimizada para Streamlit Cloud:
- ✅ Sin dependencias de GCP
- ✅ Solo pyvis y streamlit
- ✅ Archivos JSON incluidos

## 🎨 Funcionalidades del diagrama

- **Click en categorías**: Expandir/colapsar recursos (nivel 1: categorías como BigQuery)
- **Click en datasets**: Expandir/colapsar tablas (nivel 2: datasets de BigQuery)
- **Navegación jerárquica**: 4 niveles - Proyecto → Categorías → Datasets/Buckets → Tablas
- **Arrastrar nodos**: Reorganizar el layout
- **Zoom**: Rueda del mouse para acercar/alejar
- **Colores**: Verde=activo, Rojo=error, Azul=corriendo

## 📊 Servicios soportados

- 📦 **Cloud Storage (GCS)**: Buckets y información
- 📊 **BigQuery**: Datasets y tablas
- 🌊 **Dataflow**: Jobs y pipelines
- ⚙️ **Cloud Run**: Servicios (próximamente)

---
**Desarrollado por MEDICUS Team** 🏥