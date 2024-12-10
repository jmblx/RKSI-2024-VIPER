from sqlalchemy import (
    Table,
    Column,
    String,
    Boolean,
    Integer,
    ForeignKey,
    UUID as SQLAlchemyUUID,
)
from sqlalchemy.orm import relationship, composite
import uuid

from domain.entities.client.value_objects import ClientID
from domain.entities.role.value_objects import RoleID
from domain.entities.user.model import User
from domain.entities.user.value_objects import UserID, Email, HashedPassword
from infrastructure.db.models.registry import mapper_registry
from infrastructure.db.models.secondary import user_client_association_table

user_table = Table(
    "user",
    mapper_registry.metadata,
    Column("id", SQLAlchemyUUID(as_uuid=True), primary_key=True),
    Column("email", String, nullable=False),
    Column("is_email_confirmed", Boolean, default=False),
    Column("hashed_password", String, nullable=False),
    Column("role_id", Integer, ForeignKey("role.id"), nullable=False),
)

mapper_registry.map_imperatively(
    User,
    user_table,
    properties={
        "id": composite(UserID, user_table.c.id),
        "email": composite(Email, user_table.c.email),
        "hashed_password": composite(HashedPassword, user_table.c.hashed_password),
        "is_email_confirmed": user_table.c.is_email_confirmed,
        "role_id": composite(RoleID, user_table.c.role_id),
        "role": relationship("Role", back_populates="users_role", uselist=False),
        "clients": relationship(
            "Client",
            secondary=user_client_association_table,
            back_populates="users",
            uselist=True,
        ),
    },
    column_prefix="_",
)
