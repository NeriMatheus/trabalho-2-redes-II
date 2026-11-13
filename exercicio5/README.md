# Exercício 5: Tráfego HTTP

## Dependências
- `wireshark` (para captura de pacotes)
- `wget` (para requisição HTTP via terminal)
  - Instalação no Ubuntu: `sudo apt install wget`

## Como Executar
1. Inicie a captura de pacotes no Wireshark na interface de rede ativa (ex: `wlp1s0`).
2. Abra o terminal e execute o comando exato:
   `wget http://www.pudim.com.br/`
   - **Parâmetros:** A URL alvo foi passada diretamente para forçar uma requisição GET simples, evitando o redirecionamento automático para HTTPS que os navegadores web modernos forçam.
3. Pare a captura no Wireshark e filtre por `http`.

## Análise da Captura
A captura demonstra o tráfego HTTP gerado via terminal. Na requisição (GET.png), foi identificado o método GET para a URL http://www.pudim.com.br/. Na resposta do servidor (200 OK.png), o código de status retornado foi HTTP/1.1 200 OK. Ainda no pacote de resposta, foram identificados os cabeçalhos Content-Type: text/html e Server: cloudflare.
