import os
import io


class Processador():
    def __init__(self):
        self.__registradores : list[int] = [0] * 32
        self.__pc : int = 0
        self.__memoria : list[int] = [0] * 64 # numero a definir


    def busca(self):
        pass

    def decodifica(self, instrucao : str):
        return instrucao.replace(",", "").split()

    def acessaMem(self):
        pass

    def escreve(self, alvo, resultado):
        self.__registradores[alvo] = resultado


    # NAO É PRA SER FEITO ASSIM EU SÓ TO USANDO ISSO AQUI PA RA PENSAR 
    def executar(self, arq : io.TextIOWrapper):   
        for linha in arq:
            operacao, rd, rs, rt = self.decodifica(linha)
            if linha:
                operacao = linha[0]

            # Aritmeticas
            # rd <- rs + rt
            if operacao == "add": 
                rd, rs, rt = int(rd[1:]), int(rs[1:]), int(rt[1:]) # Corta o "r" da instrucao 
                self.escreve(rd, rs + rt)
            
            elif operacao == "addi":
                rd, rs = int(rd[1:]), int(rs[1:])
                self.escreve(rd, self.__registradores[rs] + int(rt))
                
            elif operacao == "sub":
                rd, rs, rt = int(rd[1:]), int(rs[1:]), int(rt[1:]) # Corta o "r" da instrucao 
                #self.__registradores[rd] = self.__registradores[rs] - self.__registradores[rt]
                self.escreve(rd, rs - rt)
                
            elif operacao == "subi":
                rd, rs = int(rd[1:]), int(rs[1:])
                #self.__registradores[rd] = self.__registradores[rs] - int(rt)
                self.escreve(rd, self.__registradores[rs] - int(rt))

            elif operacao == "mul":
                rd, rs, rt = int(rd[1:]), int(rs[1:]), int(rt[1:])
                #self.__registradores[rd] = self.__registradores[rs] * self.__registradores[rt]
                self.escreve(rd, rs * rt)

            elif operacao == "div":
                rd, rs, rt = int(rd[1:]), int(rs[1:]), int(rt[1:])
                #self.__registradores[rd] = self.__registradores[rs] // self.__registradores[rt]
                self.escreve(rd, rs // rt)

            elif operacao == "mod":
                rd, rs, rt = int(rd[1:]), int(rs[1:]), int(rt[1:])
                #self.__registradores[rd] = self.__registradores[rs] % self.__registradores[rt]
                self.escreve(rd, rs % rt)

            # Desvios
            elif operacao == "blt":
                rd, rs, imm = int(rd[1:]), int(rs[1:]), int(rt)
                if rd < rs:
                    self.__pc += imm

            elif operacao == "bgt":
                rd, rs, imm = int(rd[1:]), int(rs[1:]), int(rt)
                if rd > rs:
                    self.__pc += imm

            elif operacao == "beq":
                rd, rs, imm = int(rd[1:]), int(rs[1:]), int(rt)
                if rd == rs:
                    self.__pc += imm

            elif operacao == "j":
                imm = int(rt)
                self.__pc += imm

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
