import streamlit as st
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, JSON, Enum, Float, UniqueConstraint, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime, date
import enum
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Configuración de la base de datos
DATABASE_URL = "sqlite:///hermes.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class UserRole(enum.Enum):
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    OPERATOR = "operator"

class QuestionType(enum.Enum):
    CATEGORICAL = "categorical"
    NUMERICAL = "numerical"

class FormSection(enum.Enum):
    QUALITY = "quality"
    PRODUCTION = "production"

# Modelos
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def create_password_hash(password):
        return generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ProductionOrder(Base):
    __tablename__ = "production_orders"
    
    id = Column(Integer, primary_key=True)
    order_number = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    in_production = Column(Boolean, default=False)
    in_quality = Column(Boolean, default=False)
    quality_forms = relationship("QualityForm", back_populates="production_order")
    production_forms = relationship("ProductionForm", back_populates="production_order")

    @classmethod
    def get_by_order_number(cls, db, order_number):
        return db.query(cls).filter(cls.order_number == order_number).first()

class QualityForm(Base):
    __tablename__ = "quality_forms"
    
    id = Column(Integer, primary_key=True)
    production_order_id = Column(Integer, ForeignKey("production_orders.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    apariencia = Column(String(50), nullable=False)  # A, B, C
    color = Column(String(50), nullable=False)  # A, B, C
    olor = Column(String(50), nullable=False)  # A, B, C
    humedad = Column(Float, nullable=False)  # 10-14%
    proteina = Column(Float, nullable=False)  # 18-22%
    grasa = Column(Float, nullable=False)  # 2-4%
    fibra = Column(Float, nullable=False)  # 3-5%
    cenizas = Column(Float, nullable=False)  # 5-7%
    created_at = Column(DateTime, default=datetime.utcnow)
    
    production_order = relationship("ProductionOrder", back_populates="quality_forms")
    user = relationship("User")

class ProductionForm(Base):
    __tablename__ = "production_forms"
    
    id = Column(Integer, primary_key=True)
    production_order_id = Column(Integer, ForeignKey("production_orders.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    dieta = Column(String(50), nullable=False)
    molienda = Column(Float, nullable=False)
    durabilidad = Column(Float, nullable=False)
    dureza = Column(Integer, nullable=False)
    temperatura = Column(Integer, nullable=False)
    peletizadora = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    production_order = relationship("ProductionOrder", back_populates="production_forms")
    user = relationship("User")

class DailyPlan(Base):
    __tablename__ = 'daily_plans'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    estimated_orders = Column(Integer)
    die_size = Column(Float)
    soy_tons = Column(Float)
    corn_cake_tons = Column(Float)
    
    @classmethod
    def get_by_date(cls, db, date):
        return db.query(cls).filter(cls.date == date).first()

# Configuración de preguntas
QUESTIONS_CONFIG = {
    "admin": {
        FormSection.QUALITY: [
            {
                "id": "q1",
                "text": "¿Cuál es el estado general del producto?",
                "type": QuestionType.CATEGORICAL,
                "options": ["A - Excelente", "B - Bueno", "C - Regular"],
                "required": True
            },
            {
                "id": "q2",
                "text": "¿Cuál es el nivel de calidad del acabado?",
                "type": QuestionType.NUMERICAL,
                "min_value": 1,
                "max_value": 10,
                "required": True
            }
        ],
        FormSection.PRODUCTION: [
            {
                "id": "p1",
                "text": "¿Cuál es el estado de la línea de producción?",
                "type": QuestionType.CATEGORICAL,
                "options": ["A - Óptimo", "B - Normal", "C - Requiere atención"],
                "required": True
            },
            {
                "id": "p2",
                "text": "¿Cuál es la eficiencia de producción?",
                "type": QuestionType.NUMERICAL,
                "min_value": 0,
                "max_value": 100,
                "required": True
            }
        ]
    },
    "supervisor": {
        FormSection.QUALITY: [
            {
                "id": "q1",
                "text": "¿Cuál es el estado general del producto?",
                "type": QuestionType.CATEGORICAL,
                "options": ["A - Excelente", "B - Bueno", "C - Regular"],
                "required": True
            }
        ],
        FormSection.PRODUCTION: [
            {
                "id": "p1",
                "text": "¿Cuál es el estado de la línea de producción?",
                "type": QuestionType.CATEGORICAL,
                "options": ["A - Óptimo", "B - Normal", "C - Requiere atención"],
                "required": True
            }
        ]
    },
    "operator": {
        FormSection.QUALITY: [
            {
                "id": "q1",
                "text": "¿El producto cumple con los estándares básicos?",
                "type": QuestionType.CATEGORICAL,
                "options": ["A - Sí", "B - Parcialmente", "C - No"],
                "required": True
            }
        ],
        FormSection.PRODUCTION: [
            {
                "id": "p1",
                "text": "¿La línea está funcionando correctamente?",
                "type": QuestionType.CATEGORICAL,
                "options": ["A - Sí", "B - Parcialmente", "C - No"],
                "required": True
            }
        ]
    }
}

# Funciones de utilidad
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None

def authenticate_user(db, username, password):
    user = db.query(User).filter(User.username == username).first()
    if user and user.check_password(password):
        return user
    return None

def login_required(func):
    def wrapper(*args, **kwargs):
        if not st.session_state.authenticated:
            login_page()
            return
        return func(*args, **kwargs)
    return wrapper

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Control de Calidad",
    page_icon="🔍",
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
        background-color: #C9C9C9;
        color: black;
    }
    /* Centrar el formulario de login */
    .main .block-container {
        max-width: 800px;
        margin: 0 auto;
    }
    /* Centrar el título del login */
    .main h1 {
        text-align: center;
    }
    /* Centrar los inputs del login */
    .main .stTextInput {
        max-width: 400px;
        margin: 0 auto;
    }
    /* Centrar el botón de login */
    .main .stButton {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
init_session_state()

# Initialize database
init_db()

def login_page():
    st.title("")
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("<h2 style='text-align:center;'>Inicio de Sesión</h2>", unsafe_allow_html=True)
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            if st.button("Iniciar Sesión", use_container_width=True):
                db = next(get_db())
                user = authenticate_user(db, username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.authenticated = True
                    st.success("¡Inicio de sesión exitoso!")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

@login_required
def quality_form():
    st.title("📋 Formulario de Calidad")
    db = next(get_db())

    if "quality_action" not in st.session_state:
        st.session_state.quality_action = None
    if "quality_last_form_id" not in st.session_state:
        st.session_state.quality_last_form_id = None

    with st.form(key="quality_form", clear_on_submit=True):
        order_number = st.text_input("Número de Orden de Producción", key="quality_order_number", value="")
        apariencia = st.selectbox("Apariencia", ["A - Excelente", "B - Bueno", "C - Regular"], key="quality_apariencia", index=0)
        color = st.selectbox("Color", ["A - Excelente", "B - Bueno", "C - Regular"], key="quality_color", index=0)
        olor = st.selectbox("Olor", ["A - Excelente", "B - Bueno", "C - Regular"], key="quality_olor", index=0)
        humedad = st.number_input("Humedad (%)", min_value=10.0, max_value=14.0, step=0.1, key="quality_humedad", value=10.0)
        proteina = st.number_input("Proteína (%)", min_value=18.0, max_value=22.0, step=0.1, key="quality_proteina", value=18.0)
        grasa = st.number_input("Grasa (%)", min_value=2.0, max_value=4.0, step=0.1, key="quality_grasa", value=2.0)
        fibra = st.number_input("Fibra (%)", min_value=3.0, max_value=5.0, step=0.1, key="quality_fibra", value=3.0)
        cenizas = st.number_input("Cenizas (%)", min_value=5.0, max_value=7.0, step=0.1, key="quality_cenizas", value=5.0)
        submit_button = st.form_submit_button("💾 Enviar")

    if submit_button:
        if not order_number:
            st.error("Debes ingresar el número de orden de producción.")
            return
        production_order = ProductionOrder.get_by_order_number(db, order_number)
        if not production_order:
            production_order = ProductionOrder(order_number=order_number)
            db.add(production_order)
            db.commit()
            existing_quality_form = None
        else:
            existing_quality_form = db.query(QualityForm).filter(
                QualityForm.production_order_id == production_order.id
            ).order_by(QualityForm.created_at.desc()).first()

        if existing_quality_form:
            st.warning("Ya existe un formulario de calidad para esta orden. ¿Qué deseas hacer?")
            st.session_state.quality_last_form_id = existing_quality_form.id
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Actualizar último formulario"):
                    st.session_state.quality_action = "update"
                    st.experimental_rerun()
            with col2:
                if st.button("➕ Agregar nuevo formulario"):
                    st.session_state.quality_action = "append"
                    st.experimental_rerun()
        else:
            # No existe formulario de calidad para esta orden, guardar normalmente
            try:
                new_form = QualityForm(
                    production_order_id=production_order.id,
                    user_id=st.session_state.user.id,
                    apariencia=apariencia,
                    color=color,
                    olor=olor,
                    humedad=humedad,
                    proteina=proteina,
                    grasa=grasa,
                    fibra=fibra,
                    cenizas=cenizas
                )
                db.add(new_form)
                production_order.in_quality = True
                db.commit()
                st.toast("✅ Datos almacenados con éxito", icon="✅")
                st.session_state.quality_action = None
                st.session_state.quality_last_form_id = None
                st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ Error al guardar: {str(e)}")

    if st.session_state.quality_action == "update" and st.session_state.quality_last_form_id:
        try:
            last_form = db.query(QualityForm).get(st.session_state.quality_last_form_id)
            last_form.apariencia = st.session_state.quality_apariencia
            last_form.color = st.session_state.quality_color
            last_form.olor = st.session_state.quality_olor
            last_form.humedad = st.session_state.quality_humedad
            last_form.proteina = st.session_state.quality_proteina
            last_form.grasa = st.session_state.quality_grasa
            last_form.fibra = st.session_state.quality_fibra
            last_form.cenizas = st.session_state.quality_cenizas
            db.commit()
            st.toast("✅ Datos almacenados con éxito", icon="✅")
        except Exception as e:
            st.error(f"❌ Error al actualizar: {str(e)}")
        st.session_state.quality_action = None
        st.session_state.quality_last_form_id = None
        st.experimental_rerun()
    elif st.session_state.quality_action == "append" and st.session_state.quality_last_form_id:
        try:
            production_order = ProductionOrder.get_by_order_number(db, st.session_state.quality_order_number)
            new_form = QualityForm(
                production_order_id=production_order.id,
                user_id=st.session_state.user.id,
                apariencia=st.session_state.quality_apariencia,
                color=st.session_state.quality_color,
                olor=st.session_state.quality_olor,
                humedad=st.session_state.quality_humedad,
                proteina=st.session_state.quality_proteina,
                grasa=st.session_state.quality_grasa,
                fibra=st.session_state.quality_fibra,
                cenizas=st.session_state.quality_cenizas
            )
            db.add(new_form)
            db.commit()
            st.toast("✅ Datos almacenados con éxito", icon="✅")
        except Exception as e:
            st.error(f"❌ Error al agregar: {str(e)}")
        st.session_state.quality_action = None
        st.session_state.quality_last_form_id = None
        st.experimental_rerun()

@login_required
def production_form():
    st.title("🏭 Formulario de Producción")
    db = next(get_db())

    if "production_action" not in st.session_state:
        st.session_state.production_action = None
    if "production_last_form_id" not in st.session_state:
        st.session_state.production_last_form_id = None

    with st.form(key="production_form", clear_on_submit=True):
        order_number = st.text_input("Número de Orden de Producción", key="production_order_number", value="")
        dieta = st.selectbox("Dieta", ["Dieta 1", "Dieta 2", "Dieta 3"], key="production_dieta", index=0)
        molienda = st.number_input("Molienda (mm)", min_value=0.1, max_value=5.0, step=0.1, key="production_molienda", value=0.1)
        durabilidad = st.number_input("Durabilidad (%)", min_value=0.0, max_value=100.0, step=0.1, key="production_durabilidad", value=0.0)
        dureza = st.number_input("Dureza (kg)", min_value=1, max_value=100, step=1, key="production_dureza", value=1)
        temperatura = st.number_input("Temperatura (°C)", min_value=20, max_value=100, step=1, key="production_temperatura", value=20)
        peletizadora = st.selectbox("Peletizadora", ["Peletizadora 1", "Peletizadora 2", "Peletizadora 3"], key="production_peletizadora", index=0)
        submit_button = st.form_submit_button("💾 Enviar")

    if submit_button:
        if not order_number:
            st.error("Debes ingresar el número de orden de producción.")
            return
        production_order = ProductionOrder.get_by_order_number(db, order_number)
        if not production_order:
            production_order = ProductionOrder(order_number=order_number)
            db.add(production_order)
            db.commit()
            existing_production_form = None
        else:
            existing_production_form = db.query(ProductionForm).filter(
                ProductionForm.production_order_id == production_order.id
            ).order_by(ProductionForm.created_at.desc()).first()

        if existing_production_form:
            st.warning("Ya existe un formulario de producción para esta orden. ¿Qué deseas hacer?")
            st.session_state.production_last_form_id = existing_production_form.id
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Actualizar último formulario"):
                    st.session_state.production_action = "update"
                    st.experimental_rerun()
            with col2:
                if st.button("➕ Agregar nuevo formulario"):
                    st.session_state.production_action = "append"
                    st.experimental_rerun()
        else:
            # No existe formulario de producción para esta orden, guardar normalmente
            try:
                new_form = ProductionForm(
                    production_order_id=production_order.id,
                    user_id=st.session_state.user.id,
                    dieta=dieta,
                    molienda=molienda,
                    durabilidad=durabilidad,
                    dureza=dureza,
                    temperatura=temperatura,
                    peletizadora=peletizadora
                )
                db.add(new_form)
                production_order.in_production = True
                db.commit()
                st.toast("✅ Datos almacenados con éxito", icon="✅")
                st.session_state.production_action = None
                st.session_state.production_last_form_id = None
                st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ Error al guardar: {str(e)}")

    if st.session_state.production_action == "update" and st.session_state.production_last_form_id:
        try:
            last_form = db.query(ProductionForm).get(st.session_state.production_last_form_id)
            last_form.dieta = st.session_state.production_dieta
            last_form.molienda = st.session_state.production_molienda
            last_form.durabilidad = st.session_state.production_durabilidad
            last_form.dureza = st.session_state.production_dureza
            last_form.temperatura = st.session_state.production_temperatura
            last_form.peletizadora = st.session_state.production_peletizadora
            db.commit()
            st.toast("✅ Datos almacenados con éxito", icon="✅")
        except Exception as e:
            st.error(f"❌ Error al actualizar: {str(e)}")
        st.session_state.production_action = None
        st.session_state.production_last_form_id = None
        st.experimental_rerun()
    elif st.session_state.production_action == "append" and st.session_state.production_last_form_id:
        try:
            production_order = ProductionOrder.get_by_order_number(db, st.session_state.production_order_number)
            new_form = ProductionForm(
                production_order_id=production_order.id,
                user_id=st.session_state.user.id,
                dieta=st.session_state.production_dieta,
                molienda=st.session_state.production_molienda,
                durabilidad=st.session_state.production_durabilidad,
                dureza=st.session_state.production_dureza,
                temperatura=st.session_state.production_temperatura,
                peletizadora=st.session_state.production_peletizadora
            )
            db.add(new_form)
            db.commit()
            st.toast("✅ Datos almacenados con éxito", icon="✅")
        except Exception as e:
            st.error(f"❌ Error al agregar: {str(e)}")
        st.session_state.production_action = None
        st.session_state.production_last_form_id = None
        st.experimental_rerun()

@login_required
def daily_plan_form():
    st.title("📅 Plan Diario")
    
    if "formulario_enviado" not in st.session_state:
        st.session_state["formulario_enviado"] = False

    if st.session_state["formulario_enviado"]:
        st.session_state["ordenes_estimadas"] = None
        st.session_state["medida_dado"] = None
        st.session_state["toneladas_soya"] = None
        st.session_state["toneladas_torta_maiz"] = None
        st.session_state["formulario_enviado"] = False

    try:
        db = next(get_db())
        today = date.today()
        
        existing_plan = DailyPlan.get_by_date(db, today)
        
        if existing_plan:
            st.warning(f"⚠️ Ya existe un plan para el día {today.strftime('%Y-%m-%d')}")
            st.write("### Plan Actual")
            st.write(f"📊 Órdenes Estimadas: {existing_plan.estimated_orders}")
            st.write(f"⚙️ Medida de Dado: {existing_plan.die_size} mm")
            st.write(f"🫘 Toneladas de Soya: {existing_plan.soy_tons}")
            st.write(f"🌽 Toneladas de Torta de Maíz: {existing_plan.corn_cake_tons}")
            
            if st.button("🔄 Cargar Plan Actual para Actualizar"):
                st.session_state["ordenes_estimadas"] = existing_plan.estimated_orders
                st.session_state["medida_dado"] = existing_plan.die_size
                st.session_state["toneladas_soya"] = existing_plan.soy_tons
                st.session_state["toneladas_torta_maiz"] = existing_plan.corn_cake_tons
                st.rerun()
    except Exception as e:
        st.error("❌ Error al verificar el plan existente. Por favor, intente nuevamente.")

    with st.form(key="plan_diario_formulario"):
        st.subheader("Planificación del Día")
        
        ordenes_estimadas = st.number_input(
            "📊 Órdenes de Producción Estimadas",
            min_value=1,
            max_value=100,
            step=1,
            value=st.session_state.get("ordenes_estimadas", 1),
            key="ordenes_estimadas"
        )
        
        medida_dado = st.number_input(
            "⚙️ Medida de Dado (mm)",
            min_value=1.0,
            max_value=10.0,
            step=0.1,
            value=st.session_state.get("medida_dado", 1.0),
            key="medida_dado"
        )
        
        toneladas_soya = st.number_input(
            "🫘 Toneladas de Soya",
            min_value=0.0,
            max_value=1000.0,
            step=0.5,
            value=st.session_state.get("toneladas_soya", 0.0),
            key="toneladas_soya"
        )
        
        toneladas_torta_maiz = st.number_input(
            "🌽 Toneladas de Torta de Maíz",
            min_value=0.0,
            max_value=1000.0,
            step=0.5,
            value=st.session_state.get("toneladas_torta_maiz", 0.0),
            key="toneladas_torta_maiz"
        )
        
        confirmar = st.checkbox("✅ Confirmo que deseo guardar los datos")
        submit_button = st.form_submit_button("💾 Guardar Plan Diario")

    if submit_button:
        errores = []
        if not confirmar:
            errores.append("Debes confirmar que deseas guardar los datos.")
        if st.session_state.ordenes_estimadas is None:
            errores.append("Debes ingresar el número de **Órdenes Estimadas**.")
        if st.session_state.medida_dado is None:
            errores.append("Debes ingresar la **Medida de Dado**.")
        if st.session_state.toneladas_soya is None:
            errores.append("Debes ingresar las **Toneladas de Soya**.")
        if st.session_state.toneladas_torta_maiz is None:
            errores.append("Debes ingresar las **Toneladas de Torta de Maíz**.")

        if errores:
            for error in errores:
                st.error(f"⚠️ {error}")
        else:
            try:
                db = next(get_db())
                today = date.today()
                
                existing_plan = DailyPlan.get_by_date(db, today)
                
                if existing_plan:
                    existing_plan.estimated_orders = st.session_state.ordenes_estimadas
                    existing_plan.die_size = st.session_state.medida_dado
                    existing_plan.soy_tons = st.session_state.toneladas_soya
                    existing_plan.corn_cake_tons = st.session_state.toneladas_torta_maiz
                    db.commit()
                    st.success(
                        f"✅ Plan diario actualizado exitosamente a las {datetime.now().strftime('%H:%M:%S')}."
                    )
                    st.session_state["formulario_enviado"] = True
                    st.rerun()
                else:
                    new_plan = DailyPlan(
                        date=today,
                        estimated_orders=st.session_state.ordenes_estimadas,
                        die_size=st.session_state.medida_dado,
                        soy_tons=st.session_state.toneladas_soya,
                        corn_cake_tons=st.session_state.toneladas_torta_maiz
                    )
                    db.add(new_plan)
                    db.commit()
                    st.success(
                        f"✅ Plan diario guardado exitosamente a las {datetime.now().strftime('%H:%M:%S')}."
                    )
                    st.session_state["formulario_enviado"] = True
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error al guardar el plan diario: {str(e)}")
                db.rollback()

def main():
    if not st.session_state.authenticated:
        login_page()
    else:
        # Mostrar el logo de forma compatible
        st.sidebar.image("logo.png", width=120)
        st.sidebar.write(f"👤 Usuario: {st.session_state.user.username}")
        st.sidebar.write(f"👥 Rol: {st.session_state.user.role.value}")
        
        page = st.sidebar.radio(
            "Seleccione formulario:",
            ["📋 Formulario de Calidad", "🏭 Formulario de Producción", "📅 Plan Diario"]
        )
        
        # Espacio para empujar el botón al final
        st.sidebar.markdown("""
            <div style='flex:1; height: 200px;'></div>
        """, unsafe_allow_html=True)
        
        # Botón de cerrar sesión al final
        if st.sidebar.button("🚪 Cerrar Sesión"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
        
        if page == "📋 Formulario de Calidad":
            quality_form()
        elif page == "🏭 Formulario de Producción":
            production_form()
        elif page == "📅 Plan Diario":
            daily_plan_form()

if __name__ == "__main__":
    main() 