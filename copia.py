# main.py (versão final corrigida)

import sys
import re

# --- Configuração Inicial da CPU e Memória ---
def configurar_simulador():
    """Lê os ficheiros de configuração e de instruções."""
    if len(sys.argv) != 2:
        print("Erro: Forneça o ficheiro de instruções como argumento.")
        print("Uso: python main.py <arquivo_de_instrucoes>")
        sys.exit(1)

    arquivo_instrucoes = sys.argv[1]

    try:
        with open("config.txt", "r") as f:
            tamanho_memoria = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        print("Erro: Verifique se 'config.txt' existe e contém um número válido.")
        sys.exit(1)

    try:
        with open(arquivo_instrucoes, "r") as f:
            instrucoes = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Erro: Ficheiro de instruções '{arquivo_instrucoes}' não encontrado.")
        sys.exit(1)

    cpu = {
        "registradores": [0] * 32,
        "memoria": [0] * tamanho_memoria,
        "pc": 0,
        "instrucoes": instrucoes
    }
    return cpu

# --- Funções Auxiliares para Detetar Fontes e Destinos ---
def get_fontes(inst):
    """Retorna os registradores FONTE de uma instrução."""
    if not isinstance(inst, tuple) or len(inst) < 2: return []
    op = inst[0]
    try:
        if op in ["add", "sub", "mul", "div", "mod", "bgt", "blt", "beq"]:
            return [int(inst[2][1:]), int(inst[3][1:])]
        elif op in ["addi", "subi", "mov"]:
            return [int(inst[2][1:])]
        elif op in ["lw", "sw"]:
            return [int(inst[3][1:])]
    except (IndexError, ValueError): return []
    return []

def get_destino(inst):
    """Retorna o registrador DESTINO de uma instrução."""
    if not isinstance(inst, tuple) or len(inst) < 2: return None
    op = inst[0]
    if op in ["sw", "bgt", "blt", "beq", "j"]: return None
    try:
        return int(inst[1][1:])
    except (IndexError, ValueError): return None

# --- Estágios da Pipeline ---

def decodifica(inst_str):
    """Converte a string de uma instrução numa tupla de operandos."""
    if inst_str == "-": return "-"
    padrao_mem = re.compile(r"(-?\d+)\((r\d+)\)")
    partes = inst_str.replace(",", "").split()
    op = partes[0]
    if op in ["lw", "sw"]:
        match = padrao_mem.search(partes[2])
        if match: return (op, partes[1], match.group(1), match.group(2))
    return tuple(partes)

def executa(inst, cpu):
    """Executa a operação da instrução."""
    if not isinstance(inst, tuple): return "-"
    op = inst[0]
    try:
        if op == "add": return ("write", get_destino(inst), cpu["registradores"][int(inst[2][1:])] + cpu["registradores"][int(inst[3][1:])])
        if op == "addi": return ("write", get_destino(inst), cpu["registradores"][int(inst[2][1:])] + int(inst[3]))
        if op == "sub": return ("write", get_destino(inst), cpu["registradores"][int(inst[2][1:])] - cpu["registradores"][int(inst[3][1:])])
        if op == "mov": return ("write", get_destino(inst), cpu["registradores"][int(inst[2][1:])])
        if op == "movi": return ("write", get_destino(inst), int(inst[2]))
        if op == "lw":
            addr = int(inst[2]) + cpu["registradores"][int(inst[3][1:])]
            return ("load", get_destino(inst), addr)
        if op == "sw":
            addr = int(inst[2]) + cpu["registradores"][int(inst[3][1:])]
            val = cpu["registradores"][int(inst[1][1:])]
            return ("store", addr, val)
        if op == "blt":
            if cpu["registradores"][int(inst[1][1:])] < cpu["registradores"][int(inst[2][1:])]:
                return ("branch_taken", int(inst[3]))
            return ("-",)
    except (IndexError, ValueError): return "-"
    return "-"

def memoria(res_exec, cpu):
    """Acede à memória para 'load' ou 'store'."""
    if not isinstance(res_exec, tuple) or len(res_exec) < 2: return res_exec
    op = res_exec[0]
    if op == "load":
        _, rd, addr = res_exec
        if 0 <= addr < len(cpu["memoria"]): return ("write", rd, cpu["memoria"][addr])
        print(f"Erro: Acesso inválido à memória no endereço {addr}.")
        return ("-",)
    if op == "store":
        _, addr, val = res_exec
        if 0 <= addr < len(cpu["memoria"]): cpu["memoria"][addr] = val
        else: print(f"Erro: Acesso inválido à memória no endereço {addr}.")
        return ("-",)
    return res_exec

def escrita(res_mem, cpu):
    """Escreve o resultado final num registrador."""
    if isinstance(res_mem, tuple) and res_mem[0] == "write":
        _, rd, val = res_mem
        if rd is not None and 0 <= rd < 32: cpu["registradores"][rd] = val

# --- Funções de Impressão ---
def imprime_pipeline(p):
    estagios = ["Busca (IF)", "Decod. (ID)", "Exec. (EX)", "Memória (MEM)", "Escrita (WB)"]
    print("+-" + "-+-".join(["-" * 25] * 5) + "-+")
    print("| " + " | ".join([f"{e:^25}" for e in estagios]) + " |")
    print("+-" + "-+-".join(["-" * 25] * 5) + "-+")
    print("| " + " | ".join([f"{str(inst):^25}" for inst, _ in p]) + " |")
    print("+-" + "-+-".join(["-" * 25] * 5) + "-+")

def imprime_estado_final(cpu):
    print("\n--- Simulação Concluída ---")
    print("Valores finais dos Registradores (não-zero):")
    for i, val in enumerate(cpu["registradores"]):
        if val != 0: print(f"r{i} = {val}")
    
    print("\nValores finais da Memória (não-zero):")
    for i, val in enumerate(cpu["memoria"]):
        if val != 0: print(f"mem[{i}] = {val}")

# --- Ciclo Principal do Simulador ---
def main():
    cpu = configurar_simulador()
    # Pipeline: (instrução_string, dados_processados)
    pipeline = [("-", "-") for _ in range(5)]
    ciclo = 0

    while True:
        print(f"--- Ciclo {ciclo} ---")

        # 1. Detetar Hazards e Desvios (antes de avançar a pipeline)
        # Hazard de dados: A instrução em ID precisa de um resultado de EX ou MEM
        inst_id = pipeline[1][1]
        fontes_id = get_fontes(inst_id)
        
        destino_ex = get_destino(pipeline[2][1])
        destino_mem = get_destino(pipeline[3][1])

        stalled = False
        if fontes_id:
            if (destino_ex is not None and destino_ex in fontes_id) or \
               (destino_mem is not None and destino_mem in fontes_id):
                print(f"STALL: Hazard de dados na instrução '{pipeline[1][0]}'.")
                stalled = True
        
        # O resultado do estágio EX determina se um desvio foi tomado
        res_exec = executa(pipeline[2][1], cpu)
        branch_taken = isinstance(res_exec, tuple) and res_exec[0] == "branch_taken"

        # 2. Avançar a pipeline da direita para a esquerda (WB -> MEM -> EX)
        escrita(memoria(pipeline[3][1], cpu), cpu)
        
        # 3. Atualizar a pipeline para o próximo ciclo
        if branch_taken:
            print(f"DESVIO TOMADO: PC alterado para {res_exec[1]}. A anular IF e ID.")
            cpu["pc"] = res_exec[1]
            # Anula (flush) os estágios IF, ID e EX
            pipeline[0], pipeline[1], pipeline[2] = ("-", "-"), ("-", "-"), ("-", "-")
        elif stalled:
            # A bolha é inserida ao não avançar ID e IF, mas avançando o resto
            pipeline[4] = pipeline[3]
            pipeline[3] = ("-", "-") # Bolha entra no estágio EX (vindo de ID)
        else: # Avanço normal
            pipeline[4] = pipeline[3]
            pipeline[3] = (pipeline[2][0], res_exec)
            pipeline[2] = (pipeline[1][0], inst_id)
            pipeline[1] = pipeline[0]
            # Busca a próxima instrução
            if cpu["pc"] < len(cpu["instrucoes"]):
                inst_str = cpu["instrucoes"][cpu["pc"]]
                pipeline[0] = (inst_str, decodifica(inst_str))
                cpu["pc"] += 1
            else:
                pipeline[0] = ("-", "-")

        imprime_pipeline(pipeline)
        print(f"PC: {cpu['pc']}")
        print(f"Registradores: { {f'r{i}': v for i, v in enumerate(cpu['registradores']) if v != 0} }")
        
        ciclo += 1

        # Condição de término: pipeline vazia e todas as instruções buscadas
        if all(p[0] == '-' for p in pipeline):
            break

    imprime_estado_final(cpu)

if __name__ == "__main__":
    main()