# Athena — Backend

API REST do **Athena**, plataforma para artistas venderem suas obras (quadros/artes). Construída em **Python** com **FastAPI**, **SQLAlchemy 2.x** (PostgreSQL) e **Redis** para o carrinho de compras.

---

## 📋 Visão Geral

### Stack

| Camada            | Tecnologia                            |
|-------------------|---------------------------------------|
| Framework         | FastAPI                               |
| Servidor ASGI     | Uvicorn                               |
| ORM               | SQLAlchemy 2.x                        |
| Banco de dados    | PostgreSQL                            |
| Cache / Carrinho  | Redis (HASH, TTL 7 dias)              |
| Autenticação      | OAuth2 + JWT (`python-jose`)          |
| Hash de senha     | `passlib` + `bcrypt`                  |
| Upload de imagens | Cloudinary                            |
| E-mail            | `fastapi-mail` (recuperação de senha) |
| Migrations        | Alembic                               |

### Arquitetura

```
Frontend (website/)
       │
       │ HTTP/JSON (+ multipart/form-data para upload de imagem)
       ▼
FastAPI (main.py)
  ├── ROUTES/auth.py        → /auth      (cadastro, login, refresh, recuperação de senha)
  ├── ROUTES/produtos.py    → /arts      (CRUD de artes/quadros)
  ├── ROUTES/carrinho.py    → /cart      (carrinho via Redis)
  ├── ROUTES/purchase.py    → /purchase  (pedidos)
  └── ROUTES/user.py        → /user      (perfil, endereços, busca de CEP)
       │
       ├── SQLAlchemy Session ──► PostgreSQL
       ├── Redis Client       ──► Redis (carrinho)
       └── Cloudinary SDK     ──► Cloudinary (imagens das artes)
```

### Estrutura de Pastas

```
backend/
├── main.py                 # instância FastAPI + inclusão dos routers + CORS
├── requirements.txt
├── .env.example
├── CORE/                   # config central (chaves, algoritmo JWT, bcrypt_context)
├── DEPENDENCIES/           # get_db (Session), verificar_token, redis_client
├── MODELS/                 # modelos SQLAlchemy (um arquivo por tabela)
├── ROUTES/                 # routers da API
└── SCHEMAS/                # schemas Pydantic (request/response)
```

---

## 🔧 Variáveis de Ambiente

Crie um arquivo `.env` na raiz de `/backend` (baseado no `.env.example` já existente no repositório):

```env
DATABASE_URL=
SECRET_KEY=
ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=
REDIS_HOST=
REDIS_PORT=
REDIS_PASSWORD=
REDIS_DB=
ATHENA_EMAIL=
ATHENA_PASSWORD=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

> ⚠️ **Atenção ao `DATABASE_URL`:** o formato correto do SQLAlchemy/psycopg2 é
> `postgresql://usuario:senha@host:porta/nome_do_banco` (o exemplo do `.env.example` está com a ordem `user:host@password:port`, ajuste para o padrão real ao preencher).

| Variável                                                                 | Descrição                                                    |
|--------------------------------------------------------------------------|--------------------------------------------------------------|
| `DATABASE_URL`                                                           | String de conexão do PostgreSQL                              |
| `SECRET_KEY`                                                             | Chave usada para assinar os tokens JWT                       |
| `ALGORITHM`                                                              | Algoritmo de assinatura do JWT (ex: `HS256`)                 |
| `ACCESS_TOKEN_EXPIRE_MINUTES`                                            | Tempo de expiração do access token                           |
| `REDIS_HOST` / `REDIS_PORT` / `REDIS_PASSWORD` / `REDIS_DB`              | Conexão com o Redis (carrinho)                               |
| `ATHENA_EMAIL` / `ATHENA_PASSWORD`                                       | Credenciais de e-mail (Gmail SMTP) para recuperação de senha |
| `CLOUDINARY_CLOUD_NAME` / `CLOUDINARY_API_KEY` / `CLOUDINARY_API_SECRET` | Upload das imagens das artes                                 |

---

## 🚀 Instruções de Setup (uvicorn + FastAPI)

### Pré-requisitos

- Python 3.11+
- PostgreSQL 14+ rodando localmente (ou Redis Cloud/Upstash para o Redis)
- Redis (local via Docker, ou instância na nuvem — Redis Cloud/Upstash)
- Git

### 1. Clonar o repositório

```bash
git clone https://github.com/athena-ecommerce/backend.git
cd backend
```

### 2. Criar e ativar o ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar o `.env`

```bash
copy .env.example .env    # Windows
# cp .env.example .env    # Linux/macOS
```

Preencha as variáveis conforme a seção acima.

### 5. Criar o banco de dados

Crie um banco vazio no PostgreSQL (ex: `athena_db`) e execute o script SQL completo (ver seção **Modelagem de Dados**) usando `psql` ou uma ferramenta como DBeaver/pgAdmin:

```bash
psql -U seu_usuario -d athena_db -f script_banco.sql
```

> O projeto também possui Alembic instalado (`alembic==1.18.4`) para versionamento de schema, caso as migrations estejam configuradas no time.

### 6. Rodar o servidor com Uvicorn

```bash
uvicorn main:app --reload --port 8000
```

- `main:app` → aponta para o objeto `app` dentro de `main.py`
- `--reload` → reinicia o servidor automaticamente a cada alteração no código (uso em desenvolvimento)
- `--port 8000` → porta do servidor (ajuste se necessário)

Servidor disponível em:
```
http://127.0.0.1:8000
```

Documentação interativa (Swagger UI) gerada automaticamente pelo FastAPI:
```
http://127.0.0.1:8000/docs
```

### 7. Autorizar no Swagger (fluxo de teste)

1. Registrar um usuário em `POST /auth/signup`
2. Autenticar em `POST /auth/login-form` (usando "Authorize" no Swagger)
3. Copiar o `access_token` retornado
4. Colar como `Bearer <access_token>` no botão **Authorize** do Swagger

### Rodar em produção

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

(Sem `--reload` em produção; ajuste `--workers` conforme os recursos do servidor.)

---

## 📡 Documentação de Endpoints

### Base URL
```
http://127.0.0.1:8000
```

---

### 1. Autenticação — `/auth`

#### **POST** `/auth/signup`
Cadastra um novo usuário (cliente, artista ou administrador).

**Payload:**
```json
{
  "nome_completo": "João Silva",
  "login": "joao@example.com",
  "senha": "SenhaForte123",
  "data_nascimento": "2000-05-10",
  "cpf": "12345678900",
  "tipo_acesso": "CLIENTE"
}
```

**Resposta 200 OK:**
```json
{
  "nome_completo": "João Silva",
  "login": "joao@example.com",
  "data_nascimento": "2000-05-10",
  "cpf": "12345678900",
  "tipo_acesso": "CLIENTE"
}
```

**Resposta 400 Bad Request:**
```json
{ "detail": "E-mail já cadastrado!" }
```

---

#### **POST** `/auth/login`
Login via JSON, retorna `access_token` e `refresh_token`.

**Payload:**
```json
{
  "login": "joao@example.com",
  "senha": "SenhaForte123"
}
```

**Resposta 200 OK:**
```json
{
  "login": "joao@example.com",
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi..."
}
```

**Resposta 400 Bad Request:**
```json
{ "detail": "Usuário não encontrado!" }
```

---

#### **POST** `/auth/login-form`
Login via `application/x-www-form-urlencoded` (compatível com o botão **Authorize** do Swagger / OAuth2PasswordRequestForm).

**Form fields:** `username`, `password`

**Resposta 200 OK:**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "Bearer"
}
```

---

#### **GET** `/auth/refresh`
Gera um novo `access_token` a partir de um `refresh_token` válido.

**Query params:** `refresh_token=<token>`

**Resposta 200 OK:**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "Bearer"
}
```

---

#### **GET** `/auth/refresh-form`
Mesma função do `/auth/refresh`, porém autenticado via header `Authorization: Bearer <refresh_token>` (fluxo OAuth2 do Swagger).

---

#### **POST** `/auth/resetpassword/email`
Envia um código de 6 dígitos por e-mail para recuperação de senha.

**Payload:**
```json
{ "email": "joao@example.com" }
```

**Resposta 200 OK:**
```json
{ "mensagem": "E-mail mandado com sucesso!" }
```

---

#### **POST** `/auth/resetpassword/validation`
Valida o código recebido por e-mail (expira em 2 minutos).

**Payload:**
```json
{
  "email": "joao@example.com",
  "codigo": "123456"
}
```

**Resposta 200 OK:**
```json
{ "token_validation": "eyJhbGciOi..." }
```

---

#### **POST** `/auth/resetpassword/newpassword`
Define uma nova senha usando o `token_validation` recebido na etapa anterior.

**Query params:** `token_validation=<token>`

**Payload:**
```json
{ "senha": "NovaSenhaForte456" }
```

**Resposta 200 OK:**
```json
{ "mensagem": "Senha alterada com sucesso!" }
```

---

### 2. Artes — `/arts`

> Autenticação via header `Authorization: Bearer <access_token>` onde indicado.

#### **GET** `/arts/`
Lista artes com filtros opcionais (query params).

| Parâmetro     | Tipo   | Descrição                                  |
|---------------|--------|--------------------------------------------|
| `tipo_arte`   | string | Filtra pela categoria/tipo da arte         |
| `nome`        | string | Busca parcial pelo nome (case-insensitive) |
| `preco_min`   | float  | Preço mínimo                               |
| `preco_max`   | float  | Preço máximo                               |
| `ordenar_por` | string | `nome`, `preco-menor` ou `preco-maior`     |

**Resposta 200 OK:**
```json
[
  {
    "id_produto": 1,
    "nome": "Noite Estrelada (releitura)",
    "tipo_arte": "pintura",
    "preco": 350.00,
    "id_usuario": 4,
    "descricao": "Releitura da obra de Van Gogh",
    "imagem": {
      "id_imagem_quadro": 1,
      "imagem": "https://res.cloudinary.com/.../noite.jpg",
      "imagem_public_id": "athena/noite_estrelada",
      "descricao_foto": "Foto frontal do quadro",
      "dimensoes": "40x60cm"
    }
  }
]
```

---

#### **GET** `/arts/artist/me` 🔒
Lista as artes do artista autenticado.

**Resposta 200 OK:** mesmo formato do `GET /arts/`.

---

#### **GET** `/arts/artist/{id_usuario}`
Lista as artes publicadas por um artista específico (público).

---

#### **GET** `/arts/{id_produto}`
Retorna os detalhes de uma arte específica.

**Resposta 404 Not Found:**
```json
{ "detail": "Arte não encontrada" }
```

---

#### **POST** `/arts/` 🔒 (somente `ARTISTA`)
Cadastra uma nova arte. Enviado como `multipart/form-data` (por causa do upload de imagem).

**Form fields:**

| Campo            | Tipo             |
|------------------|------------------|
| `nome`           | string           |
| `tipo_arte`      | string           |
| `preco`          | float (> 0)      |
| `imagem`         | arquivo (upload) |
| `descricao_foto` | string           |
| `dimensoes`      | string           |

**Resposta 201 Created:** mesmo formato de `ArteResposta` (ver `GET /arts/{id}`).

**Resposta 403 Forbidden:**
```json
{ "detail": "Somente artistas podem cadastrar artes" }
```

---

#### **PUT** `/arts/{id_produto}` 🔒 (dono da arte)
Atualiza uma arte existente (também via `multipart/form-data`, mesmos campos do cadastro).

**Resposta 403 Forbidden:**
```json
{ "detail": "Essa arte não pertence a você" }
```

---

#### **DELETE** `/arts/{id_produto}` 🔒 (dono da arte)
Remove a arte (banco + imagem no Cloudinary).

**Resposta:** `204 No Content`

---

### 3. Carrinho — `/cart` 🔒

> Armazenado em Redis como HASH `carrinho:{id_usuario}`, com TTL de 7 dias. Requer autenticação em todos os endpoints.

#### **GET** `/cart/`
Retorna o carrinho do usuário autenticado.

**Resposta 200 OK:**
```json
{
  "itens": [
    {
      "id_produto": 1,
      "nome": "Noite Estrelada (releitura)",
      "preco": 350.00,
      "quantidade": 2,
      "subtotal": 700.00
    }
  ],
  "total": 700.00
}
```

---

#### **POST** `/cart/items`
Adiciona (ou incrementa) um item no carrinho.

**Payload:**
```json
{
  "id_produto": 1,
  "quantidade": 1
}
```

**Resposta 201 Created:** mesmo formato do `GET /cart/`.

**Resposta 404 Not Found:**
```json
{ "detail": "Arte não encontrada" }
```

---

#### **DELETE** `/cart/items/{art_id}`
Remove um item específico do carrinho.

**Resposta 200 OK:** carrinho atualizado (mesmo formato do `GET /cart/`).

---

#### **DELETE** `/cart/`
Limpa o carrinho por completo.

**Resposta:** `204 No Content`

---

### 4. Compras / Pedidos — `/purchase` 🔒

#### **POST** `/purchase/`
Registra um pedido a partir de uma lista de artes e um endereço já cadastrado.

**Payload:**
```json
{
  "valor_total": 700.00,
  "id_endereco": 3,
  "ids_produto": [1, 5]
}
```

---

#### **GET** `/purchase/`
Lista os pedidos do usuário autenticado.

**Resposta 200 OK:**
```json
[
  {
    "valor_total": 700.00,
    "data_pedido": "2026-08-10",
    "status": "PENDENTE",
    "endereco": {
      "rua": "Rua das Flores",
      "bairro": "Vila Mariana",
      "estado": "SP",
      "numero": "123",
      "complemento": "Apto 402",
      "cep": "01234567"
    },
    "produtos": [
      { "nome": "Noite Estrelada (releitura)", "tipo_arte": "pintura", "preco": 350.00 }
    ]
  }
]
```

> **Nota técnica:** `POST /purchase/payment` existe como placeholder no roteador, ainda não implementado.

---

### 5. Usuário — `/user`

#### **GET** `/user/profile` 🔒
Retorna os dados do usuário autenticado, incluindo endereços cadastrados.

**Resposta 200 OK:**
```json
{
  "id_usuario": 4,
  "nome_completo": "João Silva",
  "login": "joao@example.com",
  "data_nascimento": "2000-05-10",
  "tipo_acesso": "CLIENTE",
  "enderecos": [
    {
      "rua": "Rua das Flores",
      "bairro": "Vila Mariana",
      "estado": "SP",
      "numero": "123",
      "complemento": "Apto 402",
      "cep": "01234567"
    }
  ]
}
```

---

#### **POST** `/user/adicionar-endereco` 🔒
Cadastra um novo endereço para o usuário autenticado.

**Payload:**
```json
{
  "rua": "Rua das Flores",
  "bairro": "Vila Mariana",
  "estado": "SP",
  "numero": "123",
  "complemento": "Apto 402",
  "cep": "01234567"
}
```

**Resposta 400 Bad Request:**
```json
{ "detail": "Não foi possível cadastrar o endereço." }
```

---

#### **GET** `/user/cep/{cep}`
Consulta um CEP na API pública ViaCEP e retorna o endereço pré-preenchido.

**Resposta 200 OK:**
```json
{
  "rua": "Rua das Flores",
  "bairro": "Vila Mariana",
  "estado": "SP",
  "numero": null,
  "complemento": null,
  "cep": "01234-567"
}
```

**Resposta 404 Not Found:**
```json
{ "detail": "Endereço não encontrado" }
```

---

## 🗄️ Modelagem de Dados

Banco relacional em **PostgreSQL**. Abaixo o script de criação das tabelas, índices e constraints, na ordem de execução recomendada.

### Diagrama de Relacionamentos (resumo)

```
usuarios ──< enderecos
usuarios ──< telefones
usuarios ──< cartoes
usuarios ──< produtos (artista dono da arte)
usuarios ──< pedidos
usuarios >──< competencias (via usuarios_competencias)

produtos ──< imagens_quadros
produtos >──< pedidos (via pedidos_produtos)

pedidos ──> enderecos (endereço de entrega)
pedidos ──< pagamentos

pagamentos ──> cartoes (opcional; ou chave_pix)

recuperacoes_senhas (independente, ligado por "login")
```

### Script SQL completo

Disponível em `DATABASE/scrip_banco.sql`.

### Observações sobre a modelagem

- `pedidos_produtos` é uma tabela associativa **N:N** entre `pedidos` e `produtos`, sem coluna própria de quantidade — cada linha representa 1 unidade de 1 produto no pedido.
- `pagamentos` aceita **exatamente um** método por vez: `id_cartao` OU `chave_pix` (garantido pela constraint `chk_pagamento_um_metodo`).
- O **carrinho não é persistido no PostgreSQL** — ele vive inteiramente no Redis (`carrinho:{id_usuario}`) até a finalização do pedido, quando os itens viram registros em `pedidos` + `pedidos_produtos`.
- `imagens_quadros` guarda o `imagem_public_id` do Cloudinary para permitir atualização/exclusão da imagem sem duplicar upload.

---

## 🔒 CORS

Configurado em `main.py`. Atualmente libera apenas:

```python
origins = ["http://localhost:80"]
```

Ajuste essa lista conforme a porta/domínio real do frontend em desenvolvimento e produção.

---

## 📦 Dependências (requirements.txt)

```
alembic==1.18.4
fastapi==0.136.3
redis==8.1.0
passlib==1.7.4
bcrypt==4.3.0
python-dotenv==1.2.2
python-jose[cryptography]==3.5.0
SQLAlchemy==2.0.50
uvicorn==0.49.0
psycopg2-binary==2.9.12
python-multipart==0.0.32
fastapi-mail==1.6.5
email-validator==2.3.0
cloudinary==1.45.0
pydantic
```

---