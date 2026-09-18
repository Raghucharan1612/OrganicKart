from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.models.address import Address
from app.models.user import User
from app.core.security import hash_password, verify_password
from app.repositories.address_repository import AddressRepository
from app.repositories.user_repository import UserRepository
from app.schemas.address import AddressCreate, AddressUpdate
from app.schemas.auth import PasswordChangeRequest, UserProfileUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.addresses = AddressRepository(db)

    def update_profile(self, user: User, payload: UserProfileUpdate) -> User:
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        return self.users.update(user)

    def change_password(self, user: User, payload: PasswordChangeRequest) -> None:
        if not verify_password(payload.current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect.")
        user.password_hash = hash_password(payload.new_password)
        self.users.update(user)

    def list_addresses(self, user_id: int) -> list[Address]:
        return self.addresses.list_for_user(user_id)

    def create_address(self, user_id: int, payload: AddressCreate) -> Address:
        if payload.is_default:
            self.addresses.clear_default(user_id)
        return self.addresses.create(Address(user_id=user_id, **payload.model_dump()))

    def update_address(self, user_id: int, address_id: int, payload: AddressUpdate) -> Address:
        address = self._get_address(user_id, address_id)
        update_data = payload.model_dump(exclude_unset=True)
        if update_data.get("is_default") is True:
            self.addresses.clear_default(user_id)
        for field, value in update_data.items():
            setattr(address, field, value)
        return self.addresses.update(address)

    def delete_address(self, user_id: int, address_id: int) -> None:
        self.addresses.delete(self._get_address(user_id, address_id))

    def _get_address(self, user_id: int, address_id: int) -> Address:
        address = self.addresses.get_for_user(user_id, address_id)
        if address is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
        return address
