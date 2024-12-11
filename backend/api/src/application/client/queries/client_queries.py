from typing import TypedDict, Any, Mapping

from application.client.commands.validate_client_request import ValidateClientRequest
from application.client.reader import ClientReader
from domain.entities.client.model import Client
from domain.entities.client.value_objects import (
    ClientID,
    ClientRedirectUrl,
    AllowedRedirectUrls,
)
from domain.exceptions.client import ClientNotFound


class ClientAuthResponse(TypedDict):
    client_name: str


class ClientAuthValidationQueryHandler:
    def __init__(self, client_reader: ClientReader):
        self.client_reader = client_reader

    async def handle(self, query: ValidateClientRequest) -> ClientAuthResponse:
        client_data = await self.client_reader.read_for_auth_page(
            ClientID(query.client_id)
        )
        if not client_data:
            raise ClientNotFound()
        print(client_data.allowed_redirect_urls, query.redirect_url, sep="\n")
        Client.validate_redirect_url(
            allowed_redirect_urls=AllowedRedirectUrls(
                client_data.allowed_redirect_urls
            ),
            redirect_url=ClientRedirectUrl(query.redirect_url),
        )
        return {"client_name": client_data.client_name}
