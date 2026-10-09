# API de Delivery de Pizza

Este projeto é uma API REST em FastAPI para um sistema de delivery de pizza, com autenticação por JWT, controle de acesso por nível de usuário, gerenciamento de pedidos e itens do pedido, além de schemas de resposta bem definidos.

## Objetivo do projeto

A aplicação foi pensada para simular um backend completo de delivery, cobrindo operações essenciais como:

- cadastro de usuários e login;
- autenticação via OAuth2 + JWT;
- proteção de endpoints por token;
- diferenciação de acesso entre usuários comuns e administradores;
- criação de pedidos;
- adição de itens ao pedido;
- atualização de status do pedido;
- resposta estruturada via Pydantic.

## Estrutura do projeto

```text
Curso_FastAPI/
├── FastAPI/
│   ├── .env
│   ├── .env.example
│   ├── __pycache__/
│   ├── alembic/
│   ├── auth_routes.py
│   ├── config.py
│   ├── dependencies.py
│   ├── main.py
│   ├── model.py
│   ├── order_routes.py
│   ├── schemas.py
│   └── banco.db
├── README.md
└── .gitignore
```

## Principais funcionalidades implementadas

### 1) Autenticação com OAuth2 e JWT

A API usa OAuth2 para receber o token de acesso e autenticar usuários em endpoints protegidos.

- rota de cadastro: `/auth/criar_conta`
- rota de login: `/auth/login`
- rota protegida para dados do usuário: `/auth/me`

Ao fazer login, o backend gera um JWT com o identificador do usuário e expiração configurada.

### 2) Bloqueio de endpoints

Endpoints sensíveis exigem o header:

```http
Authorization: Bearer <token>
```

Se o token não for válido ou estiver ausente, a API retorna erro 401.

### 3) Níveis de acesso

O modelo `Usuario` possui o campo `admin`.

- usuários comuns acessam apenas os próprios pedidos;
- administradores podem visualizar todos os pedidos e realizar ações administrativas.

### 4) Relacionamentos e lazy loading

O banco foi modelado com SQLAlchemy usando relacionamentos entre:

- `Usuario` -> `Pedido`
- `Pedido` -> `ItemPedido`

Os relacionamentos usam `lazy="selectin"`, o que melhora a recuperação de dados e deixa o acesso aos objetos mais eficiente.

### 5) Pedido e itens do pedido

Cada pedido pode ter vários itens, por exemplo:

- pizza de muçarela;
- pizza de pepperoni;
- bebida;
- borda extra.

Os itens são persistidos com campos como:

- `quantidade`
- `sabor`
- `tamanho`
- `preco`

### 6) Finalização do pedido

Existe um endpoint para finalizar o pedido:

- `PATCH /pedidos/{pedido_id}/finalizar`

Ao finalizar, o status do pedido muda para `FINALIZADO`.

### 7) Schemas de resposta

A API utiliza Pydantic para padronizar as respostas dos endpoints e evitar payloads incompletos.

Os schemas principais estão em `schemas.py` e incluem:

- `UsuarioCreate`
- `UsuarioLogin`
- `UsuarioResponse`
- `Token`
- `ItemPedidoCreate`
- `ItemPedidoResponse`
- `PedidoCreate`
- `PedidoResponse`

## Requisitos

Certifique-se de ter Python 3.11+ e pip instalados.

## Configuração do ambiente

1. Acesse a pasta do projeto:

```bash
cd Curso_FastAPI/FastAPI
```

2. Crie ou ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instale as dependências:

```bash
pip install fastapi uvicorn sqlalchemy python-dotenv passlib[bcrypt] python-jose[cryptography] httpx
```

4. Configure as variáveis de ambiente:

```bash
cp .env.example .env
```

O arquivo `.env` deve ter algo parecido com:

```env
SECRET_KEY=sua-chave-secreta-muito-forte
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## Como rodar a aplicação

Dentro da pasta `FastAPI`:

```bash
uvicorn main:app --reload
```

Após isso, a API ficará disponível em:

```text
http://127.0.0.1:8000
```

A documentação interativa do Swagger estará em:

```text
http://127.0.0.1:8000/docs
```

## Endpoints principais

### Autenticação

```http
POST /auth/criar_conta
POST /auth/login
GET /auth/me
```

Exemplo de cadastro:

```json
{
  "nome": "João",
  "email": "joao@email.com",
  "senha": "123456",
  "ativo": true,
  "admin": false
}
```

Exemplo de login:

```json
{
  "email": "joao@email.com",
  "senha": "123456"
}
```

Resposta esperada:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Pedidos

```http
GET /pedidos/
POST /pedidos/
POST /pedidos/{pedido_id}/itens
PATCH /pedidos/{pedido_id}/finalizar
```

Exemplo de criação de pedido:

```json
{
  "status": "PENDENTE",
  "itens": [
    {
      "sabor": "Muçarela",
      "tamanho": "M",
      "quantidade": 2,
      "preco": 29.9
    },
    {
      "sabor": "Pepperoni",
      "tamanho": "G",
      "quantidade": 1,
      "preco": 39.9
    }
  ]
}
```

Resposta esperada:

```json
{
  "id": 1,
  "usuario_id": 2,
  "status": "PENDENTE",
  "preco": 99.7,
  "itens": [
    {
      "id": 1,
      "pedido_id": 1,
      "sabor": "Muçarela",
      "tamanho": "M",
      "quantidade": 2,
      "preco": 29.9
    }
  ]
}
```

## Observações importantes

- O banco usado na aplicação é SQLite (`banco.db`).
- Se você tiver uma versão antiga do banco com coluna `tamanhho`, a aplicação faz uma normalização automática para `tamanho` na inicialização.
- Para reiniciar do zero, pode remover o arquivo `banco.db` e rodar a aplicação novamente.
- A autenticação usa JWT com expiração em minutos, e a aplicação protege as rotas com `Depends`.

## Dicas para evolução

Este projeto pode evoluir com:

- CRUD de produtos;
- gestão de endereço do cliente;
- status de entrega em tempo real;
- integração com pagamentos;
- testes automatizados com pytest;
- documentação completa de cada operação.

## Resumo

A API está estruturada para funcionar como um backend de delivery completo, cobrindo autenticação, autorização, pedidos, itens do pedido, schemas de resposta e integração com banco de dados relacional usando SQLAlchemy dentro do FastAPI.
