#!/usr/bin/env python3
"""
Exercício 1 - Servidor TCP multithread
Participantes: Luann Moreira Fernandes de Oliveira, Matheus de Moura Almeida Neri, Luis Claudio Prado
"""
import argparse
import socket
import threading
from datetime import datetime


def atender_cliente(conn: socket.socket, addr: tuple) -> None:
    """Atende um cliente (uma thread por conexão)."""
    print(f"[+] Cliente conectado: {addr[0]}:{addr[1]}")
    try:
        # makefile permite ler por linhas, evitando problemas de fragmentação do TCP
        with conn, conn.makefile("r", encoding="utf-8") as entrada:
            for linha in entrada:
                msg = linha.strip()
                if not msg:  # validação de mensagem vazia
                    conn.sendall("Mensagem vazia ignorada\n".encode("utf-8"))
                    continue
                agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                print(f"[{agora}] {addr[0]}:{addr[1]} -> {msg}")
                conn.sendall("Mensagem recebida\n".encode("utf-8"))
    except (ConnectionResetError, BrokenPipeError, UnicodeDecodeError) as e:
        print(f"[!] Erro com {addr[0]}:{addr[1]}: {e}")
    finally:
        print(f"[-] Cliente desconectado: {addr[0]}:{addr[1]}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor TCP multithread")
    parser.add_argument("--host", default="0.0.0.0", help="Endereço de escuta")
    parser.add_argument("--porta", type=int, default=5000, help="Porta (padrão 5000)")
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((args.host, args.porta))
        servidor.listen()
        print(f"Servidor ouvindo em {args.host}:{args.porta} (Ctrl+C para parar)")
        try:
            while True:
                conn, addr = servidor.accept()
                threading.Thread(target=atender_cliente, args=(conn, addr),
                                 daemon=True).start()
        except KeyboardInterrupt:
            print("\nServidor encerrado.")


if __name__ == "__main__":
    main()