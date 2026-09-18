from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_customer
from app.models.user import User
from app.schemas.address import AddressCreate, AddressResponse, AddressUpdate
from app.schemas.auth import PasswordChangeRequest, UserProfileOut, UserProfileUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfileOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserProfileOut)
def update_my_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = UserService(db)
    return service.update_profile(current_user, payload)


@router.post("/me/change-password")
def change_my_password(
    payload: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    UserService(db).change_password(current_user, payload)
    return {"message": "Password changed successfully."}


@router.get("/me/addresses", response_model=list[AddressResponse])
def list_my_addresses(current_user: User = Depends(require_customer), db: Session = Depends(get_db)):
    return UserService(db).list_addresses(current_user.id)


@router.post("/me/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_my_address(payload: AddressCreate, current_user: User = Depends(require_customer), db: Session = Depends(get_db)):
    return UserService(db).create_address(current_user.id, payload)


@router.put("/me/addresses/{address_id}", response_model=AddressResponse)
def update_my_address(address_id: int, payload: AddressUpdate, current_user: User = Depends(require_customer), db: Session = Depends(get_db)):
    return UserService(db).update_address(current_user.id, address_id, payload)


@router.delete("/me/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_address(address_id: int, current_user: User = Depends(require_customer), db: Session = Depends(get_db)):
    UserService(db).delete_address(current_user.id, address_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
