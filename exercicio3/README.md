# Exercício 3 — Chat TCP

Chat TCP com vários clientes. Cada participante escolhe um nickname; as mensagens são enviadas aos demais participantes conectados.

## Requisitos

- Linux
- Python 3.10 ou superior
- Não há dependências externas; o programa usa apenas a biblioteca padrão do Python.

Confira a versão instalada:

```bash
python3 --version
```

Se necessário, instale o Python 3 pelo gerenciador de pacotes da sua distribuição. Em Debian/Ubuntu:

```bash
sudo apt update
sudo apt install -y python3
```

## Como executar

Na raiz do repositório, abra um terminal para o servidor:

```bash
cd exercicio3
python3 servidor.py --host 0.0.0.0 --porta 5001
```

Em outro terminal na mesma máquina, inicie um cliente:

```bash
cd exercicio3
python3 cliente.py --host 127.0.0.1 --porta 5001
```

Informe um nickname quando solicitado. Repita o comando do cliente em outros terminais para conectar mais participantes. Digite `sair` para desconectar.

## Parâmetros

- Servidor: `--host` define o endereço de escuta (padrão `0.0.0.0`); `--porta` define a porta TCP (padrão `5001`).
- Cliente: `--host` define o endereço IP do servidor (padrão `127.0.0.1`); `--porta` define a porta TCP (padrão `5001`).

Para clientes em outras máquinas, substitua `127.0.0.1` pelo IP do servidor e permita a porta TCP escolhida no firewall.