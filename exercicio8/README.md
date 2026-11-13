# Exercício 8: Tráfego ICMP

## Dependências
- `wireshark`
- `iputils-ping` (utilitário padrão do sistema)

## Como Executar
1. Inicie a captura de pacotes no Wireshark.
2. No terminal, execute:
   `ping -c 4 192.168.1.1`
   - **Parâmetros:** `-c 4` limita o envio a exatamente 4 pacotes ICMP Request, e `192.168.1.1` é o IP do gateway/roteador da rede local (host de destino).
3. Pare a captura no Wireshark e aplique o filtro `icmp`.

## Análise da Captura
A captura demonstra o teste de conectividade na rede local utilizando o protocolo ICMP disparado para o IP 192.168.1.1. A lista de pacotes exibe com sucesso as 4 solicitações do tipo "Echo (ping) request" e suas respectivas confirmações "Echo (ping) reply". Analisando os detalhes da camada ICMP no pacote de resposta selecionado (pacote 30), o tempo de ida e volta (RTT - Round Trip Time) exato calculado foi de 1.766 ms.
