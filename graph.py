import matplotlib.pyplot as plt
import pandas as pd


def bloco_para_dia(bloco):
        if 1 <= bloco <= 4:
            return "Segunda"
        elif 5 <= bloco <= 8:
            return "Terça"
        elif 9 <= bloco <= 12:
            return "Quarta"
        elif 13 <= bloco <= 16:
            return "Quinta"
        elif 17 <= bloco <= 20:
            return "Sexta"
        else:
            return "Outro"

def mostrar_horario(horario):
    df = pd.DataFrame(horario)

    df['Dia'] = df['Bloco'].apply(bloco_para_dia)
    df['Bloco_no_dia'] = df['Bloco'] % 4
    df['Bloco_no_dia'] = df['Bloco_no_dia'].replace(0, 4)  

    turmas = df['Turma'].unique()
    fig, ax = plt.subplots(figsize=(14, 6))

    colors = plt.cm.tab20.colors
    ucs = df['UC'].unique()
    uc_color = {uc: colors[i % len(colors)] for i, uc in enumerate(ucs)}

    dia_offsets = {"Segunda":0, "Terça":5, "Quarta":10, "Quinta":15, "Sexta":20}

    for i, turma in enumerate(turmas):
        turma_data = df[df['Turma'] == turma]
        for _, row in turma_data.iterrows():
            offset = dia_offsets[row['Dia']]
            ax.barh(i, 1, left=row['Bloco_no_dia'] + offset,
                    color=uc_color[row['UC']], edgecolor='black')
            ax.text(row['Bloco_no_dia'] + offset + 0.2, i, f"{row['UC']}\n{row['Professor']}\n{row['Sala']}",
                    va='center', ha='left', fontsize=7)

    for offset in dia_offsets.values():
        ax.axvline(offset, color='black', linestyle='--', linewidth=0.7)

    ax.set_yticks(range(len(turmas)))
    ax.set_yticklabels(turmas)
    ax.set_xlabel("Dia da semana / Bloco")
    ax.set_ylabel("Turma")
    ax.set_title("Horário das Turmas")

    ax.set_xticks([dia_offsets[d] + 2 for d in dia_offsets])
    ax.set_xticklabels(list(dia_offsets.keys()))

    ax.set_xlim(0, 25)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.show()