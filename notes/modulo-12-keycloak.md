# Módulo 12 - Autenticação com Keycloak

# Aula 1 - Configurando o Keycloak

```dockerfile
  keycloak:
    image: quay.io/keycloak/keycloak:26.0
    container_name: keycloak
    ports:
      - "8080:8080"
    environment:
      KEYCLOAK_ADMIN: ${KEYCLOAK_ADMIN:-admin}
      KEYCLOAK_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD:-admin}
    command: ["start-dev"]  # Para não precisar configurar um banco de dados
    volumes:
      - keycloak_data:/opt/keycloak/data
```
1. Criar .env
2. Criar um Realm: codeflix
3. Criar um Client: codeflix-list-api
4. Criar um User (completo - email verified!)
5. Definir password para o usuário ("Temporary" - desligado)
6. Gerar um token para o usuário
    ```bash
    curl --request POST \
      --url http://localhost:8080/realms/codeflix/protocol/openid-connect/token \
      --header 'Content-Type: application/x-www-form-urlencoded' \
      --data 'grant_type=password&client_id=codeflix-list-api&username=john&password=admin'
    ```
7. Verificar token em: https://jwt.io/
   - "aud": "account" 
   - "alg": "RS256"


# Aula 2 - Rota com autenticação

- Instalar PyJWT
```bash
pip install pyjwt
```
- Documentação JWT sobre como decodificar um token RS256: https://pyjwt.readthedocs.io/en/latest/usage.html#encoding-decoding-tokens-with-rs256-rsa
- Public Key (RS256): http://localhost:8080/admin/master/console/#/codeflix/realm-settings/keys
- Adicionar public key ao .env
- FastAPI HTTPBearer: https://fastapi.tiangolo.com/reference/security/#fastapi.security.HTTPBearer

```python
security = HTTPBearer()
public_key = f"-----BEGIN PUBLIC KEY-----\n{os.getenv('KEYCLOAK_PUBLIC_KEY', '')}\n-----END PUBLIC KEY-----\n"


def authenticate(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> None:
    try:
        jwt.decode(jwt=credentials.credentials, key=public_key, algorithms=["RS256"], audience="account")
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired token.'
        )

```

- Adicionar `Depends(authenticate)` à rota `/categories`
- Atualizar testes - Depends override
