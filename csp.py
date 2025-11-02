from parser import parse_dataset
from pprint import pprint
from itertools import combinations
from collections import defaultdict
from constraints import AllDifferentAttrConstraint, not_same_room, MaxAulasPorDiaConstraint, hill_climbing, OnlineMax3SameDayConstraint
from models import Aula
import data
from graph import mostar_horario


from constraint import Problem, AllDifferentConstraint

problema = Problem()

parsed_data = data.parsed_data

TURMAS = data.TURMAS
PROFESSORES = data.PROFESSORES
BLOCOS = data.BLOCOS
SALAS = data.SALAS
UCS = data.UCS


for professor, cursos in parsed_data["teacher_courses"].items():
    
    for uc in cursos:
        blocos_invalidos = list(parsed_data["teacher_restrictions"].get(professor, []))
        blocos_validos = [b for b in BLOCOS if b not in blocos_invalidos]

        turma = data.achar_turma_por_prof_e_uc(professor,uc)

        room = parsed_data["room_restrictions"].get(uc)
        if room:
                rooms = [room]
        else:
                rooms = SALAS
        
        lista_aulas = []
        lista_aulas_online = []

        for bloco in blocos_validos:
            for room in rooms:
                lista_aulas.append(Aula(room,bloco))
            lista_aulas_online.append(Aula("Online",bloco))

        if uc in parsed_data["online_classes"]:
                aula_online = parsed_data["online_classes"][uc]
                if aula_online == 1:
                        problema.addVariable(f"aula_{uc}_{professor}_{turma}_1", lista_aulas_online)
                        problema.addVariable(f"aula_{uc}_{professor}_{turma}_2", lista_aulas)
                elif aula_online == 2:
                        problema.addVariable(f"aula_{uc}_{professor}_{turma}_1", lista_aulas)
                        problema.addVariable(f"aula_{uc}_{professor}_{turma}_2", lista_aulas_online)
        else:
                problema.addVariable(f"aula_{uc}_{professor}_{turma}_1", lista_aulas)
                problema.addVariable(f"aula_{uc}_{professor}_{turma}_2", lista_aulas)
             

for turma in TURMAS:
        vars_uc = []
        vars_uc.extend([v for v in problema._variables.keys() if turma in v and v.startswith("aula_")])
    
        problema.addConstraint(AllDifferentAttrConstraint("bloco"), vars_uc)
        problema.addConstraint(MaxAulasPorDiaConstraint(max_por_dia=3), vars_uc)
        

for prof in PROFESSORES:
        vars_prof = []
        
        vars_prof.extend([v for v in problema._variables.keys() if prof in v and v.startswith("aula_")])

        problema.addConstraint(AllDifferentAttrConstraint("bloco"), vars_prof)

aulas_vars = [v for v in problema._variables.keys() if v.startswith("aula_")]
problema.addConstraint(OnlineMax3SameDayConstraint(), aulas_vars)

pares_aulas = list(combinations(aulas_vars, 2))

for a1, a2 in pares_aulas:
    problema.addConstraint(not_same_room, (a1, a2))

solucao = problema.getSolution()
solucao_otimizada = hill_climbing(solucao, iteracoes=50000)
horario = []

for var, valor in sorted(solucao_otimizada.items()):
    if var.startswith("aula_"):
        partes = var.split("_")
        _, uc, professor, turma, aula_idx = partes
        aula = "1ª" if aula_idx == "1" else "2ª"
        bloco = valor.bloco
        sala = valor.sala

        horario.append({
            "Turma": turma,
            "UC": uc,
            "Aula": aula,
            "Bloco": bloco,
            "Professor": professor,
            "Sala": sala
        })

mostar_horario(horario)