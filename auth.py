from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import User, UserRole
import streamlit as st

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str) -> User:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_user(db: Session, username: str, password: str, role: UserRole) -> User:
    hashed_password = get_password_hash(password)
    db_user = User(
        username=username,
        password_hash=hashed_password,
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

def login_required(func):
    def wrapper(*args, **kwargs):
        if not st.session_state.authenticated:
            st.error("Por favor inicie sesión para acceder a esta página")
            return
        return func(*args, **kwargs)
    return wrapper 