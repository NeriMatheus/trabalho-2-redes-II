# Trabalho 2 de Redes de Computadores II
# Participantes: Matheus de Moura Almeida Neri, Luann Moreira Fernandes de Oliveira, Luis Claudio Lucas Prado Goncalves
"""
Exercicio 10 - Cliente de chat em rede com WebSockets.

Conecta ao servidor, envia o nome de usuario como primeira mensagem e, a
partir dai, envia cada linha digitada e exibe em tempo real as mensagens dos
outros participantes. Digite /sair (ou Ctrl+C / Ctrl+D) para encerrar.

Duas atividades acontecem ao mesmo tempo:
    - uma thread le o teclado (input() e bloqueante e travaria o event loop);
    - o event loop do asyncio recebe as mensagens do servidor e envia as
      linhas digitadas, que chegam da thread por uma asyncio.Queue.
"""

import argparse
import asyncio
import os
import sys
import threading

try:
    from websockets.asyncio.client import ClientConnection, connect
    from websockets.exceptions import ConnectionClosed, InvalidHandshake, InvalidURI
except ImportError:
    sys.exit("Dependencia ausente ou antiga. Instale com: pip install -r requirements.txt")

COMANDO_SAIR = "/sair"
TAMANHO_MAX_NOME = 20


def ler_teclado(loop: asyncio.AbstractEventLoop, fila: asyncio.Queue) -> None:
    """Executada em uma thread: le linhas do teclado e as entrega ao event loop.

    Coloca None na fila quando a entrada termina (Ctrl+D / EOF).
    """
    try:
        while True:
            try:
                linha = input()
            except EOFError:
                linha = None
            # asyncio.Queue nao e thread-safe; call_soon_threadsafe agenda a
            # insercao para ser feita pela thread do event loop.
            loop.call_soon_threadsafe(fila.put_nowait, linha)
            if linha is None:
                return
    except RuntimeError:
        pass  # o event loop ja foi fechado; nada mais a fazer


async def receber_mensagens(conexao: ClientConnection) -> None:
    """Exibe cada mensagem recebida do servidor ate a conexao fechar."""
    async for mensagem in conexao:
        print(mensagem)


async def enviar_mensagens(conexao: ClientConnection, fila: asyncio.Queue) -> None:
    """Envia ao servidor cada linha digitada, ate o usuario pedir para sair."""
    while True:
        linha = await fila.get()
        if linha is None or linha.strip().lower() == COMANDO_SAIR:
            return
        if linha.strip():  # nao envia linhas em branco
            await conexao.send(linha)


async def conversar(uri: str, nome: str) -> int:
    """Conecta, identifica-se e mantem o chat ate alguem encerrar."""
    async with connect(uri) as conexao:
        # Identificacao: primeira mensagem e o nome; servidor responde OK/ERRO.
        await conexao.send(nome)
        resposta = await conexao.recv()
        if resposta != "OK":
            print(f"Servidor recusou a entrada: {resposta}", file=sys.stderr)
            return 1

        print(f"Conectado a {uri} como '{nome}'. Digite as mensagens e tecle Enter ({COMANDO_SAIR} para sair).")

        # Thread daemon para o teclado: nao impede o programa de terminar se
        # o servidor cair enquanto input() esta esperando.
        fila: asyncio.Queue = asyncio.Queue()
        threading.Thread(target=ler_teclado, args=(asyncio.get_running_loop(), fila), daemon=True).start()

        recebimento = asyncio.create_task(receber_mensagens(conexao))
        envio = asyncio.create_task(enviar_mensagens(conexao, fila))

        # Termina quando a primeira tarefa acabar: o usuario saiu (envio) ou
        # o servidor fechou a conexao (recebimento).
        concluidas, pendentes = await asyncio.wait(
            {recebimento, envio}, return_when=asyncio.FIRST_COMPLETED
        )
        for tarefa in pendentes:
            tarefa.cancel()
        await asyncio.gather(*pendentes, return_exceptions=True)

        # Propaga uma eventual ConnectionClosed da tarefa que terminou.
        for tarefa in concluidas:
            tarefa.result()

        if recebimento in concluidas:
            print("Conexao encerrada pelo servidor.", file=sys.stderr)
            return 1
        print("Voce saiu do chat.")
        return 0


def porta_valida(texto: str) -> int:
    """Validador do argparse: aceita apenas portas entre 1 e 65535."""
    try:
        porta = int(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"porta invalida: {texto!r} (deve ser um numero inteiro)")
    if not 1 <= porta <= 65535:
        raise argparse.ArgumentTypeError(f"porta fora do intervalo 1-65535: {porta}")
    return porta


def nome_valido(texto: str) -> str:
    """Validador do argparse: nome nao vazio e dentro do limite do servidor."""
    nome = texto.strip()
    if not nome:
        raise argparse.ArgumentTypeError("o nome de usuario nao pode ser vazio")
    if len(nome) > TAMANHO_MAX_NOME:
        raise argparse.ArgumentTypeError(f"o nome de usuario deve ter no maximo {TAMANHO_MAX_NOME} caracteres")
    return nome


def ler_argumentos() -> argparse.Namespace:
    """Define e processa os parametros de linha de comando."""
    parser = argparse.ArgumentParser(description="Cliente de chat com WebSockets.")
    parser.add_argument("--host", default="127.0.0.1",
                        help="endereco do servidor (padrao: 127.0.0.1)")
    parser.add_argument("--porta", type=porta_valida, default=8765,
                        help="porta do servidor (padrao: 8765)")
    parser.add_argument("--nome", type=nome_valido,
                        help="nome de usuario (se omitido, e perguntado ao iniciar)")
    return parser.parse_args()


def perguntar_nome() -> str:
    """Pede o nome de usuario no terminal ate receber um valor valido."""
    while True:
        try:
            return nome_valido(input("Nome de usuario: "))
        except argparse.ArgumentTypeError as erro:
            print(f"Nome invalido: {erro}")


def main() -> int:
    args = ler_argumentos()
    try:
        nome = args.nome or perguntar_nome()
        uri = f"ws://{args.host}:{args.porta}"
        return asyncio.run(conversar(uri, nome))
    except (KeyboardInterrupt, EOFError):
        print("\nCliente encerrado pelo usuario.")
        return 0
    except ConnectionClosed:
        print("Conexao com o servidor perdida.", file=sys.stderr)
    except (InvalidURI, InvalidHandshake) as erro:
        print(f"Erro: o endereco nao e um servidor WebSocket valido: {erro}", file=sys.stderr)
    except TimeoutError:
        print("Erro: tempo esgotado ao conectar ao servidor.", file=sys.stderr)
    except OSError as erro:
        # Ex.: conexao recusada (servidor fora do ar) ou host desconhecido.
        print(f"Erro: nao foi possivel conectar a {args.host}:{args.porta}: {erro}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    codigo = main()
    # A thread do teclado pode ainda estar bloqueada em input(). Um sys.exit()
    # comum tentaria finalizar o stdin em uso por ela e o interpretador
    # abortaria com erro; por isso descarregamos as saidas e encerramos o
    # processo diretamente.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(codigo)
