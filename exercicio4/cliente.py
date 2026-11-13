# Trabalho 2 de Redes de Computadores II
# Participantes: Matheus de Moura Almeida Neri, Luann Moreira Fernandes de Oliveira, Luis Claudio Lucas Prado Goncalves
"""
Exercicio 4 - Cliente do Servidor de Hora (TCP).

Conecta ao servidor, envia "HORA\\n", le a resposta ("HH:MM:SS\\n") e a exibe.

A opcao --clientes dispara varios clientes ao mesmo tempo (um por thread),
o que permite demonstrar o atendimento em paralelo e o contador do servidor.
"""

import argparse
import socket
import sys
import threading

COMANDO_HORA = "HORA"


def solicitar_hora(host: str, porta: int, timeout: float) -> str:
    """Abre uma conexao, pede a hora e devolve a resposta do servidor.

    Levanta OSError (e subclasses) em falhas de rede e ValueError se o
    servidor responder com erro.
    """
    with socket.create_connection((host, porta), timeout=timeout) as conexao:
        conexao.sendall(f"{COMANDO_HORA}\n".encode("utf-8"))

        # Acumula ate o '\n': a resposta pode chegar em mais de um recv().
        dados = b""
        while b"\n" not in dados:
            bloco = conexao.recv(1024)
            if not bloco:
                break  # servidor fechou a conexao
            dados += bloco

    resposta = dados.decode("utf-8", errors="replace").strip()
    if not resposta:
        raise ConnectionError("o servidor fechou a conexao sem responder")
    if resposta.startswith("ERRO"):
        raise ValueError(resposta)
    return resposta


def executar_cliente(numero: int, host: str, porta: int, timeout: float, falhas: list) -> None:
    """Faz uma solicitacao e imprime o resultado; registra falhas na lista."""
    prefixo = f"[cliente {numero}] "
    try:
        hora = solicitar_hora(host, porta, timeout)
        print(f"{prefixo}Hora recebida do servidor: {hora}")
    except ConnectionRefusedError:
        print(f"{prefixo}Erro: conexao recusada em {host}:{porta}. O servidor esta rodando?", file=sys.stderr)
        falhas.append(numero)  # list.append e atomico em CPython
    except socket.timeout:
        print(f"{prefixo}Erro: tempo esgotado ({timeout:g}s) aguardando o servidor.", file=sys.stderr)
        falhas.append(numero)
    except socket.gaierror:
        print(f"{prefixo}Erro: host desconhecido: {host!r}.", file=sys.stderr)
        falhas.append(numero)
    except (OSError, ValueError) as erro:
        print(f"{prefixo}Erro: {erro}", file=sys.stderr)
        falhas.append(numero)


def porta_valida(texto: str) -> int:
    """Validador do argparse: aceita apenas portas entre 1 e 65535."""
    try:
        porta = int(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"porta invalida: {texto!r} (deve ser um numero inteiro)")
    if not 1 <= porta <= 65535:
        raise argparse.ArgumentTypeError(f"porta fora do intervalo 1-65535: {porta}")
    return porta


def inteiro_positivo(texto: str) -> int:
    """Validador do argparse: aceita apenas inteiros maiores que zero."""
    try:
        valor = int(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"valor invalido: {texto!r} (deve ser um numero inteiro)")
    if valor < 1:
        raise argparse.ArgumentTypeError("o valor deve ser maior ou igual a 1")
    return valor


def timeout_valido(texto: str) -> float:
    """Validador do argparse: aceita apenas timeouts positivos."""
    try:
        valor = float(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"timeout invalido: {texto!r}")
    if valor <= 0:
        raise argparse.ArgumentTypeError("o timeout deve ser maior que zero")
    return valor


def ler_argumentos() -> argparse.Namespace:
    """Define e processa os parametros de linha de comando."""
    parser = argparse.ArgumentParser(description="Cliente do servidor de hora (TCP).")
    parser.add_argument("--host", default="127.0.0.1",
                        help="endereco do servidor (padrao: 127.0.0.1)")
    parser.add_argument("--porta", type=porta_valida, default=7000,
                        help="porta TCP do servidor (padrao: 7000)")
    parser.add_argument("--timeout", type=timeout_valido, default=5.0,
                        help="segundos de espera por conexao/resposta (padrao: 5)")
    parser.add_argument("--clientes", type=inteiro_positivo, default=1,
                        help="numero de clientes simultaneos a disparar (padrao: 1)")
    return parser.parse_args()


def main() -> int:
    args = ler_argumentos()
    falhas: list = []

    # Um cliente por thread, todos iniciados juntos, para exercitar o
    # atendimento concorrente do servidor.
    threads = [
        threading.Thread(target=executar_cliente,
                         args=(numero, args.host, args.porta, args.timeout, falhas))
        for numero in range(1, args.clientes + 1)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Codigo de saida diferente de zero se alguma solicitacao falhou.
    return 1 if falhas else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nCliente interrompido pelo usuario.", file=sys.stderr)
        sys.exit(130)
