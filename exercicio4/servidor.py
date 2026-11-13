# Trabalho 2 de Redes de Computadores II
# Participantes: Matheus de Moura Almeida Neri, Luann Moreira Fernandes de Oliveira, Luis Claudio Lucas Prado Goncalves
"""
Exercicio 4 - Servidor de Hora com Threads (TCP).

Protocolo de aplicacao (texto, uma linha por mensagem, terminada em '\\n'):
    cliente  -> servidor : "HORA\\n"
    servidor -> cliente  : "HH:MM:SS\\n"   (ou "ERRO: ...\\n" se o comando for invalido)

Cada conexao aceita e atendida em uma thread propria, de modo que um cliente
lento ou com falha nao bloqueia os demais. O total de clientes atendidos fica
em um contador protegido por threading.Lock e aparece em toda linha de log.
"""

import argparse
import logging
import socket
import sys
import threading
from datetime import datetime

# Comando que o cliente deve enviar para pedir a hora.
COMANDO_HORA = "HORA"
# Tamanho maximo aceito para a linha de requisicao (evita consumo de memoria
# por um cliente que nunca envia o '\n').
TAMANHO_MAX_REQUISICAO = 1024


class ContadorAtendimentos:
    """Contador thread-safe do numero de clientes atendidos."""

    def __init__(self) -> None:
        self._valor = 0
        self._lock = threading.Lock()

    def incrementar(self) -> int:
        """Soma 1 ao contador e devolve o novo valor (operacao atomica)."""
        # Sem o lock, duas threads poderiam ler o mesmo valor e gravar o mesmo
        # resultado, perdendo um atendimento (condicao de corrida).
        with self._lock:
            self._valor += 1
            return self._valor

    @property
    def valor(self) -> int:
        """Leitura do valor atual, tambem protegida pelo lock."""
        with self._lock:
            return self._valor


def log(nivel: int, contador: ContadorAtendimentos, cliente: str, mensagem: str) -> None:
    """Registra uma linha de log com cliente e contador de atendimentos.

    A data/hora e acrescentada pelo formatador do modulo logging.
    """
    logging.log(nivel, "cliente=%s | atendidos=%d | %s", cliente, contador.valor, mensagem)


def receber_linha(conexao: socket.socket) -> str:
    """Le do socket ate encontrar '\\n' e devolve a linha sem espacos nas pontas.

    TCP e um fluxo de bytes: um unico recv() pode trazer a mensagem em pedacos,
    por isso acumulamos ate achar o delimitador.
    """
    dados = b""
    while b"\n" not in dados:
        bloco = conexao.recv(1024)
        if not bloco:
            # recv() vazio significa que o cliente fechou a conexao.
            raise ConnectionError("conexao encerrada pelo cliente antes de enviar a solicitacao")
        dados += bloco
        if len(dados) > TAMANHO_MAX_REQUISICAO:
            raise ValueError("solicitacao excede o tamanho maximo permitido")
    linha, _, _ = dados.partition(b"\n")
    return linha.decode("utf-8", errors="replace").strip()


def atender_cliente(
    conexao: socket.socket,
    endereco: tuple,
    contador: ContadorAtendimentos,
    timeout: float,
) -> None:
    """Funcao executada por cada thread: atende um unico cliente.

    Qualquer excecao e capturada aqui para que a falha de um cliente encerre
    apenas a sua propria thread, nunca o servidor.
    """
    cliente = f"{endereco[0]}:{endereco[1]}"
    try:
        # O 'with' garante o fechamento do socket mesmo em caso de erro.
        with conexao:
            # Timeout evita que um cliente que conecta e nao envia nada
            # mantenha a thread presa indefinidamente.
            conexao.settimeout(timeout)

            comando = receber_linha(conexao)
            log(logging.INFO, contador, cliente, f"solicitacao recebida: {comando!r}")

            if comando.upper() != COMANDO_HORA:
                conexao.sendall(f"ERRO: comando invalido, envie {COMANDO_HORA}\n".encode("utf-8"))
                log(logging.WARNING, contador, cliente, "solicitacao rejeitada: comando invalido")
                return

            hora = datetime.now().strftime("%H:%M:%S")
            conexao.sendall(f"{hora}\n".encode("utf-8"))

            # So conta como atendido depois que a resposta foi enviada.
            contador.incrementar()
            log(logging.INFO, contador, cliente, f"solicitacao atendida: hora enviada {hora}")
    except socket.timeout:
        log(logging.WARNING, contador, cliente, f"falha: cliente nao enviou solicitacao em {timeout:g}s")
    except (ConnectionError, ValueError, OSError) as erro:
        log(logging.WARNING, contador, cliente, f"falha no atendimento: {erro}")
    except Exception as erro:  # ultima barreira: nada derruba o servidor
        log(logging.ERROR, contador, cliente, f"erro inesperado: {erro!r}")


def porta_valida(texto: str) -> int:
    """Validador do argparse: aceita apenas portas entre 1 e 65535."""
    try:
        porta = int(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"porta invalida: {texto!r} (deve ser um numero inteiro)")
    if not 1 <= porta <= 65535:
        raise argparse.ArgumentTypeError(f"porta fora do intervalo 1-65535: {porta}")
    return porta


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
    parser = argparse.ArgumentParser(description="Servidor de hora multithread (TCP).")
    parser.add_argument("--host", default="0.0.0.0",
                        help="endereco em que o servidor escuta (padrao: 0.0.0.0)")
    parser.add_argument("--porta", type=porta_valida, default=7000,
                        help="porta TCP em que o servidor escuta (padrao: 7000)")
    parser.add_argument("--timeout", type=timeout_valido, default=10.0,
                        help="segundos de espera pela solicitacao de cada cliente (padrao: 10)")
    return parser.parse_args()


def main() -> int:
    args = ler_argumentos()

    # Formato do log: data/hora, nivel, nome da thread e a mensagem
    # (que ja contem cliente e contador de atendimentos).
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(threadName)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    contador = ContadorAtendimentos()

    try:
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Permite reiniciar o servidor sem esperar o TIME_WAIT da porta.
        # No Windows essa opcao tem outro significado (deixaria dois
        # processos escutarem na mesma porta), entao so e usada fora dele.
        if sys.platform != "win32":
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((args.host, args.porta))
        servidor.listen()
    except OSError as erro:
        logging.error("nao foi possivel iniciar o servidor em %s:%d: %s", args.host, args.porta, erro)
        return 1

    # Timeout curto no accept() para que o Ctrl+C seja percebido rapidamente
    # em qualquer sistema operacional.
    servidor.settimeout(1.0)
    log(logging.INFO, contador, "-", f"servidor escutando em {args.host}:{args.porta} (Ctrl+C para encerrar)")

    try:
        with servidor:
            while True:
                try:
                    conexao, endereco = servidor.accept()
                except socket.timeout:
                    continue  # ninguem conectou neste intervalo; volta a esperar
                except OSError as erro:
                    # Erro pontual ao aceitar uma conexao nao deve parar o servidor.
                    log(logging.ERROR, contador, "-", f"erro ao aceitar conexao: {erro}")
                    continue

                # Uma thread por cliente. daemon=True: threads de atendimento
                # nao impedem o encerramento do processo.
                thread = threading.Thread(
                    target=atender_cliente,
                    args=(conexao, endereco, contador, args.timeout),
                    daemon=True,
                )
                thread.start()
    except KeyboardInterrupt:
        log(logging.INFO, contador, "-", "servidor encerrado pelo usuario")
    return 0


if __name__ == "__main__":
    sys.exit(main())
