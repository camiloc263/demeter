from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db import models
from db.models import get_db
from schemas import usuario
from core import security

router = APIRouter(prefix="/usuarios", tags=["Gestión de Usuarios y Seguridad"])

@router.post("/", response_model=usuario.UsuarioResponse)
def registrar_usuario(nuevo_usuario: usuario.UsuarioCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario encriptando su contraseña en la Base de Datos."""
    
    # 1. Validar que el nombre de usuario no esté registrado
    usuario_existente = db.query(models.UsuarioORM).filter(models.UsuarioORM.username == nuevo_usuario.username).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado.")
    
    datos_usuario = nuevo_usuario.model_dump()
    
    # 2. ENCRIPTACIÓN REAL: Reemplazamos la clave en texto plano por el hash de bcrypt
    password_plana = datos_usuario.pop("password")
    datos_usuario["password_hash"] = security.encriptar_password(password_plana)

    # 3. Guardar en base de datos
    db_usuario = models.UsuarioORM(**datos_usuario)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario

@router.post("/login", response_model=usuario.Token)
def login(credenciales: usuario.LoginRequest, db: Session = Depends(get_db)):
    """Autentica al usuario y genera un Token de Acceso JWT."""
    
    # 1. Buscar al usuario por su username
    user = db.query(models.UsuarioORM).filter(models.UsuarioORM.username == credenciales.username).first()
    
    # 2. Validar que el usuario exista y que la contraseña coincida con el hash
    if not user or not security.verificar_password(credenciales.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas (Usuario o contraseña inválidos).",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Validar si la cuenta está activa
    if not user.activo:
        raise HTTPException(status_code=400, detail="Usuario inactivo en el sistema.")

    # 4. Generar el Token de Acceso JWT con el nombre de usuario y su rol
    token_data = {"sub": user.username, "rol": user.rol}
    access_token = security.crear_token_acceso(data=token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "rol": user.rol
    }

@router.get("/", response_model=List[usuario.UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    """Obtiene la lista de todos los usuarios registrados."""
    return db.query(models.UsuarioORM).all()