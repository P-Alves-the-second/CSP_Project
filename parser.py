import re
from pprint import pprint


def parse_dataset(dataset_text: str):
    sections = {}
    current_section = None
    lines = dataset_text.strip().splitlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#head"):
            continue
        
        # Detecta nova seção (ex: #cc, #dsd, #tr, etc.)
        if line.startswith("#"):
            current_section = line[1:].split("—")[0].strip()
            sections[current_section] = []
            continue
        
        # Adiciona linha à seção atual
        if current_section:
            sections[current_section].append(line)

    # Converte seções em estruturas Python
    parsed = {}

    # #cc — courses assigned to classes (class, courses*)
    if "cc" in sections:
        class_courses = {}
        for l in sections["cc"]:
            parts = l.split()
            class_courses[parts[0]] = parts[1:]
        parsed["class_courses"] = class_courses

    # #olw — courses with just one lesson per week
    if "olw" in sections:
        parsed["one_lesson_week"] = [l.strip() for l in sections["olw"]]

    # #dsd — courses assigned to lecturers (teacher, courses*)
    if "dsd" in sections:
        teacher_courses = {}
        for l in sections["dsd"]:
            parts = l.split()
            teacher_courses[parts[0]] = parts[1:]
        parsed["teacher_courses"] = teacher_courses

    # #tr — timeslot restrictions (teacher, slots_unavailable*)
    if "tr" in sections:
        teacher_restrictions = {}
        for l in sections["tr"]:
            parts = l.split()
            teacher_restrictions[parts[0]] = list(map(int, parts[1:]))
        parsed["teacher_restrictions"] = teacher_restrictions

    # #rr — room restrictions (course, room)
    if "rr" in sections:
        room_restrictions = {}
        for l in sections["rr"]:
            parts = l.split()
            room_restrictions[parts[0]] = parts[1]
        parsed["room_restrictions"] = room_restrictions

    # #oc — online classes (course, lesson_week_index)
    if "oc" in sections:
        online_classes = {}
        for l in sections["oc"]:
            parts = l.split()
            online_classes[parts[0]] = int(parts[1])
        parsed["online_classes"] = online_classes

    return parsed


if __name__ == "__main__":
    # 🔽 Lê o dataset de um arquivo de texto
    with open("dataset.txt", "r", encoding="utf-8") as f:
        dataset = f.read()

    parsed_data = parse_dataset(dataset)

    # Mostra o resultado formatado
    pprint(parsed_data)
