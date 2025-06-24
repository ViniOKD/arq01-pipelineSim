import os
import io
#IF ID EX MEM WB
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
    if instrucao == "-":
        return instrucao
    else:
        return instrucao.replace(",", " ").split()

def executaOperacao(instrucao):
    if instrucao == "-":
        return instrucao
    
    operacao = instrucao[0]

    if operacao == "add":
        rd,rs,rt =  instrucao[1], instrucao[2], instrucao[3]
        rd, rs, rt = int(rd[1:]), int(rs[1:]), int(rt[1:]) 
        return("add", rd, cpu["registradores"][rs] + cpu["registradores"][rt])
    
    elif operacao == "addi":
        rd,rs,rt =  instrucao[1], instrucao[2], instrucao[3]
        rd, rs = int(rd[1:]), int(rs[1:])
        return("addi", rd, cpu["registradores"][rs] + int(rt))
        
    elif operacao == "sub":
        rd,rs,rt =  instrucao[1], instrucao[2], instrucao[3]
        rd, rs, rt = int(rd[1:]), int(rs[1:]), int(rt[1:]) 
        return("sub", rd, cpu["registradores"][rs] - cpu["registradores"][rt])
        
    elif operacao == "subi":
        rd,rs =  instrucao[1], instrucao[2]
        rd, rs = int(rd[1:]), int(rs[1:])
        return("subi", rd, cpu["registradores"][rs] - int(rt))

    elif operacao == "mul":
        rd,rs,rt =  instrucao[1], instrucao[2], instrucao[3]
        rd, rs, rt = int(rd[1:]), int(rs[1:]), int(rt[1:])
        #self.__registradores[rd] = self.__registradores[rs] * self.__registradores[rt]
        return("mul", rd, cpu["registradores"][rs] * cpu["registradores"][rt])

    elif operacao == "div":
        rd,rs,rt =  instrucao[1], instrucao[2], instrucao[3]
        rd, rs, rt = int(rd[1:]), int(rs[1:]), int(rt[1:])
        return("div", rd, cpu["registradores"][rs] // cpu["registradores"][rt])

    elif operacao == "mod":
        rd,rs,rt =  instrucao[1], instrucao[2], instrucao[3]
        rd, rs, rt = int(rd[1:]), int(rs[1:]), int(rt[1:])
        return("mod", rd, cpu["registradores"][rs] % cpu["registradores"][rt])

    # Desvios
    elif operacao == "blt":
        rd,rs,rt =  instrucao[1], instrucao[2], instrucao[3]
        rd, rs, imm = int(rd[1:]), int(rs[1:]), int(rt)
        if rd < rs:
            cpu["pc"] += imm

    elif operacao == "bgt":
        rd,rs,rt =  instrucao[1], instrucao[2], instrucao[3]
        rd, rs, imm = int(rd[1:]), int(rs[1:]), int(rt)
        if rd > rs:
            cpu["pc"] += imm

    elif operacao == "beq":
        rd,rs,rt =  instrucao[1], instrucao[2], instrucao[3]
        rd, rs, imm = int(rd[1:]), int(rs[1:]), int(rt)
        if rd == rs:
            cpu["pc"] += imm

    elif operacao == "j":
        imm = int(instrucao[1])
        cpu["pc"] += imm

    # Memoria
    elif operacao == "lw":
        rd,rs,rt =  instrucao[1], instrucao[2], instrucao[3]
        rd, rs, imm = int(rd[1:]), int(rs[1:]), int(rt)
        return("lw", rd, rs+imm)

    elif operacao == "sw":
        rd,rs,rt =  instrucao[1], instrucao[2], instrucao[3]
        rd, rs, imm = int(rd[1:]), int(rs[1:]), int(rt)
        return("lw", rd, rs+imm)
    
    # Movimentacao
    elif operacao == "mov":
        rd,rs =  instrucao[1], instrucao[2]
        rd, rs = int(rd[1:]), int(rs[1:])
        return ("mov", rd, cpu["registradores"][rs])

    elif operacao == "movi":
        rd, imm =  int((instrucao[1])[1:]), int(instrucao[2])
        
        return("movi", rd, imm)

    else:
        raise ValueError("operacao invalida")

def acessaMem(resultado):
    if resultado == "-":
        return resultado

    op, rd, imm = resultado
    if op != "lw" or "sw":
        return resultado
    
    if op == "lw":
        valor = cpu["memoria_instrucoes"][imm]
        cpu["registradores"][rd] = valor

    elif op == "sw":
        cpu["registradores"][imm] = rd
    else:
        raise ValueError("mem")

def escreveReg(resultado):
    
    if resultado == "-" :
        return
    op, rd, result = resultado
    if op == "lw" or op == "sw":
        return

    cpu["registradores"][rd] = result


def getDestino(instrucao):
    ## Ela só pega o registrador o qual sera aplicado tal operacao.
    if instrucao != "-":
        return instrucao[1]

def getFonte(instrucao):
    if instrucao == "-":
        return []
    operacao = instrucao[0]
    ## Devido a diferenca de tamanho de argumentos precisa rolar esses ifs aqui, essa funcao vai retornar os registradores "fonte" de valores,
    ## Ai comparando com a funcao de cima getDestino ele verifica se algum registrador que sera utilizado na primeira operacao sera utilizado novamente
    ## Se for utilizado novamente implementa o stall
    if operacao in ["add", "sub", "mul", "div", "mod"]:
        return [int(instrucao[2][1:]), int(instrucao[3][1:])]
    elif operacao in ["addi", "subi"]:
        return [int(instrucao[2][1:])]
    elif operacao == "lw":
        return [int(instrucao[2][1:])]  
    elif operacao == "sw":
        return [int(instrucao[1][1:]), int(instrucao[3][1:])]
    elif operacao == "mov":
        return [int(instrucao[2][1:])]
    elif operacao in ["beq","blt","bgt"]:
        return [int(instrucao[1][1:]), int(instrucao[2][1:])]
    else:
        return []


def hazard():
    fonte = getFonte(pipeline[1]) # ID
    destinos = [getDestino(pipeline[2]), getDestino(pipeline[3]), getDestino(pipeline[4])] # EX MEM WB
    return any(reg in destinos for reg in fonte if reg is not None) # retorna qualquer registro do destinos se o mesmo aparecer na fonte



def avancar_pipeline():
    escreveReg(pipeline[4])
    pipeline[4] = pipeline[3] 
    pipeline[3] = acessaMem(pipeline[2])
    if hazard():
        print("hazard - stall implementado")
        pipeline[2] = '-'
        return
    else:
        pipeline[2] = executaOperacao(pipeline[1])
        pipeline[1] = decodificaInstrucao(pipeline[0])
        pipeline[0] = buscaInstrucao()


def initialise():
    with open("add_mov.txt", "rt") as arq:
        return [linha.strip() for linha in arq]

def main() -> None:
    global instrucoes
    instrucoes = initialise()
    ciclo = 0
    while any(estado != "-" for estado in pipeline) or (cpu["pc"] < len(instrucoes)):
        print(f" Ciclo {ciclo}")
        avancar_pipeline()
        print(pipeline)
        ciclo += 1

    print("\n--- Registradores ---")
    for i, val in enumerate(cpu["registradores"]):
        if val != 0:
            print(f"r{i} = {val}")
            
if __name__ == "__main__":
    main()
    