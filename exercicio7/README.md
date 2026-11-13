# Exercício 7: Resolução de Nomes (DNS)

## Dependências
- `wireshark`
- `iputils-ping` (pacote padrão do sistema contendo o utilitário ping)

## Como Executar
1. Inicie a captura de pacotes no Wireshark.
2. No terminal, dispare o comando:
   `ping -c 1 www.uol.com.br`
   - **Parâmetros:** `-c 1` define a contagem (count) limitando o teste a apenas 1 disparo de pacote, o que já é suficiente para forçar o sistema operacional a realizar uma consulta DNS e descobrir o IP do host antes de enviar o ping.
3. Pare a captura no Wireshark e aplique o filtro `dns`.

## Análise da Captura
A captura demonstra o processo de resolução de nomes via protocolo DNS. Analisando a requisição expandida na aba "Queries", o tipo de registro consultado foi o Tipo A (type A) para o domínio www.uol.com.br. O servidor DNS responsável por processar e responder à requisição foi o de IP 177.74.224.29 (identificado na coluna Source do pacote de resposta). No pacote de resposta (pacote 61), o servidor retornou 5 registros (Answer RRs: 5), incluindo o endereço IPv4 solicitado e um apontamento CNAME.
