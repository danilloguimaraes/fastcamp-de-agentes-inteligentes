"""
Example 1 from the Pydantic documentation.

Aqui foi utilizado o pydantic pra fazer uma validação simples, utilizando somente built-in types.
"""
from enum import auto, IntFlag
from typing import Any

# Importando as classes necessárias do pydantic.
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    SecretStr,
    ValidationError,
)

# Definindo uma enumeração para os roles do usuário.
class Role(IntFlag):
    Author = auto()
    Editor = auto()
    Developer = auto()
    Admin = Author | Editor | Developer


# Definindo o modelo do usuário. Herdar de BaseModel é a forma de indicar que a classe é um modelo de dados e 
# com isso, pode utilizar suas propriedades e métodos,como o model_validate.
class User(BaseModel):

    name: str = Field(examples=["Arjan"])
    email: EmailStr = Field(
        examples=["example@arjancodes.com"],
        description="The email address of the user",
        frozen=True,
    )
    password: SecretStr = Field(
        examples=["Password123"], description="The password of the user"
    )
    role: Role = Field(default=None, description="The role of the user")

# Função para validar os dados do usuário. É utilizada para validar os dados do usuário por meio da ... 
# ... classe User, que herda de BaseModel.
def validate(data: dict[str, Any]) -> None:
    try:
        user = User.model_validate(data)

        print("User is valid")
        print(user)
    except ValidationError as e:
        print("User is invalid")
        for error in e.errors():
            print(error)

# Mera inicialização dos dados do usuário e a chamada da função validate.
def main() -> None:
    good_data = {
        "name": "Arjan",
        "email": "example@arjancodes.com",
        "password": "Password123",
    }

    bad_data = {"email": "<bad data>", "password": "<bad data>"}

    validate(good_data)
    validate(bad_data)


if __name__ == "__main__":
    main()