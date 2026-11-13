A captura demonstra o tráfego do protocolo DHCP gerado na rede local ao reiniciar a interface de rede. 
Como o dispositivo já possuía uma concessão de IP prévia em cache, o sistema realizou uma Renovação (DHCP Renew) em vez do processo DORA completo.
Foram identificadas perfeitamente as duas mensagens dessa negociação:
1. Request: O cliente (máquina local) enviou uma requisição solicitando a manutenção do endereço IP utilizado anteriormente.
2. ACK (Acknowledgment): O servidor DHCP (roteador) respondeu confirmando a renovação do aluguel (lease) do endereço IP para o cliente.
