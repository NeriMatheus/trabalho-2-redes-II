#!/usr/bin/env python3
"""
Exercício 1 - Cliente TCP
Participantes: Luann Moreira Fernandes de Oliveira, Matheus de Moura Almeida Neri, Luis Claudio Prado
"""
import argparse
import socket


def main() -> None:
    parser = argparse.ArgumentParser(description="Cliente TCP")
    parser.add_argument("--host", default="127.0.0.1", help="Endereço do servidor")
    parser.add_argument("--porta", type=int, default=5000, help="Porta do servidor")
    args = parser.parse_args()

    try:
        sock = socket.create_connection((args.host, args.porta), timeout=5)
    except ConnectionRefusedError:
        print(f"Erro: servidor indisponível em {args.host}:{args.porta}.")
        return
    except OSError as e:
        print(f"Erro ao conectar: {e}")
        return

    sock.settimeout(None)
    # with garante o fechamento seguro da conexão
    with sock, sock.makefile("r", encoding="utf-8") as leitor:
        print("Conectado. Digite mensagens ('sair' para encerrar).")
        try:
            while True:
                msg = input("> ").strip()
                if not msg:
                    print("Mensagem vazia não é permitida.")
                    continue
                if msg.lower() == "sair":
                    break
                sock.sendall((msg + "\n").encode("utf-8"))
                resposta = leitor.readline()
                if not resposta:
                    print("Servidor encerrou a conexão.")
                    break
                print(f"Servidor: {resposta.strip()}")
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando...")
        except (ConnectionResetError, BrokenPipeError):
            print("Conexão perdida com o servidor.")


if __name__ == "__main__":
    main()