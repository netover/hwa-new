from __future__ import annotations

from inspect import signature as _mutmut_signature
from typing import Annotated, Callable, ClassVar

from fastapi import Request
from fastapi.exceptions import HTTPException
from jose import JWTError

from resync.security.oauth2 import verify_oauth2_token

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


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_orig(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_1(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = None
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_2(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get(None)
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_3(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("XXAuthorizationXX")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_4(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_5(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("AUTHORIZATION")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_6(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token and not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_7(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_8(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_9(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith(None):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_10(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("XXBearer XX"):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_11(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_12(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("BEARER "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_13(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=None, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_14(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail=None)

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_15(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_16(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
            )

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_17(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=402, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_18(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(
                status_code=401, detail="XXMissing Authorization headerXX"
            )

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_19(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="missing authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_20(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="MISSING AUTHORIZATION HEADER")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_21(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = None
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_22(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(None)[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_23(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split("XX XX")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_24(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[2]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_25(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token.split(" ")[1]
        user = None

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_26(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token.split(" ")[1]
        user = await verify_oauth2_token(None)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_27(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = None

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_28(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=None, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_29(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError:
        raise HTTPException(status_code=401, detail=None)

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_30(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_31(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError:
        raise HTTPException(
            status_code=401,
        )

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_32(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=402, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_33(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(None)}")

    # Proceed to next middleware or route handler
    return await call_next(request)


# --- OAuth2 Middleware ---
async def x_oauth2_middleware__mutmut_34(request: Request, call_next: Callable):
    """
    Middleware to enforce OAuth2/JWT authentication for all routes.
    """
    try:
        # Get token from Authorization header
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Verify token
        token_value = token.split(" ")[1]
        user = await verify_oauth2_token(token_value)

        # Add user to request state for downstream use
        request.state.user = user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Proceed to next middleware or route handler
    return await call_next(None)


x_oauth2_middleware__mutmut_mutants: ClassVar[MutantDict] = {
    "x_oauth2_middleware__mutmut_1": x_oauth2_middleware__mutmut_1,
    "x_oauth2_middleware__mutmut_2": x_oauth2_middleware__mutmut_2,
    "x_oauth2_middleware__mutmut_3": x_oauth2_middleware__mutmut_3,
    "x_oauth2_middleware__mutmut_4": x_oauth2_middleware__mutmut_4,
    "x_oauth2_middleware__mutmut_5": x_oauth2_middleware__mutmut_5,
    "x_oauth2_middleware__mutmut_6": x_oauth2_middleware__mutmut_6,
    "x_oauth2_middleware__mutmut_7": x_oauth2_middleware__mutmut_7,
    "x_oauth2_middleware__mutmut_8": x_oauth2_middleware__mutmut_8,
    "x_oauth2_middleware__mutmut_9": x_oauth2_middleware__mutmut_9,
    "x_oauth2_middleware__mutmut_10": x_oauth2_middleware__mutmut_10,
    "x_oauth2_middleware__mutmut_11": x_oauth2_middleware__mutmut_11,
    "x_oauth2_middleware__mutmut_12": x_oauth2_middleware__mutmut_12,
    "x_oauth2_middleware__mutmut_13": x_oauth2_middleware__mutmut_13,
    "x_oauth2_middleware__mutmut_14": x_oauth2_middleware__mutmut_14,
    "x_oauth2_middleware__mutmut_15": x_oauth2_middleware__mutmut_15,
    "x_oauth2_middleware__mutmut_16": x_oauth2_middleware__mutmut_16,
    "x_oauth2_middleware__mutmut_17": x_oauth2_middleware__mutmut_17,
    "x_oauth2_middleware__mutmut_18": x_oauth2_middleware__mutmut_18,
    "x_oauth2_middleware__mutmut_19": x_oauth2_middleware__mutmut_19,
    "x_oauth2_middleware__mutmut_20": x_oauth2_middleware__mutmut_20,
    "x_oauth2_middleware__mutmut_21": x_oauth2_middleware__mutmut_21,
    "x_oauth2_middleware__mutmut_22": x_oauth2_middleware__mutmut_22,
    "x_oauth2_middleware__mutmut_23": x_oauth2_middleware__mutmut_23,
    "x_oauth2_middleware__mutmut_24": x_oauth2_middleware__mutmut_24,
    "x_oauth2_middleware__mutmut_25": x_oauth2_middleware__mutmut_25,
    "x_oauth2_middleware__mutmut_26": x_oauth2_middleware__mutmut_26,
    "x_oauth2_middleware__mutmut_27": x_oauth2_middleware__mutmut_27,
    "x_oauth2_middleware__mutmut_28": x_oauth2_middleware__mutmut_28,
    "x_oauth2_middleware__mutmut_29": x_oauth2_middleware__mutmut_29,
    "x_oauth2_middleware__mutmut_30": x_oauth2_middleware__mutmut_30,
    "x_oauth2_middleware__mutmut_31": x_oauth2_middleware__mutmut_31,
    "x_oauth2_middleware__mutmut_32": x_oauth2_middleware__mutmut_32,
    "x_oauth2_middleware__mutmut_33": x_oauth2_middleware__mutmut_33,
    "x_oauth2_middleware__mutmut_34": x_oauth2_middleware__mutmut_34,
}


def oauth2_middleware(*args, **kwargs):
    result = _mutmut_trampoline(
        x_oauth2_middleware__mutmut_orig,
        x_oauth2_middleware__mutmut_mutants,
        args,
        kwargs,
    )
    return result


oauth2_middleware.__signature__ = _mutmut_signature(x_oauth2_middleware__mutmut_orig)
x_oauth2_middleware__mutmut_orig.__name__ = "x_oauth2_middleware"
