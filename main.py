import sys

if len(sys.argv) != 2:
    print("Uso: python main.py <arquivo>")
    sys.exit(1)

arquivo = sys.argv[1]

config_file = open("config.txt", "r")
memoria = int(config_file.read())

cpu = {
    "registradores": [0] * 32,
    "memoria" : [0] * memoria,
    "pc" : 0,
    "instrucoes" : []
}
# Inicia a pipeline como uma lista de tuplas: (instrucao_original, valor_atual)
# instrucao_original: str, valor_atual: pode ser str, tupla, ou qualquer tipo dependendo do estagio
pipeline = [("-", "-") for _ in range(5)]


operacoes = {
    "add": lambda x, y: x + y,
    "sub": lambda x, y: x - y,
    "mul": lambda x, y: x * y,
    "div": lambda x, y: x // y,
    "mod": lambda x, y: x % y,
}

def buscaInstrucao():
    if cpu["pc"] < len(cpu["instrucoes"]):
        atual = cpu["instrucoes"][cpu["pc"]]
        cpu["pc"] += 1
        return (atual, atual)
    return ("-", "-")

def decodificaInstrucao(instrucao):
    if instrucao == "-":
        return instrucao
    else:
        instrucao = instrucao.replace(",", " ").split()
        if instrucao[0] == "lw" or instrucao[0] == "sw":
            # Remove os parenteses e separa o valor imediato e o registrador
            offset_reg = instrucao[2].replace('(', ' ').replace(')', '').split() # coloca um espaco no lugar do "(" e remove o ')'
            instrucao[2] = offset_reg[0]  # offset
            instrucao.insert(3, offset_reg[1])  # register
            print(instrucao)
        return tuple(instrucao)

def executaOperacao(instrucao):
    
    if instrucao == "-":
        return instrucao
    # O retorno dessa funcao é uma tupla com a operacao e os argumentos no formato (operacao, destino, fonte1, fonte2)
    operacao = instrucao[0]

    if operacao == "add":
        rd,rs,rt =  int(instrucao[1][1:]), int(instrucao[2][1:]), int(instrucao[3][1:]) # remove os r dos registradores e transforma em int
        return("add", rd, operacoes["add"](cpu["registradores"][rs], cpu["registradores"][rt]))
    
    elif operacao == "addi":
        rd,rs,rt =  int(instrucao[1][1:]), int(instrucao[2][1:]), int(instrucao[3])
        return("addi", rd, cpu["registradores"][rs] + rt)
        
    elif operacao == "sub":
        rd,rs,rt =  int(instrucao[1][1:]), int(instrucao[2][1:]), int(instrucao[3][1:]) # remove os r dos registradores e transforma em int
        return("sub", rd, operacoes["sub"](cpu["registradores"][rs], cpu["registradores"][rt]))
        
    elif operacao == "subi":
        rd,rs,rt =  int(instrucao[1][1:]), int(instrucao[2][1:]), int(instrucao[3])
        return("subi", rd, cpu["registradores"][rs] - rt)

    elif operacao == "mul":
        rd,rs,rt =  int(instrucao[1][1:]), int(instrucao[2][1:]), int(instrucao[3])
        return("mul", rd, operacoes["mul"](cpu["registradores"][rs], cpu["registradores"][rt]))

    elif operacao == "div":
        rd,rs,rt =  int(instrucao[1][1:]), int(instrucao[2][1:]), int(instrucao[3])
        return("div", rd, operacoes["div"](cpu["registradores"][rs], cpu["registradores"][rt]))

    elif operacao == "mod":
        rd,rs,rt =  int(instrucao[1][1:]), int(instrucao[2][1:]), int(instrucao[3])
        return("mod", rd, operacoes["mod"](cpu["registradores"][rs], cpu["registradores"][rt]))

    # Desvios
    elif operacao == "blt":
        rd,rs,imm =  int(instrucao[1][1:]), int(instrucao[2][1:]), int(instrucao[3])
        if cpu["registradores"][rd] < cpu["registradores"][rs]:
            print("desvio tomado")
            cpu["pc"] = imm
            pipeline[0] = ("-", "-")
            pipeline[1] = ("-", "-")
        else:
            print("desvio nao tomado")
        return("blt", rd, rs, imm)

    elif operacao == "bgt":
        rd,rs,imm =  int(instrucao[1][1:]), int(instrucao[2][1:]), int(instrucao[3])
        if cpu["registradores"][rd] > cpu["registradores"][rs]:
            print("desvio tomado")
            cpu["pc"] = imm
            pipeline[0] = ("-", "-")
            pipeline[1] = ("-", "-")
        else:
            print("desvio nao tomado")

        return("bgt", rd, rs, imm)

    elif operacao == "beq":
        rd,rs,imm =  int(instrucao[1][1:]), int(instrucao[2][1:]), int(instrucao[3])
        if cpu["registradores"][rd] == cpu["registradores"][rs]:
            print("desvio tomado")
            cpu["pc"] = imm
            pipeline[0] = ("-", "-")
            pipeline[1] = ("-", "-")
        else:
            print("desvio nao tomado")
        return("beq", rd, rs, imm)

    elif operacao == "j":
        imm = int(instrucao[1])
        cpu["pc"] = imm
        pipeline[0] = ("-", "-")
        pipeline[1] = ("-", "-")
        print("desvio incondicional tomado")
        return("j", imm)

    # Memoria
    elif operacao == "lw":
        rd,imm,rs =  int(instrucao[1][1:]), int(instrucao[2]), int(instrucao[3][1:])
        rs = cpu["registradores"][rs]
        return("lw", rd, rs+imm)

    elif operacao == "sw":
        # Armazena o valor de rs na memoria no endereco imm + rt
        rs, imm, rt =  int(instrucao[1][1:]), int(instrucao[2]), int(instrucao[3][1:])
        rt = cpu["registradores"][rt]
        return("sw", rs, rt+imm)
    
    # Movimentacao
    elif operacao == "mov":
        # Atribui o valor de rs ao registrador rd
        # Exemplo: mov r1, r2 -> r1 = r2
        rd, rs = int(instrucao[1][1:]), int(instrucao[2][1:])
        return ("mov", rd, cpu["registradores"][rs])

    elif operacao == "movi":
        # Atribui o valor imediato ao registrador rd
        # Exemplo: movi r1, 10 -> r1 = 10
        rd, imm =  int((instrucao[1])[1:]), int(instrucao[2])
        
        return("movi", rd, imm)

    else:
        raise ValueError("operacao invalida")

def acessaMem(resultado):
    if resultado == "-":
        return resultado

    op = resultado[0]
    if op != "lw" and op != "sw":
        return resultado
    
    if op == "lw":
        return ("lw", resultado[1], cpu['memoria'][resultado[2]])

    elif op == "sw":
        print(resultado)
        cpu["memoria"][resultado[2]] = cpu["registradores"][resultado[1]]
        return resultado
    else:
        raise ValueError("mem")

def escreveReg(resultado):
    
    if resultado == "-" :
        return resultado
    op = resultado[0]
    if op == "sw" or op == "blt" or op == "bgt" or op == "beq" or op == "j":
        return resultado

    cpu["registradores"][resultado[1]] = resultado[2]
    return resultado

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
    if operacao in operacoes:
        return [int(instrucao[2][1:]), int(instrucao[3][1:])]
    elif operacao in ["addi", "subi", "mov"]:
        return [int(instrucao[2][1:])]
    elif operacao == "lw" or operacao == "sw":
        return [int(instrucao[1][1:]), int(instrucao[3][1:])]  
    elif operacao in ["beq","blt","bgt","j"]:
        return [int(instrucao[1][1:]), int(instrucao[2][1:])]
    elif operacao == "movi":
        return [int(instrucao[1][1:])]
    else:
        return []

def hazard():
    fonte = getFonte(pipeline[1][1]) # ID
    destinos = [getDestino(pipeline[2][1]), getDestino(pipeline[3][1]), getDestino(pipeline[4][1])] # EX MEM WB
    return any(reg in destinos for reg in fonte if reg is not None) # retorna qualquer registro do destinos se o mesmo aparecer na fonte

def avancarPipeline():
    escreveReg(pipeline[4][1])
    pipeline[4] = pipeline[3]
    pipeline[3] = (pipeline[2][0], acessaMem(pipeline[2][1]))
    if hazard():
        print("hazard - stall implementado")
        pipeline[2] = ("-", "-")
        return
    else:
        pipeline[2] = (pipeline[1][0], executaOperacao(pipeline[1][1]))
        pipeline[1] = (pipeline[0][0], decodificaInstrucao(pipeline[0][1]))
        pipeline[0] = buscaInstrucao()

def initialise():
    with open(arquivo, "rt") as arq:
        return [linha.strip() for linha in arq]

def imprimePipeline(pipeline):
    cabecalho = ["Busca", "Decodifica", "Executa", "Memoria", "Regist"]
    print("|" + "|".join(f"{x:^15}" for x in cabecalho) + "|")
    print("|" + "|".join(f"{estagio[0]:^15}" for estagio in pipeline) + "|")

def main() -> None:
    cpu["instrucoes"] = initialise()
    print(cpu["instrucoes"])
    ciclo = 0
    # Enquanto houver instrucoes no pipeline ou o pc for menor que o tamanho das instrucoes
    # O any é para verificar se algum estado do pipeline é diferente de "-"
    # se fizesse só com or teria que fazer comparacoes para cada estado do pipeline
    while any(estado[1] != "-" for estado in pipeline) or (cpu["pc"] < len(cpu["instrucoes"])):
        print(f" Ciclo {ciclo}")
        avancarPipeline()
        #print(pipeline)
        imprimePipeline(pipeline)
        print(f"PC: {cpu['pc']}")


       
        # Esses :^15 sao para alinhar os valores no terminal, 15 é o tamanho do alinhamento
        # o map(str, pipeline[2]) é para converter os valores da lista em strings
        # o join é para juntar os valores em uma string
        ciclo += 1

    print("\n--- Registradores ---")
    for i, val in enumerate(cpu["registradores"]):
        if val != 0:
            print(f"r{i} = {val}")
    
    print("\n--- Memoria ---")
    for i, val in enumerate(cpu["memoria"]):
        if val != 0:
            print(f"mem[{i}] = {val}") 
    
if __name__ == "__main__":
    main()
    