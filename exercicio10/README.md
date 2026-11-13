# Exercício 10 — Chat em Rede com WebSockets

Chat em tempo real com WebSockets. O servidor aceita vários clientes ao mesmo tempo e
retransmite (broadcast) cada mensagem recebida para todos os demais, identificando o
remetente pelo nome de usuário. Servidor e cliente são escritos em Python com a biblioteca
`websockets` e `asyncio`.

## Dependências

- Python 3.10 ou superior.
- Biblioteca `websockets` (versão 13 ou superior).

Em Debian/Ubuntu, `pip` e `venv` não vêm com o Python e precisam ser instalados antes:

```bash
sudo apt update && sudo apt install -y python3-pip python3-venv
```

Instalação (dentro do diretório `exercicio10/`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Como executar

Abra um terminal para o servidor e um para cada participante, todos dentro de `exercicio10/`
(com o ambiente virtual ativado).

**Terminal 1 — servidor:**

```bash
python3 servidor.py --host 0.0.0.0 --porta 8765
```

**Terminais 2, 3, ... — clientes:**

```bash
python3 cliente.py --host 127.0.0.1 --porta 8765 --nome ana
```

```bash
python3 cliente.py --host 127.0.0.1 --porta 8765 --nome bia
```

Se `--nome` for omitido, o cliente pergunta o nome ao iniciar.

Digite uma mensagem e tecle Enter para enviá-la. Para sair, digite `/sair` (ou use `Ctrl+C` / `Ctrl+D`).
Encerre o servidor com `Ctrl+C`.

Exemplo do que a `ana` vê:

```
Conectado a ws://127.0.0.1:8765 como 'ana'. Digite as mensagens e tecle Enter (/sair para sair).
*** bia entrou no chat ***
[bia] oi ana
*** bia saiu do chat ***
```

## Parâmetros

### `servidor.py`

| Parâmetro | Padrão    | Descrição                           |
|-----------|-----------|-------------------------------------|
| `--host`  | `0.0.0.0` | Endereço em que o servidor escuta.  |
| `--porta` | `8765`    | Porta (1–65535).                    |

### `cliente.py`

| Parâmetro | Padrão      | Descrição                                                    |
|-----------|-------------|--------------------------------------------------------------|
| `--host`  | `127.0.0.1` | Endereço do servidor.                                        |
| `--porta` | `8765`      | Porta do servidor (1–65535).                                 |
| `--nome`  | (pergunta)  | Nome de usuário, com até 20 caracteres.                      |

## Protocolo

Mensagens de texto sobre WebSocket:

1. A primeira mensagem do cliente é o seu nome de usuário. O servidor responde `OK` ou
   `ERRO: <motivo>` (nome vazio, com mais de 20 caracteres ou já em uso) e, no caso de erro,
   fecha a conexão.
2. Cada mensagem seguinte é retransmitida aos demais clientes como `[nome] texto`.
3. Entradas e saídas são anunciadas como `*** nome entrou no chat ***` e `*** nome saiu do chat ***`.

Mensagens vazias são ignoradas e mensagens com mais de 1000 caracteres são recusadas.

## Tratamento de falhas

- **Queda inesperada de um cliente** (processo morto, rede interrompida): o servidor registra
  um aviso no log, remove o cliente, avisa os demais que ele saiu e continua atendendo normalmente.
- **Erro ao atender um cliente**: fica restrito à conexão daquele cliente.
- **Cliente que conecta e não informa o nome**: é desconectado após 30 segundos.
- **Servidor fora do ar ou encerrado durante o chat**: o cliente exibe uma mensagem de erro e
  termina com código de saída `1`.
- **Porta já em uso**: o servidor informa o erro e termina com código de saída `1`.
