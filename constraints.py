
from constraint import AllDifferentConstraint,Constraint
from graph import bloco_para_dia
import random
from collections import defaultdict, Counter
import copy

class AllDifferentAttrConstraint(AllDifferentConstraint):
    def __init__(self, attr):
        super().__init__()
        self.attr = attr

    def __call__(self, variables, domains, assignments, forwardcheck=False):
        seen = set()
        for var in variables:
            if var in assignments:
                val = getattr(assignments[var], self.attr)
                if val in seen:
                    return False
                seen.add(val)
        return True

def not_same_room(aula1,aula2):
    if aula1.sala=="Online" or aula2.sala=="Online":
         return True
    return not (aula1.bloco == aula2.bloco and aula1.sala == aula2.sala)

class MaxAulasPorDiaConstraint(Constraint):

    def __init__(self, max_por_dia=3):
        self.max_por_dia = max_por_dia

    def __call__(self, variables, domains, assignments, forwardcheck=False):

        contagem_dias = defaultdict(int)

        for var in variables:
            if var in assignments:
                aula = assignments[var]
                bloco = aula.bloco
                dia = bloco_para_dia(bloco)
                contagem_dias[dia] += 1
                if contagem_dias[dia] > self.max_por_dia:
                    return False
        return True

class OnlineMax3SameDayConstraint(Constraint):

    def __call__(self, variables, domains, assignments, forwardcheck=False):
        aulas_por_turma = defaultdict(list)

        for var in variables:
            if var in assignments and assignments[var].sala == "Online":
                partes = var.split("_")
                turma = partes[3]
                aulas_por_turma[turma].append(assignments[var])

        for aulas_online in aulas_por_turma.values():
            if len(aulas_online) <= 3:
                dias = {bloco_para_dia(a.bloco) for a in aulas_online}
                if len(dias) > 1:
                    return False  
        return True
    
def penalidade_uc_dias_distintos(solucao):
    penalidade = 0
    ucs_por_turma = defaultdict(list)
    
    for var, aula in solucao.items():
        if var.startswith("aula_"):
            partes = var.split("_")
            _, uc, _, turma, _ = partes
            ucs_por_turma[(turma, uc)].append(aula)
    
    for aulas_uc in ucs_por_turma.values():
        dias = [bloco_para_dia(aula.bloco) for aula in aulas_uc]
        contador = Counter(dias)
        for dia, quantidade in contador.items():
            if quantidade > 1:
                penalidade += 2 * (quantidade - 1)
    
    return penalidade

def penalidade_max_4_dias_por_turma(solucao):
    penalidade = 0
    turmas = defaultdict(set)
    for var, aula in solucao.items():
        if var.startswith("aula_"):
            partes = var.split("_")
            _, _, _, turma, _ = partes
            dia = bloco_para_dia(aula.bloco)
            turmas[turma].add(dia)
    for dias_turma in turmas.values():
        if len(dias_turma) >= 4:
            penalidade += len(dias_turma) - 4
    return penalidade

def penalidade_aulas_consecutivas(solucao):
    penalidade = 0
    turmas = defaultdict(lambda: defaultdict(list))
    for var, aula in solucao.items():
        if var.startswith("aula_"):
            partes = var.split("_")
            _, _, _, turma, _ = partes
            dia = bloco_para_dia(aula.bloco)
            turmas[turma][dia].append(aula.bloco)
    for turma, dias in turmas.items():
        for blocos in dias.values():
            blocos.sort()
            for i in range(1, len(blocos)):
                if blocos[i] != blocos[i-1] + 1:
                    penalidade += 1
    return penalidade

def penalidade_aulas_sozinhas(solucao):

    penalidade = 0
    turmas = defaultdict(lambda: defaultdict(list))  

    for var, aula in solucao.items():
        if var.startswith("aula_"):
            partes = var.split("_")
            _, _, _, turma, _ = partes
            dia = bloco_para_dia(aula.bloco)
            turmas[turma][dia].append(aula.bloco)

    for turma, dias in turmas.items():
        for blocos in dias.values():
            if len(blocos) == 1:
                penalidade += 1  

    return penalidade

def penalidade_min_salas_por_turma_por_dia(solucao):

    penalidade = 0
    turmas_por_dia = defaultdict(lambda: defaultdict(set))  # turma -> dia -> salas

    for var, aula in solucao.items():
        if var.startswith("aula_"):
            partes = var.split("_")
            turma = partes[3]
            dia = bloco_para_dia(aula.bloco)
            turmas_por_dia[turma][dia].add(aula.sala)

    for turma, dias in turmas_por_dia.items():
        for salas in dias.values():
            if len(salas) > 1:
                # Penaliza cada sala extra além da primeira
                penalidade += len(salas) - 1

    return penalidade

def pontuacao(solucao):
    return (penalidade_uc_dias_distintos(solucao) +
            penalidade_max_4_dias_por_turma(solucao) +
            penalidade_aulas_consecutivas(solucao) +
            penalidade_aulas_sozinhas(solucao) +
            penalidade_min_salas_por_turma_por_dia(solucao))

def hill_climbing(solucao_inicial, iteracoes=10000):
    melhor_solucao = copy.deepcopy(solucao_inicial)
    melhor_pontuacao = pontuacao(melhor_solucao)

    variaveis = [v for v in melhor_solucao.keys() if v.startswith("aula_")]

    for _ in range(iteracoes):

        var = random.choice(variaveis)
        aula_atual = melhor_solucao[var]

        blocos_possiveis = [b for b in range(1, 21) if b != aula_atual.bloco]
        if not blocos_possiveis:
            continue
        bloco_novo = random.choice(blocos_possiveis)

        nova_solucao = copy.deepcopy(melhor_solucao)
        nova_solucao[var].bloco = bloco_novo

        nova_pontuacao = pontuacao(nova_solucao)
        if nova_pontuacao < melhor_pontuacao:
            melhor_solucao = nova_solucao
            melhor_pontuacao = nova_pontuacao

    return melhor_solucao
