import os
# Instalar o Gradio usando os.system
os.system("pip install gradio")

import csv
import random
import shutil
import datetime
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

def zerar_scores():
    repertorio = carregar_repertorio()
    for musica in repertorio:
        musica["score"] = 0
    salvar_repertorio(repertorio)
    return "✅ Scores zerados com sucesso!"
        
def restaurar_repertorio():
    try:
        # Obter data e hora atuais
        agora = datetime.datetime.now()
        nome_backup = agora.strftime("repertorio_%d_%m_%Y_%H_%M_%S.csv")

        # Renomear o arquivo atual
        os.rename("repertorio.csv", nome_backup)

        # Copiar o backup
        shutil.copyfile("repertorio_backup.csv", "repertorio.csv")
        
        return f"✅ Repertório restaurado com sucesso! Backup salvo como {nome_backup}"
    except Exception as e:
        return f"❌ Erro ao restaurar o repertório: {e}"

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

def gerar_setlist(modo, tempo_ensaio, quantidade_musicas=20):  # Adicionando parâmetro
    if modo == "Por tempo (min)":
        return gerar_por_tempo(tempo_ensaio)
    elif modo == "Quantidade de músicas":  # Nova condição
        repertorio = carregar_repertorio()
        repertorio.sort(key=lambda x: (x['score'], random.random()))
        setlist = repertorio[:quantidade_musicas]  # Usando a quantidade
        for musica in setlist:
            musica["score"] += 1
        salvar_repertorio(repertorio)
        return formatar_setlist(setlist)
    else:
        return gerar_20_musicas()  # Mantendo a opção de 20 músicas como padrão

def formatar_setlist(setlist):
    linhas = []
    for i, m in enumerate(setlist):
        linha = f"{i+1}. {m['titulo']} - {m['autor']} ({round(m['tempo_min'], 2)} min)"
        linhas.append(linha)
    return "\n".join(linhas)


def editar_musica(index, novo_titulo, novo_autor, novo_tempo):
    try:
        index = int(index) - 1  # Adjust index to match list
        repertorio = carregar_repertorio()
        
        if 0 <= index < len(repertorio):
            repertorio[index]["titulo"] = novo_titulo
            repertorio[index]["autor"] = novo_autor
            repertorio[index]["tempo_min"] = converter_tempo(novo_tempo)
            salvar_repertorio(repertorio)
            return "✅ Música editada com sucesso!"
        else:
            return "❌ Índice de música inválido."
    except Exception as e:
        return f"❌ Erro: {e}"

def mostrar_repertorio():
    repertorio = carregar_repertorio()
    repertorio.sort(key=lambda x: x['titulo'])
    linhas = ["📋 Repertório atual:"]
    for i, m in enumerate(repertorio):
        linha = f"{i+1}. {m['titulo']} - {m['autor']} ({round(m['tempo_min'], 2)} min) | Score: {m['score']}"
        linhas.append(linha)  

    total_musicas = len(repertorio)
    linhas.append(f"\nTotal de músicas: {total_musicas}")
    return "\n".join(linhas)

def deletar_musica(nome_musica):
    repertorio = carregar_repertorio()
    musicas_encontradas = [musica for musica in repertorio if musica['titulo'] == nome_musica]
    
    if musicas_encontradas:
        for musica in musicas_encontradas:
            repertorio.remove(musica)
        salvar_repertorio(repertorio)
        return f"✅ Música(s) '{nome_musica}' deletada(s) com sucesso!"
    else:
        return f"❌ Música '{nome_musica}' não encontrada no repertório."

# Inicializar CSV se não existir
inicializar_csv()

# --- Interface Gradio ---
with gr.Blocks() as demo:
    gr.Markdown("# 🎸 OUTLIERS Setlist Generator Tabajara")

    with gr.Tab("➕"):
        titulo = gr.Textbox(label="Título")
        autor = gr.Textbox(label="Autor/banda")
        tempo = gr.Textbox(label="Tempo (ex: 4.5 ou 3:30)")
        botao_add = gr.Button("Adicionar ao repertório")
        resultado_add = gr.Textbox(label="Resultado")
        botao_add.click(fn=adicionar_musica, inputs=[titulo, autor, tempo], outputs=resultado_add)

    with gr.Tab("➖"):
        nome_musica_deletar = gr.Textbox(label="Nome da música a ser deletada")  # Mudança aqui
        botao_deletar = gr.Button("Deletar Música")
        resultado_deletar = gr.Textbox(label="Resultado")
        botao_deletar.click(fn=deletar_musica, inputs=[nome_musica_deletar], outputs=[resultado_deletar])  # Mudança aqui

    with gr.Tab("🎶 Setlist"):
        modo = gr.Radio(["Por tempo (min)", "Quantidade de músicas"], label="Modo de geração") # Mudando opções do Radio
        tempo_ensaio = gr.Number(label="Tempo total do ensaio (em minutos)", value=60)
        quantidade_musicas = gr.Number(label="Quantidade de músicas", value=20)  # Novo componente
        botao_gerar = gr.Button("Gerar Setlist")
        saida_setlist = gr.Textbox(label="Setlist Gerada", lines=20)

        botao_gerar.click(fn=gerar_setlist, inputs=[modo, tempo_ensaio, quantidade_musicas], outputs=saida_setlist) # Adicionando input        

    with gr.Tab("📚 Repertório"):
        botao_rep = gr.Button("Mostrar repertório completo")
        saida_rep = gr.Textbox(label="Repertório", lines=20)
        botao_rep.click(fn=mostrar_repertorio, inputs=[], outputs=saida_rep)

    with gr.Tab("🔄 Zerar Scores"):  # Nova aba para zerar scores
        botao_zerar_scores = gr.Button("Zerar Scores")
        resultado_zerar_scores = gr.Textbox(label="Resultado")
        botao_zerar_scores.click(fn=zerar_scores, inputs=[], outputs=[resultado_zerar_scores])

    with gr.Tab("📜 Reset"):
        botao_restaurar = gr.Button("Restaurar Repertório")
        resultado_restaurar = gr.Textbox(label="Resultado")
        botao_restaurar.click(fn=restaurar_repertorio, inputs=[], outputs=[resultado_restaurar])

demo.launch(share=True)

