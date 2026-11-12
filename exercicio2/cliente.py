#!/usr/bin/env python3
"""
Exercício 2 - Cliente Echo UDP
Participantes: Luann Moreira Fernandes de Oliveira, Matheus de Moura Almeida Neri, Luis Claudio Prado
"""
import argparse
import socket

TAM_MAX_UDP = 65507  # payload máximo de um datagrama UDP sobre IPv4


def main() -> None:
    parser = argparse.ArgumentParser(description="Cliente Echo UDP")
    parser.add_argument("--host", default="127.0.0.1", help="Endereço do servidor")
    parser.add_argument("--porta", type=int, default=6000, help="Porta do servidor")
    parser.add_argument("--timeout", type=float, default=3.0,
                        help="Tempo limite de resposta em segundos")
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(args.timeout)
        print("Digite mensagens ('sair' para encerrar).")
        try:
            while True:
                msg = input("> ").strip()
                if not msg:
                    print("Mensagem vazia não é permitida.")
                    continue
                if msg.lower() == "sair":
                    break

                dados = msg.encode("utf-8")
                if len(dados) > TAM_MAX_UDP:  # validação do tamanho máximo
                    print(f"Mensagem muito grande ({len(dados)} bytes). "
                          f"Máximo: {TAM_MAX_UDP} bytes.")
                    continue

                try:
                    sock.sendto(dados, (args.host, args.porta))
                    resposta, _ = sock.recvfrom(65535)
                    print(f"Eco: {resposta.decode('utf-8', errors='replace')}")
                except socket.timeout:
                    print(f"Sem resposta em {args.timeout}s (UDP não garante entrega).")
                except ConnectionRefusedError:
                    print("Servidor indisponível (porta fechada).")
                except OSError as e:
                    print(f"Erro de comunicação: {e}")
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando...")


if __name__ == "__main__":
    main()