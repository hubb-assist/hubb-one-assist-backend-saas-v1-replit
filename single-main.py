"""
FastAPI - HUBB ONE Assist API - Versão Simplificada

Esta é uma versão simplificada da API que mantém toda a funcionalidade em um único arquivo
para facilitar o desenvolvimento no ambiente Replit.
"""

import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Generic, TypeVar

# Definir o TypeVar para a classe genérica
T = TypeVar('T')

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import JWTError, jwt

# Configurações
API_V1_STR = "/api/v1"
PROJECT_NAME = "HUBB ONE - Assist SaaS"
PROJECT_VERSION = "1.0.0"
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "a_super_secret_key_you_should_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Configuração do banco de dados
DATABASE_URL = os.environ.get("DATABASE_URL") or "sqlite:///./hubbone_assist.db"

# Criar engine SQLAlchemy
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos do banco de dados
class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    DIRETOR = "DIRETOR"
    COLABORADOR_NIVEL_2 = "COLABORADOR_NIVEL_2"

class User(Base):
    """
    Modelo de usuário no banco de dados
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.COLABORADOR_NIVEL_2)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.email}>"

# Criar tabelas
Base.metadata.create_all(bind=engine)

# Esquemas Pydantic
class UserBase(BaseModel):
    """Base user schema with common attributes"""
    name: str
    email: EmailStr
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    role: Optional[UserRole] = UserRole.COLABORADOR_NIVEL_2

class UserUpdate(BaseModel):
    """Schema for updating a user - all fields are optional"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(extra="forbid")

class UserOut(UserBase):
    """Schema for user responses - includes read-only fields"""
    id: int
    role: UserRole
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    """Schema for authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token data"""
    user_id: int
    token_type: str

class PaginationParams:
    """
    Pagination parameters for list endpoints
    """
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(10, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.limit = limit
        self.skip = (page - 1) * limit

class PaginationResponse(BaseModel, Generic[T]):
    """
    Pagination response model
    """
    data: List[T]
    total: int
    page: int
    limit: int
    
    @property
    def pages(self) -> int:
        """Calculate total number of pages"""
        return (self.total + self.limit - 1) // self.limit if self.limit > 0 else 0
    
    model_config = ConfigDict(from_attributes=True)

# Utilitários de Segurança
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{API_V1_STR}/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependências
def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
            
        token_data = TokenData(user_id=int(user_id), token_type=token_type)
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if user is None:
        raise credentials_exception
        
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def check_admin_permission(current_user: User = Depends(get_current_active_user)) -> User:
    """Check if user has admin permissions"""
    if current_user.role != UserRole.SUPER_ADMIN and current_user.role != UserRole.DIRETOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user

# Inicialização do app FastAPI
app = FastAPI(
    title=PROJECT_NAME,
    version=PROJECT_VERSION,
    description="HUBB ONE - Assist SaaS API",
    openapi_url=f"{API_V1_STR}/openapi.json",
    docs_url=f"{API_V1_STR}/docs",
    redoc_url=f"{API_V1_STR}/redoc",
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas da API
@app.post(f"{API_V1_STR}/auth/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Create access and refresh tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        subject=user.id, expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@app.post(f"{API_V1_STR}/auth/refresh", response_model=Token)
async def refresh_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get a new access token using refresh token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Create new access and refresh tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        subject=user.id, expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@app.get(f"{API_V1_STR}/users", response_model=List[UserOut])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    pagination: PaginationParams = Depends(),
    name: Optional[str] = Query(None, description="Filter by name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    role: Optional[str] = Query(None, description="Filter by role"),
):
    """
    List all users with pagination and optional filtering.
    Only accessible by authorized users.
    """
    # Base query
    query = db.query(User)
    
    # Apply filters if provided
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if role:
        try:
            role_enum = UserRole(role)
            query = query.filter(User.role == role_enum)
        except ValueError:
            pass  # Invalid role value, ignore filter
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    users = query.offset(pagination.skip).limit(pagination.limit).all()
    
    return {
        "data": users,
        "total": total,
        "page": pagination.page,
        "limit": pagination.limit
    }

@app.get(f"{API_V1_STR}/users/me", response_model=UserOut)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information.
    """
    return current_user

@app.get(f"{API_V1_STR}/users/{{user_id}}", response_model=UserOut)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific user by ID.
    Only accessible by authorized users or the user themselves.
    """
    # Users can see their own profile, admins can see any profile
    is_admin = current_user.role in [UserRole.SUPER_ADMIN, UserRole.DIRETOR]
    if not is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this user",
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@app.post(f"{API_V1_STR}/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new user.
    Only accessible by SUPER_ADMIN or DIRETOR.
    """
    # Check permissions
    if current_user.role != UserRole.SUPER_ADMIN and current_user.role != UserRole.DIRETOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Check if user with this email already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        role=user_in.role,
        is_active=user_in.is_active,
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@app.put(f"{API_V1_STR}/users/{{user_id}}", response_model=UserOut)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a user.
    Users can update their own information, but only SUPER_ADMIN or DIRETOR can update other users.
    """
    # Check permissions
    is_admin = current_user.role in [UserRole.SUPER_ADMIN, UserRole.DIRETOR]
    if not is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Only SUPER_ADMIN can change roles
    if user_in.role is not None and user_in.role != user.role and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to change user role",
        )
    
    # Check if trying to update email to one that already exists
    if user_in.email is not None and user_in.email != user.email:
        existing_user = db.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Update user attributes
    user_data = user_in.model_dump(exclude_unset=True)
    
    # Handle password separately
    if "password" in user_data:
        user_data["password_hash"] = get_password_hash(user_data.pop("password"))
    
    # Update user
    for key, value in user_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    
    return user

@app.delete(f"{API_V1_STR}/users/{{user_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a user.
    Only accessible by SUPER_ADMIN.
    """
    # Check permissions
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Can't delete yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own user account",
        )
    
    # Delete user
    db.delete(user)
    db.commit()
    
    return None

@app.get(f"{API_V1_STR}/status")
async def get_status():
    """
    Get API status.
    """
    return {
        "status": "online",
        "name": PROJECT_NAME,
        "version": PROJECT_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Root endpoint returning HTML page with API info.
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{PROJECT_NAME}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }}
            h1 {{ color: #333; }}
            h2 {{ color: #555; margin-top: 30px; }}
            p {{ margin-bottom: 15px; }}
            code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
            pre {{ background: #f8f8f8; padding: 10px; border-radius: 5px; overflow-x: auto; }}
            .container {{ margin-top: 20px; border: 1px solid #ddd; padding: 20px; border-radius: 5px; }}
            .info {{ color: blue; }}
            .note {{ background: #ffffcc; padding: 10px; border-left: 4px solid #ffcc00; margin-top: 20px; }}
            .endpoints {{ margin-top: 30px; }}
            .endpoint {{ margin-bottom: 15px; }}
            .method {{ display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; margin-right: 5px; }}
            .get {{ background: #61affe; color: white; }}
            .post {{ background: #49cc90; color: white; }}
            .put {{ background: #fca130; color: white; }}
            .delete {{ background: #f93e3e; color: white; }}
        </style>
    </head>
    <body>
        <h1>{PROJECT_NAME} v{PROJECT_VERSION}</h1>
        
        <div class="container">
            <p>Esta API está rodando e você pode acessar a documentação OpenAPI:</p>
            <ul>
                <li><a href="{API_V1_STR}/docs">{API_V1_STR}/docs</a> - Swagger UI (documentação interativa)</li>
                <li><a href="{API_V1_STR}/redoc">{API_V1_STR}/redoc</a> - ReDoc (documentação alternativa)</li>
            </ul>
            <p class="info">A API retorna respostas JSON em todos os endpoints.</p>
        </div>
        
        <h2>Endpoints Disponíveis</h2>
        
        <div class="endpoints">
            <div class="endpoint">
                <span class="method get">GET</span> <code>{API_V1_STR}/status</code> - Status da API
            </div>
            <div class="endpoint">
                <span class="method post">POST</span> <code>{API_V1_STR}/auth/login</code> - Login (Obter Token JWT)
            </div>
            <div class="endpoint">
                <span class="method post">POST</span> <code>{API_V1_STR}/auth/refresh</code> - Renovar Token JWT
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> <code>{API_V1_STR}/users</code> - Listar usuários
            </div>
            <div class="endpoint">
                <span class="method post">POST</span> <code>{API_V1_STR}/users</code> - Criar usuário
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> <code>{API_V1_STR}/users/me</code> - Obter informações do usuário atual
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> <code>{API_V1_STR}/users/{{user_id}}</code> - Obter usuário específico
            </div>
            <div class="endpoint">
                <span class="method put">PUT</span> <code>{API_V1_STR}/users/{{user_id}}</code> - Atualizar usuário
            </div>
            <div class="endpoint">
                <span class="method delete">DELETE</span> <code>{API_V1_STR}/users/{{user_id}}</code> - Excluir usuário
            </div>
        </div>
        
        <div class="note">
            <p>Autenticação: A maioria dos endpoints requer um token JWT. Use <code>{API_V1_STR}/auth/login</code> para obter um token e inclua-o nas requisições subsequentes no cabeçalho <code>Authorization: Bearer [token]</code>.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Inicializar aplicação
if __name__ == "__main__":
    uvicorn.run("single-main:app", host="0.0.0.0", port=5000, reload=True)