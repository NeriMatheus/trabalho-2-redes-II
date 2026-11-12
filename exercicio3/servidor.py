#!/usr/bin/env python3
"""
Exercício 3 - Servidor de chat TCP (multithread, com broadcast)
Participantes: Luann Moreira Fernandes de Oliveira, Matheus de Moura Almeida Neri, Luis Claudio Prado
"""
import argparse
import socket
import threading

clientes: dict[socket.socket, str] = {}  # conexão -> nickname
trava = threading.Lock()                 # protege o dicionário de clientes


def broadcast(msg: str, excluir: socket.socket | None = None) -> None:
    """Envia a mensagem a todos os clientes, exceto 'excluir'."""
    with trava:
        destinos = [c for c in clientes if c is not excluir]
    for c in destinos:
        try:
            c.sendall((msg + "\n").encode("utf-8"))
        except OSError:
            pass  # a thread desse cliente fará a limpeza


def atender_cliente(conn: socket.socket, addr: tuple) -> None:
    nick = None
    try:
        with conn, conn.makefile("r", encoding="utf-8") as entrada:
            # A primeira linha enviada pelo cliente é o nickname
            nick = (entrada.readline() or "").strip()
            with trava:
                invalido = not nick or nick in clientes.values()
                if not invalido:
                    clientes[conn] = nick
            if invalido:
                conn.sendall("[Servidor] Nickname vazio ou já em uso.\n".encode("utf-8"))
                nick = None
                return

            print(f"[+] {nick} entrou ({addr[0]}:{addr[1]})")
            broadcast(f"[Servidor] {nick} entrou no chat.", excluir=conn)
            conn.sendall(f"[Servidor] Bem-vindo, {nick}!\n".encode("utf-8"))

            for linha in entrada:
                msg = linha.strip()
                if msg:
                    broadcast(f"{nick}: {msg}", excluir=conn)
    except (ConnectionResetError, BrokenPipeError, UnicodeDecodeError):
        pass
    finally:
        # Remove o cliente e avisa os demais, sem derrubar o servidor
        if nick:
            with trava:
                clientes.pop(conn, None)
            print(f"[-] {nick} saiu")
            broadcast(f"[Servidor] {nick} saiu do chat.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor de chat TCP")
    parser.add_argument("--host", default="0.0.0.0", help="Endereço de escuta")
    parser.add_argument("--porta", type=int, default=5001, help="Porta (padrão 5001)")
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((args.host, args.porta))
        servidor.listen()
        print(f"Chat ouvindo em {args.host}:{args.porta} (Ctrl+C para parar)")
        try:
            while True:
                conn, addr = servidor.accept()
                threading.Thread(target=atender_cliente, args=(conn, addr),
                                 daemon=True).start()
        except KeyboardInterrupt:
            print("\nServidor encerrado.")


if __name__ == "__main__":
    main()