import enum


class RoleEnum(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    FARMER = "FARMER"
    VENDOR = "VENDOR"
    DELIVERY_PARTNER = "DELIVERY_PARTNER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
