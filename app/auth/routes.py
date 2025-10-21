from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.crud import authenticate_user, create_user, get_user_by_username, get_user_by_email
from app.auth.schemas import Token, UserCreate, User
from app.auth.security import create_access_token
from app.auth.dependencies import get_current_active_user
from app.core.config import settings

router = APIRouter()


@router.get("/test-db")
async def test_db(db: Session = Depends(get_db)):
    """Тестовый эндпоинт для проверки работы с базой данных"""
    try:
        # Проверка подключения к БД
        from app.db.crud import get_user_by_username
        user = get_user_by_username(db, "test")
        return {"status": "ok", "user_exists": user is not None}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя
    """
    try:
        # Проверка существования пользователя по имени
        db_user = get_user_by_username(db, username=user.username)
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Username already registered"
            )
        
        # Проверка существования пользователя по email
        db_user = get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        return create_user(db=db, username=user.username, email=user.email, password=user.password)
    except HTTPException:
        raise
    except Exception as e:
        # Логирование ошибки
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error during registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Аутентификация пользователя и получение JWT токена
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Получение информации о текущем пользователе
    """
    return current_user