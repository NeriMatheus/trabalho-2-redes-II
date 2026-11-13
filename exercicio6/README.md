# Exercício 6: Conexão TCP (Handshake e Encerramento)

## Dependências
- `wireshark`
- `telnet` (para estabelecer conexão raw via TCP)
  - Instalação no Ubuntu: `sudo apt install telnet`

## Como Executar
1. Inicie a captura no Wireshark.
2. No terminal, execute o comando:
   `telnet www.pudim.com.br 80`
   - **Parâmetros:** `www.pudim.com.br` (host de destino) e `80` (porta TCP padrão para HTTP).
3. Aguarde a mensagem "Connected". Para forçar o encerramento, pressione `Ctrl + ]` para chamar o prompt do telnet e digite o comando `quit`.
4. Pare a captura e aplique o filtro `tcp.port == 80`.

## Análise da Captura
A captura demonstra o estabelecimento e o encerramento de uma conexão TCP na porta 80. No início da comunicação, é possível identificar os três pacotes do three-way handshake: [SYN] (pacote 88), [SYN, ACK] (pacote 94) e [ACK] (pacote 95). Ao final da captura, após a interrupção manual via terminal, observam-se os pacotes de encerramento seguro da conexão contendo as flags [FIN, ACK] (pacotes 214 e 260) e suas respectivas confirmações [ACK].
