from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import List

from spyne import (
    Application,
    Uuid,
    Array,
    Boolean,
    ComplexModel,
    Integer,
    ServiceBase,
    Unicode,
    rpc,
)
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication


@dataclass
class Org:
    name: str
    id: UUID = field(default_factory=uuid4)


@dataclass
class User:
    name: str
    age: int
    is_active: bool
    org: Org
    id: UUID = field(default_factory=uuid4)


@dataclass
class DB:
    users: List[User]


org = Org(name="reckonsys")
user = User(name="dhilipsiva", age=32, is_active=True, org=org)
db = DB(users=[user])


class OrgModel(ComplexModel):
    name = Unicode
    id = Uuid


class UserModel(ComplexModel):
    name = Unicode
    age = Integer
    is_active = Boolean
    id = Uuid
    org = Org


class UserService(ServiceBase):
    @rpc(_returns=Array(UserModel))
    def list_users(ctx):
        """list the users
        <b>What fun!</b>
        @return the user's array
        """
        print(db.users)
        return db.users

    @rpc(UserModel, _returns=UserModel)
    def add_user(ctx, user: UserModel):
        """list the users
        <b>What fun!</b>
        # @param user the user to create
        @return the user's array
        """
        org = Org(name=user.org)
        user = User(
            name=user.name, age=user.age, is_active=user.is_active, org=org
        )  # noqa: E501

        db.users.append(user)
        return user


application = Application(
    [UserService],
    "com.reckonsys.users",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11(),
)

wsgi_application = WsgiApplication(application)


if __name__ == "__main__":
    import logging
    from wsgiref.simple_server import make_server

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("spyne.protocol.xml").setLevel(logging.DEBUG)

    logging.info("listening to http://127.0.0.1:8000")
    logging.info("wsdl is at: http://localhost:8000/?wsdl")

    server = make_server("127.0.0.1", 8000, wsgi_application)
    server.serve_forever()
