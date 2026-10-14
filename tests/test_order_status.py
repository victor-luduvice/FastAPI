import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from dependencies import criar_token, pegar_session
from main import app
from model import Pedido, Usuario, base


class OrderStatusTests(unittest.TestCase):
    def setUp(self):
        self.original_overrides = app.dependency_overrides.copy()
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        base.metadata.create_all(bind=self.engine)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

        session = self.session_factory()
        self.customer = Usuario(
            nome="Cliente Teste",
            email="cliente-teste@example.com",
            senha="unused",
            admin=False,
        )
        self.admin = Usuario(
            nome="Admin Teste",
            email="admin-teste@example.com",
            senha="unused",
            admin=True,
        )
        session.add_all([self.customer, self.admin])
        session.flush()
        self.order = Pedido(usuario_id=self.customer.id, status="PENDENTE", preco=0.0)
        session.add(self.order)
        session.commit()
        self.customer_id = self.customer.id
        self.admin_id = self.admin.id
        self.order_id = self.order.id
        session.close()

        def override_session():
            test_session = self.session_factory()
            try:
                yield test_session
            finally:
                test_session.close()

        app.dependency_overrides[pegar_session] = override_session
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(self.original_overrides)
        base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def headers_for(self, user_id: int) -> dict[str, str]:
        return {"Authorization": f"Bearer {criar_token(user_id)}"}

    def test_admin_can_advance_delivery_statuses(self):
        for next_status in ("EM_PREPARO", "PRONTO", "EM_ENTREGA", "FINALIZADO"):
            response = self.client.patch(
                f"/pedidos/{self.order_id}/status",
                json={"status": next_status},
                headers=self.headers_for(self.admin_id),
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], next_status)

    def test_admin_cannot_skip_statuses(self):
        response = self.client.patch(
            f"/pedidos/{self.order_id}/status",
            json={"status": "PRONTO"},
            headers=self.headers_for(self.admin_id),
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["detail"], "Não é permitido alterar o status de PENDENTE para PRONTO.")

    def test_cancelled_order_cannot_be_reopened(self):
        cancel_response = self.client.patch(
            f"/pedidos/{self.order_id}/status",
            json={"status": "CANCELADO"},
            headers=self.headers_for(self.admin_id),
        )
        reopen_response = self.client.patch(
            f"/pedidos/{self.order_id}/status",
            json={"status": "EM_PREPARO"},
            headers=self.headers_for(self.admin_id),
        )

        self.assertEqual(cancel_response.status_code, 200)
        self.assertEqual(cancel_response.json()["status"], "CANCELADO")
        self.assertEqual(reopen_response.status_code, 409)

    def test_customer_cannot_change_order_status(self):
        response = self.client.patch(
            f"/pedidos/{self.order_id}/status",
            json={"status": "EM_PREPARO"},
            headers=self.headers_for(self.customer_id),
        )

        self.assertEqual(response.status_code, 403)

    def test_customer_cannot_use_legacy_finalize_route(self):
        response = self.client.patch(
            f"/pedidos/{self.order_id}/finalizar",
            headers=self.headers_for(self.customer_id),
        )

        self.assertEqual(response.status_code, 403)

    def test_new_order_always_starts_pending(self):
        response = self.client.post(
            "/pedidos/",
            json={"status": "FINALIZADO", "itens": []},
            headers=self.headers_for(self.customer_id),
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "PENDENTE")

    def test_public_signup_cannot_grant_admin(self):
        response = self.client.post(
            "/auth/criar_conta",
            json={
                "nome": "Conta Pública",
                "email": "conta-publica@example.com",
                "senha": "SenhaTeste123!",
                "admin": True,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.json()["admin"])


if __name__ == "__main__":
    unittest.main()