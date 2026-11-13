# Exercício 9: Tráfego DHCP

## Dependências
- `wireshark`
- `network-manager` / `systemd` (padrão do Ubuntu para gerenciar interfaces de rede)

## Como Executar
1. Inicie a captura de pacotes no Wireshark.
2. No terminal, execute:
   `sudo systemctl restart NetworkManager`
   - **Parâmetros:** Comando executado com privilégios de superusuário (`sudo`) para reiniciar o serviço do gerenciador de rede, forçando a interface a se desconectar e solicitar novamente configurações de rede ao servidor DHCP.
3. Pare a captura no Wireshark e filtre por `dhcp` (ou `bootp`).

## Análise da Captura
A captura demonstra o tráfego do protocolo DHCP gerado na rede local ao reiniciar a interface de rede.

**Por que a captura exibe apenas dois pacotes em vez de quatro?**
O processo de alocação de IP padrão (DORA) possui quatro mensagens: Discover, Offer, Request e ACK. No entanto, como o dispositivo já possuía uma concessão de IP prévia válida guardada em cache, o sistema operacional pulou as etapas iniciais de descoberta e realizou apenas uma **Renovação (DHCP Renew)**. 

Por esse motivo, apenas duas mensagens aparecem na comunicação:
1. **Request:** O cliente (máquina local) envia uma requisição direta ao roteador solicitando a manutenção do endereço IP que já estava utilizando.
2. **ACK (Acknowledgment):** O servidor DHCP (roteador) responde confirmando a renovação do aluguel (lease) daquele endereço IP, finalizando a negociação rapidamente.
