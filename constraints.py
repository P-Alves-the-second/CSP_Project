
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
                # Penalidade para cada aula extra no mesmo dia
                penalidade += 1 * (quantidade - 1)
    
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
    turmas = defaultdict(lambda: defaultdict(list))  # turma -> dia -> lista de blocos

    for var, aula in solucao.items():
        if var.startswith("aula_"):
            partes = var.split("_")
            _, _, _, turma, _ = partes
            dia = bloco_para_dia(aula.bloco)
            turmas[turma][dia].append(aula.bloco)

    for turma, dias in turmas.items():
        for blocos in dias.values():
            if len(blocos) == 1:
                penalidade += 1  # aula isolada → penalidade

    return penalidade


def pontuacao(solucao):
    return (penalidade_uc_dias_distintos(solucao) +
            penalidade_max_4_dias_por_turma(solucao) +
            penalidade_aulas_consecutivas(solucao) +
            penalidade_aulas_sozinhas(solucao))

def hill_climbing(solucao_inicial, iteracoes=10000):
    melhor_solucao = copy.deepcopy(solucao_inicial)
    melhor_pontuacao = pontuacao(melhor_solucao)

    variaveis = [v for v in melhor_solucao.keys() if v.startswith("aula_")]

    for _ in range(iteracoes):
        # Escolher uma aula aleatória
        var = random.choice(variaveis)
        aula_atual = melhor_solucao[var]

        # Trocar para outro bloco aleatório
        blocos_possiveis = [b for b in range(1, 21) if b != aula_atual.bloco]
        if not blocos_possiveis:
            continue
        bloco_novo = random.choice(blocos_possiveis)

        # Criar nova solução candidata
        nova_solucao = copy.deepcopy(melhor_solucao)
        nova_solucao[var].bloco = bloco_novo

        # Avaliar pontuação completa (todas as penalidades)
        nova_pontuacao = pontuacao(nova_solucao)
        if nova_pontuacao < melhor_pontuacao:
            melhor_solucao = nova_solucao
            melhor_pontuacao = nova_pontuacao

    return melhor_solucao
