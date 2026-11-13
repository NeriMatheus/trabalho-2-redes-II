A captura demonstra o estabelecimento e o encerramento de uma conexão TCP na porta 80, gerada através da ferramenta telnet.
No início da comunicação, é possível identificar os três pacotes do three-way handshake: [SYN] (pacote 88), [SYN, ACK] (pacote 94) e [ACK] (pacote 95).
Ao final da captura, após a interrupção manual via terminal, observam-se os pacotes de encerramento seguro da conexão contendo as flags [FIN, ACK] (pacotes 214 e 260) e suas respectivas confirmações [ACK].
