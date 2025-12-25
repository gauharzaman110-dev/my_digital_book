from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from passlib.context import CryptContext

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize bearer token authentication
security = HTTPBearer()


class AuthMiddleware:
    def __init__(self):
        # Using a secret key from environment or default (in production, always use env var)
        self.secret_key = os.getenv("JWT_SECRET_KEY", "default_secret_key_for_development")
        self.algorithm = "HS256"
        self.token_expiry_hours = 24
    
    def create_access_token(self, data: dict) -> str:
        """
        Create a new access token with expiry.
        
        Args:
            data: Data to encode in the token
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Decoded token data if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)


# Global instance
auth_middleware = AuthMiddleware()


# Dependency to get current user from token
async def get_current_user(request: Request) -> Optional[dict]:
    """
    Get the current user from the authorization header.
    
    Args:
        request: The incoming request
        
    Returns:
        User data from the token or raises HTTPException
    """
    credentials: HTTPAuthorizationCredentials = await security(request)
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = auth_middleware.verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data