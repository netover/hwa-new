from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- JWT Configuration ---
# These values should be read from settings in production
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dummy-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- OAuth2 Setup ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
from inspect import signature as _mutmut_signature
from typing import Annotated, Callable, ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg=None):
    """Forward call to original or mutated function, depending on the environment"""
    import os

    mutant_under_test = os.environ["MUTANT_UNDER_TEST"]
    if mutant_under_test == "fail":
        from mutmut.__main__ import MutmutProgrammaticFailException

        raise MutmutProgrammaticFailException("Failed programmatically")
    elif mutant_under_test == "stats":
        from mutmut.__main__ import record_trampoline_hit

        record_trampoline_hit(orig.__module__ + "." + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + "." + orig.__name__ + "__mutmut_"
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition(".")[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


# --- Token Models ---
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# --- Simulated User Database ---
# In a real application, this would connect to a user database
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$gSr1dl6RMwezmdFTjwvLmuRJTmh5WuV5K7t9kTPB6Z7vju1zLzgRG",
        "disabled": False,
    }
}


# --- Token Functions ---
def x_create_access_token__mutmut_orig(
    data: dict, expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Token Functions ---
def x_create_access_token__mutmut_1(
    data: dict, expires_delta: Optional[timedelta] = None
):
    to_encode = None
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Token Functions ---
def x_create_access_token__mutmut_2(
    data: dict, expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = None
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Token Functions ---
def x_create_access_token__mutmut_3(
    data: dict, expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.utcnow() - (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Token Functions ---
def x_create_access_token__mutmut_4(
    data: dict, expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta and timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Token Functions ---
def x_create_access_token__mutmut_5(
    data: dict, expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=None))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Token Functions ---
def x_create_access_token__mutmut_6(
    data: dict, expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=16))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Token Functions ---
def x_create_access_token__mutmut_7(
    data: dict, expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update(None)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Token Functions ---
def x_create_access_token__mutmut_8(
    data: dict, expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"XXexpXX": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Token Functions ---
def x_create_access_token__mutmut_9(
    data: dict, expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"EXP": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Token Functions ---
def x_create_access_token__mutmut_10(
    data: dict, expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = None
    return encoded_jwt


# --- Token Functions ---
def x_create_access_token__mutmut_11(
    data: dict, expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(None, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Token Functions ---
def x_create_access_token__mutmut_12(
    data: dict, expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, None, algorithm=ALGORITHM)
    return encoded_jwt


# --- Token Functions ---
def x_create_access_token__mutmut_13(
    data: dict, expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=None)
    return encoded_jwt


# --- Token Functions ---
def x_create_access_token__mutmut_14(
    data: dict, expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Token Functions ---
def x_create_access_token__mutmut_15(
    data: dict, expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, algorithm=ALGORITHM)
    return encoded_jwt


# --- Token Functions ---
def x_create_access_token__mutmut_16(
    data: dict, expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
    )
    return encoded_jwt


x_create_access_token__mutmut_mutants: ClassVar[MutantDict] = {
    "x_create_access_token__mutmut_1": x_create_access_token__mutmut_1,
    "x_create_access_token__mutmut_2": x_create_access_token__mutmut_2,
    "x_create_access_token__mutmut_3": x_create_access_token__mutmut_3,
    "x_create_access_token__mutmut_4": x_create_access_token__mutmut_4,
    "x_create_access_token__mutmut_5": x_create_access_token__mutmut_5,
    "x_create_access_token__mutmut_6": x_create_access_token__mutmut_6,
    "x_create_access_token__mutmut_7": x_create_access_token__mutmut_7,
    "x_create_access_token__mutmut_8": x_create_access_token__mutmut_8,
    "x_create_access_token__mutmut_9": x_create_access_token__mutmut_9,
    "x_create_access_token__mutmut_10": x_create_access_token__mutmut_10,
    "x_create_access_token__mutmut_11": x_create_access_token__mutmut_11,
    "x_create_access_token__mutmut_12": x_create_access_token__mutmut_12,
    "x_create_access_token__mutmut_13": x_create_access_token__mutmut_13,
    "x_create_access_token__mutmut_14": x_create_access_token__mutmut_14,
    "x_create_access_token__mutmut_15": x_create_access_token__mutmut_15,
    "x_create_access_token__mutmut_16": x_create_access_token__mutmut_16,
}


def create_access_token(*args, **kwargs):
    result = _mutmut_trampoline(
        x_create_access_token__mutmut_orig,
        x_create_access_token__mutmut_mutants,
        args,
        kwargs,
    )
    return result


create_access_token.__signature__ = _mutmut_signature(
    x_create_access_token__mutmut_orig
)
x_create_access_token__mutmut_orig.__name__ = "x_create_access_token"


def x_get_user__mutmut_orig(db, username: str):
    if username in db:
        return db[username]


def x_get_user__mutmut_1(db, username: str):
    if username not in db:
        return db[username]


x_get_user__mutmut_mutants: ClassVar[MutantDict] = {
    "x_get_user__mutmut_1": x_get_user__mutmut_1
}


def get_user(*args, **kwargs):
    result = _mutmut_trampoline(
        x_get_user__mutmut_orig, x_get_user__mutmut_mutants, args, kwargs
    )
    return result


get_user.__signature__ = _mutmut_signature(x_get_user__mutmut_orig)
x_get_user__mutmut_orig.__name__ = "x_get_user"


def x_authenticate_user__mutmut_orig(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    # In real application, compare password with hashed_password
    if not pwd_context.verify(password, user["hashed_password"]):
        return False
    return user


def x_authenticate_user__mutmut_1(fake_db, username: str, password: str):
    user = None
    if not user:
        return False
    # In real application, compare password with hashed_password
    if not pwd_context.verify(password, user["hashed_password"]):
        return False
    return user


def x_authenticate_user__mutmut_2(fake_db, username: str, password: str):
    user = get_user(None, username)
    if not user:
        return False
    # In real application, compare password with hashed_password
    if not pwd_context.verify(password, user["hashed_password"]):
        return False
    return user


def x_authenticate_user__mutmut_3(fake_db, username: str, password: str):
    user = get_user(fake_db, None)
    if not user:
        return False
    # In real application, compare password with hashed_password
    if not pwd_context.verify(password, user["hashed_password"]):
        return False
    return user


def x_authenticate_user__mutmut_4(fake_db, username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    # In real application, compare password with hashed_password
    if not pwd_context.verify(password, user["hashed_password"]):
        return False
    return user


def x_authenticate_user__mutmut_5(fake_db, username: str, password: str):
    user = get_user(
        fake_db,
    )
    if not user:
        return False
    # In real application, compare password with hashed_password
    if not pwd_context.verify(password, user["hashed_password"]):
        return False
    return user


def x_authenticate_user__mutmut_6(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if user:
        return False
    # In real application, compare password with hashed_password
    if not pwd_context.verify(password, user["hashed_password"]):
        return False
    return user


def x_authenticate_user__mutmut_7(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return True
    # In real application, compare password with hashed_password
    if not pwd_context.verify(password, user["hashed_password"]):
        return False
    return user


def x_authenticate_user__mutmut_8(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    # In real application, compare password with hashed_password
    if pwd_context.verify(password, user["hashed_password"]):
        return False
    return user


def x_authenticate_user__mutmut_9(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    # In real application, compare password with hashed_password
    if not pwd_context.verify(None, user["hashed_password"]):
        return False
    return user


def x_authenticate_user__mutmut_10(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    # In real application, compare password with hashed_password
    if not pwd_context.verify(password, None):
        return False
    return user


def x_authenticate_user__mutmut_11(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    # In real application, compare password with hashed_password
    if not pwd_context.verify(user["hashed_password"]):
        return False
    return user


def x_authenticate_user__mutmut_12(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    # In real application, compare password with hashed_password
    if not pwd_context.verify(
        password,
    ):
        return False
    return user


def x_authenticate_user__mutmut_13(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    # In real application, compare password with hashed_password
    if not pwd_context.verify(password, user["XXhashed_passwordXX"]):
        return False
    return user


def x_authenticate_user__mutmut_14(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    # In real application, compare password with hashed_password
    if not pwd_context.verify(password, user["HASHED_PASSWORD"]):
        return False
    return user


def x_authenticate_user__mutmut_15(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    # In real application, compare password with hashed_password
    if not pwd_context.verify(password, user["hashed_password"]):
        return True
    return user


x_authenticate_user__mutmut_mutants: ClassVar[MutantDict] = {
    "x_authenticate_user__mutmut_1": x_authenticate_user__mutmut_1,
    "x_authenticate_user__mutmut_2": x_authenticate_user__mutmut_2,
    "x_authenticate_user__mutmut_3": x_authenticate_user__mutmut_3,
    "x_authenticate_user__mutmut_4": x_authenticate_user__mutmut_4,
    "x_authenticate_user__mutmut_5": x_authenticate_user__mutmut_5,
    "x_authenticate_user__mutmut_6": x_authenticate_user__mutmut_6,
    "x_authenticate_user__mutmut_7": x_authenticate_user__mutmut_7,
    "x_authenticate_user__mutmut_8": x_authenticate_user__mutmut_8,
    "x_authenticate_user__mutmut_9": x_authenticate_user__mutmut_9,
    "x_authenticate_user__mutmut_10": x_authenticate_user__mutmut_10,
    "x_authenticate_user__mutmut_11": x_authenticate_user__mutmut_11,
    "x_authenticate_user__mutmut_12": x_authenticate_user__mutmut_12,
    "x_authenticate_user__mutmut_13": x_authenticate_user__mutmut_13,
    "x_authenticate_user__mutmut_14": x_authenticate_user__mutmut_14,
    "x_authenticate_user__mutmut_15": x_authenticate_user__mutmut_15,
}


def authenticate_user(*args, **kwargs):
    result = _mutmut_trampoline(
        x_authenticate_user__mutmut_orig,
        x_authenticate_user__mutmut_mutants,
        args,
        kwargs,
    )
    return result


authenticate_user.__signature__ = _mutmut_signature(x_authenticate_user__mutmut_orig)
x_authenticate_user__mutmut_orig.__name__ = "x_authenticate_user"


def x_verify_oauth2_token__mutmut_orig(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_1(token: str = Depends(oauth2_scheme)):
    credentials_exception = None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_2(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=None,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_3(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=None,
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_4(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers=None,
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_5(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_6(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_7(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_8(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="XXCould not validate credentialsXX",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_9(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_10(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="COULD NOT VALIDATE CREDENTIALS",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_11(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"XXWWW-AuthenticateXX": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_12(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"www-authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_13(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-AUTHENTICATE": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_14(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "XXBearerXX"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_15(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_16(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "BEARER"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_17(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = None
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_18(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(None, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_19(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, None, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_20(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=None)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_21(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_22(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_23(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_24(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = None
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_25(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get(None)
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_26(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("XXsubXX")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_27(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("SUB")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_28(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is not None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_29(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = None
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_30(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=None)
        user = get_user(fake_users_db, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_31(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = None
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_32(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(None, token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_33(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, None)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_34(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_35(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(
            fake_users_db,
        )
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def x_verify_oauth2_token__mutmut_36(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(fake_users_db, token_data.username)
        if user is not None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


x_verify_oauth2_token__mutmut_mutants: ClassVar[MutantDict] = {
    "x_verify_oauth2_token__mutmut_1": x_verify_oauth2_token__mutmut_1,
    "x_verify_oauth2_token__mutmut_2": x_verify_oauth2_token__mutmut_2,
    "x_verify_oauth2_token__mutmut_3": x_verify_oauth2_token__mutmut_3,
    "x_verify_oauth2_token__mutmut_4": x_verify_oauth2_token__mutmut_4,
    "x_verify_oauth2_token__mutmut_5": x_verify_oauth2_token__mutmut_5,
    "x_verify_oauth2_token__mutmut_6": x_verify_oauth2_token__mutmut_6,
    "x_verify_oauth2_token__mutmut_7": x_verify_oauth2_token__mutmut_7,
    "x_verify_oauth2_token__mutmut_8": x_verify_oauth2_token__mutmut_8,
    "x_verify_oauth2_token__mutmut_9": x_verify_oauth2_token__mutmut_9,
    "x_verify_oauth2_token__mutmut_10": x_verify_oauth2_token__mutmut_10,
    "x_verify_oauth2_token__mutmut_11": x_verify_oauth2_token__mutmut_11,
    "x_verify_oauth2_token__mutmut_12": x_verify_oauth2_token__mutmut_12,
    "x_verify_oauth2_token__mutmut_13": x_verify_oauth2_token__mutmut_13,
    "x_verify_oauth2_token__mutmut_14": x_verify_oauth2_token__mutmut_14,
    "x_verify_oauth2_token__mutmut_15": x_verify_oauth2_token__mutmut_15,
    "x_verify_oauth2_token__mutmut_16": x_verify_oauth2_token__mutmut_16,
    "x_verify_oauth2_token__mutmut_17": x_verify_oauth2_token__mutmut_17,
    "x_verify_oauth2_token__mutmut_18": x_verify_oauth2_token__mutmut_18,
    "x_verify_oauth2_token__mutmut_19": x_verify_oauth2_token__mutmut_19,
    "x_verify_oauth2_token__mutmut_20": x_verify_oauth2_token__mutmut_20,
    "x_verify_oauth2_token__mutmut_21": x_verify_oauth2_token__mutmut_21,
    "x_verify_oauth2_token__mutmut_22": x_verify_oauth2_token__mutmut_22,
    "x_verify_oauth2_token__mutmut_23": x_verify_oauth2_token__mutmut_23,
    "x_verify_oauth2_token__mutmut_24": x_verify_oauth2_token__mutmut_24,
    "x_verify_oauth2_token__mutmut_25": x_verify_oauth2_token__mutmut_25,
    "x_verify_oauth2_token__mutmut_26": x_verify_oauth2_token__mutmut_26,
    "x_verify_oauth2_token__mutmut_27": x_verify_oauth2_token__mutmut_27,
    "x_verify_oauth2_token__mutmut_28": x_verify_oauth2_token__mutmut_28,
    "x_verify_oauth2_token__mutmut_29": x_verify_oauth2_token__mutmut_29,
    "x_verify_oauth2_token__mutmut_30": x_verify_oauth2_token__mutmut_30,
    "x_verify_oauth2_token__mutmut_31": x_verify_oauth2_token__mutmut_31,
    "x_verify_oauth2_token__mutmut_32": x_verify_oauth2_token__mutmut_32,
    "x_verify_oauth2_token__mutmut_33": x_verify_oauth2_token__mutmut_33,
    "x_verify_oauth2_token__mutmut_34": x_verify_oauth2_token__mutmut_34,
    "x_verify_oauth2_token__mutmut_35": x_verify_oauth2_token__mutmut_35,
    "x_verify_oauth2_token__mutmut_36": x_verify_oauth2_token__mutmut_36,
}


def verify_oauth2_token(*args, **kwargs):
    result = _mutmut_trampoline(
        x_verify_oauth2_token__mutmut_orig,
        x_verify_oauth2_token__mutmut_mutants,
        args,
        kwargs,
    )
    return result


verify_oauth2_token.__signature__ = _mutmut_signature(
    x_verify_oauth2_token__mutmut_orig
)
x_verify_oauth2_token__mutmut_orig.__name__ = "x_verify_oauth2_token"
