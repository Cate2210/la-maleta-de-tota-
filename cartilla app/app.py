from io import BytesIO
import os
import pandas as pd
import streamlit as st

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="La Maleta de Tota: Plataforma Interactiva",
    page_icon="🎒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Contraseña privada para la Pestaña 7 de Análisis y Base de Datos
CLAVE_ANALISIS = "tota2026"

# Paleta de colores: Azul profundo del lago corporativo, fondo oscuro, tarjetas azules y texto blanco
PRIMARY_COLOR = "#135DB6"  # Azul profundo del lago oscuro
ACCENT_COLOR = "#4D9E95"  # Turquesa profesional
SIDEBAR_COLOR = "#122338"  # Azul oscuro elegante para la barra lateral
BG_COLOR = "#0B192C"  # Fondo general azul muy oscuro
CARD_COLOR = "#1E3E62"  # Azul medio para tarjetas y formularios
TEXT_LIGHT = "#FFFFFF"  # Texto blanco para máxima legibilidad

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BG_COLOR};
        color: {TEXT_LIGHT};
    }}
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, .streamlit-expanderHeader {{
        color: {TEXT_LIGHT} !important;
    }}
    .main-header {{
        background: linear-gradient(135deg, {PRIMARY_COLOR}, #1C3144);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        color: {TEXT_LIGHT} !important;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        border: 1px solid #314755;
    }}
    .main-header h1, .main-header h3, .main-header p {{
        color: {TEXT_LIGHT} !important;
    }}
    .form-box {{
        background-color: {CARD_COLOR};
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 1px solid #314755;
        margin-top: 1rem;
    }}
    .plato-card {{
        background-color: {CARD_COLOR};
        padding: 1.3rem;
        border-radius: 14px;
        border-left: 6px solid {ACCENT_COLOR};
        border-top: 1px solid #314755;
        border-right: 1px solid #314755;
        border-bottom: 1px solid #314755;
        box-shadow: 0 4px 10px rgba(0,0,0,0.25);
        margin-bottom: 1.2rem;
    }}
    .plato-badge {{
        display: inline-block;
        background-color: {PRIMARY_COLOR};
        color: {TEXT_LIGHT} !important;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-bottom: 0.6rem;
    }}
    .casilla-card {{
        background-color: {CARD_COLOR};
        padding: 1.3rem 1.5rem;
        border-radius: 14px;
        border-left: 6px solid {PRIMARY_COLOR};
        border-top: 1px solid #314755;
        border-right: 1px solid #314755;
        border-bottom: 1px solid #314755;
        box-shadow: 0 4px 10px rgba(0,0,0,0.25);
        margin-bottom: 1.4rem;
    }}
    section[data-testid="stSidebar"] {{
        background-color: {SIDEBAR_COLOR};
    }}
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown {{
        color: {TEXT_LIGHT} !important;
    }}
    .stButton>button {{
        background-color: {ACCENT_COLOR};
        color: {TEXT_LIGHT} !important;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        padding: 0.6rem 1.5rem;
        width: 100%;
    }}
    .stButton>button:hover {{
        background-color: {PRIMARY_COLOR};
        color: {TEXT_LIGHT} !important;
    }}
    input, select, textarea {{
        background-color: {BG_COLOR} !important;
        color: {TEXT_LIGHT} !important;
        border-color: #314755 !important;
    }}
    /* Estilo para agrandar los emojis de los objetos en la maleta */
    .emoji-item {{
        font-size: 2.2rem;
        text-align: center;
        margin: 0;
        padding: 0;
    }}
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# GESTIÓN DE BASE DE DATOS LOCAL Y CONSOLIDADO
# ==========================================
DB_FILE = "base_datos_tota.csv"
DB_COMPLETA_FILE = "base_datos_completa_tota.csv"


def cargar_base_datos():
  if not os.path.exists(DB_FILE):
    df_inicial = pd.DataFrame(columns=[
        "alias",
        "tipo_turista",
        "origen",
        "rango_edad",
        "genero",
        "compania",
        "fecha",
    ])
    df_inicial.to_csv(DB_FILE, index=False)
  return pd.read_csv(DB_FILE)


def guardar_checkin(registro):
  df = cargar_base_datos()
  df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
  df.to_csv(DB_FILE, index=False)


def cargar_db_completa():
  if not os.path.exists(DB_COMPLETA_FILE):
    return pd.DataFrame()
  return pd.read_csv(DB_COMPLETA_FILE)


def sincronizar_db_completa(actualizaciones):
  """Actualiza o crea la fila del viajero actual en base_datos_completa_tota.csv."""
  if "sesion_viajero_id" not in st.session_state:
    st.session_state.sesion_viajero_id = (
        f"{st.session_state.get('alias', 'viajero')}_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"
    )

  sid = st.session_state.sesion_viajero_id
  df = cargar_db_completa()
  if not df.empty:
    df = df.astype(object)

  fila_base = {
      "sesion_id": sid,
      "fecha_registro": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
      "alias": st.session_state.get("alias", ""),
      "tipo_turista": st.session_state.get("tipo_turista_guardado", ""),
      "origen": st.session_state.get("origen_guardado", ""),
      "rango_edad": st.session_state.get("rango_edad_guardado", ""),
      "genero": st.session_state.get("genero_guardado", ""),
      "compania": st.session_state.get("compania_guardado", ""),
      "perfil_m1": st.session_state.get("perfil_m1_guardado", ""),
      "maleta_completada": st.session_state.get("maleta_completada", False),
      "m1_vengo": st.session_state.get("m1_vengo", ""),
      "m1_espero": st.session_state.get("m1_espero", ""),
      "m1_dejar": st.session_state.get("m1_dejar", ""),
      "m2_menu": st.session_state.get("m2_menu_guardado", ""),
      "m2_cantidad_platos": st.session_state.get("m2_cant_platos", 0),
      "m2_me_llevo": st.session_state.get("m2_me_llevo", ""),
      "m2_compromiso_economia": st.session_state.get("m2_compromiso", ""),
      "m3_puntaje": st.session_state.get("m3_puntaje_guardado", 0),
      "m3_casilla": st.session_state.get("m3_casilla_guardado", 1),
      "m3_no_use": st.session_state.get("m3_no_use", ""),
      "m3_evitable": st.session_state.get("m3_evitable", ""),
      "m3_habito_cambiar": st.session_state.get("m3_habito", ""),
      "m4_dias": st.session_state.get("m4_dias_guardados", 0),
      "m4_pct_local_estrella": st.session_state.get("m4_pct_local", 0),
      "m4_recuerdo": st.session_state.get("m4_recuerdo", ""),
      "m4_quien_hizo": st.session_state.get("m4_quien", ""),
      "m4_oficio": st.session_state.get("m4_oficio", ""),
      "m4_cuidado_recuerdo": st.session_state.get("m4_cuidado", ""),
      "m4_agradecimiento": st.session_state.get("m4_agradecimiento", ""),
      "m4_gasto_dejo": st.session_state.get("m4_gasto_dejo", ""),
      "m4_proxima_vez": st.session_state.get("m4_proxima", ""),
      "nombre_certificado": st.session_state.get("nombre_cert_guardado", ""),
      "sello_cedazo": st.session_state.get("sello_cedazo", False),
      "sello_gota": st.session_state.get("sello_gota", False),
      "sello_dinero": st.session_state.get("sello_dinero", False),
  }
  fila_base.update(actualizaciones)

  if not df.empty and "sesion_id" in df.columns and sid in df["sesion_id"].values:
    idx = df.index[df["sesion_id"] == sid][0]
    for col, val in fila_base.items():
      if col not in df.columns:
        df[col] = pd.Series(dtype=object)
      df.at[idx, col] = val
  else:
    df = pd.concat([df, pd.DataFrame([fila_base])], ignore_index=True)

  df.to_csv(DB_COMPLETA_FILE, index=False)


# Inicializar variables de estado
if "registrado" not in st.session_state:
  st.session_state.registrado = False
if "alias" not in st.session_state:
  st.session_state.alias = ""
if "trucha_m1" not in st.session_state:
  st.session_state.trucha_m1 = False
if "maleta_completada" not in st.session_state:
  st.session_state.maleta_completada = False
if "trucha_m2" not in st.session_state:
  st.session_state.trucha_m2 = False
if "sello_cedazo" not in st.session_state:
  st.session_state.sello_cedazo = False
if "sello_gota" not in st.session_state:
  st.session_state.sello_gota = False
if "sello_dinero" not in st.session_state:
  st.session_state.sello_dinero = False
if "analisis_autenticado" not in st.session_state:
  st.session_state.analisis_autenticado = False

# ==========================================
# BARRA LATERAL (PASAPORTE DE TOTA Y NAVEGACIÓN)
# ==========================================
with st.sidebar:
  st.title("Pasaporte de Tota")
  st.markdown("---")
  if st.session_state.registrado:
    st.markdown(f"**Viajero:** {st.session_state.alias}")
    estado_truchas = (
        "Trucha M1 Conquistada 🐟"
        if st.session_state.trucha_m1
        else "Pendiente M1 🐟"
    )
    st.markdown(f"**Progreso:** {estado_truchas}")
    if st.session_state.trucha_m2:
      st.markdown("**Módulo 2:** Trucha M2 Conquistada 🐟")
    if st.session_state.sello_cedazo:
      st.markdown("**Insignia:** Sello 6: Cedazo")
    if st.session_state.sello_gota:
      st.markdown("**Insignia:** Sello 7: Gota de agua")
    if st.session_state.sello_dinero:
      st.markdown("**Insignia:** Sello 10: Dinero")
  else:
    st.markdown("**Aviso:** Realiza tu registro en la opcion de Inicio")
  st.markdown("---")
  st.markdown("### Seleccion de Modulos")

  menu_opcion = st.radio(
      "Navegacion", [
          "1. Registro",
          "2. Modulo 1",
          "3. Modulo 2",
          "4. Modulo 3",
          "5. Modulo 4",
          "6. Recompensa",
          "7. Análisis y Base de Datos",
      ],
      label_visibility="collapsed",
  )

  st.markdown("---")
  st.caption("Cartilla Turistica Sostenible • Municipio de Tota, Boyacá")

# ==========================================
# ENCABEZADO PRINCIPAL
# ==========================================
st.markdown(
    """
    <div class="main-header">
        <h1>La Maleta de Tota</h1>
        <h3 style="margin-top: 0.5rem; font-weight: 400;">Plataforma Interactiva de Juegos</h3>
        <p style="margin-top: 1rem; font-size: 1.1rem; opacity: 0.95;">Bienvenidos a la experiencia digital. Inicia tu recorrido virtual y pon a prueba tus decisiones de turismo consciente.</p>
    </div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# LÓGICA DE VISTAS SEGÚN EL PANEL LATERAL
# ==========================================

if menu_opcion == "1. Registro":
  st.header("Registro de Viajero")
  st.write(
      "Esta aplicacion interactiva complementa tu cartilla fisica mediante"
      " juegos y desafios dinamicos. Activa tu pasaporte para comenzar."
  )

  st.markdown("---")
  st.markdown("### Activa tu Pasaporte de Viajero")

  tipo_turista = st.radio(
      "Origen", ["Turista Nacional", "Turista Extranjero"], key="tipo_turista_radio"
  )

  origen_valor = ""
  if tipo_turista == "Turista Nacional":
    departamentos_colombia = [
        "Amazonas",
        "Antioquia",
        "Arauca",
        "Atlántico",
        "Bolívar",
        "Boyacá",
        "Caldas",
        "Caquetá",
        "Casanare",
        "Cauca",
        "Cesar",
        "Chocó",
        "Córdoba",
        "Cundinamarca",
        "Guainía",
        "Guaviare",
        "Huila",
        "La Guajira",
        "Magdalena",
        "Meta",
        "Nariño",
        "Norte de Santander",
        "Putumayo",
        "Quindío",
        "Risaralda",
        "San Andrés y Providencia",
        "Santander",
        "Sucre",
        "Tolima",
        "Valle del Cauca",
        "Vaupés",
        "Vichada",
        "Bogotá D.C.",
    ]
    origen_valor = st.selectbox(
        "Selecciona tu Departamento de origen", departamentos_colombia
    )
  else:
    origen_valor = st.text_input(
        "Escribe tu País de origen",
        placeholder="Ej. España, Mexico, Estados Unidos...",
    )

  with st.form("form_registro_viajero"):
    st.markdown("#### Quién eres")

    alias_in = st.text_input(
        "Alias o Nombre de Viajero *", placeholder="Ej. CaminanteDelLago"
    )
    rango_edad = st.selectbox(
        "Rango de Edad", [
            "18 - 25 años",
            "26 - 35 años",
            "36 - 50 años",
            "Más de 50 años",
        ]
    )
    genero_in = st.selectbox(
        "Género", ["Femenino", "Masculino", "No binario", "Prefiero no decirlo"]
    )

    compania_in = st.selectbox(
        "¿Con quién viajas?",
        [
            "Con amigos",
            "En familia",
            "En pareja",
            "De parte del trabajo",
        ],
    )

    st.markdown("<br>", unsafe_allow_html=True)
    btn_check = st.form_submit_button("Guardar mi Pasaporte y Activar Viaje")

    if btn_check:
      if not alias_in.strip():
        st.error("Por favor ingresa un Alias o nombre de viajero válido.")
      elif tipo_turista == "Turista Extranjero" and not origen_valor.strip():
        st.error("Por favor escribe tu país de origen.")
      else:
        st.session_state.alias = alias_in.strip()
        st.session_state.registrado = True
        st.session_state.tipo_turista_guardado = tipo_turista
        st.session_state.origen_guardado = origen_valor
        st.session_state.rango_edad_guardado = rango_edad
        st.session_state.genero_guardado = genero_in
        st.session_state.compania_guardado = compania_in
        st.session_state.sesion_viajero_id = (
            f"{alias_in.strip()}_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"
        )

        nuevo_registro = {
            "alias": alias_in.strip(),
            "tipo_turista": tipo_turista,
            "origen": origen_valor,
            "rango_edad": rango_edad,
            "genero": genero_in,
            "compania": compania_in,
            "fecha": pd.Timestamp.now().strftime("%Y-%m-%d"),
        }
        guardar_checkin(nuevo_registro)
        sincronizar_db_completa({
            "alias": alias_in.strip(),
            "tipo_turista": tipo_turista,
            "origen": origen_valor,
            "rango_edad": rango_edad,
            "genero": genero_in,
            "compania": compania_in,
        })
        st.success(
            "Pasaporte activado con éxito. Ya puedes navegar por los módulos"
            " desde el panel lateral."
        )

# ==========================================
# MÓDULO 1: JUEGO 1 Y JUEGO 2 (MALETA DIGITAL)
# ==========================================
elif menu_opcion == "2. Modulo 1":
  if not st.session_state.get("registrado", False):
    st.warning(
        "Aún no has activado tu pasaporte. Por favor ve a la opción '1."
        " Registro' en el panel lateral para registrarte antes de ingresar al"
        " módulo."
    )
  else:
    st.header(
        "Módulo 1 · Cierro la maleta con propósito y preparo mi viaje a Tota"
    )
    st.write(
        f"Hola, {st.session_state.alias}. Este módulo consta de dos desafíos"
        " interactivos para calibrar tu espíritu viajero y armar tu equipaje"
        " responsable."
    )
    st.markdown("---")

    # Pestañas internas para los dos juegos del Módulo 1
    sub_juego1, sub_juego2 = st.tabs([
        "🎮 Desafío 1: ¿Qué tipo de turista eres?",
        "🎒 Desafío 2: La Maleta Digital",
    ])

    # ------------------------------------------
    # JUEGO 1: TEST DE PERFIL DE TURISTA
    # ------------------------------------------
    with sub_juego1:
      st.subheader("Ven y descubre qué tipo de turista eres")
      st.write(
          "Responde las siguientes 12 preguntas para revelar tu arquetipo de"
          " viaje en Tota."
      )

      with st.form("form_test_perfil"):
        st.markdown(
            "**1. Al llegar a la plaza principal de Tota o a su entorno natural,"
            " tu primer instinto es:**"
        )
        p1 = st.radio(
            "1",
            [
                "A) Buscar un rincón solitario para contemplar la montaña y el"
                " silencio.",
                "B) Preguntar por los amasijos tradicionales, la sopa de mute"
                " o la trucha.",
                "C) Recorrer el templo doctrinero colonial y conocer la"
                " historia local.",
                "D) Preparar el equipo para recorrer los senderos veredales.",
            ],
            label_visibility="collapsed",
        )

        st.markdown(
            "**2. ¿Qué te drena más la energía durante un viaje a un municipio"
            " patrimonial y natural?**"
        )
        p2 = st.radio(
            "2",
            [
                "A) El ruido excesivo y las multitudes en los espacios abiertos.",
                "B) La comida industrial o los lugares que no ofrecen identidad"
                " local.",
                "C) La indiferencia ante la historia, las artesanías y las"
                " tradiciones.",
                "D) Estar sin hacer nada o sin planes de exploración activa.",
            ],
            label_visibility="collapsed",
        )

        st.markdown(
            "**3. Para combatir el frío típico de la alta montaña de Tota, tu"
            " bebida ideal es:**"
        )
        p3 = st.radio(
            "3",
            [
                "A) Un té o infusión caliente mientras observo el paisaje desde"
                " el alojamiento.",
                "B) Una aguapanela caliente con queso campesino bien cargada.",
                "C) Un canelazo o bebida tradicional conversando con los abuelos"
                " del pueblo.",
                "D) Algo rápido y energético para calentar el cuerpo antes de la"
                " caminata.",
            ],
            label_visibility="collapsed",
        )

        st.markdown(
            "**4. Si compras un recuerdo o detalle en Tota, prefieres que sea:**"
        )
        p4 = st.radio(
            "4",
            [
                "A) Ninguno; mi mejor recuerdo se queda en la memoria y en la"
                " contemplación.",
                "B) Unos cubios, papas nativas, amasijos o productos de la"
                " despensa local.",
                "C) Una artesanía tradicional representativa como un producto"
                " de lana o cedazo.",
                "D) Un accesorio útil o práctico para mis próximas travesías al"
                " aire libre.",
            ],
            label_visibility="collapsed",
        )

        st.markdown(
            "**5. ¿Cómo te imaginas tu atardecer perfecto en el territorio de"
            " Tota?**"
        )
        p5 = st.radio(
            "5",
            [
                "A) Sentado contemplando el paisaje y la calma de la alta"
                " montaña.",
                "B) Disfrutando una cena con platos típicos andinos junto a una"
                " chimenea.",
                "C) Escuchando los mitos y leyendas locales contados por los"
                " pobladores.",
                "D) Terminando un recorrido largo en bicicleta o caminata por"
                " los cerros.",
            ],
            label_visibility="collapsed",
        )

        st.markdown(
            "**6. Al elegir un lugar para hospedarte en la región, buscas"
            " principalmente:**"
        )
        p6 = st.radio(
            "6",
            [
                "A) Un refugio rústico, aislado y rodeado de absoluta calma y"
                " naturaleza.",
                "B) Una posada tradicional o estancia cerca de fondas de"
                " comida casera.",
                "C) Una arquitectura colonial que conecte con la historia del"
                " municipio.",
                "D) Un punto estratégico y cómodo para arrancar temprano las"
                " rutas de trekking.",
            ],
            label_visibility="collapsed",
        )

        st.markdown(
            "**7. Si encuentras un camino rural o sendero de herencia ancestral,"
            " tú:**"
        )
        p7 = st.radio(
            "7",
            [
                "A) Lo recorro despacio, cuidando cada pisada para no alterar"
                " el entorno natural.",
                "B) Indago si por allí hay alguna huerta, cultivo o puesto de"
                " productos locales.",
                "C) Me pregunto qué historias y caminos usaban los antiguos"
                " pobladores.",
                "D) Me emociona recorrerlo completo y medir mi resistencia"
                " física.",
            ],
            label_visibility="collapsed",
        )

        st.markdown(
            "**8. ¿Qué significa para ti 'viajar con propósito' en un"
            " municipio como Tota?**"
        )
        p8 = st.radio(
            "8",
            [
                "A) Sanar el espíritu conectando con la inmensidad del paisaje"
                " de páramo.",
                "B) Valorar el trabajo del campesino apoyando la economía de"
                " su plaza de mercado.",
                "C) Honrar el patrimonio, la memoria colectiva y las costumbres"
                " del pueblo.",
                "D) Retarse a uno mismo explorando los senderos de forma"
                " responsable y activa.",
            ],
            label_visibility="collapsed",
        )

        st.markdown(
            "**9. ¿Qué tipo de contenido prefieres capturar en tus fotos o"
            " recuerdos visuales?**"
        )
        p9 = st.radio(
            "9",
            [
                "A) Paisajes amplios, frailejones, aves y texturas de la alta"
                " montaña.",
                "B) Platos típicos, mercados campesinos y productos de la"
                " tierra.",
                "C) La fachada de la iglesia colonial, monumentos y detalles"
                " artesanales.",
                "D) Fotos en movimiento, cimas, caminos y paisajes de aventura.",
            ],
            label_visibility="collapsed",
        )

        st.markdown(
            "**10. Ante un cambio imprevisto de clima (viento fuerte o llovizna"
            " helada en el páramo), tú:**"
        )
        p10 = st.radio(
            "10",
            [
                "A) Lo disfruto; le da un toque místico y melancólico al"
                " paisaje andino.",
                "B) Busco un restaurante o tienda tradicional a comer algo"
                " caliente y reconfortante.",
                "C) Pienso en cómo las comunidades locales han convivido con"
                " este clima por generaciones.",
                "D) Saco mi equipo impermeable y continúo el recorrido con"
                " energía.",
            ],
            label_visibility="collapsed",
        )

        st.markdown("**11. ¿Qué valoras más de los habitantes de Tota?**")
        p11 = st.radio(
            "11",
            [
                "A) Su tranquilidad y la sabiduría que transmite la vida rural.",
                "B) Su sazón y la generosidad al compartir su cocina"
                " tradicional.",
                "C) Su sentido de pertenencia, su memoria oral y sus oficios"
                " tradicionales.",
                "D) Su disposición para dar indicaciones sobre rutas y caminos"
                " rurales.",
            ],
            label_visibility="collapsed",
        )

        st.markdown(
            "**12. ¿Qué palabra define mejor tu estado de ánimo ideal al viajar"
            " por Tota?**"
        )
        p12 = st.radio(
            "12",
            ["A) Paz.", "B) Sabor.", "C) Identidad.", "D) Aventura."],
            label_visibility="collapsed",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        btn_resultado = st.form_submit_button(
            "Descubrir mi Perfil de Viajero y Ganar mi Trucha"
        )

        if btn_resultado:
          respuestas = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12]
          conteo = {"A": 0, "B": 0, "C": 0, "D": 0}

          for r in respuestas:
            letra = r.split(")")[0].strip()
            if letra in conteo:
              conteo[letra] += 1

          conteo_ordenado = sorted(
              conteo.items(), key=lambda item: item[1], reverse=True
          )
          primer_lugar, primer_puntaje = conteo_ordenado[0]
          segundo_lugar, segundo_puntaje = conteo_ordenado[1]

          st.session_state.trucha_m1 = True

          st.markdown("---")
          st.markdown(
              f"### ¡Felicidades, {st.session_state.alias}! 🐟 Has obtenido tu"
              " primera trucha dorada."
          )

          nombres_perfiles = {
              "A": (
                  "Contemplativo del Lago y la Naturaleza 🌿",
                  (
                      "Te mueve la introversión regenerativa, el silencio y el"
                      " respeto profundo por la calma del páramo."
                  ),
              ),
              "B": (
                  "Explorador de Sabores 🥔",
                  (
                      "Te mueve la estimulación sensorial, la curiosidad"
                      " gastronómica y el apoyo directo a la economía"
                      " campesina."
                  ),
              ),
              "C": (
                  "Guardián Cultural y Ancestral 🧶",
                  (
                      "Te mueve el amor por la historia, los mitos muiscas, la"
                      " arquitectura colonial y los oficios artesanales."
                  ),
              ),
              "D": (
                  "Aventurero del Páramo y Senderos 🥾",
                  (
                      "Te mueve la exploración activa, el reto físico y el"
                      " descubrimiento de rutas y caminos en la alta montaña."
                  ),
              ),
          }

          if primer_puntaje == segundo_puntaje:
            p1_nombre, p1_desc = nombres_perfiles[primer_lugar]
            p2_nombre, p2_desc = nombres_perfiles[segundo_lugar]
            perfil_texto = f"Mixto: {p1_nombre} y {p2_nombre}"

            st.markdown(
                "#### Según tus resultados, tienes una maravillosa mezcla"
                f" entre: **{p1_nombre}** y **{p2_nombre}**."
            )
            st.write(f"• **Sobre tu primer enfoque:** {p1_desc}")
            st.write(f"• **Sobre tu segundo enfoque:** {p2_desc}")
            st.markdown(
                "¡Qué gran combinación! Tienes lo mejor de dos mundos para"
                " disfrutar este territorio."
            )
          else:
            nombre_p, desc_p = nombres_perfiles[primer_lugar]
            perfil_texto = nombre_p
            st.markdown(f"#### Según tus resultados, tú eres: **{nombre_p}**")
            st.write(desc_p)

          st.session_state.perfil_m1_guardado = perfil_texto
          sincronizar_db_completa({"perfil_m1": perfil_texto})

          st.markdown(
              "Sigue disfrutando de esos paisajes maravillosos y de la riqueza"
              " cultural del municipio. Sigue teniendo buenas acciones,"
              " cuidando el entorno y respetando a la comunidad para poder"
              " seguir disfrutando de estas experiencias por mucho tiempo"
              " más."
          )

    # ------------------------------------------
    # JUEGO 2: LA MALETA DIGITAL (CON TRES ZONAS Y EMOJIS GRANDES)
    # ------------------------------------------
    with sub_juego2:
      st.subheader("Desafío 2: La Maleta Digital con Propósito")
      st.write(
          "Para un destino de alta montaña y clima frío como Tota, cada objeto"
          " cuenta. Clasifica los 12 elementos en las tres zonas"
          " según tu criterio de viajero responsable y escribe tu compromiso"
          " personal."
      )
      st.markdown("---")

      objetos_maleta = {
          "Termo para agua": "🥤",
          "Bolsa de tela para residuos": "🛍️",
          "Ruana artesanal de lana": "🧥",
          "Impermeable": "🧥",
          "Protector solar": "🧴",
          "Zapatos cerrados de trekking": "🥾",
          "Parlante con volumen alto": "🔊",
          "Vajilla plástica desechable": "🍽️",
          "Cámara fotográfica": "📷",
          "Mapa del municipio": "🗺️",
          "Efectivo en moneda local": "💵",
          "Libreta de campo": "📓",
      }

      with st.form("form_maleta_digital"):
        st.markdown(
            "#### Clasifica cada objeto en una de las tres zonas de la maleta:"
        )

        clasificacion_usuario = {}
        cols_obj = st.columns(2)
        i = 0
        for obj, emoji in objetos_maleta.items():
          with cols_obj[i % 2]:
            st.markdown(f"<p class='emoji-item'>{emoji}</p>", unsafe_allow_html=True)
            clasificacion_usuario[obj] = st.selectbox(
                f"¿Qué haces con: {obj}?",
                [
                    "Selecciona una zona...",
                    "Lo necesito",
                    "Lo cuido o lo uso con respeto",
                    "Lo dejo en casa",
                ],
                key=f"sel_{obj}",
            )
          i += 1

        st.markdown("---")
        st.markdown("#### Tarjeta de Compromiso con el Territorio")
        compromiso_vengo = st.text_input(
            "Vengo a... (Ej. aprender de la cultura y desconectarme sin hacer ruido)"
        )
        compromiso_espero = st.text_input(
            "Espero encontrar... (Ej. paisajes limpios, gastronomía local y calma)"
        )
        compromiso_dejar = st.text_input(
            "Me comprometo a dejar... (Ej. cero residuos y respeto por los habitantes)"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        btn_maleta = st.form_submit_button(
            "Cerrar mi Maleta Digital con Propósito"
        )

        if btn_maleta:
          sin_clasificar = [
              k
              for k, v in clasificacion_usuario.items()
              if v == "Selecciona una zona..."
          ]
          if sin_clasificar:
            st.error(
                "Por favor clasifica todos los 12 objetos en alguna de las tres"
                " zonas antes de cerrar tu maleta."
            )
          elif (
              not compromiso_vengo
              or not compromiso_espero
              or not compromiso_dejar
          ):
            st.error(
                "Por favor completa las tres líneas de tu tarjeta de"
                " compromiso."
            )
          else:
            st.session_state.maleta_completada = True
            st.session_state.clasificacion_maleta = clasificacion_usuario
            st.session_state.m1_vengo = compromiso_vengo.strip()
            st.session_state.m1_espero = compromiso_espero.strip()
            st.session_state.m1_dejar = compromiso_dejar.strip()
            sincronizar_db_completa({
                "maleta_completada": True,
                "m1_vengo": compromiso_vengo.strip(),
                "m1_espero": compromiso_espero.strip(),
                "m1_dejar": compromiso_dejar.strip(),
            })
            st.success(
                f"¡Excelente trabajo, {st.session_state.alias}! Has cerrado"
                " tu maleta digital de manera consciente."
            )
            st.markdown(
                "**Tu reflexión:** Mi equipaje refleja una intención de viaje"
                " consciente porque demuestra que el verdadero viajero no"
                " transporta peso innecesario, sino respeto y cuidado por el"
                f" territorio de Tota. ¡Has completado con éxito el Módulo 1!"
            )

# ==========================================
# MÓDULO 2: ARMA TU MENÚ DEL DÍA O DEL VIAJE
# ==========================================
elif menu_opcion == "3. Modulo 2":
  if not st.session_state.get("registrado", False):
    st.warning(
        "Aún no has activado tu pasaporte. Por favor ve a la opción '1."
        " Registro' en el panel lateral para registrarte antes de ingresar al"
        " módulo."
    )
  else:
    st.markdown("# Arma tu Menú del Día o del Viaje")
    st.write(
        f"¡Bienvenido a la parte gastronómica, {st.session_state.alias}! Aquí"
        " se come rico: escoge tu menú para que disfrutes de la gastronomía"
        " que ofrece el lugar y conozcas las historias que hay detrás de cada"
        " sabor."
    )
    st.markdown("---")

    catalogo_platos = {
        "Caldo de costilla": {
            "imagen": "imagenes_platos/caldo_costilla.jpg",
            "historia": (
                "Nació en las cocinas rurales andinas como la comida esencial"
                " para iniciar las jornadas agrícolas antes del amanecer, en"
                " medio de las bajas temperaturas de la alta montaña."
            ),
            "quienes": (
                "Familias ganaderas de las veredas de Tota y agricultores de"
                " papa sabanera y cilantro de huerta."
            ),
            "dato_curioso": (
                "La papa que se usa se corta en trozos firmes para que absorba"
                " el sabor de la costilla sin deshacerse y le dé cuerpo al"
                " caldo."
            ),
            "significado": (
                "Representa el abrigo, la fuerza del trabajo en el campo y el"
                " punto de encuentro temprano en las fondas del parque."
            ),
            "consumo_consciente": (
                "Búscalo en fondas y desayunaderos tradicionales cerca de la"
                " plaza principal o en caminos veredales, principalmente en las"
                " mañanas (6:30 a. m. a 10:00 a. m.). Recomendación: pide en"
                " loza y apoya a los comedores locales."
            ),
        },
        "Changua boyacense": {
            "imagen": "imagenes_platos/changua.jpg",
            "historia": (
                "Receta ancestral muisca adaptada tras la llegada de la"
                " ganadería lechera al altiplano cundiboyacense."
            ),
            "quienes": (
                "Pequeños productores lecheros de las veredas de Tota y"
                " panaderos artesanales que hornean los calados."
            ),
            "dato_curioso": (
                "El secreto de su sabor está en que la leche nunca debe hervir a"
                " borbotones después de agregar el huevo, para que la yema"
                " quede entera y cremosa."
            ),
            "significado": (
                "Simboliza la sencillez y la generosidad de la despensa rural:"
                " con pocos ingredientes frescos se logra un alimento completo."
            ),
            "consumo_consciente": (
                "Se consigue en desayunaderos familiares y tiendas de vereda"
                " en las horas de la mañana (6:30 a. m. a 10:00 a. m.)."
                " Recomendación: acompáñala con pan o calado recién horneado"
                " en el pueblo."
            ),
        },
        "Trucha arcoíris": {
            "imagen": "imagenes_platos/trucha.jpg",
            "historia": (
                "Introducida en el siglo XX en las aguas frías del altiplano,"
                " se convirtió rápidamente en el plato más reconocido por los"
                " visitantes de la cuenca del Lago de Tota."
            ),
            "quienes": (
                "Familias piscicultoras ribereñas de Tota y Aquitania, junto a"
                " cocineras tradicionales de la región."
            ),
            "dato_curioso": (
                "Aunque es el emblema gastronómico y económico del destino, no"
                " es una especie nativa del lago; su crianza requiere buenas"
                " prácticas para proteger la calidad del agua."
            ),
            "significado": (
                "Es el motor económico de decenas de hogares locales y el plato"
                " insignia con el que se recibe a los viajeros."
            ),
            "consumo_consciente": (
                "Disponible en restaurantes y comedores de la zona y vía al"
                " lago, especialmente al mediodía y en la tarde (11:30 a. m."
                " a 5:00 p. m.). Recomendación: evita pedir para llevar en"
                " icopor."
            ),
        },
        "Sopa de mute boyacense": {
            "imagen": "imagenes_platos/mute.jpg",
            "historia": (
                "Heredera de los grandes cocidos comunitarios indígenas y"
                " mestizos, donde se reunían distintos granos de la cosecha en"
                " una sola olla de barro."
            ),
            "quienes": (
                "Cultivadores de maíz pelado, fríjol, garbanzo y habas de las"
                " veredas La Puerta y Tota Centro."
            ),
            "dato_curioso": (
                "El maíz blanco se cocina previamente con ceniza de leña o cal"
                " para quitarle la cáscara y lograr esa textura tierna"
                " característica."
            ),
            "significado": (
                "Para Boyacá y Tota es sinónimo de fiesta grande, reunión"
                " familiar y celebración del Aguinaldo Totense en diciembre."
            ),
            "consumo_consciente": (
                "Encuéntrala en cocinas tradicionales y puestos de comida"
                " típica en horario de almuerzo (12:00 m. a 3:30 p. m.)."
                " Recomendación: disfrútala con calma en el lugar para evitar"
                " desechables."
            ),
        },
        "Cocido con tubérculos andinos": {
            "imagen": "imagenes_platos/cocido.jpg",
            "historia": (
                "Es uno de los platos más antiguos de los Andes; conserva los"
                " tubérculos que alimentaron a los pueblos originarios mucho"
                " antes de la conquista."
            ),
            "quienes": (
                "Agricultores guardianes de semillas nativas en las veredas"
                " altas de páramo como Ranchería y La Puerta."
            ),
            "dato_curioso": (
                "Los cubios, hibias y rubas que lleva este plato solo crecen en"
                " suelos fríos de alta montaña y cada variedad aporta un toque"
                " entre dulce, terroso y ligeramente picante."
            ),
            "significado": (
                "Representa la resistencia cultural y la soberanía alimentaria"
                " del campesinado boyacense."
            ),
            "consumo_consciente": (
                "Suele ofrecerse en comedores de cocina típica al mediodía"
                " (12:00 m. a 3:00 p. m.) o por encargo local. Recomendación:"
                " prueba cada tubérculo para valorar las semillas nativas."
            ),
        },
        "Cuchuco de trigo con espinazo": {
            "imagen": "imagenes_platos/cuchuco.jpg",
            "historia": (
                "Surgió en las zonas trigueras de Boyacá como aprovechamiento"
                " del grano partido en molinos de piedra tradicionales."
            ),
            "quienes": (
                "Campesinos cultivadores de trigo, cebada y arveja en las"
                " laderas agrícolas de Tota."
            ),
            "dato_curioso": (
                "Se suele consumir con mayor frecuencia en días fríos y lluviosos"
                " de cosecha, acompañado de hojas frescas de tallos o repollo"
                " picado."
            ),
            "significado": (
                "Evoca el ciclo agrícola de la siembra, la siega y la trilla"
                " compartida entre vecinos de vereda."
            ),
            "consumo_consciente": (
                "Disponible en fondas y comedores de comida casera en"
                " horario de almuerzo (12:00 m. a 3:30 p. m.). Recomendación:"
                " pregunta qué días preparan olla recién hecha."
            ),
        },
        "Arepa boyacense": {
            "imagen": "imagenes_platos/arepa_boyacense.jpg",
            "historia": (
                "Combina el maíz ancestral con la cuajada fresca y la panela,"
                " horneada tradicionalmente en tiestos de barro u hornos de"
                " leña."
            ),
            "quienes": (
                "Amasanderas tradicionales de la vereda El Guáimaro y el casco"
                " urbano de Tota."
            ),
            "dato_curioso": (
                "A diferencia de otras arepas del país, lleva un relleno interno"
                " de cuajada campesina molida con panela que se carameliza al"
                " dorarse."
            ),
            "significado": (
                "Es el bocado emblemático de Boyacá para dar la bienvenida a"
                " cualquier visitante en la carretera o en el hogar."
            ),
            "consumo_consciente": (
                "Se consigue en puestos callejeros, panaderías y puntos cerca"
                " de la plaza o vías de acceso desde la mañana hasta la tarde"
                " (8:00 a. m. a 6:00 p. m.). Recomendación: llévala en bolsa"
                " de tela o papel."
            ),
        },
        "Amasijos tradicionales (almojábanas y garullas)": {
            "imagen": "imagenes_platos/amasijos.jpg",
            "historia": (
                "Tradición panadera campesina que perfeccionó el uso del queso"
                " fresco recién cuajado mezclado con harina de maíz."
            ),
            "quienes": (
                "Familias horneras y talleres artesanales de amasijos en Tota."
            ),
            "dato_curioso": (
                "Su textura esponjosa depende de que la cuajada sea fresca del"
                " mismo día y no tenga exceso de suero."
            ),
            "significado": (
                "Protagonistas de las onces familiares y de las meriendas"
                " durante el Festival del Cedazo en junio."
            ),
            "consumo_consciente": (
                "Ideales en panaderías artesanales y puestos locales en la"
                " tarde (3:00 p. m. a 6:30 p. m.). Recomendación: compra en"
                " hornos locales y evita empaques plásticos innecesarios."
            ),
        },
        "Envueltos de mazorca": {
            "imagen": "imagenes_platos/envueltos.jpg",
            "historia": (
                "Técnica precolombina de cocción al vapor utilizando las"
                " propias hojas de la mazorca como envoltorio natural."
            ),
            "quienes": (
                "Mujeres rurales y asociaciones de productores maiceros de Tota."
            ),
            "dato_curioso": (
                "El amero (hoja del maíz) no solo protege la masa durante la"
                " cocción, sino que le transfiere un aroma dulce e"
                " inconfundible."
            ),
            "significado": (
                "Demuestra la sabiduría sostenible de la cocina campesina: cero"
                " plásticos y cero desperdicios."
            ),
            "consumo_consciente": (
                "Se encuentran en puestos tradicionales cerca de la plaza o"
                " puntos de venta local en la tarde (2:30 p. m. a 6:30 p. m.)."
                " Recomendación: deposita la hoja de maíz en residuos"
                " orgánicos."
            ),
        },
        "Postre de cuajada con melao": {
            "imagen": "imagenes_platos/cuajada_melao.jpg",
            "historia": (
                "Postre clásico de las haciendas y fincas lecheras boyacenses,"
                " nacido del encuentro entre la leche fresca y la miel de caña."
            ),
            "quienes": (
                "Queserías familiares locales y productores de panela artesanal"
                " de la región."
            ),
            "dato_curioso": (
                "El melao se cocina lentamente con astillas de canela y clavos"
                " de olor hasta lograr un punto de hilo brillante que contrasta"
                " con lo salado de la cuajada."
            ),
            "significado": (
                "Es el cierre festivo de los almuerzos familiares en días de"
                " celebración patronal en agosto y diciembre."
            ),
            "consumo_consciente": (
                "Disponible en comedores típicos y tiendas de productos lácteos"
                " de la tarde (1:00 p. m. a 6:00 p. m.). Recomendación:"
                " consúmelo en loza o recipiente reutilizable."
            ),
        },
        "Aguapanela caliente con queso": {
            "imagen": "imagenes_platos/aguapanela_queso.jpg",
            "historia": (
                "Compañera histórica de caminantes, arrieros y campesinos para"
                " recuperar calor y energía en las tardes heladas del páramo."
            ),
            "quienes": (
                "Productores de queso campesino de las veredas lecheras de Tota"
                " y tiendas veredales."
            ),
            "dato_curioso": (
                "La costumbre local consiste en sumergir trozos de queso"
                " campesino dentro de la taza caliente para comerlo blando con"
                " cuchara al final."
            ),
            "significado": (
                "Es el máximo símbolo de hospitalidad en Tota: ofrecer una"
                " aguapanela caliente es abrir las puertas de la casa."
            ),
            "consumo_consciente": (
                "Se consigue en tiendas, cafeterías y puestos de vereda o"
                " cerca de la plaza, especialmente al caer la tarde"
                " (4:00 p. m. a 8:00 p. m.). Recomendación: lleva tu termo si"
                " vas a caminar en el frío."
            ),
        },
        "Sorbete de curuba o feijoa": {
            "imagen": "imagenes_platos/sorbete_curuba.jpg",
            "historia": (
                "Bebida refrescante elaborada con frutas de tierra fría que"
                " crecen de forma natural en los cercos y huertas boyacenses."
            ),
            "quienes": (
                "Huertas familiares y pequeños cultivadores de frutales andinos"
                " de Tota."
            ),
            "dato_curioso": (
                "La curuba y la feijoa son ricas en antioxidantes y su aroma"
                " intenso permite preparar bebidas cremosas sin necesidad de"
                " saborizantes artificiales."
            ),
            "significado": (
                "Conecta la mesa con la biodiversidad de las huertas campesinas"
                " de alta montaña."
            ),
            "consumo_consciente": (
                "Disponible en restaurantes y juguerías locales durante el día"
                " (10:00 a. m. a 5:00 p. m.). Recomendación: pide sin pitillo"
                " plástico y prefiere fruta local."
            ),
        },
    }

    st.subheader("Arma tu carta favorita del día")

    col_m1, col_m2 = st.columns(2)

    with col_m1:
      sel_desayuno = st.selectbox(
          "🍳 Desayuno",
          [
              "Ninguno por ahora",
              "Caldo de costilla",
              "Changua boyacense",
              "Arepa boyacense",
          ],
          key="menu_desayuno",
      )
      sel_almuerzo = st.selectbox(
          "🍲 Almuerzo",
          [
              "Ninguno por ahora",
              "Trucha arcoíris",
              "Sopa de mute boyacense",
              "Cocido con tubérculos andinos",
              "Cuchuco de trigo con espinazo",
          ],
          key="menu_almuerzo",
      )
      sel_onces = st.selectbox(
          "🥐 Onces",
          [
              "Ninguno por ahora",
              "Amasijos tradicionales (almojábanas y garullas)",
              "Arepa boyacense",
              "Envueltos de mazorca",
          ],
          key="menu_onces",
      )
      sel_cena = st.selectbox(
          "🌙 Cena",
          [
              "Ninguno por ahora",
              "Caldo de costilla",
              "Sopa de mute boyacense",
              "Trucha arcoíris",
              "Changua boyacense",
          ],
          key="menu_cena",
      )

    with col_m2:
      sel_postre = st.selectbox(
          "🍮 Postre",
          [
              "Ninguno por ahora",
              "Postre de cuajada con melao",
          ],
          key="menu_postre",
      )
      sel_antojo = st.selectbox(
          "🌽 Antojo extra",
          [
              "Ninguno por ahora",
              "Envueltos de mazorca",
              "Amasijos tradicionales (almojábanas y garullas)",
              "Arepa boyacense",
          ],
          key="menu_antojo",
      )
      sel_bebida = st.selectbox(
          "🫖 Bebida",
          [
              "Ninguno por ahora",
              "Aguapanela caliente con queso",
              "Sorbete de curuba o feijoa",
          ],
          key="menu_bebida",
      )

    selecciones_menu = [
        ("🍳 Desayuno", sel_desayuno),
        ("🍲 Almuerzo", sel_almuerzo),
        ("🥐 Onces", sel_onces),
        ("🌙 Cena", sel_cena),
        ("🍮 Postre", sel_postre),
        ("🌽 Antojo extra", sel_antojo),
        ("🫖 Bebida", sel_bebida),
    ]
    menu_activo = [
        (tiempo, plato)
        for tiempo, plato in selecciones_menu
        if plato != "Ninguno por ahora"
    ]

    if menu_activo:
      st.markdown("---")
      st.subheader("Tu Menú del Día en Tota")
      st.metric("Opciones elegidas en tu menú", f"{len(menu_activo)} de 7")

      for tiempo, plato in menu_activo:
        info = catalogo_platos[plato]
        st.markdown(
            f"""
            <div class="plato-card">
                <span class="plato-badge">{tiempo}</span>
                <h4 style="margin: 0.2rem 0 0.4rem 0; color: #FFFFFF;">{plato}</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_img, col_txt = st.columns([1, 2])
        with col_img:
          if os.path.exists(info["imagen"]):
            st.image(info["imagen"], use_container_width=True)
          else:
            st.info(
                f"Imagen pendiente: guarda la foto en '{info['imagen']}' para"
                " visualizar el plato aquí."
            )
        with col_txt:
          st.markdown(f"**Historia y origen:** {info['historia']}")
          st.markdown(
              f"**Quiénes lo cultivan y preparan:** {info['quienes']}"
          )
          st.markdown(f"**Dato curioso:** {info['dato_curioso']}")
          st.markdown(
              f"**Qué significa para Tota, Boyacá:** {info['significado']}"
          )
          st.markdown(f"**Consumo consciente:** {info['consumo_consciente']}")
          st.markdown("**Restaurantes recomendados:** Pendiente")
        st.markdown("---")

    st.subheader("¿Qué aprendí de la comida local?")
    with st.form("form_cierre_modulo2"):
      reflexion_llevo = st.text_area(
          "De la cultura y la comida local de Tota me llevo...",
          placeholder=(
              "Escribe qué descubriste sobre el origen de los platos, las"
              " familias campesinas y las tradiciones..."
          ),
      )
      reflexion_compromiso = st.text_area(
          "Y mi compromiso con su economía local es...",
          placeholder=(
              "Escribe cómo apoyarás a los productores, plazas y cocinas"
              " tradicionales..."
          ),
      )

      btn_guardar_m2 = st.form_submit_button(
          "Guardar mi Menú del Día y reclamar Sello 6: Cedazo"
      )

      if btn_guardar_m2:
        if not menu_activo:
          st.error(
              "Por favor selecciona al menos un plato en tu Menú del Día antes"
              " de finalizar."
          )
        elif not reflexion_llevo.strip() or not reflexion_compromiso.strip():
          st.error(
              "Por favor completa ambos campos de reflexión para recibir tu"
              " sello."
          )
        else:
          archivo_platos = "analitica_platos_tota.csv"
          resumen_platos = [
              f"{tiempo}: {plato}" for tiempo, plato in menu_activo
          ]
          resumen_str = " | ".join(resumen_platos)
          registro_plato = pd.DataFrame([{
              "platos_elegidos": resumen_str,
              "cantidad_platos": len(menu_activo),
              "fecha": pd.Timestamp.now().strftime("%Y-%m-%d"),
          }])
          if not os.path.exists(archivo_platos):
            registro_plato.to_csv(archivo_platos, index=False)
          else:
            df_prev = pd.read_csv(archivo_platos)
            pd.concat([df_prev, registro_plato], ignore_index=True).to_csv(
                archivo_platos, index=False
            )

          st.session_state.trucha_m2 = True
          st.session_state.sello_cedazo = True
          st.session_state.m2_menu_guardado = resumen_str
          st.session_state.m2_cant_platos = len(menu_activo)
          st.session_state.m2_me_llevo = reflexion_llevo.strip()
          st.session_state.m2_compromiso = reflexion_compromiso.strip()
          sincronizar_db_completa({
              "m2_menu": resumen_str,
              "m2_cantidad_platos": len(menu_activo),
              "m2_me_llevo": reflexion_llevo.strip(),
              "m2_compromiso_economia": reflexion_compromiso.strip(),
              "sello_cedazo": True,
          })

          st.success(
              f"Felicitaciones, {st.session_state.alias}. Has guardado tu Menú"
              " del Día, registrado tu aporte anónimo a la analítica"
              " comunitaria y desbloqueado el Sello 6: Cedazo."
          )
          st.markdown(
              f"**Tu compromiso registrado:** De la cultura y la comida local"
              f" de Tota me llevo {reflexion_llevo.strip()} y mi compromiso"
              f" con su economía local es {reflexion_compromiso.strip()}."
          )

# ==========================================
# MÓDULO 3: EL SENDERO DE LAS 11 DECISIONES (UNA SOLA PÁGINA)
# ==========================================
elif menu_opcion == "4. Modulo 3":
  if not st.session_state.get("registrado", False):
    st.warning(
        "Aún no has activado tu pasaporte. Por favor ve a la opción '1."
        " Registro' en el panel lateral para registrarte antes de ingresar al"
        " módulo."
    )
  else:
    st.header("Módulo 3 · El Sendero de las 11 Decisiones")
    st.write(
        f"¡Hola, {st.session_state.alias}! Recorre en una sola página el"
        " trayecto desde la plaza de Tota hasta la orilla del lago. Cada"
        " casilla plantea un dilema con tres caminos posibles —desde lo más"
        " inmediato hasta miradas morales, culturales o de cuidado del"
        " territorio a mediano y largo plazo— para que decidas desde dónde"
        " actúas."
    )
    st.markdown("---")

    casillas_sendero = [
        {
            "num": 1,
            "titulo": "Casilla 1 · La envoltura a mitad de la caminata",
            "situacion": (
                "Llevas una hora subiendo, el morral pesa y la envoltura del"
                " snack quedó manchada y húmeda. No hay caneca a la vista en"
                " los próximos tramos."
            ),
            "imagen_futura": None,
            "pregunta_abierta": None,
            "opciones": {
                "Dejarla bien doblada debajo de una piedra grande para que el viento no se la lleve": (
                    -1,
                    "Corto plazo / comodidad: aunque no vuele de inmediato, un residuo escondido igual tarda años en degradarse y puede ser desenterrado por animales o lluvias.",
                ),
                "Guardar la envoltura en una bolsita aparte dentro de tu morral y bajarla hasta el pueblo": (
                    2,
                    "Cuidado del territorio a futuro: asumes el peso de tu propio consumo para que el sendero y la cuenca mantengan su ciclo limpio.",
                ),
                "Preguntar en la siguiente casa o puesto veredal si tienen dónde disponerla de forma adecuada": (
                    1,
                    "Relación y respeto local: buscas apoyo con amabilidad sin imponer tu basura a cualquiera ni dejarla tirada.",
                ),
            },
        },
        {
            "num": 2,
            "titulo": "Casilla 2 · El frailejón junto al recodo húmedo",
            "situacion": (
                "Ves un frailejón en un punto donde el suelo está blando. Tu"
                " grupo quiere una foto con él de fondo, pero el camino"
                " demarcado queda a un par de metros."
            ),
            "imagen_futura": None,
            "pregunta_abierta": (
                "¿Qué le dirías a alguien de tu grupo que insiste en pisar"
                " fuera del sendero para lograr la foto?"
            ),
            "opciones": {
                "Entrar rápido con cuidado de pisar solo donde parece firme y salir enseguida": (
                    -1,
                    "Impulso del momento: en alta montaña el suelo y las plantas crecen muy despacio; un paso 'rápido' deja huella duradera.",
                ),
                "Tomar la foto desde el sendero autorizado y explicar que cuidar el frailejón es cuidar el agua de todos": (
                    2,
                    "Visión de territorio a largo plazo: proteges un regulador hídrico clave y compartes el sentido del cuidado con quienes viajan contigo.",
                ),
                "Invitar al grupo a encuadrar la foto desde el borde permitido para que la imagen también muestre el paisaje completo": (
                    1,
                    "Enfoque creativo y considerado: resuelves el deseo de la foto sin invadir la planta ni generar confrontación.",
                ),
            },
        },
        {
            "num": 3,
            "titulo": "Casilla 3 · Dos caminos en la vereda",
            "situacion": (
                "En un cruce rural, el mapa del celular no tiene señal clara y"
                " aparece un atajo estrecho que parece recortar media hora de"
                " caminata."
            ),
            "imagen_futura": None,
            "pregunta_abierta": None,
            "opciones": {
                "Tomar el atajo para ahorrar tiempo y llegar más temprano": (
                    -1,
                    "Inmediatez: los atajos improvisados suelen pasar por linderos, cultivos o zonas frágiles y desorientan a más caminantes.",
                ),
                "Esperar o acercarse a conversar con un habitante o guía local de la zona": (
                    2,
                    "Sabiduría local y territorio: reconoces que quien habita el lugar conoce los caminos, los tiempos reales y los acuerdos comunitarios.",
                ),
                "Volver al último punto señalizado y seguir la ruta principal con calma": (
                    1,
                    "Prudencia y respeto por el camino: priorizas la seguridad del recorrido y el tránsito ordenado.",
                ),
            },
        },
        {
            "num": 4,
            "titulo": "Casilla 4 · El parlante en el tramo silencioso",
            "situacion": (
                "Alguien del grupo saca un parlante portátil para animar la"
                " caminata, justo cuando se escuchan aves y el viento del"
                " páramo."
            ),
            "imagen_futura": None,
            "pregunta_abierta": None,
            "opciones": {
                "Dejarlo sonar a volumen moderado para no cortar el ambiente festivo": (
                    -1,
                    "Enfoque recreativo inmediato: incluso un volumen moderado altera la escucha de la fauna y cambia la experiencia de otras personas.",
                ),
                "Proponer apagarlo y escuchar los sonidos del lugar como parte del viaje": (
                    2,
                    "Ética ecológica y contemplativa: das espacio a la biodiversidad y a la calma propia de la alta montaña.",
                ),
                "Hablar con cercanía con quien lo encendió para acordar usarlo solo en un espacio cerrado o permitido": (
                    1,
                    "Criterio moral y de convivencia: cuidas la armonía del grupo sin tratar al otro como culpable.",
                ),
            },
        },
        {
            "num": 5,
            "titulo": "Casilla 5 · Una botella plástica a un lado del camino",
            "situacion": (
                "Encuentras una botella vacía que claramente no es tuya. Tienes"
                " las manos ocupadas o el morral casi lleno."
            ),
            "imagen_futura": None,
            "pregunta_abierta": None,
            "opciones": {
                "Seguir de largo: no es tu residuo y ya cargaste suficiente": (
                    0,
                    "Postura neutra: no generas el problema, aunque el residuo permanece expuesto en el entorno.",
                ),
                "Acomodar espacio o llevarla colgando/en bolsa hasta el próximo punto de reciclaje o disposición": (
                    2,
                    "Corresponsabilidad activa: entiendes que el cuidado del territorio compartido va más allá de lo que uno mismo produce.",
                ),
                "Avisar a un guía, puesto local o grupo de limpieza cercano si no puedes cargarla todo el tramo": (
                    1,
                    "Actitud colaborativa: buscas una solución concreta dentro de tus posibilidades reales.",
                ),
            },
        },
        {
            "num": 6,
            "titulo": "Casilla 6 · Sed y calor en pleno ascenso",
            "situacion": (
                "El sol pega fuerte entre nubes y se te acaba el agua del termo"
                " antes de lo previsto."
            ),
            "imagen_futura": None,
            "pregunta_abierta": (
                "¿Qué prefieres llevar siempre en tu maleta para no depender"
                " de envases desechables en ruta?"
            ),
            "opciones": {
                "Comprar agua embotellada y dejar la botella en la primera caneca o punto que veas": (
                    0,
                    "Solución práctica de momento: resuelve la sed, pero suma plástico de un solo uso al circuito del viaje.",
                ),
                "Llenar tu termo reutilizable en un punto seguro o racionar mejor tu hidratación desde el inicio": (
                    2,
                    "Hábito sostenible a futuro: reduces residuos desde la planeación del recorrido.",
                ),
                "Preguntar en una tienda local si puedes recargar agua segura o comprar un recipiente reutilizable": (
                    1,
                    "Consumo consciente y local: apoyas el comercio cercano y evitas acumular envases.",
                ),
            },
        },
        {
            "num": 7,
            "titulo": "Casilla 7 · Aves posadas cerca del agua",
            "situacion": (
                "Un grupo de aves descansa cerca de la orilla. Tienes un trozo"
                " de pan o galleta en la mano."
            ),
            "imagen_futura": None,
            "pregunta_abierta": None,
            "opciones": {
                "Lanzarles unas migas para verlas acercarse": (
                    -1,
                    "Intención afectiva pero riesgosa: alimentar fauna silvestre con comida humana altera su dieta y las vuelve dependientes o vulnerables.",
                ),
                "Observarlas en silencio sin ofrecer comida ni invadir su espacio": (
                    2,
                    "Respeto por la vida silvestre: permites que mantengan sus hábitos naturales y su tranquilidad.",
                ),
                "Guardar el alimento y disfrutar su movimiento a distancia con calma": (
                    1,
                    "Contemplación responsable: valoras el encuentro sin intervenir en el comportamiento de las aves.",
                ),
            },
        },
        {
            "num": 8,
            "titulo": "Casilla 8 · El borde de una huerta o cultivo",
            "situacion": (
                "Pasas junto a una parcela donde hay frutos o flores de"
                " temporada y no hay nadie cerca en ese instante."
            ),
            "imagen_futura": None,
            "pregunta_abierta": None,
            "opciones": {
                "Tomar un par de frutos pensando que es solo un detalle sin importancia": (
                    -1,
                    "Mirada individualista: aunque parezca mínimo, el trabajo agrícola tiene esfuerzo, tiempo y sustento familiar detrás.",
                ),
                "Respetar el cultivo y, si deseas probar algo, comprarlo o pedir permiso directamente a quien lo trabaja": (
                    2,
                    "Justicia y economía local: honras el trabajo campesino y fortaleces el intercambio justo.",
                ),
                "Apreciar el cultivo desde el camino y seguir tu ruta sin tocar nada": (
                    1,
                    "Respeto por la propiedad y el oficio: evitas cualquier daño o malentendido en el predio.",
                ),
            },
        },
        {
            "num": 9,
            "titulo": "Casilla 9 · Viento helado y llovizna repentina",
            "situacion": (
                "Cambia el clima de golpe: baja la temperatura y empieza a"
                " lloviznar. El grupo quiere apurar el paso."
            ),
            "imagen_futura": None,
            "pregunta_abierta": None,
            "opciones": {
                "Apurar sin abrigo para terminar rápido, dejando algo suelto en el morral": (
                    -1,
                    "Prisa en clima cambiante: correr en terreno mojado y frío aumenta el riesgo de resbalones o descuidos con el equipo.",
                ),
                "Abrigarte bien, cuidar el ritmo del grupo y asegurarte de que no quede nada atrás": (
                    2,
                    "Cuidado integral y preventivo: proteges tu bienestar, el del grupo y el orden del sendero.",
                ),
                "Buscar un resguardo temporal adecuado mientras pasa la ráfaga más fuerte": (
                    1,
                    "Adaptación al entorno de montaña: lees las señales del clima en lugar de forzar el paso.",
                ),
            },
        },
        {
            "num": 10,
            "titulo": "Casilla 10 · Pausa antes del tramo final",
            "situacion": (
                "Hacen una parada corta para descansar y comer algo ligero"
                " antes de ver la orilla."
            ),
            "imagen_futura": None,
            "pregunta_abierta": None,
            "opciones": {
                "Tirar cáscaras de fruta al pasto creyendo que se descomponen rápido": (
                    -1,
                    "Mito común: en alta montaña la descomposición es lenta y los restos orgánicos fuera de lugar alteran el suelo y atraen fauna.",
                ),
                "Guardar todos los restos en tu bolsa y disponerlos donde corresponda al regresar": (
                    2,
                    "Ética de cero rastro: dejas el lugar sin alteraciones visibles ni residuos de ningún tipo.",
                ),
                "Revisar en grupo el lugar antes de reanudar la marcha para no olvidar nada": (
                    1,
                    "Hábito colectivo de cuidado: conviertes la revisión final en una costumbre compartida.",
                ),
            },
        },
        {
            "num": 11,
            "titulo": "Casilla 11 · Llegada a la orilla del lago",
            "situacion": (
                "Llegas al borde del espejo de agua. El paisaje invita a"
                " quedarse un rato y respirar."
            ),
            "imagen_futura": None,
            "pregunta_abierta": (
                "¿Qué sensación o enseñanza te deja llegar a la orilla después"
                " de estas decisiones?"
            ),
            "opciones": {
                "Lanzar piedras o acercarte al borde inestable solo para probar el agua": (
                    -1,
                    "Impulso lúdico sin medida: alterar orillas frágiles o arrojar elementos al agua afecta el borde del ecosistema.",
                ),
                "Quedarte en un punto seguro, en silencio, cuidando el agua y la orilla como un bien común": (
                    2,
                    "Vínculo consciente con el lago: cierras el recorrido honrando el ecosistema que sostiene la vida y la cultura de Tota.",
                ),
                "Agradecer el recorrido y compartir una reflexión breve con quienes caminaron contigo": (
                    1,
                    "Cierre humano y significativo: conectas la experiencia del paisaje con el sentido del viaje.",
                ),
            },
        },
    ]

    if "decisiones_m3" not in st.session_state:
      st.session_state.decisiones_m3 = {}
    if "abiertas_m3" not in st.session_state:
      st.session_state.abiertas_m3 = {}

    for c in casillas_sendero:
      st.markdown(
          f"""
          <div class="casilla-card">
              <h4 style="margin: 0 0 0.4rem 0; color: #FFFFFF;">{c['titulo']}</h4>
          </div>
          """,
          unsafe_allow_html=True,
      )

      if c.get("imagen_futura") and os.path.exists(c["imagen_futura"]):
        st.image(c["imagen_futura"], use_container_width=True)

      st.write(c["situacion"])

      elegida = st.radio(
          f"¿Cómo actúas en la {c['titulo']}?",
          list(c["opciones"].keys()),
          key=f"m3_op_{c['num']}",
          label_visibility="collapsed",
      )
      st.session_state.decisiones_m3[c["num"]] = elegida
      pts, lectura_matiz = c["opciones"][elegida]
      st.caption(lectura_matiz)

      if c.get("pregunta_abierta"):
        resp_abierta = st.text_input(
            c["pregunta_abierta"],
            key=f"m3_abierta_{c['num']}",
            placeholder="Escribe tu respuesta breve aquí...",
        )
        st.session_state.abiertas_m3[c["num"]] = resp_abierta

      st.markdown("---")

    puntaje_total = 0
    for c in casillas_sendero:
      op_sel = st.session_state.decisiones_m3.get(c["num"])
      if op_sel in c["opciones"]:
        puntaje_total += c["opciones"][op_sel][0]

    casilla_alcanzada = max(1, min(11, round(1 + ((puntaje_total + 8) / 30) * 10)))

    st.subheader("Tu avance en el sendero hasta la orilla")
    m3_col1, m3_col2 = st.columns(2)
    with m3_col1:
      st.metric("Puntaje de decisiones", f"{puntaje_total:+d}")
    with m3_col2:
      st.metric("Casilla alcanzada", f"Casilla {casilla_alcanzada} de 11")

    st.progress(casilla_alcanzada / 11)
    st.markdown("---")

    st.subheader("Auditoría de la Maleta")
    st.write(
        "Al llegar a la orilla, vuelve a mirar tu maleta y compárala con lo"
        " vivido en el recorrido y en tu diario de residuos."
    )

    if st.session_state.get("clasificacion_maleta"):
      with st.expander("Ver lo que clasificaste en tu Maleta Digital (Módulo 1)"):
        for obj, zona in st.session_state["clasificacion_maleta"].items():
          st.write(f"• **{obj}:** {zona}")

    with st.form("form_cierre_modulo3"):
      que_no_use = st.text_area(
          "¿Qué llevé que no usé?",
          placeholder="Escribe qué objetos sobraron o no necesitaste...",
      )
      que_genere_evitable = st.text_area(
          "¿Qué generé que pude evitar?",
          placeholder=(
              "Escribe qué residuos, ruido o impactos pudiste evitar..."
          ),
      )

      st.markdown("---")
      st.markdown("### ¿Qué aprendí?")
      habito_cambiar = st.text_area(
          "Un hábito de mi maleta que voy a cambiar es...",
          placeholder="Completa tu compromiso de cambio de hábito...",
      )

      btn_sello7 = st.form_submit_button(
          "Completar auditoría y reclamar Sello 7: Gota de agua"
      )

      if btn_sello7:
        if (
            not que_no_use.strip()
            or not que_genere_evitable.strip()
            or not habito_cambiar.strip()
        ):
          st.error(
              "Por favor responde las dos preguntas de auditoría y completa"
              " la frase de aprendizaje para recibir tu sello."
          )
        else:
          st.session_state.sello_gota = True
          st.session_state.m3_puntaje_guardado = puntaje_total
          st.session_state.m3_casilla_guardado = casilla_alcanzada
          st.session_state.m3_no_use = que_no_use.strip()
          st.session_state.m3_evitable = que_genere_evitable.strip()
          st.session_state.m3_habito = habito_cambiar.strip()
          sincronizar_db_completa({
              "m3_puntaje": puntaje_total,
              "m3_casilla": casilla_alcanzada,
              "m3_no_use": que_no_use.strip(),
              "m3_evitable": que_genere_evitable.strip(),
              "m3_habito_cambiar": habito_cambiar.strip(),
              "sello_gota": True,
          })

          st.success(
              f"¡Felicitaciones, {st.session_state.alias}! Has completado el"
              " sendero y la auditoría, y desbloqueado el Sello 7: Gota de"
              " agua."
          )
          st.markdown(
              "**Tu compromiso:** Un hábito de mi maleta que voy a cambiar"
              f" es {habito_cambiar.strip()}."
          )

# ==========================================
# MÓDULO 4: MI PRESUPUESTO CON SENTIDO
# ==========================================
elif menu_opcion == "5. Modulo 4":
  if not st.session_state.get("registrado", False):
    st.warning(
        "Aún no has activado tu pasaporte. Por favor ve a la opción '1."
        " Registro' en el panel lateral para registrarte antes de ingresar al"
        " módulo."
    )
  else:
    st.header("Módulo 4 · Mi presupuesto con sentido")
    st.write(
        f"¡Hola, {st.session_state.alias}! En este cuarto módulo revisas cómo"
        " distribuyes en porcentajes tu gasto para los días planeados de"
        " viaje, qué llega directo a la economía local, el recuerdo que"
        " eliges cuidar y tu agradecimiento en el recorrido."
    )
    st.markdown("---")

    st.subheader("1. Reparto del gasto (porcentajes para los días planeados)")
    dias_planeados = st.number_input(
        "Días planeados para el viaje",
        min_value=1,
        max_value=30,
        value=3,
        step=1,
        key="m4_dias",
    )
    st.caption(
        "Reparte el 100 % de tu presupuesto entre estos rubros y marca con ★"
        " los que llegan directamente a familias o prestadores locales."
    )

    rubros_lista = [
        "Alojamiento",
        "Comida",
        "Transporte",
        "Guías",
        "Artesanías",
        "Otros",
    ]
    valores_default = {
        "Alojamiento": 25,
        "Comida": 25,
        "Transporte": 15,
        "Guías": 15,
        "Artesanías": 10,
        "Otros": 10,
    }

    porcentajes_rubros = {}
    local_estrella = {}

    for rubro in rubros_lista:
      c_pct, c_est = st.columns([3, 1])
      with c_pct:
        porcentajes_rubros[rubro] = st.number_input(
            f"{rubro} (%)",
            min_value=0,
            max_value=100,
            value=valores_default[rubro],
            step=5,
            key=f"m4_pct_{rubro}",
        )
      with c_est:
        st.markdown("<br>", unsafe_allow_html=True)
        local_estrella[rubro] = st.checkbox(
            "★ Local directo",
            value=(rubro in ["Alojamiento", "Comida", "Guías", "Artesanías"]),
            key=f"m4_est_{rubro}",
        )

    total_pct = sum(porcentajes_rubros.values())
    pct_local_directo = sum(
        pct for r, pct in porcentajes_rubros.items() if local_estrella[r]
    )

    m4_c1, m4_c2 = st.columns(2)
    with m4_c1:
      st.metric("Total repartido", f"{total_pct}%")
    with m4_c2:
      st.metric("Porcentaje marcado con ★ (local directo)", f"{pct_local_directo}%")

    if total_pct != 100:
      st.warning(
          f"Tu reparto actual suma {total_pct} %. Ajusta los porcentajes para"
          " que sumen exactamente 100 %."
      )

    st.markdown("---")
    st.subheader("2. Un recuerdo con historia")
    recuerdo_objeto = st.text_input(
        "Recuerdo elegido (una prenda de lana, un producto local, etc.)",
        placeholder="Ej. Ruana de lana, amasijos, producto de la despensa...",
    )
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
      recuerdo_quien = st.text_input(
          "¿Quién lo hizo?",
          placeholder="Persona, familia o taller...",
      )
    with col_r2:
      recuerdo_oficio = st.text_input(
          "¿Qué oficio representa?",
          placeholder="Ej. Tejeduría, agricultura, panadería...",
      )
    with col_r3:
      recuerdo_cuidado = st.text_input(
          "¿Cómo lo cuidaré?",
          placeholder="Cómo lo conservarás o usarás...",
      )

    st.markdown("---")
    st.subheader("3. Una palabra de agradecimiento")
    mensaje_agradecimiento = st.text_area(
        "Escribe un mensaje breve para la persona o el recorrido que más te"
        " ayudó durante el viaje",
        placeholder=(
            "Escribe tu agradecimiento por el acompañamiento, la hospitalidad"
            " o el recorrido..."
        ),
    )

    st.markdown("---")
    st.subheader("4. ¿Qué aprendí?")
    with st.form("form_cierre_modulo4"):
      gasto_dejo = st.text_area(
          "Mi manera de gastar en Tota dejó...",
          placeholder="Completa qué dejó tu forma de gastar en el territorio...",
      )
      gasto_proxima = st.text_area(
          "Y la próxima vez...",
          placeholder="Completa qué harás diferente o igual la próxima vez...",
      )

      btn_guardar_m4 = st.form_submit_button(
          "Finalizar cuarto módulo y reclamar Sello 10: Dinero"
      )

      if btn_guardar_m4:
        if total_pct != 100:
          st.error(
              "Por favor ajusta los porcentajes de tu presupuesto para que"
              " sumen 100 %."
          )
        elif (
            not recuerdo_objeto.strip()
            or not recuerdo_quien.strip()
            or not recuerdo_oficio.strip()
            or not recuerdo_cuidado.strip()
        ):
          st.error(
              "Por favor completa los datos de tu recuerdo con historia."
          )
        elif not mensaje_agradecimiento.strip():
          st.error("Por favor escribe tu palabra de agradecimiento.")
        elif not gasto_dejo.strip() or not gasto_proxima.strip():
          st.error(
              "Por favor completa ambas partes de '¿Qué aprendí?' para"
              " finalizar el módulo."
          )
        else:
          st.session_state.sello_dinero = True
          st.session_state.m4_dias_guardados = int(dias_planeados)
          st.session_state.m4_pct_local = int(pct_local_directo)
          st.session_state.m4_recuerdo = recuerdo_objeto.strip()
          st.session_state.m4_quien = recuerdo_quien.strip()
          st.session_state.m4_oficio = recuerdo_oficio.strip()
          st.session_state.m4_cuidado = recuerdo_cuidado.strip()
          st.session_state.m4_agradecimiento = mensaje_agradecimiento.strip()
          st.session_state.m4_gasto_dejo = gasto_dejo.strip()
          st.session_state.m4_proxima = gasto_proxima.strip()
          sincronizar_db_completa({
              "m4_dias": int(dias_planeados),
              "m4_pct_local_estrella": int(pct_local_directo),
              "m4_recuerdo": recuerdo_objeto.strip(),
              "m4_quien_hizo": recuerdo_quien.strip(),
              "m4_oficio": recuerdo_oficio.strip(),
              "m4_cuidado_recuerdo": recuerdo_cuidado.strip(),
              "m4_agradecimiento": mensaje_agradecimiento.strip(),
              "m4_gasto_dejo": gasto_dejo.strip(),
              "m4_proxima_vez": gasto_proxima.strip(),
              "sello_dinero": True,
          })

          st.success(
              f"¡Has finalizado el cuarto módulo, {st.session_state.alias}! Se"
              " ha activado el Sello 10: Dinero para tu viaje de"
              f" {dias_planeados} día(s)."
          )
          st.markdown(
              f"**Tu cierre:** Mi manera de gastar en Tota dejó"
              f" {gasto_dejo.strip()} y la próxima vez {gasto_proxima.strip()}."
          )
          st.info(
              "Si ya finalizaste la cartilla física y ahora que acabas de"
              " completar los cuatro módulos, ve a la siguiente pestaña para"
              " reclamar tus certificados."
          )

# ==========================================
# PESTAÑA 6: RECOMPENSA Y CERTIFICADO
# ==========================================
elif menu_opcion == "6. Recompensa":
  st.header("Recompensa · Tu cierre en Tota y Certificado")
  st.markdown(
      "### ¡Felicidades! Has completado la cartilla completa, la de La Maleta"
      " de Tota."
  )
  st.write(
      "Has completado también todos los sellos y ahora recibe aquí tu"
      " certificado."
  )

  st.subheader("Tus sellos y logros en la maleta viajera")
  logros = [
      (
          "Trucha Módulo 1 (Perfil y Maleta)",
          st.session_state.get("trucha_m1", False)
          or st.session_state.get("maleta_completada", False),
      ),
      (
          "Trucha Módulo 2 y Sello 6: Cedazo",
          st.session_state.get("trucha_m2", False)
          or st.session_state.get("sello_cedazo", False),
      ),
      ("Sello 7: Gota de agua", st.session_state.get("sello_gota", False)),
      ("Sello 10: Dinero", st.session_state.get("sello_dinero", False)),
  ]
  cols_logros = st.columns(4)
  for idx, (nombre_logro, conseguido) in enumerate(logros):
    with cols_logros[idx]:
      estado_txt = "Completado" if conseguido else "Por completar"
      st.metric(nombre_logro, estado_txt)

  st.markdown("---")
  st.subheader("Reflexión general: visitar Tota, Boyacá y Colombia")
  st.write(
      "Visitar Tota es mucho más que contemplar un espejo de agua o recorrer"
      " un camino de alta montaña: es encontrarse con el agua que sostiene la"
      " vida, con los saberes de quienes cultivan y tejen el territorio, y con"
      " la hospitalidad de su gente. Gracias por participar en esta"
      " experiencia y por seguir conociendo y aprendiendo de lo hermoso que es"
      " Boyacá y Colombia."
  )

  st.markdown("---")
  st.subheader("Genera y descarga tu certificado")
  nombre_sugerido = (
      st.session_state.alias if st.session_state.get("alias") else ""
  )
  nombre_certificado = st.text_input(
      "¿Qué nombre quieres que aparezca en tu certificado?",
      value=nombre_sugerido,
      placeholder="Escribe tu nombre completo aquí...",
      key="nombre_completo_certificado",
  )

  base_dir = os.path.dirname(os.path.abspath(__file__))
  posibles_logos = [
      os.path.join(base_dir, "imagenes", "logo_me_gusta_viajar.png"),
      os.path.join(base_dir, "imagenes", "logo_me_gusta_viajar.jpg"),
      os.path.join(base_dir, "imagenes", "logo_me_gusta_viajar.jpeg"),
      os.path.join(base_dir, "imagenes", "logo_me_gusta_viajar.webp"),
  ]
  ruta_logo = next(
      (p for p in posibles_logos if os.path.exists(p)), posibles_logos[0]
  )
  fecha_hoy = pd.Timestamp.now().strftime("%Y-%m-%d")

  if nombre_certificado.strip():
    nombre_limpio = nombre_certificado.strip()
    st.session_state.nombre_cert_guardado = nombre_limpio
    if st.session_state.get("registrado", False):
      sincronizar_db_completa({"nombre_certificado": nombre_limpio})

    texto_reconocimiento = (
        "Me Gusta Viajar, Me Gusta Cuidar te da este certificado por"
        " participar, por hacer un uso consciente del viaje y por seguir"
        " aprendiendo a ser turista consciente. Te deseamos mucha suerte"
        " consiguiendo transmitir estos conocimientos e influyendo"
        " positivamente en las demás personas."
    )

    col_logo, col_cert = st.columns([1, 3])
    with col_logo:
      if os.path.exists(ruta_logo):
        st.image(ruta_logo, use_container_width=True)
      else:
        st.markdown(
            """
            <div style="background: #1E3E62; border: 1px dashed #4D9E95; border-radius: 14px; padding: 1.2rem; text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.4rem;">🧭🏔️💧</div>
                <p style="font-size: 0.88rem; margin: 0;"><strong>Me Gusta Viajar, Me Gusta Cuidar</strong></p>
                <p style="font-size: 0.78rem; opacity: 0.85; margin-top: 0.4rem;">Guarda tu logo en <code>imagenes/logo_me_gusta_viajar.png</code> para mostrarlo aquí.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_cert:
      st.markdown(
          f"""
          <div style="
              background: linear-gradient(180deg, #F8FAFC 0%, #EFF6F5 100%);
              color: #122338;
              padding: 2.2rem 2.4rem;
              border-radius: 18px;
              border: 3px solid #4D9E95;
              box-shadow: 0 10px 26px rgba(0,0,0,0.35);
              position: relative;
              font-family: Georgia, 'Times New Roman', serif;
          ">
              <div style="
                  border: 1.5px solid #135DB6;
                  border-radius: 12px;
                  padding: 1.6rem 1.8rem;
                  background: rgba(255,255,255,0.72);
              ">
                  <div style="text-align: center; font-size: 1.55rem; letter-spacing: 8px; color: #135DB6; margin-bottom: 0.5rem;">
                      🏔️ 🧭 💧 🌿 🥾
                  </div>
                  <p style="text-align: center; font-family: sans-serif; font-size: 0.82rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #4D9E95; margin: 0 0 0.4rem 0;">
                      Me Gusta Viajar, Me Gusta Cuidar
                  </p>
                  <h2 style="text-align: center; color: #122338; font-size: 1.85rem; margin: 0.2rem 0 0.9rem 0;">
                      Certificado de Turista Consciente
                  </h2>
                  <p style="text-align: center; font-family: sans-serif; color: #334155; font-size: 0.95rem; margin: 0 0 0.35rem 0;">
                      Se otorga con orgullo este reconocimiento a:
                  </p>
                  <div style="text-align: center; margin: 0.4rem auto 1.15rem auto; max-width: 85%; border-bottom: 2px solid #4D9E95; padding-bottom: 0.45rem;">
                      <span style="font-size: 1.5rem; font-weight: 700; color: #135DB6;">✦ {nombre_limpio} ✦</span>
                  </div>
                  <p style="text-align: center; font-family: sans-serif; color: #1E293B; font-size: 1rem; line-height: 1.6; margin: 0 auto 1.3rem auto; max-width: 92%;">
                      {texto_reconocimiento}
                  </p>
                  <div style="display: flex; justify-content: space-between; align-items: flex-end; gap: 1rem; border-top: 1px solid #CBD5E1; padding-top: 1rem; font-family: sans-serif; font-size: 0.85rem; color: #334155;">
                      <div>
                          <div style="font-weight: 700; color: #122338;">✦ Me Gusta Viajar, Me Gusta Cuidar</div>
                          <div>La Maleta de Tota · Tota, Boyacá · Colombia</div>
                      </div>
                      <div style="text-align: right;">
                          <div><strong>Fecha:</strong> {fecha_hoy}</div>
                          <div style="color: #4D9E95; font-weight: 600;">Cartilla y Sellos Completados</div>
                      </div>
                  </div>
              </div>
          </div>
          """,
          unsafe_allow_html=True,
      )

    try:
      from PIL import Image, ImageDraw, ImageFont

      ancho, alto = 1320, 840
      img = Image.new("RGB", (ancho, alto), color=(244, 248, 250))
      draw = ImageDraw.Draw(img)

      draw.rectangle([0, 0, ancho, 22], fill=(19, 93, 182))
      draw.rectangle([0, 22, ancho, 30], fill=(77, 158, 149))
      draw.rectangle(
          [34, 46, ancho - 34, alto - 34], outline=(77, 158, 149), width=6
      )
      draw.rectangle(
          [50, 62, ancho - 50, alto - 50], outline=(19, 93, 182), width=2
      )

      draw.polygon(
          [(85, 175), (135, 100), (185, 175)],
          fill=(19, 93, 182),
          outline=(18, 35, 56),
      )
      draw.polygon(
          [(145, 175), (190, 115), (235, 175)],
          fill=(77, 158, 149),
          outline=(18, 35, 56),
      )
      draw.arc(
          [85, 675, 165, 715], start=0, end=180, fill=(19, 93, 182), width=4
      )
      draw.arc(
          [145, 675, 225, 715], start=0, end=180, fill=(77, 158, 149), width=4
      )
      cx, cy, r = ancho - 135, 135, 42
      draw.ellipse(
          [cx - r, cy - r, cx + r, cy + r], outline=(19, 93, 182), width=4
      )
      draw.polygon(
          [(cx, cy - 30), (cx + 10, cy), (cx, cy + 30), (cx - 10, cy)],
          fill=(77, 158, 149),
      )
      draw.polygon(
          [(cx - 30, cy), (cx, cy - 10), (cx + 30, cy), (cx, cy + 10)],
          fill=(19, 93, 182),
      )

      if os.path.exists(ruta_logo):
        try:
          logo_img = Image.open(ruta_logo).convert("RGBA")
          logo_img.thumbnail((145, 145))
          fondo_claro = Image.new(
              "RGBA", logo_img.size, (244, 248, 250, 255)
          )
          logo_comp = Image.alpha_composite(fondo_claro, logo_img).convert(
              "RGB"
          )
          img.paste(logo_comp, (265, 82))
        except Exception:
          pass

      try:
        fuente_marca = ImageFont.truetype("arial.ttf", 22)
        fuente_titulo = ImageFont.truetype("arialbd.ttf", 40)
        fuente_nombre = ImageFont.truetype("arialbd.ttf", 36)
        fuente_cuerpo = ImageFont.truetype("arial.ttf", 24)
        fuente_pie = ImageFont.truetype("arial.ttf", 19)
      except Exception:
        fuente_marca = ImageFont.load_default()
        fuente_titulo = ImageFont.load_default()
        fuente_nombre = ImageFont.load_default()
        fuente_cuerpo = ImageFont.load_default()
        fuente_pie = ImageFont.load_default()

      draw.text(
          (435, 100),
          "ME GUSTA VIAJAR, ME GUSTA CUIDAR",
          fill=(77, 158, 149),
          font=fuente_marca,
      )
      draw.text(
          (435, 138),
          "CERTIFICADO DE TURISTA CONSCIENTE",
          fill=(18, 35, 56),
          font=fuente_titulo,
      )

      draw.line([(90, 225), (ancho - 90, 225)], fill=(203, 213, 225), width=2)

      draw.text(
          (90, 260),
          "Se otorga este reconocimiento a:",
          fill=(51, 65, 85),
          font=fuente_cuerpo,
      )
      draw.text(
          (90, 305),
          f"* {nombre_limpio} *",
          fill=(19, 93, 182),
          font=fuente_nombre,
      )
      draw.line([(90, 358), (680, 358)], fill=(77, 158, 149), width=3)

      lineas_cuerpo = [
          "Me Gusta Viajar, Me Gusta Cuidar te da este certificado por",
          "participar, por hacer un uso consciente del viaje y por seguir",
          "aprendiendo a ser turista consciente. Te deseamos mucha suerte",
          "consiguiendo transmitir estos conocimientos e influyendo",
          "positivamente en las demás personas.",
      ]
      y_texto = 395
      for linea in lineas_cuerpo:
        draw.text((90, y_texto), linea, fill=(30, 41, 59), font=fuente_cuerpo)
        y_texto += 36

      draw.line([(90, 635), (ancho - 90, 635)], fill=(203, 213, 225), width=2)
      draw.text(
          (250, 682),
          "Firma y respaldo: Me Gusta Viajar, Me Gusta Cuidar · La Maleta de"
          " Tota (Tota, Boyacá)",
          fill=(18, 35, 56),
          font=fuente_pie,
      )
      draw.text(
          (250, 714),
          f"Fecha de emisión: {fecha_hoy}  |  Cartilla y sellos completados",
          fill=(77, 158, 149),
          font=fuente_pie,
      )

      buffer_img = BytesIO()
      img.save(buffer_img, format="PNG")
      buffer_img.seek(0)

      st.download_button(
          label="Descargar certificado (.PNG)",
          data=buffer_img,
          file_name=(
              f"certificado_tota_{nombre_limpio.lower().replace(' ', '_')}.png"
          ),
          mime="image/png",
      )
    except Exception:
      html_cert = f"""
      <html><body style="font-family: Georgia, serif; padding: 36px; background: #EFF6F5; color: #122338;">
        <div style="border: 3px solid #4D9E95; padding: 28px; border-radius: 16px; background: #FFFFFF; text-align: center;">
          <div style="font-size: 24px; letter-spacing: 6px; margin-bottom: 8px;">🏔️ 🧭 💧 🌿 🥾</div>
          <p style="font-family: sans-serif; color: #4D9E95; font-weight: bold;">ME GUSTA VIAJAR, ME GUSTA CUIDAR</p>
          <h2>Certificado de Turista Consciente</h2>
          <p style="font-family: sans-serif;">Se otorga este reconocimiento a:</p>
          <h3 style="color: #135DB6; border-bottom: 2px solid #4D9E95; display: inline-block; padding-bottom: 6px;">{nombre_limpio}</h3>
          <p style="font-family: sans-serif; max-width: 680px; margin: 18px auto; line-height: 1.6;">{texto_reconocimiento}</p>
          <hr>
          <p style="font-family: sans-serif; font-size: 14px;"><strong>Firma y respaldo:</strong> Me Gusta Viajar, Me Gusta Cuidar · La Maleta de Tota · {fecha_hoy}</p>
        </div>
      </body></html>
      """
      st.download_button(
          label="Descargar certificado (.HTML)",
          data=html_cert.encode("utf-8"),
          file_name=(
              f"certificado_tota_{nombre_limpio.lower().replace(' ', '_')}.html"
          ),
          mime="text/html",
      )
  else:
    st.info(
        "Escribe el nombre completo que deseas que aparezca en tu certificado"
        " para generar la vista previa y habilitar la descarga."
    )

# ==========================================
# PESTAÑA 7: ANÁLISIS Y BASE DE DATOS (PRIVADA)
# ==========================================
elif menu_opcion == "7. Análisis y Base de Datos":
  st.header("7. Análisis y Base de Datos")

  if not st.session_state.get("analisis_autenticado", False):
    st.warning(
        "Esta sección es privada para análisis de datos. Ingresa la contraseña"
        " para acceder."
    )
    with st.form("form_clave_analisis"):
      clave_ingresada = st.text_input(
          "Contraseña de análisis",
          type="password",
          placeholder="Ingresa la contraseña...",
      )
      btn_entrar_analisis = st.form_submit_button("Ingresar a Análisis")
      if btn_entrar_analisis:
        if clave_ingresada == CLAVE_ANALISIS:
          st.session_state.analisis_autenticado = True
          st.rerun()
        else:
          st.error("Contraseña incorrecta.")
  else:
    col_top_a, col_top_b = st.columns([4, 1])
    with col_top_a:
      st.success("Acceso autorizado al panel de análisis y base de datos.")
    with col_top_b:
      if st.button("Bloquear vista"):
        st.session_state.analisis_autenticado = False
        st.rerun()

    df_completa = cargar_db_completa()
    df_checkin = cargar_base_datos()

    if not df_checkin.empty and df_completa.empty:
      df_completa = df_checkin.copy()

    if df_completa.empty:
      st.info(
          "Aún no hay registros guardados en la base de datos. Cuando los"
          " viajeros completen su registro y módulos, aparecerán aquí."
      )
    else:
      st.subheader("Filtros de exploración")
      f_col1, f_col2, f_col3 = st.columns(3)
      df_filtrado = df_completa.copy()

      with f_col1:
        if "tipo_turista" in df_filtrado.columns:
          tipos_disp = ["Todos"] + sorted([
              str(x)
              for x in df_filtrado["tipo_turista"].dropna().unique()
              if str(x).strip()
          ])
          sel_tipo = st.selectbox("Tipo de turista", tipos_disp, key="f_tipo_t")
          if sel_tipo != "Todos":
            df_filtrado = df_filtrado[df_filtrado["tipo_turista"] == sel_tipo]

      with f_col2:
        if "genero" in df_filtrado.columns:
          generos_disp = ["Todos"] + sorted([
              str(x)
              for x in df_filtrado["genero"].dropna().unique()
              if str(x).strip()
          ])
          sel_gen = st.selectbox("Género", generos_disp, key="f_gen_t")
          if sel_gen != "Todos":
            df_filtrado = df_filtrado[df_filtrado["genero"] == sel_gen]

      with f_col3:
        if "rango_edad" in df_filtrado.columns:
          edades_disp = ["Todos"] + sorted([
              str(x)
              for x in df_filtrado["rango_edad"].dropna().unique()
              if str(x).strip()
          ])
          sel_edad = st.selectbox("Rango de edad", edades_disp, key="f_edad_t")
          if sel_edad != "Todos":
            df_filtrado = df_filtrado[df_filtrado["rango_edad"] == sel_edad]

      st.markdown("---")
      m1, m2, m3 = st.columns(3)
      with m1:
        st.metric("Total de registros", len(df_filtrado))
      with m2:
        if "m4_pct_local_estrella" in df_filtrado.columns:
          prom_local = pd.to_numeric(
              df_filtrado["m4_pct_local_estrella"], errors="coerce"
          ).mean()
          st.metric(
              "Promedio gasto local ★",
              f"{0 if pd.isna(prom_local) else prom_local:.1f}%",
          )
        else:
          st.metric("Promedio gasto local ★", "N/D")
      with m3:
        if "sello_dinero" in df_filtrado.columns:
          completados_m4 = int(
              df_filtrado["sello_dinero"].fillna(False).astype(bool).sum()
          )
          st.metric("Finalizaron Módulo 4", completados_m4)
        else:
          st.metric("Finalizaron Módulo 4", 0)

      st.markdown("---")
      st.subheader("Gráficas exploratorias")
      g_col1, g_col2 = st.columns(2)

      with g_col1:
        if (
            "tipo_turista" in df_filtrado.columns
            and not df_filtrado["tipo_turista"].dropna().empty
        ):
          st.markdown("**Tipo de turista (Nacional / Extranjero)**")
          st.bar_chart(df_filtrado["tipo_turista"].value_counts())

        if (
            "rango_edad" in df_filtrado.columns
            and not df_filtrado["rango_edad"].dropna().empty
        ):
          st.markdown("**Distribución por rango de edad**")
          st.bar_chart(df_filtrado["rango_edad"].value_counts())

      with g_col2:
        if (
            "genero" in df_filtrado.columns
            and not df_filtrado["genero"].dropna().empty
        ):
          st.markdown("**Distribución por género**")
          st.bar_chart(df_filtrado["genero"].value_counts())

        if (
            "perfil_m1" in df_filtrado.columns
            and not df_filtrado["perfil_m1"].replace("", pd.NA).dropna().empty
        ):
          st.markdown("**Perfiles turísticos más frecuentes (Módulo 1)**")
          st.bar_chart(
              df_filtrado["perfil_m1"].replace("", pd.NA).dropna().value_counts()
          )

      st.markdown("---")
      tab_df_general, tab_df_textos = st.tabs([
          "Vista del DataFrame completo",
          "Textos abiertos (análisis de texto / sentimientos)",
      ])

      with tab_df_general:
        st.dataframe(df_filtrado, use_container_width=True)

      with tab_df_textos:
        cols_texto = [
            c
            for c in [
                "alias",
                "m1_vengo",
                "m1_espero",
                "m1_dejar",
                "m2_me_llevo",
                "m2_compromiso_economia",
                "m3_no_use",
                "m3_evitable",
                "m3_habito_cambiar",
                "m4_recuerdo",
                "m4_agradecimiento",
                "m4_gasto_dejo",
                "m4_proxima_vez",
            ]
            if c in df_filtrado.columns
        ]
        if cols_texto:
          st.dataframe(df_filtrado[cols_texto], use_container_width=True)
        else:
          st.info("Aún no hay respuestas de texto registradas.")

      st.markdown("---")
      st.subheader("Exportar base de datos")
      try:
        buffer_xlsx = BytesIO()
        with pd.ExcelWriter(buffer_xlsx, engine="openpyxl") as writer:
          df_completa.to_excel(writer, index=False, sheet_name="Consolidado")
        buffer_xlsx.seek(0)
        st.download_button(
            label="Descargar base de datos en Excel (.XLSX)",
            data=buffer_xlsx,
            file_name="base_datos_maleta_de_tota.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
      except Exception:
        st.caption(
            "Nota: si no tienes `openpyxl` instalado, puedes descargar el"
            " consolidado en CSV y abrirlo directo en Excel."
        )
        st.download_button(
            label="Descargar base de datos (.CSV)",
            data=df_completa.to_csv(index=False).encode("utf-8"),
            file_name="base_datos_maleta_de_tota.csv",
            mime="text/csv",
        )

    st.markdown("---")
    st.subheader("Administrar / Eliminar base de datos")
    confirmar_borrado = st.checkbox(
        "Confirmo que deseo eliminar permanentemente la base de datos"
        " consolidada y el registro de check-in.",
        key="conf_borrar_db",
    )
    if st.button("Eliminar base de datos"):
      if not confirmar_borrado:
        st.error(
            "Marca primero la casilla de confirmación para eliminar la base de"
            " datos."
        )
      else:
        for archivo_borrar in [DB_COMPLETA_FILE, DB_FILE]:
          if os.path.exists(archivo_borrar):
            os.remove(archivo_borrar)
        st.success("Base de datos eliminada correctamente.")
        st.rerun()