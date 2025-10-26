from parser import parse_dataset
from pprint import pprint
from constraint import Problem, AllDifferentConstraint

problema = Problem()

with open("dataset.txt", "r", encoding="utf-8") as f:
        dataset = f.read()

parsed_data = parse_dataset(dataset)

TURMAS = list(parsed_data["class_courses"].keys())
PROFESSORES = list(parsed_data["teacher_courses"].keys())
BLOCOS = list(range(1,21))
SALAS = ["Room A","Room B","Room c","Lab 02","Lab 01"]
UCS = []

curso_para_prof = {}
for prof, cursos in parsed_data["teacher_courses"].items():
    for uc in cursos:
        curso_para_prof[uc] = prof

for cursos_prof in parsed_data["teacher_courses"].values():
    for uc in cursos_prof:
        UCS.append(uc)

        professor = curso_para_prof[uc]
        blocos_invalidos = list(parsed_data["teacher_restrictions"].get(professor, []))
        blocos_validos = [b for b in BLOCOS if b not in blocos_invalidos]

        problema.addVariable("bloco_" + uc + "_1",blocos_validos)
        problema.addVariable("bloco_" + uc + "_2",blocos_validos)

        rooms = [parsed_data["room_restrictions"].get(uc, [])]
        if uc in parsed_data["online_classes"]:
                aula_online = parsed_data["online_classes"][uc]
                if aula_online==1:
                        problema.addVariable("sala_" + uc + "_1",["Online"])
                        if uc in parsed_data["room_restrictions"]: problema.addVariable("sala_" + uc + "_2", rooms)
                        else: problema.addVariable("sala_" + uc + "_2", SALAS)
                elif aula_online==2:
                        if uc in parsed_data["room_restrictions"]: problema.addVariable("sala_" + uc + "_1", rooms)
                        else: problema.addVariable("sala_" + uc + "_1", SALAS)  
                        problema.addVariable("sala_" + uc + "_2",["Online"])   
        else: 
                if uc in parsed_data["room_restrictions"]:
                        problema.addVariable("sala_" + uc + "_1", rooms)
                        problema.addVariable("sala_" + uc + "_2", rooms)
                else:
                        problema.addVariable("sala_" + uc + "_1", SALAS)
                        problema.addVariable("sala_" + uc + "_2", SALAS)

for professor in PROFESSORES:
      blocos_invalidos = list(parsed_data["teacher_restrictions"].get(professor, []))
      blocos_validos = [b for b in BLOCOS if b not in blocos_invalidos]

for turma in TURMAS:
      problema.addVariable("ucs_"+turma,parsed_data["class_courses"][turma])

def mostrar_variaveis(problema):
    print("\n=== VARIÁVEIS ADICIONADAS ===")
    for var, domain in problema._variables.items():
        print(f"{var:<25} → {list(domain)}")

mostrar_variaveis(problema)