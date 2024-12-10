from application.auth.commands.register_user_command import RegisterUserCommand
from application.auth.services.auth_code import (
    AuthorizationCodeStorage,
    AuthCodeData,
)
from application.auth.services.pkce import PKCEData, PKCEService
from application.client.commands.validate_client_request import ValidateClientRequest
from application.client.service import ClientService
from application.common.uow import Uow
from application.user.interfaces.repo import UserRepository
from domain.entities.user.model import User
from domain.entities.user.value_objects import Email
from domain.exceptions.user import UserAlreadyExistsError
from domain.common.services.pwd_service import PasswordHasher


class RegisterUserHandler:
    def __init__(
        self,
        user_repository: UserRepository,
        hash_service: PasswordHasher,
        auth_code_storage: AuthorizationCodeStorage,
        client_service: ClientService,
        uow: Uow,
        pkce_service: PKCEService,
    ):
        self.user_repository = user_repository
        self.hash_service = hash_service
        self.auth_code_storage = auth_code_storage
        self.client_service = client_service
        self.uow = uow
        self.pkce_service = pkce_service

    async def handle(self, command: RegisterUserCommand) -> str:
        client = await self.client_service.get_validated_client(
            ValidateClientRequest(
                client_id=command.client_id,
                redirect_url=command.redirect_url,
            )
        )
        existing_user = await self.user_repository.by_email(Email(command.email))
        if existing_user:
            raise UserAlreadyExistsError(existing_user.email.value)

        user_id = User.generate_id()
        user = User.create(
            user_id=user_id,
            role_id=command.role_id,
            email=command.email,
            raw_password=command.password,
            password_hasher=self.hash_service,
        )
        user.clients.append(client)
        await self.user_repository.save(user)

        auth_code = self.auth_code_storage.generate_auth_code()
        pkce_data = PKCEData(
            code_verifier=command.code_verifier,
            code_challenge_method=command.code_challenge_method,
        )

        auth_code_data: AuthCodeData = {
            "user_id": str(user_id),
            "client_id": str(client.id.value),
            "redirect_url": command.redirect_url,
            "code_challenger": self.pkce_service.generate_code_challenge(pkce_data),
        }

        await self.auth_code_storage.store_auth_code_data(
            auth_code, auth_code_data, expiration_time=6000
        )
        await self.uow.commit()
        return auth_code
