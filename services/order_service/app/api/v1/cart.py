from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.session import get_db
from app.schemas.cart import CartItemCreate, CartItemResponse, CartItemUpdate, CartResponse
from app.services.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["cart"])
security = HTTPBearer(auto_error=False)


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated.",
        )
    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if payload.get("role", "CUSTOMER") != "CUSTOMER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can access cart operations.",
        )
    return int(payload["sub"])


@router.get("", response_model=CartResponse)
def get_cart(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    cart = CartService(db).get_cart(user_id)
    items = [
        CartItemResponse(
            id=item.id,
            cart_id=item.cart_id,
            product_id=item.product_id,
            product_name=item.product_name,
            unit_price=item.unit_price,
            quantity=item.quantity,
            image_url=item.image_url,
            unit=item.unit,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in cart.items
    ]
    return CartResponse(id=cart.id, user_id=cart.user_id, items=items, created_at=cart.created_at, updated_at=cart.updated_at)


@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_item(payload: CartItemCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    item = CartService(db).add_item(user_id, payload)
    return CartItemResponse(
        id=item.id,
        cart_id=item.cart_id,
        product_id=item.product_id,
        product_name=item.product_name,
        unit_price=item.unit_price,
        quantity=item.quantity,
        image_url=item.image_url,
        unit=item.unit,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.put("/items/{item_id}", response_model=CartItemResponse)
def update_item(item_id: int, payload: CartItemUpdate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    item = CartService(db).update_item(user_id, item_id, payload)
    return CartItemResponse(
        id=item.id,
        cart_id=item.cart_id,
        product_id=item.product_id,
        product_name=item.product_name,
        unit_price=item.unit_price,
        quantity=item.quantity,
        image_url=item.image_url,
        unit=item.unit,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(item_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    CartService(db).remove_item(user_id, item_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    CartService(db).clear_cart(user_id)
