
from constraint import AllDifferentConstraint,Constraint
from graph import bloco_para_dia
import random
from collections import defaultdict, Counter
import copy
import math

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
            penalidade += (len(dias_turma) - 4)*2
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
                penalidade += 2  

    return penalidade

def penalidade_min_salas_por_turma_por_dia(solucao):

    penalidade = 0
    turmas_por_dia = defaultdict(lambda: defaultdict(set)) 

    for var, aula in solucao.items():
        if var.startswith("aula_"):
            partes = var.split("_")
            turma = partes[3]
            dia = bloco_para_dia(aula.bloco)
            turmas_por_dia[turma][dia].add(aula.sala)

    for turma, dias in turmas_por_dia.items():
        for salas in dias.values():
            if len(salas) > 1:
                penalidade += len(salas) - 1

    return penalidade

def pontuacao(solucao):
    return (penalidade_uc_dias_distintos(solucao) +
            penalidade_max_4_dias_por_turma(solucao) +
            penalidade_aulas_consecutivas(solucao) +
            penalidade_aulas_sozinhas(solucao) +
            penalidade_min_salas_por_turma_por_dia(solucao))

MAX_AULAS_POR_DIA = 3

def get_parts(var_name):
    partes = var_name.split("_")
    return partes[1], partes[2], partes[3]  

def violates_hard_constraints_for_move(solucao, var, bloco_novo, all_variables):

    uc, professor, turma = get_parts(var)
    nova_aula = copy.deepcopy(solucao[var])
    nova_aula.bloco = bloco_novo


    for other_var, other_aula in solucao.items():
        if other_var == var:
            continue
        if not other_var.startswith("aula_"):
            continue
        _, _, other_turma = get_parts(other_var)
        if other_turma == turma:
            if other_aula.bloco == bloco_novo:
                return True


    for other_var, other_aula in solucao.items():
        if other_var == var:
            continue
        if not other_var.startswith("aula_"):
            continue
        _, other_prof, _ = get_parts(other_var)
        if other_prof == professor:
            if other_aula.bloco == bloco_novo:
                return True


    sala_nova = nova_aula.sala
    if sala_nova != "Online":
        for other_var, other_aula in solucao.items():
            if other_var == var:
                continue
            if not other_var.startswith("aula_"):
                continue
            if getattr(other_aula, "sala", None) == sala_nova:
                if other_aula.bloco == bloco_novo:
                    return True

    contagem_dias = defaultdict(int)

    for other_var, other_aula in solucao.items():
        if not other_var.startswith("aula_"):
            continue
        _, _, other_turma = get_parts(other_var)
        if other_turma != turma:
            continue
        if other_var == var:
            continue
        dia = bloco_para_dia(other_aula.bloco)
        contagem_dias[dia] += 1

    dia_novo = bloco_para_dia(bloco_novo)
    contagem_dias[dia_novo] += 1

    for cont in contagem_dias.values():
        if cont > MAX_AULAS_POR_DIA:
            return True

    online_aulas = []
    for other_var, other_aula in solucao.items():
        if not other_var.startswith("aula_"):
            continue
        _, _, other_turma = get_parts(other_var)
        if other_turma != turma:
            continue
        if other_var == var:
            continue
        if getattr(other_aula, "sala", None) == "Online":
            online_aulas.append(other_aula)

    if sala_nova == "Online":
        online_aulas.append(nova_aula)

    if 1 <= len(online_aulas) <= 3:
        dias_online = {bloco_para_dia(a.bloco) for a in online_aulas}
        if len(dias_online) > 1:
            return True

    return False


def hill_climbing(solucao_inicial, iteracoes=10000, temp_inicial=10.0, decaimento=0.995):
    melhor_solucao = copy.deepcopy(solucao_inicial)
    melhor_pontuacao = pontuacao(melhor_solucao)
    variaveis = [v for v in melhor_solucao.keys() if v.startswith("aula_")]

    temperatura = temp_inicial

    for i in range(iteracoes):
        var = random.choice(variaveis)
        aula_atual = melhor_solucao[var]
        blocos_possiveis = [b for b in range(1, 21) if b != aula_atual.bloco]
        bloco_novo = random.choice(blocos_possiveis)

        if violates_hard_constraints_for_move(melhor_solucao, var, bloco_novo, variaveis):
            continue

        nova_solucao = copy.deepcopy(melhor_solucao)
        nova_solucao[var].bloco = bloco_novo

        nova_pontuacao = pontuacao(nova_solucao)
        delta = nova_pontuacao - melhor_pontuacao

        if delta < 0 or random.random() < math.exp(-delta / temperatura):
            melhor_solucao = nova_solucao
            melhor_pontuacao = nova_pontuacao

        temperatura *= decaimento

    return melhor_solucao
