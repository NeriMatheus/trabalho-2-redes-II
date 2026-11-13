# Trabalho 2 de Redes de Computadores II
# Participantes: Matheus de Moura Almeida Neri, Luann Moreira Fernandes de Oliveira, Luis Claudio Lucas Prado Goncalves
"""
Exercicio 10 - Servidor de chat em rede com WebSockets.

Protocolo de aplicacao (mensagens de texto sobre WebSocket):
    1. A primeira mensagem enviada pelo cliente e o seu nome de usuario.
       O servidor responde "OK" se o nome foi aceito ou "ERRO: <motivo>" e
       fecha a conexao caso contrario (nome vazio, longo demais ou em uso).
    2. Dai em diante, cada mensagem do cliente e retransmitida (broadcast)
       para todos os DEMAIS clientes no formato "[nome] texto".
    3. Entradas e saidas sao anunciadas com "*** nome entrou no chat ***" e
       "*** nome saiu do chat ***".

O servidor usa asyncio: cada conexao e atendida por uma corrotina propria,
entao varios clientes sao atendidos simultaneamente em uma unica thread.
"""

import argparse
import asyncio
import logging
import sys

try:
    from websockets.asyncio.server import ServerConnection, broadcast, serve
    from websockets.exceptions import ConnectionClosed
except ImportError:
    sys.exit("Dependencia ausente ou antiga. Instale com: pip install -r requirements.txt")

# Limites usados na validacao das entradas dos clientes.
TAMANHO_MAX_NOME = 20
TAMANHO_MAX_MENSAGEM = 1000
# Tempo maximo (s) para o cliente informar o nome apos conectar.
TEMPO_MAX_IDENTIFICACAO = 30

# Clientes identificados: conexao -> nome de usuario.
# Nao precisa de lock: todas as corrotinas rodam na mesma thread (event loop)
# e o dicionario so e alterado em trechos sem 'await' no meio.
clientes: dict[ServerConnection, str] = {}


def endereco_de(conexao: ServerConnection) -> str:
    """Devolve "ip:porta" do cliente para uso nos logs."""
    endereco = conexao.remote_address
    return f"{endereco[0]}:{endereco[1]}" if endereco else "desconhecido"


def retransmitir(mensagem: str, remetente: ServerConnection | None = None) -> None:
    """Envia a mensagem a todos os clientes conectados, exceto o remetente.

    broadcast() nao bloqueia e ignora conexoes que ja cairam, portanto um
    cliente lento ou desconectado nao atrapalha a entrega aos demais.
    """
    destinatarios = [conexao for conexao in clientes if conexao is not remetente]
    broadcast(destinatarios, mensagem)


async def identificar(conexao: ServerConnection) -> str | None:
    """Recebe e valida o nome de usuario (primeira mensagem do cliente).

    Devolve o nome aceito, ou None se o cliente foi rejeitado.
    """
    try:
        bruto = await asyncio.wait_for(conexao.recv(), timeout=TEMPO_MAX_IDENTIFICACAO)
    except asyncio.TimeoutError:
        await conexao.close(code=1008, reason="nome de usuario nao informado")
        return None

    # Mensagens binarias nao fazem parte do protocolo.
    nome = bruto.strip() if isinstance(bruto, str) else ""

    if not nome:
        motivo = "nome de usuario vazio ou invalido"
    elif len(nome) > TAMANHO_MAX_NOME:
        motivo = f"nome de usuario com mais de {TAMANHO_MAX_NOME} caracteres"
    elif nome.lower() in (existente.lower() for existente in clientes.values()):
        motivo = f"o nome '{nome}' ja esta em uso"
    else:
        # Registra antes de qualquer 'await' para que dois clientes nao
        # consigam reservar o mesmo nome ao mesmo tempo.
        clientes[conexao] = nome
        await conexao.send("OK")
        return nome

    await conexao.send(f"ERRO: {motivo}")
    await conexao.close(code=1008, reason=motivo[:100])
    logging.warning("%s rejeitado: %s", endereco_de(conexao), motivo)
    return None


async def atender_cliente(conexao: ServerConnection) -> None:
    """Corrotina executada para cada conexao WebSocket aceita."""
    endereco = endereco_de(conexao)
    nome = None
    try:
        nome = await identificar(conexao)
        if nome is None:
            return

        logging.info("%s entrou como '%s' (%d conectado(s))", endereco, nome, len(clientes))
        retransmitir(f"*** {nome} entrou no chat ***", remetente=conexao)

        # O 'async for' termina sozinho quando o cliente fecha a conexao
        # normalmente; quedas abruptas levantam ConnectionClosed.
        async for mensagem in conexao:
            if not isinstance(mensagem, str):
                continue  # ignora quadros binarios
            texto = mensagem.strip()
            if not texto:
                continue  # ignora mensagens vazias
            if len(texto) > TAMANHO_MAX_MENSAGEM:
                await conexao.send(f"ERRO: mensagem com mais de {TAMANHO_MAX_MENSAGEM} caracteres")
                continue
            logging.info("[%s] %s", nome, texto)
            retransmitir(f"[{nome}] {texto}", remetente=conexao)
    except ConnectionClosed:
        # Desconexao inesperada (queda de rede, processo morto etc.).
        logging.warning("%s (%s) desconectou inesperadamente", endereco, nome or "sem nome")
    except Exception:
        # Qualquer outro erro fica restrito a este cliente; o servidor segue.
        logging.exception("erro ao atender %s (%s)", endereco, nome or "sem nome")
    finally:
        # Sempre remove o cliente e avisa os demais, seja qual for o motivo.
        if clientes.pop(conexao, None) is not None:
            logging.info("'%s' saiu (%d conectado(s))", nome, len(clientes))
            retransmitir(f"*** {nome} saiu do chat ***")


def porta_valida(texto: str) -> int:
    """Validador do argparse: aceita apenas portas entre 1 e 65535."""
    try:
        porta = int(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"porta invalida: {texto!r} (deve ser um numero inteiro)")
    if not 1 <= porta <= 65535:
        raise argparse.ArgumentTypeError(f"porta fora do intervalo 1-65535: {porta}")
    return porta


def ler_argumentos() -> argparse.Namespace:
    """Define e processa os parametros de linha de comando."""
    parser = argparse.ArgumentParser(description="Servidor de chat com WebSockets.")
    parser.add_argument("--host", default="0.0.0.0",
                        help="endereco em que o servidor escuta (padrao: 0.0.0.0)")
    parser.add_argument("--porta", type=porta_valida, default=8765,
                        help="porta em que o servidor escuta (padrao: 8765)")
    return parser.parse_args()


async def executar(host: str, porta: int) -> None:
    """Sobe o servidor WebSocket e o mantem rodando ate ser cancelado."""
    # serve() cria uma tarefa atender_cliente() para cada conexao aceita.
    # Os pings automaticos da biblioteca detectam clientes que sumiram sem
    # fechar a conexao.
    async with serve(atender_cliente, host, porta):
        logging.info("servidor de chat escutando em ws://%s:%d (Ctrl+C para encerrar)", host, porta)
        await asyncio.Future()  # espera para sempre


def main() -> int:
    args = ler_argumentos()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # A biblioteca tambem registra "connection open/closed"; deixamos so os
    # avisos dela para o log mostrar apenas os eventos do chat.
    logging.getLogger("websockets").setLevel(logging.WARNING)
    try:
        asyncio.run(executar(args.host, args.porta))
    except KeyboardInterrupt:
        logging.info("servidor encerrado pelo usuario")
    except OSError as erro:
        # Ex.: porta ja em uso ou endereco invalido.
        logging.error("nao foi possivel iniciar o servidor em %s:%d: %s", args.host, args.porta, erro)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
