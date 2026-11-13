# Exercício 4 — Servidor de Hora com Threads (TCP)

Servidor TCP multithread que devolve a hora atual (`HH:MM:SS`) a cada cliente que a solicita.
Cada conexão é atendida em uma thread própria e o total de clientes atendidos é mantido em um
contador protegido por `threading.Lock`, exibido em todas as linhas de log.

## Dependências

- Python 3.10 ou superior.
- Nenhuma biblioteca externa (apenas a biblioteca padrão).

## Como executar

Abra dois terminais dentro do diretório `exercicio4/`.

**Terminal 1 — servidor:**

```bash
python3 servidor.py --host 0.0.0.0 --porta 7000
```

**Terminal 2 — cliente:**

```bash
python3 cliente.py --host 127.0.0.1 --porta 7000
```

Saída esperada no cliente:

```
[cliente 1] Hora recebida do servidor: 16:38:29
```

Para demonstrar o atendimento em paralelo, dispare vários clientes de uma vez:

```bash
python3 cliente.py --host 127.0.0.1 --porta 7000 --clientes 20
```

Encerre o servidor com `Ctrl+C`.

## Parâmetros

### `servidor.py`

| Parâmetro   | Padrão    | Descrição                                                        |
|-------------|-----------|------------------------------------------------------------------|
| `--host`    | `0.0.0.0` | Endereço em que o servidor escuta.                               |
| `--porta`   | `7000`    | Porta TCP (1–65535).                                             |
| `--timeout` | `10`      | Segundos de espera pela solicitação de cada cliente conectado.   |

### `cliente.py`

| Parâmetro    | Padrão      | Descrição                                          |
|--------------|-------------|----------------------------------------------------|
| `--host`     | `127.0.0.1` | Endereço do servidor.                              |
| `--porta`    | `7000`      | Porta TCP do servidor (1–65535).                   |
| `--timeout`  | `5`         | Segundos de espera pela conexão e pela resposta.   |
| `--clientes` | `1`         | Número de clientes simultâneos (um por thread).    |

## Protocolo

Mensagens de texto em UTF-8, uma por linha (terminadas em `\n`):

| Sentido            | Mensagem                                             |
|--------------------|------------------------------------------------------|
| cliente → servidor | `HORA`                                               |
| servidor → cliente | `HH:MM:SS` (ou `ERRO: ...` para um comando inválido) |

Após responder, o servidor fecha a conexão.

## Logs do servidor

Cada linha traz data/hora, nível, thread, cliente (`ip:porta`) e o contador de atendimentos.
Há uma linha quando a solicitação é recebida e outra quando é atendida:

```
2026-11-12 16:38:29 | INFO    | Thread-1 (atender_cliente) | cliente=127.0.0.1:64386 | atendidos=0 | solicitacao recebida: 'HORA'
2026-11-12 16:38:29 | INFO    | Thread-1 (atender_cliente) | cliente=127.0.0.1:64386 | atendidos=1 | solicitacao atendida: hora enviada 16:38:29
```

## Tratamento de falhas

O servidor continua funcionando quando um cliente falha. Cada caso abaixo gera apenas uma
linha de aviso no log e encerra somente a thread daquele cliente:

- cliente fecha a conexão sem enviar nada;
- cliente conecta e fica mudo (encerrado após `--timeout` segundos);
- conexão é derrubada abruptamente (reset);
- comando inválido (o servidor responde `ERRO: ...`).

O cliente trata conexão recusada, host desconhecido, tempo esgotado e resposta de erro,
terminando com código de saída `1` nesses casos. Portas e demais parâmetros inválidos são
rejeitados na linha de comando.
