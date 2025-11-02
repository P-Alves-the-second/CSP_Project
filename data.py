from parser import parse_dataset

with open("dataset.txt", "r", encoding="utf-8") as f:
        dataset = f.read()

parsed_data = parse_dataset(dataset)

def listar_ucs(parsed_data):

    ucs = set()

    if "class_courses" in parsed_data:
        for cursos in parsed_data["class_courses"].values():
            ucs.update(cursos)

    if "teacher_courses" in parsed_data:
        for cursos in parsed_data["teacher_courses"].values():
            ucs.update(cursos)

    return sorted(list(ucs))

TURMAS = list(parsed_data["class_courses"].keys())
PROFESSORES = list(parsed_data["teacher_courses"].keys())
BLOCOS = list(range(1,21))
SALAS = parsed_data["rooms"]
UCS = listar_ucs(parsed_data)

professores_por_turma = {
    "LESI": {"PDM": "João", "ISI": "Pedro", "IA": "Pedro", "SETR": "António", "PA": "Manuel"},
    "LEEC": {"PS": "João", "IM": "João", "R": "Pedro", "IE": "António", "RCSD": "Manuel"},
    "LEIM": {"GSI": "João", "IA": "António", "RCE": "António", "AST": "Manuel", "ISC": "Manuel", "GUS": "Manuel"},
    "LDJG": {"IAAJ": "Ana", "PVR": "Isabel", "TCGEV": "Isabel", "PAG": "Ana"}
}

def achar_turma_por_prof_e_uc(professor, uc):
    for turma, ucs in professores_por_turma.items():
        if uc in ucs and ucs[uc] == professor:
            return turma
    return None
