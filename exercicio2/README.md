# Exercício 2 — Echo UDP

Servidor UDP que devolve ao cliente o mesmo datagrama recebido.

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
cd exercicio2
python3 servidor.py --host 0.0.0.0 --porta 6000
```

Em outro terminal na mesma máquina, execute o cliente:

```bash
cd exercicio2
python3 cliente.py --host 127.0.0.1 --porta 6000 --timeout 3
```

Digite mensagens no cliente para receber o eco. Use `sair` para encerrar.

## Parâmetros

- Servidor: `--host` define o endereço de escuta (padrão `0.0.0.0`); `--porta` define a porta UDP (padrão `6000`).
- Cliente: `--host` define o endereço IP do servidor (padrão `127.0.0.1`); `--porta` define a porta UDP (padrão `6000`); `--timeout` define o tempo de espera por resposta em segundos (padrão `3`).

Para clientes em outras máquinas, substitua `127.0.0.1` pelo IP do servidor e permita a porta UDP escolhida no firewall.