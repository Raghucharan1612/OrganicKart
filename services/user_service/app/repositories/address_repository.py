from sqlalchemy.orm import Session

from app.models.address import Address


class AddressRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: int) -> list[Address]:
        return self.db.query(Address).filter(Address.user_id == user_id).order_by(Address.is_default.desc(), Address.created_at.desc()).all()

    def get_for_user(self, user_id: int, address_id: int) -> Address | None:
        return self.db.query(Address).filter(Address.id == address_id, Address.user_id == user_id).first()

    def clear_default(self, user_id: int) -> None:
        self.db.query(Address).filter(Address.user_id == user_id, Address.is_default.is_(True)).update({Address.is_default: False})

    def create(self, address: Address) -> Address:
        self.db.add(address)
        self.db.commit()
        self.db.refresh(address)
        return address

    def update(self, address: Address) -> Address:
        self.db.commit()
        self.db.refresh(address)
        return address

    def delete(self, address: Address) -> None:
        self.db.delete(address)
        self.db.commit()
