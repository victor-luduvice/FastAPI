import argparse
import sys

from model import SessionLocal, Usuario


def main() -> int:
    parser = argparse.ArgumentParser(description="Promove uma conta existente a administradora.")
    parser.add_argument("email", help="E-mail da conta já cadastrada")
    args = parser.parse_args()

    session = SessionLocal()
    try:
        usuario = session.query(Usuario).filter(Usuario.email == args.email).first()
        if usuario is None:
            print(f"Nenhuma conta encontrada para {args.email}.", file=sys.stderr)
            return 1
        if usuario.admin:
            print(f"{usuario.email} já é uma conta administradora.")
            return 0

        usuario.admin = True
        session.commit()
        print(f"A conta {usuario.email} agora é administradora.")
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())