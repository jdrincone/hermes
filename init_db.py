from app import Base, User, UserRole, engine, SessionLocal

def init_db():
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        # Verificar si ya existen usuarios
        if db.query(User).first() is None:
            # Crear usuarios de prueba
            users = [
                User(
                    username="admin",
                    password_hash=User.create_password_hash("admin123"),
                    role=UserRole.ADMIN
                ),
                User(
                    username="supervisor",
                    password_hash=User.create_password_hash("super123"),
                    role=UserRole.SUPERVISOR
                ),
                User(
                    username="operator",
                    password_hash=User.create_password_hash("oper123"),
                    role=UserRole.OPERATOR
                )
            ]
            
            # Agregar usuarios a la base de datos
            for user in users:
                db.add(user)
            
            # Guardar cambios
            db.commit()
            print("✅ Usuarios de prueba creados exitosamente")
        else:
            print("ℹ️ La base de datos ya contiene usuarios")
            
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 