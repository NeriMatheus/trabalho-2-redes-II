#!/usr/bin/env python3
"""
Exercício 2 - Servidor Echo UDP
Participantes: Luann Moreira Fernandes de Oliveira, Matheus de Moura Almeida Neri, Luis Claudio Prado
"""
import argparse
import socket

TAM_MAX_UDP = 65507  # payload máximo de um datagrama UDP sobre IPv4


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor Echo UDP")
    parser.add_argument("--host", default="0.0.0.0", help="Endereço de escuta")
    parser.add_argument("--porta", type=int, default=6000, help="Porta (padrão 6000)")
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((args.host, args.porta))
        print(f"Servidor UDP ouvindo em {args.host}:{args.porta} (Ctrl+C para parar)")
        try:
            while True:
                dados, addr = sock.recvfrom(65535)
                texto = dados.decode("utf-8", errors="replace")
                print(f"{addr[0]}:{addr[1]} -> {texto}")
                try:
                    sock.sendto(dados, addr)  # eco
                except OSError as e:
                    print(f"[!] Falha ao responder {addr}: {e}")
        except KeyboardInterrupt:
            print("\nServidor encerrado.")


if __name__ == "__main__":
    main()