from datetime import datetime
from hashlib import sha256
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, EmailStr, Field, SecretStr, field_serializer, field_validator, UUID4

app = FastAPI()

# Converter de string para hash SHA256.
def sha256_hex(value: str) -> str:
    return sha256(value.encode()).hexdigest()


# Definindo o modelo de dados do usuário
class User(BaseModel):

    
    model_config = {
        # extra: forbid indica que qualquer campo que não foi definido no modelo de dados será considerado um erro.
        "extra": "forbid",
    }
    __users__ = []

    name: str = Field(..., description="Name of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    password_sha256: str = Field(..., description="Password hash (SHA256)")
    friends: list[UUID4] = Field(
        default_factory=list, max_length=500, description="List of friends"
    )
    blocked: list[UUID4] = Field(
        default_factory=list, max_length=500, description="List of blocked users"
    )
    signup_ts: Optional[datetime] = Field(
        default_factory=datetime.now, description="Signup timestamp", kw_only=True
    )
    id: UUID4 = Field(
        default_factory=uuid4, description="Unique identifier", kw_only=True
    )

    # Validator que converte a senha em hash SHA256 antes de salvar.
    # Assim, a senha nunca é armazenada em texto plano.
    @field_validator("password_sha256", mode="before")
    @classmethod
    def normalize_password_hash(cls, v: str) -> str:

        # Se já for um hash SHA256 (64 chars hex), não re-hashar
        if isinstance(v, str) and len(v) == 64:
            try:
                int(v, 16)
                return v
            except ValueError:
                pass
        return sha256_hex(v)

    # Serialização do id do usuário, utilizando Field_Serializer.
    @field_serializer("id", when_used="json")
    def serialize_id(self, id: UUID4) -> str:
        return str(id)

# Modelo de resposta que exclui a senha do retorno da API.
# Isso demonstra o uso de herança e configuração de campos no Pydantic.
class UserResponse(BaseModel):
    model_config = {
        # extra: forbid indica que qualquer campo que não foi definido no modelo de dados será considerado um erro.
        "extra": "forbid",
    }
    name: str
    email: EmailStr
    friends: list[UUID4] = Field(default_factory=list)
    blocked: list[UUID4] = Field(default_factory=list)
    signup_ts: Optional[datetime] = None
    id: UUID4

    @field_serializer("id", when_used="json")
    def serialize_id(self, id: UUID4) -> str:
        return str(id)


# Modelo para criação de usuário (recebe senha em texto).
class CreateUserRequest(BaseModel):
    model_config = {
        # extra: forbid indica que qualquer campo que não foi definido no modelo de dados será considerado um erro.
        "extra": "forbid",
    }
    name: str = Field(..., description="Name of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    password: SecretStr = Field(..., description="Password of the user")


# Modelo para login, utilizando SecretStr para não expor a senha em logs.
class LoginRequest(BaseModel):
    model_config = {
        # extra: forbid indica que qualquer campo que não foi definido no modelo de dados será considerado um erro.
        "extra": "forbid",
    }
    email: EmailStr = Field(..., description="Email address of the user")
    password: SecretStr = Field(..., description="Password of the user")


# Modelo para atualização de senha.
class UpdatePasswordRequest(BaseModel):
    model_config = {
        # extra: forbid indica que qualquer campo que não foi definido no modelo de dados será considerado um erro.
        "extra": "forbid",
    }
    current_password: SecretStr
    new_password: SecretStr


# Definição de endpoints da API com FastAPI.
# Suas definições tem o único propósito de testar as funcionalidades definidas nos modelos do Pydantic.

@app.get("/users", response_model=list[UserResponse])
async def get_users() -> list[UserResponse]:
    return list(User.__users__)


@app.post("/users", response_model=UserResponse)
async def create_user(user: CreateUserRequest):
    new_user = User(
        name=user.name,
        email=user.email,
        password_sha256=sha256_hex(user.password.get_secret_value()),
    )
    User.__users__.append(new_user)
    return new_user


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID4) -> UserResponse | JSONResponse:
    try:
        return next((user for user in User.__users__ if user.id == user_id))
    except StopIteration:
        return JSONResponse(status_code=404, content={"message": "User not found"})


@app.post("/login")
async def login(request: LoginRequest):
    password_hash = sha256_hex(request.password.get_secret_value())
    try:
        user = next(
            u for u in User.__users__
            if u.email == request.email and u.password_sha256 == password_hash
        )
        return {"message": "Login successful", "user_id": str(user.id)}
    except StopIteration:
        return JSONResponse(status_code=401, content={"message": "Invalid credentials"})


@app.put("/users/{user_id}/password")
async def update_password(user_id: UUID4, request: UpdatePasswordRequest):
    try:
        user = next(u for u in User.__users__ if u.id == user_id)
    except StopIteration:
        return JSONResponse(status_code=404, content={"message": "User not found"})

    current_hash = sha256_hex(request.current_password.get_secret_value())
    if user.password_sha256 != current_hash:
        return JSONResponse(status_code=401, content={"message": "Current password is incorrect"})

    new_hash = sha256_hex(request.new_password.get_secret_value())
    # Recria o usuário com a nova senha (Pydantic models são imutáveis por padrão).
    updated_user = user.model_copy(update={"password_sha256": new_hash})
    idx = User.__users__.index(user)
    User.__users__[idx] = updated_user
    return {"message": "Password updated successfully"}


# Testes para o endpoint realizados com o TestClient.
def main() -> None:
    with TestClient(app) as client:
        # Limpa a lista de usuários antes dos testes
        User.__users__.clear()

        for i in range(5):
            response = client.post(
                "/users",
                json={"name": f"User {i}", "email": f"example{i}@arjancodes.com", "password": f"pass{i}"},
            )
            assert response.status_code == 200
            assert response.json()["name"] == f"User {i}", (
                "The name of the user should be User {i}"
            )
            assert response.json()["id"], "The user should have an id"
            # A senha não deve aparecer na resposta (UserResponse não inclui password)
            assert "password" not in response.json(), "Password should not be in response"

        response = client.get("/users")
        assert response.status_code == 200, "Response code should be 200"
        assert len(response.json()) == 5, "There should be 5 users"
        # Verifica que nenhum usuário retornado possui o campo password
        for u in response.json():
            assert "password" not in u, "Password should not be in list response"

        response = client.post(
            "/users", json={"name": "User 5", "email": "example5@arjancodes.com", "password": "secret123"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "User 5"
        assert "password" not in response.json(), "Password should not be in response"
        user_5_id = response.json()["id"]

        response = client.get(f"/users/{user_5_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "User 5"

        response = client.get(f"/users/{uuid4()}")
        assert response.status_code == 404
        assert response.json()["message"] == "User not found"

        response = client.post("/users", json={"name": "User 6", "email": "wrong", "password": "abc"})
        assert response.status_code == 422, "The email address should be invalid"

        # Testa que criar usuário sem password retorna erro de validação
        response = client.post("/users", json={"name": "User 7", "email": "user7@test.com"})
        assert response.status_code == 422, "Password is required"

        # --- Testes de Login ---
        # Login com credenciais corretas
        response = client.post("/login", json={"email": "example5@arjancodes.com", "password": "secret123"})
        assert response.status_code == 200, "Login should succeed"
        assert response.json()["message"] == "Login successful"
        assert response.json()["user_id"] == user_5_id

        # Login com senha errada
        response = client.post("/login", json={"email": "example5@arjancodes.com", "password": "wrong"})
        assert response.status_code == 401, "Login should fail with wrong password"
        assert response.json()["message"] == "Invalid credentials"

        # Login com email inexistente
        response = client.post("/login", json={"email": "nobody@test.com", "password": "abc"})
        assert response.status_code == 401, "Login should fail with unknown email"

        # --- Testes de Update Password ---
        # Troca de senha com senha atual correta
        response = client.put(
            f"/users/{user_5_id}/password",
            json={"current_password": "secret123", "new_password": "newsecret456"},
        )
        assert response.status_code == 200, "Password update should succeed"
        assert response.json()["message"] == "Password updated successfully"

        # Login com a senha antiga deve falhar
        response = client.post("/login", json={"email": "example5@arjancodes.com", "password": "secret123"})
        assert response.status_code == 401, "Old password should no longer work"

        # Login com a nova senha deve funcionar
        response = client.post("/login", json={"email": "example5@arjancodes.com", "password": "newsecret456"})
        assert response.status_code == 200, "New password should work"

        # Troca de senha com senha atual errada
        response = client.put(
            f"/users/{user_5_id}/password",
            json={"current_password": "wrong", "new_password": "another"},
        )
        assert response.status_code == 401, "Should reject wrong current password"

        # Troca de senha para usuário inexistente
        response = client.put(
            f"/users/{uuid4()}/password",
            json={"current_password": "a", "new_password": "b"},
        )
        assert response.status_code == 404, "Should return not found"

        # Verifica que a senha é armazenada como hash SHA256 (não texto plano)
        user_obj = next(u for u in User.__users__ if str(u.id) == user_5_id)
        stored_password = user_obj.password_sha256
        assert len(stored_password) == 64, "Password should be stored as SHA256 hash"
        assert stored_password == sha256("newsecret456".encode()).hexdigest(), (
            "Stored hash should match SHA256 of the password"
        )

        print("All tests passed!")


if __name__ == "__main__":
    main()