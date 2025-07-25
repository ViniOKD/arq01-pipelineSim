import sys

# O arquivo de configuração (config.txt) deve conter um único número inteiro representando o tamanho da memória
# 
# Verifica se o número de argumentos é correto
if len(sys.argv) != 2:
    print("Uso: python main.py <arquivo>")
    sys.exit(1)

arquivo = sys.argv[1]
if not arquivo.endswith(".txt"):
    raise ValueError("O arquivo deve ter a extensão .txt")

# Verifica se o arquivo de configuração existe e lê o tamanho da memória
try:
    config_file = open("config.txt", "r")
except FileNotFoundError:
    raise FileNotFoundError("Arquivo de configuração 'config.txt' não encontrado.")

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

# Dicionário de operações
operacoes = {
    "add": lambda x, y: x + y,
    "sub": lambda x, y: x - y,
    "mul": lambda x, y: x * y,
    "div": lambda x, y: x // y if y != 0 else 0,
    "mod": lambda x, y: x % y if y != 0 else 0,
}

def buscaInstrucao():
    ''' Busca a próxima instrução a ser executada.
    '''
    if cpu["pc"] < len(cpu["instrucoes"]):
        atual = cpu["instrucoes"][cpu["pc"]]
        cpu["pc"] += 1
        return (atual, atual)
    return ("-", "-")

def decodificaInstrucao(instrucao):
    ''' Decodifica uma instrução em uma tupla.
    Retorna uma tupla no formato (operacao, destino, fonte1, fonte2)
    '''
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
    ''' Executa a operação da instrução decodificada.
    Retorna uma tupla com a operação e os resultados.
    Formato: (operacao, destino, resultado)
    '''
    
    if instrucao == "-":
        return instrucao
    # O retorno dessa funcao é uma tupla com a operacao e os argumentos no formato (operacao, destino, fonte1, fonte2)
    operacao = instrucao[0]


    if operacao in operacoes:
        rd,rs,rt =  int(instrucao[1][1:]), int(instrucao[2][1:]), int(instrucao[3][1:]) # remove os r dos registradores e transforma em int
        return(operacao, rd, operacoes[operacao](cpu["registradores"][rs], cpu["registradores"][rt]))

    if operacao in ["addi", "subi"]:
        rd, rs, imm = int(instrucao[1][1:]), int(instrucao[2][1:]), int(instrucao[3])
        resultado = cpu["registradores"][rs] + imm if operacao == "addi" else cpu["registradores"][rs] - imm
        return (operacao, rd, resultado)

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
        rd,imm,rs =  int(instrucao[1][1:]), int(instrucao[2]), int(instrucao[3][1:])
        rs = cpu["registradores"][rs]
        return("sw", rd, rs+imm)
    
    # Movimentacao
    elif operacao == "mov":
        rd,rs =  int(instrucao[1][1:]), int(instrucao[2][1:])
        return ("mov", rd, cpu["registradores"][rs])

    elif operacao == "movi":
        rd, imm =  int((instrucao[1])[1:]), int(instrucao[2])
        
        return("movi", rd, imm)

    else:
        raise ValueError("Há uma instrução inválida: " + operacao)

def acessaMem(resultado):
    '''
    Acessa a memória para ler ou escrever valores.
    '''
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
    '''
    Escreve o resultado de uma instrução no registrador correspondente.
    '''
    if resultado == "-" :
        return resultado
    op = resultado[0]
    if op == "sw" or op == "blt" or op == "bgt" or op == "beq" or op == "j":
        return resultado

    cpu["registradores"][resultado[1]] = resultado[2]
    return resultado


def getDestino(instrucao):
    if instrucao == "-":
        return None
    
    operacao = instrucao[0]
    
    # Instruções que não escrevem em registradores
    if operacao in ["sw", "beq", "blt", "bgt", "j"]:
        return None
    
    # Verificar tipo do segundo elemento
    destino = instrucao[1]
    
    if isinstance(destino, str):
        # Formato "r1" → extrair número
        return int(destino[1:])
    elif isinstance(destino, int):
        # Já é número do registrador
        return destino
    else:
        return None
def getFonte(instrucao):
    if instrucao == "-":
        return []
    
    op = instrucao[0]
    
    # 2 registradores fonte
    if op in ["add", "sub", "mul", "div", "mod"]:
        return [int(instrucao[2][1:]), int(instrucao[3][1:])]
    
    # 1 registrador fonte    
    elif op in ["addi", "subi", "mov"]:
        return [int(instrucao[2][1:])]
    
    # Casos especiais
    elif op == "lw":
        return [int(instrucao[3][1:])]  # só o registrador base
    elif op == "sw": 
        return [int(instrucao[1][1:]), int(instrucao[3][1:])]
    elif op in ["beq", "blt", "bgt"]:
        return [int(instrucao[1][1:]), int(instrucao[2][1:])]
    
    # Sem fontes: movi, j
    return []

def hazard():
    ''' Verifica se há hazard de dados no pipeline.
    A funcao getFonte retorna os registradores fonte de uma instrução.
    A funcao getDestino retorna o registrador destino de uma instrução.
    A funcao hazard verifica se algum dos registradores fonte da instrução atual (ID) está sendo escrito em um dos estágios seguintes (EX, MEM, WB).
    '''
    fonte = getFonte(pipeline[1][1]) # ID
    destinos = [getDestino(pipeline[2][1]), getDestino(pipeline[3][1]), getDestino(pipeline[4][1])] # EX MEM WB
    return any(reg in destinos for reg in fonte if reg is not None) # retorna qualquer registro do destinos se o mesmo aparecer na fonte

def avancarPipeline():
    escreveReg(pipeline[4][1])
    pipeline[4] = pipeline[3]
    pipeline[3] = (pipeline[2][0], acessaMem(pipeline[2][1]))
    if hazard():
        print("Hazard de dados - Inserindo stall")
        pipeline[2] = ("-", "-")
        return
    else:
        pipeline[2] = (pipeline[1][0], executaOperacao(pipeline[1][1]))
        pipeline[1] = (pipeline[0][0], decodificaInstrucao(pipeline[0][1]))
        pipeline[0] = buscaInstrucao()

def initialise():
    try:
        with open(arquivo, "rt") as arq:
            instrucoes = [linha.strip() for linha in arq]
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo de instruções '{arquivo}' não encontrado.")
    return instrucoes

def imprimePipeline(pipeline):
    cabecalho = ["Busca", "Decodifica", "Executa", "Memoria", "Regist"]
    print("|" + "|".join(f"{x:^15}" for x in cabecalho) + "|")
    print("|" + "|".join(f"{estagio[0]:^15}" for estagio in pipeline) + "|")

def main() -> None:
    cpu["instrucoes"] = initialise()
    ciclo = 0
    if not cpu["instrucoes"]:
        raise ValueError("Nenhuma instrução encontrada no arquivo.")
    # Enquanto houver instrucoes no pipeline ou o pc for menor que o tamanho das instrucoes
    # O any é para verificar se algum estado do pipeline é diferente de "-"
    # se fizesse só com or teria que fazer comparacoes para cada estado do pipeline
    while any(estado[1] != "-" for estado in pipeline) or (cpu["pc"] < len(cpu["instrucoes"])):
        print(f" Ciclo {ciclo}")
        avancarPipeline()

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
    