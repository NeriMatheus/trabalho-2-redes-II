#!/usr/bin/env python3
"""
Exercício 3 - Cliente de chat TCP
Participantes: Luann Moreira Fernandes de Oliveira, Matheus de Moura Almeida Neri, Luis Claudio Prado
"""
import argparse
import socket
import threading


def receber(leitor, encerrar: threading.Event) -> None:
    """Thread dedicada à leitura contínua das mensagens do servidor."""
    try:
        for linha in leitor:
            print(f"\r{linha.rstrip()}\n> ", end="", flush=True)
    except (OSError, ValueError):
        pass
    finally:
        encerrar.set()
        print("\n[Conexão encerrada. Pressione Enter para sair.]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Cliente de chat TCP")
    parser.add_argument("--host", default="127.0.0.1", help="Endereço do servidor")
    parser.add_argument("--porta", type=int, default=5001, help="Porta do servidor")
    args = parser.parse_args()

    nick = input("Nickname: ").strip()
    if not nick:
        print("Nickname não pode ser vazio.")
        return

    try:
        sock = socket.create_connection((args.host, args.porta), timeout=5)
    except ConnectionRefusedError:
        print(f"Erro: servidor indisponível em {args.host}:{args.porta}.")
        return
    except OSError as e:
        print(f"Erro ao conectar: {e}")
        return

    sock.settimeout(None)
    encerrar = threading.Event()
    with sock, sock.makefile("r", encoding="utf-8") as leitor:
        sock.sendall((nick + "\n").encode("utf-8"))
        threading.Thread(target=receber, args=(leitor, encerrar), daemon=True).start()

        print("Digite mensagens ('sair' para encerrar).")
        try:
            while not encerrar.is_set():
                msg = input("> ").strip()
                if encerrar.is_set() or msg.lower() == "sair":
                    break
                if msg:
                    sock.sendall((msg + "\n").encode("utf-8"))
        except (KeyboardInterrupt, EOFError):
            print("\nSaindo...")
        except (BrokenPipeError, ConnectionResetError):
            print("Conexão perdida com o servidor.")
        finally:
            try:
                sock.shutdown(socket.SHUT_RDWR)  # servidor percebe a saída
            except OSError:
                pass


if __name__ == "__main__":
    main()