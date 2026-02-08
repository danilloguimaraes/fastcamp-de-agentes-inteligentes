"""
Example 2 from the Pydantic documentation.

Aqui foi utilizado o pydantic pra fazer uma validação mais complexa, utilizando built-in types e enumerações.
"""

import enum
import hashlib
import re
from typing import Any

# Importando as classes necessárias do pydantic. 
# BaseModel: classe básica do Pydantic que identifica as regras de validação de dados de uma instância.
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
    SecretStr,
    ValidationError,
)

# Definindo as expressões regulares para validar o nome e a senha do usuário.
VALID_PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")
VALID_NAME_REGEX = re.compile(r"^[a-zA-Z]{2,}$")


# Definindo uma enumeração para os roles do usuário.
class Role(enum.IntFlag):
    Author = 1
    Editor = 2
    Admin = 4
    SuperAdmin = 8


# Definindo o modelo de dados do usuário.
class User(BaseModel):
    # Definindo a validação do nome do usuário, utilizando Field_Validator.
    name: str = Field(examples=["Arjan"])

    # Definindo a validação do email do usuário, utilizando Field_Validator.
    email: EmailStr = Field(
        examples=["user@arjancodes.com"],
        description="The email address of the user",
        frozen=True,
    )

    # Definindo a validação da senha do usuário, utilizando Field_Validator.
    password: SecretStr = Field(
        examples=["Password123"], description="The password of the user"
    )

    # Definindo a validação do role do usuário, utilizando Field_Validator.
    role: Role = Field(
        default=None, description="The role of the user", examples=[1, 2, 4, 8]
    )

    # Definindo a validação do nome do usuário, utilizando Field_Validator.
    # classmethod annotation indica que é um método de classe e não de instância.
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not VALID_NAME_REGEX.match(v):
            raise ValueError(
                "Name is invalid, must contain only letters and be at least 2 characters long"
            )
        return v

    # Definindo a validação do role do usuário, utilizando Field_Validator. Mode: before indica que a validação será feita antes de qualquer outra validação, pois 
    # o valor ainda não foi convertido para o tipo Role.
    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, v: int | str | Role) -> Role:
        op = {int: lambda x: Role(x), str: lambda x: Role[x], Role: lambda x: x}
        try:
            return op[type(v)](v)
        except (KeyError, ValueError):
            raise ValueError(
                f"Role is invalid, please use one of the following: {', '.join([x.name for x in Role])}"
            )

    # Definindo a validação do usuário, utilizando Model_Validator. Aqui é possível validar os dados do usuário de forma mais complexa, como a validação de senha e nome.
    # Aqui o objeto de validação é o próprio modelo de dados do usuário, e não um campo específico. Aqui temos condições de validar dados de usuários simultâneamente e 
    # considerando que um atributo pode depender de outro.
    @model_validator(mode="before")
    @classmethod
    def validate_user(cls, v: dict[str, Any]) -> dict[str, Any]:
        if "name" not in v or "password" not in v:
            raise ValueError("Name and password are required")
        if v["name"].casefold() in v["password"].casefold():
            raise ValueError("Password cannot contain name")
        if not VALID_PASSWORD_REGEX.match(v["password"]):
            raise ValueError(
                "Password is invalid, must contain 8 characters, 1 uppercase, 1 lowercase, 1 number"
            )
        v["password"] = hashlib.sha256(v["password"].encode()).hexdigest()
        return v

# Função para validar os dados do usuário. É utilizada para validar os dados do usuário por meio da ... 
# ... classe User, que herda de BaseModel. 
def validate(data: dict[str, Any]) -> None:
    try:
        user = User.model_validate(data)
        print(user)
    except ValidationError as e:
        print("User is invalid:")
        print(e)


# Inicialização dos dados do usuário e a chamada da função validate. Aqui ele aumentou o número e tipos de testes, 
# para validar os dados do usuário, possibilitando uma validação mais robusta e testando diferentes cenários de erro.
def main() -> None:
    test_data = dict(
        good_data={
            "name": "Arjan",
            "email": "example@arjancodes.com",
            "password": "Password123",
            "role": "Admin",
        },
        bad_role={
            "name": "Arjan",
            "email": "example@arjancodes.com",
            "password": "Password123",
            "role": "Programmer",
        },
        bad_data={
            "name": "Arjan",
            "email": "bad email",
            "password": "bad password",
        },
        bad_name={
            "name": "Arjan<-_->",
            "email": "example@arjancodes.com",
            "password": "Password123",
        },
        duplicate={
            "name": "Arjan",
            "email": "example@arjancodes.com",
            "password": "Arjan123",
        },
        missing_data={
            "email": "<bad data>",
            "password": "<bad data>",
        },
    )

    for example_name, data in test_data.items():
        print(example_name)
        validate(data)
        print()


if __name__ == "__main__":
    main()