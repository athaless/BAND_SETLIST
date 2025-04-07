# Instalar o Gradio (se necessário)
!pip install gradio --quiet

import csv
import os
import random
import gradio as gr

ARQUIVO_CSV = "repertorio.csv"

# --- Utilitários ---

def converter_tempo(tempo_str):
    tempo_str = str(tempo_str).strip().replace(',', '.')
    if ':' in tempo_str:
        minutos, segundos = map(int, tempo_str.split(':'))
        return minutos + (segundos / 60)
    return float(tempo_str)

def inicializar_csv():
    if not os.path.exists(ARQUIVO_CSV):
        with open(ARQUIVO_CSV, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["titulo", "autor", "tempo_min", "score"])

def carregar_repertorio():
    repertorio = []
    with open(ARQUIVO_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["tempo_min"] = converter_tempo(row["tempo_min"])
                row["score"] = int(row["score"])
                repertorio.append(row)
            except Exception as e:
                pass
    return repertorio

def salvar_repertorio(repertorio):
    with open(ARQUIVO_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["titulo", "autor", "tempo_min", "score"])
        writer.writeheader()
        for musica in repertorio:
            writer.writerow(musica)

# --- Funções principais ---

def adicionar_musica(titulo, autor, tempo):
    try:
        tempo_float = converter_tempo(tempo)
        nova = {"titulo": titulo, "autor": autor, "tempo_min": tempo_float, "score": 0}
        rep = carregar_repertorio()
        rep.append(nova)
        salvar_repertorio(rep)
        return "✅ Música adicionada com sucesso!"
    except Exception as e:
        return f"❌ Erro: {e}"

def gerar_por_tempo(tempo_total):
    tempo_total = float(tempo_total)
    repertorio = carregar_repertorio()
    repertorio.sort(key=lambda x: x['score'])
    random.shuffle(repertorio)

    setlist = []
    tempo_acumulado = 0

    for musica in repertorio:
        if tempo_acumulado + musica["tempo_min"] <= tempo_total:
            setlist.append(musica)
            tempo_acumulado += musica["tempo_min"]
            musica["score"] += 1

    salvar_repertorio(repertorio)
    return formatar_setlist(setlist)

def gerar_20_musicas():
    repertorio = carregar_repertorio()
    repertorio.sort(key=lambda x: (x['score'], random.random()))
    setlist = repertorio[:20]
    for musica in setlist:
        musica["score"] += 1
    salvar_repertorio(repertorio)
    return formatar_setlist(setlist)

def formatar_setlist(setlist):
    linhas = []
    for i, m in enumerate(setlist):
        linha = f"{i+1}. {m['titulo']} - {m['autor']} ({round(m['tempo_min'], 2)} min)"
        linhas.append(linha)
    return "\n".join(linhas)

def mostrar_repertorio():
    repertorio = carregar_repertorio()
    # repertorio = sorted(repertorio, key=lambda x: x['titulo'])
    repertorio.sort(key=lambda x: x['titulo'])
    linhas = ["📋 Repertório atual:"]
    for m in repertorio:
        linha = f"{m['titulo']} - {m['autor']} ({round(m['tempo_min'], 2)} min) | Score: {m['score']}"
        linhas.append(linha)
    return "\n".join(linhas)

# Inicializar CSV se não existir
inicializar_csv()

# --- Interface Gradio ---
with gr.Blocks() as demo:
    gr.Markdown("# 🎸 Setlist Generator da Banda")

    with gr.Tab("➕ Adicionar Música"):
        titulo = gr.Textbox(label="Título da música")
        autor = gr.Textbox(label="Autor/banda")
        tempo = gr.Textbox(label="Tempo (ex: 4.5 ou 3:30)")
        botao_add = gr.Button("Adicionar ao repertório")
        resultado_add = gr.Textbox(label="Resultado")
        botao_add.click(fn=adicionar_musica, inputs=[titulo, autor, tempo], outputs=resultado_add)

    with gr.Tab("🎶 Gerar Setlist"):
        modo = gr.Radio(["Por tempo (min)", "20 músicas aleatórias"], label="Modo de geração")
        tempo_ensaio = gr.Number(label="Tempo total do ensaio (em minutos)", value=60)
        botao_gerar = gr.Button("Gerar Setlist")
        saida_setlist = gr.Textbox(label="Setlist Gerada", lines=20)
        def gerar_setlist(modo, tempo_ensaio):
            if modo == "20 músicas aleatórias":
                return gerar_20_musicas()
            return gerar_por_tempo(tempo_ensaio)
        botao_gerar.click(fn=gerar_setlist, inputs=[modo, tempo_ensaio], outputs=saida_setlist)

    with gr.Tab("📚 Ver Repertório"):
        botao_rep = gr.Button("Mostrar repertório completo")
        saida_rep = gr.Textbox(label="Repertório", lines=20)
        botao_rep.click(fn=mostrar_repertorio, inputs=[], outputs=saida_rep)

demo.launch()
