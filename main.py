import os
from processador import *
import io


# Verificar se o arquivo de instrucoes tera nome fixo ou sera passado como argumento
def initialise() -> io.TextIOWrapper:
    arq = open("instrucoes.txt", "rt")   
    return arq

def main() -> None:
    cpu = Processador()
    arq = initialise() 

if __name__ == "__main__":
    main()
    