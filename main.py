import os
import io
#
# BUSCA -> DECOD -> EXEC -> ACESSO -> ESCRITA
#
cpu = {
    "registradores": [0] * 32,
    "memoria_instrucoes" : [0] * 64,
    "pc" : 0,
}
pipeline = ["-"] * 5


def buscaInstrucao():
    if cpu["pc"] < len(instrucoes):
        atual = instrucoes[cpu["pc"]]
        cpu["pc"] += 1
        return atual
    return "-"

def decodificaInstrucao(instrucao):
    return instrucao.replace(",", "").split()

def executaOperacao(instrucao):

    operacao,rd,rs,rt = instrucao[0], instrucao[1], instrucao[2], instrucao[3], 

    if operacao == "add": 
        rd, rs, rt = int(rd[1:]), int(rs[1:]), int(rt[1:]) 
        return(rd, cpu["registradores"][rs] + cpu["registradores"][rt])
    
    elif operacao == "addi":
        rd, rs = int(rd[1:]), int(rs[1:])
        return(rd, cpu["registradores"][rs] + int(rt))
        
    elif operacao == "sub":
        rd, rs, rt = int(rd[1:]), int(rs[1:]), int(rt[1:]) 
        return( rd, cpu["registradores"][rs] - cpu["registradores"][rt])
        
    elif operacao == "subi":
        rd, rs = int(rd[1:]), int(rs[1:])
        return( rd, cpu["registradores"][rs] - int(rt))

    elif operacao == "mul":
        rd, rs, rt = int(rd[1:]), int(rs[1:]), int(rt[1:])
        #self.__registradores[rd] = self.__registradores[rs] * self.__registradores[rt]
        return( rd, cpu["registradores"][rs] * cpu["registradores"][rt])

    elif operacao == "div":
        rd, rs, rt = int(rd[1:]), int(rs[1:]), int(rt[1:])
        return( rd, cpu["registradores"][rs] // cpu["registradores"][rt])

    elif operacao == "mod":
        rd, rs, rt = int(rd[1:]), int(rs[1:]), int(rt[1:])
        return( rd, cpu["registradores"][rs] % cpu["registradores"][rt])

    # Desvios
    elif operacao == "blt":
        rd, rs, imm = int(rd[1:]), int(rs[1:]), int(rt)
        if rd < rs:
            cpu["pc"] += imm

    elif operacao == "bgt":
        rd, rs, imm = int(rd[1:]), int(rs[1:]), int(rt)
        if rd > rs:
            cpu["pc"] += imm

    elif operacao == "beq":
        rd, rs, imm = int(rd[1:]), int(rs[1:]), int(rt)
        if rd == rs:
            cpu["pc"] += imm

    elif operacao == "j":
        imm = int(rt)
        cpu["pc"] += imm

    # Memoria
    elif operacao == "lw":
        pass

    elif operacao == "sw":
        pass
    
    # Movimentacao
    elif operacao == "mov":
        pass

    elif operacao == "movi":
        pass

    else:
        raise ValueError("operacao invalida")
    pass

def acessaMem(resultado):
    print("???")
    return resultado


def escreveReg(resultado):
    if resultado == "-":
        return
    rd, result = resultado
    cpu["registradores"][rd] = result


# Ta zoado isso aqui.
def avancar_pipeline():
    escreveReg(pipeline[4])
    pipeline[4] = pipeline[3] 
    pipeline[3] = acessaMem(pipeline[2])

    pipeline[2] = executaOperacao(pipeline[1])
    pipeline[1] = decodificaInstrucao(pipeline[0])
    pipeline[0] = buscaInstrucao()


def initialise():
    with open("instrucoes.txt", "rt") as arq:
        return [linha.replace(",", "").split() for linha in arq]

def main() -> None:
    global instrucoes
    instrucoes = initialise()
    ciclo = 0
    while (estado != "-" for estado in pipeline) or (cpu["pc"] < len(instrucoes)):
        print(f" Ciclo {ciclo}")
        avancar_pipeline()
        ciclo += 1

if __name__ == "__main__":
    main()
    