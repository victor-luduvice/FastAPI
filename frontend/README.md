# Forno Pizzeria

Frontend de delivery feito com React, TypeScript e Vite, integrado à API FastAPI deste repositório.

## Requisitos

- Node.js 20.19+ ou 22.12+
- API FastAPI executando em `http://127.0.0.1:8000`

## Executar localmente

Em um terminal, inicie a API na pasta `FastAPI`:

```bash
cd FastAPI
source .venv/bin/activate
uvicorn main:app --reload
```

Em outro terminal, inicie o frontend:

```bash
cd FastAPI/frontend
npm install
npm run dev
```

Abra `http://localhost:5173`. O Vite encaminha `/auth` e `/pedidos` para a API local.

## Funcionalidades

- Cardápio responsivo com filtros, tamanhos e sacola.
- Cadastro e login usando `/auth/criar_conta`, `/auth/login` e `/auth/me`.
- Criação e consulta de pedidos autenticados usando `/pedidos/`.
- Linha do tempo do pedido atualizada automaticamente a cada 15 segundos.
- Aba de produção para administradores, com avanço de status e histórico.
- Token de sessão armazenado no `localStorage`.

## Acesso administrativo

O cadastro público não concede perfil administrativo. Cadastre a conta normalmente e, em um terminal confiável na pasta `FastAPI`, promova-a com:

```bash
python promote_admin.py pessoa@example.com
```

O painel de produção atualiza os pedidos a cada 15 segundos. A API aceita apenas transições válidas e impede clientes de alterarem o status.

## Cardápio e preços

A API atual não oferece catálogo nem preços. Por isso, os produtos e valores exibidos estão definidos localmente em `src/App.tsx`; ao enviar o pedido, sabor, tamanho, quantidade e preço seguem no payload esperado pelo backend. A integração com um catálogo persistido depende de endpoints de produtos no FastAPI.

## Verificações

```bash
npm run build
npm run lint
```