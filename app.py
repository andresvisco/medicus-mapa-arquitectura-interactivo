import streamlit as st
import json
import os
from datetime import datetime
from pyvis.network import Network
import streamlit.components.v1 as components

# Importar las librerías de Google Cloud - COMENTADO PARA MODO SOLO-CACHE
# try:
#     from google.cloud import storage
#     from google.cloud import bigquery
#     from google.cloud import run_v2 # Para Cloud Run
#     from google.cloud import dataflow_v1beta3 # Para Dataflow
#     # from google.auth.exceptions import DefaultCredentialsError
#     GCP_LIBRARIES_AVAILABLE = True
# except ImportError:
#     st.error("🚨 Error: Faltan librerías de Google Cloud. Ejecuta: pip install google-cloud-storage google-cloud-bigquery google-cloud-run")
#     GCP_LIBRARIES_AVAILABLE = False
# except Exception as e:
#     st.error(f"Error al cargar las librerías de GCP: {e}")
#     GCP_LIBRARIES_AVAILABLE = False

# Modo solo cache - sin librerías GCP
GCP_LIBRARIES_AVAILABLE = False  # Deshabilitado para modo solo-cache


# --- Configuración del Proyecto y Página ---

# Usa el ID de proyecto conceptual que mencionaste como valor por defecto.
# El usuario deberá cambiarlo o usar el que tenga configurado como predeterminado.
DEFAULT_PROJECT_ID = "medicus-data-dataml-dev"

# Directorio para archivos de cache JSON
CACHE_DIR = "./"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

st.set_page_config(layout="wide", page_title="Diagrama GCP - Modo Cache")

# --- Funciones de Lógica de la Aplicación ---

def get_cache_file_path(project_id):
    """Obtiene la ruta del archivo de cache para un proyecto específico."""
    return os.path.join(CACHE_DIR, f"{project_id}_gcp_data.json")

def save_data_to_cache(project_id, data):
    """Guarda los datos de GCP en un archivo JSON local."""
    try:
        cache_file = get_cache_file_path(project_id)
        
        # Agregar timestamp y metadata
        cache_data = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "project_id": project_id,
            "data": data,
            "generated_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False, default=str)
        
        return True, cache_file
    except Exception as e:
        return False, str(e)

def load_data_from_cache(project_id):
    """Carga los datos de GCP desde el archivo JSON local."""
    try:
        cache_file = get_cache_file_path(project_id)
        
        if not os.path.exists(cache_file):
            return None, f"No existe archivo de cache para proyecto '{project_id}'"
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Validar estructura del cache
        if 'data' not in cache_data:
            return None, "Archivo de cache inválido - falta 'data'"
            
        return cache_data['data'], cache_data.get('timestamp', 'N/A')
    except Exception as e:
        return None, f"Error al cargar cache: {str(e)}"

def get_available_cache_files():
    """Obtiene lista de proyectos con archivos de cache disponibles."""
    cache_files = []
    try:
        if os.path.exists(CACHE_DIR):
            for filename in os.listdir(CACHE_DIR):
                if filename.endswith('_gcp_data.json'):
                    project_id = filename.replace('_gcp_data.json', '')
                    file_path = os.path.join(CACHE_DIR, filename)
                    
                    # Obtener fecha de modificación
                    mod_time = os.path.getmtime(file_path)
                    mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
                    
                    cache_files.append({
                        'project_id': project_id,
                        'filename': filename,
                        'modified': mod_date,
                        'size_kb': round(os.path.getsize(file_path) / 1024, 2)
                    })
    except Exception as e:
        st.error(f"Error al listar archivos de cache: {e}")
    
    return cache_files

# FUNCIÓN COMENTADA - NO SE USA EN MODO SOLO-CACHE
# @st.cache_data(show_spinner="Conectando a GCP y obteniendo recursos...")
# def fetch_and_build_graph_live(project_id):
#     """
#     Se conecta a las APIs de GCP, obtiene los recursos y construye la estructura
#     de nodos y bordes para el grafo Pyvis. (Versión en vivo) - DESHABILITADA
#     """
#     return {"nodes": [], "edges": [], "error": "Función deshabilitada en modo solo-cache"}

def fetch_and_build_graph(project_id):
    """
    Función principal - SOLO MODO CACHE LOCAL
    """
    # Solo cargar desde cache - no hay modo live en esta versión
    data, timestamp = load_data_from_cache(project_id)
    if data is not None:
        st.success(f"✅ Datos cargados desde cache (generados: {timestamp})")
        return data
    else:
        st.warning(f"⚠️ No hay cache disponible para '{project_id}'.")
        return {"nodes": [], "edges": [], "error": "No cache available"}

def create_network_graph(data):
    """
    Crea el objeto de red (Network) de Pyvis a partir de los datos con funcionalidad de colapso/expansión.
    """
    # Debug: Mostrar información de los datos recibidos
    print(f"🔍 Debug - Nodos totales: {len(data.get('nodes', []))}")
    print(f"🔍 Debug - Edges totales: {len(data.get('edges', []))}")
    
    # Verificar que tenemos datos válidos
    if not data.get('nodes') or not data.get('edges'):
        st.error("⚠️ No hay datos válidos para crear el grafo")
        return None
        
    net = Network(height='700px', width='100%', 
                  bgcolor='#f0f2f6', font_color='black', 
                  cdn_resources='remote',
                  directed=True,
                  select_menu=True,  # Habilitar menú de selección
                  filter_menu=True   # Habilitar filtros
                  )
    
    # Configuración mejorada con clustering y colapso
    options_config = {
        "physics": {
            "barnesHut": {
                "gravitationalConstant": -1,
                "centralGravity": 0.2,
                "springLength": 200,
                "springConstant": 0.15,
                "damping": 0.01,
                "avoidOverlap": 1
            },
            "minVelocity": 0.75,
            "solver": "barnesHut",
            "enabled": True,
            "stabilization": {
                "enabled": True,
                "iterations": 100,
                "updateInterval": 25
            }
        },
        "interaction": {
            "hover": True,
            "tooltipDelay": 100,
            "zoomView": True,
            "dragView": True,
            "selectConnectedEdges": True,
            "multiselect": True
        },
        "edges": {
            "font": {"size": 12, "color": "#666666"},
            "smooth": {
                "type": "cubicBezier",
                "forceDirection": "horizontal",
                "roundness": 0.4
            },
            "arrows": {"to": {"enabled": True, "scaleFactor": 0.8}},
            "color": {"inherit": "from"},
            "width": 2
        },
        "nodes": {
            "borderWidth": 2,
            "borderWidthSelected": 4,
            "font": {
                "size": 14,
                "color": "#333333"
            },
            "shadow": {
                "enabled": True,
                "color": "rgba(0,0,0,0.2)",
                "size": 10,
                "x": 2,
                "y": 2
            }
        },
        "layout": {
            "hierarchical": {
                "enabled": False,
                "levelSeparation": 150,
                "nodeSpacing": 100,
                "treeSpacing": 200,
                "blockShifting": True,
                "edgeMinimization": True,
                "parentCentralization": True,
                "direction": "UD"
            }
        },
        "configure": {
            "enabled": False
        }
    }
    
    # Aplicar las opciones
    net.set_options(json.dumps(options_config))
    
    # Separar nodos por nivel para manejar colapso/expansión
    project_nodes = [n for n in data['nodes'] if n.get('level') == 0]  # Proyecto raíz
    category_nodes = [n for n in data['nodes'] if n.get('level') == 1]  # Categorías
    detail_nodes = [n for n in data['nodes'] if n.get('level') == 2]   # Detalles (datasets, buckets)
    table_nodes = [n for n in data['nodes'] if n.get('level') == 3]    # Tablas (inicialmente ocultos)
    
    # Añadir nodo del proyecto
    for node in project_nodes:
        title_text = node.get('title', f"Proyecto: {node['id']}")
        net.add_node(
            n_id=node['id'], 
            label=node['label'], 
            title=title_text,
            size=node['size'],
            color=node['color'],
            physics=True,
            level=0
        )
    
    # Añadir nodos de categoría con indicador de expansión
    for node in category_nodes:
        # Contar cuántos nodos hijos tiene esta categoría
        children_count = len([n for n in detail_nodes if any(
            e['source'] == node['id'] and e['target'] == n['id'] 
            for e in data['edges']
        )])
        
        # Añadir indicador visual de expansión
        expanded_label = f"{node['label']} [{children_count}]" if children_count > 0 else node['label']
        title_text = node.get('title', f"Categoría: {node.get('group', 'N/A')}<br>ID: {node['id']}")
        title_text += f"<br><br>🔍 Click para expandir ({children_count} elementos)"
        
        net.add_node(
            n_id=node['id'], 
            label=expanded_label,
            title=title_text,
            size=node['size'],
            color=node['color'],
            physics=True,
            level=1,
            hidden=False  # Categorías visibles inicialmente
        )
    
    # Añadir nodos de detalle (datasets/buckets) con indicador de expansión
    for node in detail_nodes:
        # Contar cuántos nodos hijos (tablas) tiene este dataset
        children_count = len([n for n in table_nodes if any(
            e['source'] == node['id'] and e['target'] == n['id'] 
            for e in data['edges']
        )])
        
        # Añadir indicador visual de expansión si hay tablas
        expanded_label = f"{node['label']} [{children_count}]" if children_count > 0 else node['label']
        title_text = node.get('title', f"Recurso: {node.get('group', 'N/A')}<br>ID: {node['id']}")
        if children_count > 0:
            title_text += f"<br><br>🔍 Click para expandir ({children_count} tablas)"
        
        net.add_node(
            n_id=node['id'], 
            label=expanded_label, 
            title=title_text,
            size=node['size'],
            color=node['color'],
            physics=True,
            level=2,
            hidden=True  # Detalles ocultos inicialmente
        )
    
    # Añadir nodos de tabla (level 3, inicialmente ocultos)
    for node in table_nodes:
        title_text = node.get('title', f"Tabla: {node.get('group', 'N/A')}<br>ID: {node['id']}")
        net.add_node(
            n_id=node['id'], 
            label=node['label'], 
            title=title_text,
            size=node['size'],
            color=node['color'],
            physics=True,
            level=3,
            hidden=True  # Tablas ocultas inicialmente
        )
    
    # Crear un conjunto de IDs de nodos existentes para validación
    existing_node_ids = set()
    for node_list in [project_nodes, category_nodes, detail_nodes, table_nodes]:
        for node in node_list:
            existing_node_ids.add(node['id'])
    
    # Añadir bordes solo si ambos nodos existen
    for edge in data['edges']:
        source_id = edge['source']
        target_id = edge['target']
        
        # Verificar que ambos nodos existen antes de crear el edge
        if source_id not in existing_node_ids or target_id not in existing_node_ids:
            print(f"⚠️  Saltando edge: {source_id} -> {target_id} (nodo faltante)")
            continue
            
        # Determinar si el borde debe estar oculto inicialmente
        source_level = next((n.get('level', 0) for n in data['nodes'] if n['id'] == source_id), 0)
        target_level = next((n.get('level', 0) for n in data['nodes'] if n['id'] == target_id), 0)
        
        # Ocultar bordes que van a nodos de nivel 2 o 3 (detalles y tablas)
        edge_hidden = target_level in [2, 3]
        
        try:
            net.add_edge(
                source=source_id, 
                to=target_id, 
                title=edge.get('label', 'Conexión'), 
                label=edge.get('label', ''),
                color=edge.get('color', '#888888'),
                hidden=edge_hidden
            )
        except AssertionError as e:
            print(f"❌ Error al crear edge {source_id} -> {target_id}: {e}")
            continue

    # Guarda la red en un archivo HTML temporal
    path = 'gcp_network.html'
    try:
        net.save_graph(path)
        
        # Agregar JavaScript personalizado para colapso/expansión
        with open(path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # JavaScript para funcionalidad de expansión/colapso
        custom_js = """
        <script type="text/javascript">
        // Estado de expansión de nodos (categorías y datasets)
        let expandedNodes = new Set();
        
        // Función para alternar expansión de nodos
        function toggleNode(nodeId) {
            const isExpanded = expandedNodes.has(nodeId);
            
            if (isExpanded) {
                // Colapsar: ocultar nodos hijos y bordes
                collapseNode(nodeId);
                expandedNodes.delete(nodeId);
            } else {
                // Expandir: mostrar nodos hijos y bordes
                expandNode(nodeId);
                expandedNodes.add(nodeId);
            }
            
            // Actualizar la red
            network.setData({nodes: nodes, edges: edges});
            network.fit();
        }
        
        function expandNode(nodeId) {
            // Encontrar y mostrar todos los nodos hijos directos
            const childNodes = nodes.get().filter(node => {
                return edges.get().some(edge => 
                    edge.from === nodeId && edge.to === node.id
                );
            });
            
            childNodes.forEach(node => {
                nodes.update({id: node.id, hidden: false});
            });
            
            // Mostrar bordes a nodos hijos directos
            const childEdges = edges.get().filter(edge => 
                edge.from === nodeId && childNodes.some(n => n.id === edge.to)
            );
            
            childEdges.forEach(edge => {
                edges.update({id: edge.id, hidden: false});
            });
        }
        
        function collapseNode(nodeId) {
            // Encontrar todos los nodos hijos directos
            const childNodes = nodes.get().filter(node => {
                return edges.get().some(edge => 
                    edge.from === nodeId && edge.to === node.id
                );
            });
            
            childNodes.forEach(node => {
                // Ocultar el nodo hijo
                nodes.update({id: node.id, hidden: true});
                
                // Si el hijo también estaba expandido, colapsarlo recursivamente
                if (expandedNodes.has(node.id)) {
                    collapseNode(node.id);
                    expandedNodes.delete(node.id);
                }
            });
            
            // Ocultar bordes a nodos hijos
            const childEdges = edges.get().filter(edge => 
                childNodes.some(n => n.id === edge.to && edge.from === nodeId)
            );
            
            childEdges.forEach(edge => {
                edges.update({id: edge.id, hidden: true});
            });
            
            // También ocultar bordes desde nodos hijos (para tablas)
            const descendantEdges = edges.get().filter(edge => 
                childNodes.some(n => n.id === edge.from)
            );
            
            descendantEdges.forEach(edge => {
                edges.update({id: edge.id, hidden: true});
            });
        }
        
        // Agregar evento de click después de que la red esté lista
        network.on("click", function(params) {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                const node = nodes.get(nodeId);
                
                // Permitir expansión en nodos de categoría (level 1) y dataset (level 2)
                if (node && (node.level === 1 || node.level === 2)) {
                    toggleNode(nodeId);
                }
            }
        });
        
        // Agregar indicadores visuales para nodos expandibles
        network.on("hoverNode", function(params) {
            const node = nodes.get(params.node);
            if (node && (node.level === 1 || node.level === 2)) {
                document.body.style.cursor = 'pointer';
            }
        });
        
        network.on("blurNode", function(params) {
            document.body.style.cursor = 'default';
        });
        </script>
        """
        
        # Insertar el JavaScript antes del cierre del body
        html_content = html_content.replace('</body>', custom_js + '</body>')
        
        # Guardar el HTML modificado
        with open(path, 'w', encoding='utf-8') as file:
            file.write(html_content)
            
    except Exception as e:
        st.error(f"Error al guardar el HTML de la red: {e}")
        return None
        
    return path

# --- Interfaz de Streamlit ---

st.title("☁️ Arquitectura GCP MEDICUS - Viewer Local")

# Sidebar para información
# with st.sidebar:
#     st.header("📋 Información")
    
#     st.info("""
#     **📁 Modo: Solo Cache Local**
    
#     Esta aplicación usa únicamente archivos JSON 
#     previamente descargados. 
    
#     ✅ No requiere conexión a GCP
#     ✅ No requiere autenticación  
#     ✅ Acceso instantáneo
#     """)
    
#     # Mostrar archivos cache disponibles
#     st.subheader("📁 Archivos Disponibles")
#     cache_files = get_available_cache_files()
    
#     if cache_files:
#         for file_info in cache_files:
#             st.write(f"� **{file_info['project_id']}**")
#             st.write(f"📅 {file_info['modified']}")
#             st.write(f"📏 {file_info['size_kb']} KB")
#             st.write("---")
#     else:
#         st.warning("No hay archivos cache disponibles")
#         st.info("""
#         **Para agregar archivos:**
#         1. Ejecuta la versión completa con GCP
#         2. Usa 'Descargar y Guardar' 
#         3. Copia los archivos del directorio `gcp_cache/`
#         """)

st.markdown("""
<style>
    .stCodeBlock { background-color: #f7f9fb; border-radius: 5px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# Entrada para el ID del Proyecto
project_input = st.text_input(
    "Selecciona el Proyecto GCP:", 
    value=DEFAULT_PROJECT_ID,
    help="Debe coincidir con uno de los archivos cache disponibles."
)


# Contenedor para el JSON y el Diagrama
col1, col2 = st.columns([1, 9])

# with col1:
#     st.subheader("� Cargar Datos")
    
#     # Botón simple para cargar desde cache
#     if st.button("📁 Cargar Proyecto", use_container_width=True, type="primary"):
#         graph_data, timestamp = load_data_from_cache(project_input)
        
#         if graph_data:
#             st.session_state['graph_data'] = graph_data
#             st.success(f"✅ Datos cargados exitosamente")
#             st.info(f"📅 **Generados:** {timestamp}")
            
#             # Mostrar resumen
#             st.subheader("📊 Resumen de Datos")
#             st.write(f"🔹 **Nodos:** {len(graph_data.get('nodes', []))}")
#             st.write(f"🔹 **Conexiones:** {len(graph_data.get('edges', []))}")
            
#             # Mostrar JSON expandible
#             with st.expander("🔍 Ver JSON completo", expanded=False):
#                 st.json(graph_data)
#         else:
#             st.error(f"❌ No se encontró archivo cache para: `{project_input}`")
#             st.info("""
#             **💡 Soluciones:**
#             • Verifica que el nombre del proyecto sea correcto
#             • Revisa los archivos disponibles en el sidebar
#             • Asegúrate de que el archivo esté en el directorio `gcp_cache/`
#             """)
    
#     # Estado inicial
#     if 'graph_data' not in st.session_state:
#         st.session_state['graph_data'] = None
#         st.markdown("""
#         **� Para empezar:**
#         1. Selecciona un proyecto de la lista del sidebar
#         2. Haz click en 'Cargar Proyecto'  
#         3. Explora el diagrama interactivo
#         """)

with col2:
    st.subheader("🎯 Visualización Interactiva")
    if st.button("📁 Cargar Proyecto", use_container_width=True, type="primary"):
        graph_data, timestamp = load_data_from_cache(project_input)
        
        if graph_data:
            st.session_state['graph_data'] = graph_data
            st.success(f"✅ Datos cargados exitosamente")
            st.info(f"📅 **Generados:** {timestamp}")
            
            # Mostrar resumen
            st.subheader("📊 Resumen de Datos")
            st.write(f"🔹 **Nodos:** {len(graph_data.get('nodes', []))}")
            st.write(f"🔹 **Conexiones:** {len(graph_data.get('edges', []))}")
            
            # Mostrar JSON expandible
            with st.expander("🔍 Ver JSON completo", expanded=False):
                st.json(graph_data)
    # Verificar si tenemos datos para mostrar
    if st.session_state.get('graph_data') and st.session_state['graph_data'].get('nodes'):
        
        graph_data = st.session_state['graph_data']
        
        # Información del dataset
        total_nodes = len(graph_data.get('nodes', []))
        total_edges = len(graph_data.get('edges', []))
        
        st.write(f"📊 **Dataset:** {total_nodes} nodos, {total_edges} conexiones")
        
        # Generar el grafo Pyvis
        with st.spinner("🎨 Generando diagrama interactivo..."):
            html_file_path = create_network_graph(graph_data)

        if html_file_path:
            # Leer el HTML generado por pyvis
            try:
                with open(html_file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Renderizar el HTML en Streamlit
                components.html(html_content, height=750, scrolling=True)
                
            except FileNotFoundError:
                st.error("❌ No se encontró el archivo de visualización.")
            finally:
                # Limpiar el archivo HTML temporal
                if os.path.exists(html_file_path):
                    os.remove(html_file_path)

        st.success("🎯 Diagrama interactivo listo!")
        st.info("""
        **💡 Cómo usar el diagrama:**
        • 🖱️ **Click en categorías** para expandir/colapsar detalles
        • 🔄 **Arrastra** los nodos para reorganizar 
        • 🔍 **Zoom** con la rueda del mouse
        • 📊 Los números **[X]** indican recursos en cada categoría
        • 🎨 **Colores** por estado: verde=activo, rojo=error, azul=corriendo
        
        **📁 Fuente:** Archivo cache local JSON
        """)
        
    elif st.session_state.get('graph_data') and not st.session_state['graph_data'].get('nodes'):
        st.warning("⚠️ No se encontraron recursos o hubo errores. Revisa los mensajes en el panel izquierdo.")
    else:
        # Mostrar placeholder informativo
        st.info("👈 **Selecciona una opción en el panel izquierdo para cargar datos**")
        
        # Mostrar archivos cache disponibles como referencia
        cache_files = get_available_cache_files()
        if cache_files:
            st.write("**📁 Archivos cache disponibles:**")
            for file_info in cache_files:
                st.write(f"• `{file_info['project_id']}` - {file_info['modified']}")
        else:
            st.write("**ℹ️ No hay archivos cache. Usa 'Descargar y Guardar' primero.**")
