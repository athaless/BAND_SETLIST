import pandas as pd
import random
import os

ARQUIVO = "repertorio.csv"

# -------------------------------
# Funções de manipulação de dados
# -------------------------------

def carregar_repertorio():
    if os.path.exists(ARQUIVO):
        return pd.read_csv(ARQUIVO)
    else:
        df = pd.DataFrame(columns=["titulo", "autor", "tempo_min", "score"])
        df.to_csv(ARQUIVO, index=False)
        return df

def salvar_repertorio(df):
    df.to_csv(ARQUIVO, index=False)

def adicionar_musica(df, titulo, autor, tempo_min):
    nova_musica = pd.DataFrame([{
        "titulo": titulo,
        "autor": autor,
        "tempo_min": float(tempo_min),
        "score": 0
    }])
    df = pd.concat([df, nova_musica], ignore_index=True)
    salvar_repertorio(df)
    return df

def editar_musica(df, titulo_original, novo_titulo=None, novo_autor=None, novo_tempo_min=None):
    idx = df[df['titulo'].str.lower() == titulo_original.lower()].index
    if len(idx) == 0:
        print("🎵 Música não encontrada.")
        return df
    if novo_titulo:
        df.at[idx[0], 'titulo'] = novo_titulo
    if novo_autor:
        df.at[idx[0], 'autor'] = novo_autor
    if novo_tempo_min:
        df.at[idx[0], 'tempo_min'] = float(novo_tempo_min)
    salvar_repertorio(df)
    return df

# --------------------------------
# Funções de geração de setlist
# --------------------------------

def gerar_setlist_aleatoria(df, tamanho=20):
    if len(df) == 0:
        print("⚠️ Repertório vazio.")
        return []

    df_ordenado = df.sort_values(by='score', ascending=True).reset_index(drop=True)
    selecionadas = []

    while len(selecionadas) < tamanho and len(df_ordenado) > 0:
        grupo = df_ordenado.head(10)
        escolha = grupo.sample(1).iloc[0]
        selecionadas.append(escolha)
        df_ordenado = df_ordenado[df_ordenado['titulo'] != escolha['titulo']]

    for musica in selecionadas:
        idx = df[df['titulo'] == musica['titulo']].index
        df.at[idx[0], 'score'] += 1

    salvar_repertorio(df)
    return selecionadas

def gerar_setlist_por_tempo(df, tempo_total_minutos):
    if len(df) == 0:
        print("⚠️ Repertório vazio.")
        return []

    df = df.copy()
    df['tempo_min'] = df['tempo_min'].astype(float)
    df_ordenado = df.sort_values(by='score', ascending=True).reset_index(drop=True)
    musicas_possiveis = df_ordenado.sample(frac=1).reset_index(drop=True)

    setlist = []
    tempo_total = 0

    for _, musica in musicas_possiveis.iterrows():
        tempo_musica = float(musica['tempo_min'])
        if tempo_total + tempo_musica <= tempo_total_minutos:
            setlist.append(musica)
            tempo_total += tempo_musica

    for musica in setlist:
        idx = df[df['titulo'] == musica['titulo']].index
        df.at[idx[0], 'score'] += 1

    salvar_repertorio(df)
    return setlist

# def exibir_setlist(setlist):
#     if not setlist:
#         print("⚠️ Nenhuma música selecionada.")
#         return
#     print("\n🎶 SETLIST DO DIA 🎶\n")
#     tempo_total = 0
#     for i, musica in enumerate(setlist, start=1):
#         print(f"{i}. {musica['titulo']} - {musica['autor']} ({musica['tempo_min']} min)")
#         tempo_total += float(musica['tempo_min'])
#     print(f"\n⏱️ Duração total: {tempo_total:.1f} minutos\n")

def exibir_setlist(setlist):
    if not setlist:
        print("⚠️ Nenhuma música selecionada.")
        return
    print("\n🎶 SETLIST DO DIA 🎶\n")
    tempo_total = 0
    for i, musica in enumerate(setlist, start=1):
        print(f"{i}. {musica['titulo']} - {musica['autor']} ({musica['tempo_min']} min)")
        # Convert 'tempo_min' to float if it's in 'minutes:seconds' format
        if isinstance(musica['tempo_min'], str) and ':' in musica['tempo_min']:
            minutes, seconds = map(int, musica['tempo_min'].split(':'))
            tempo_musica = minutes + seconds / 60
        else:
            tempo_musica = float(musica['tempo_min'])
        tempo_total += tempo_musica  # Add the converted time to the total
    print(f"\n⏱️ Duração total: {tempo_total:.1f} minutos\n")

# -----------------------
# Interface de Terminal
# -----------------------

def menu():
    df = carregar_repertorio()
    while True:
        print("\n🎸 MENU DA BANDA 🎸")
        print("1. Adicionar música")
        print("2. Editar música")
        print("3. Gerar setlist aleatória (20 músicas)")
        print("4. Gerar setlist por tempo de ensaio")
        print("5. Mostrar repertório completo")
        print("0. Sair")

        escolha = input("Escolha uma opção: ")
        if escolha == "1":
            titulo = input("Título: ")
            autor = input("Autor: ")
            tempo = input("Tempo (minutos, ex: 3.5): ").replace(",", ".")
            try:
                tempo = float(tempo)
                df = adicionar_musica(df, titulo, autor, tempo)
                print("✅ Música adicionada!")
            except:
                print("⚠️ Tempo inválido.")
        elif escolha == "2":
            titulo = input("Título da música a editar: ")
            novo_titulo = input("Novo título (ou Enter para manter): ")
            novo_autor = input("Novo autor (ou Enter para manter): ")
            novo_tempo = input("Novo tempo (ou Enter para manter): ").replace(",", ".")
            try:
                novo_tempo = float(novo_tempo) if novo_tempo else None
                df = editar_musica(df, titulo, novo_titulo or None, novo_autor or None, novo_tempo)
                print("✅ Música editada.")
            except:
                print("⚠️ Tempo inválido.")
        elif escolha == "3":
            setlist = gerar_setlist_aleatoria(df)
            exibir_setlist(setlist)
        elif escolha == "4":
            tempo_input = input("Quantos minutos terá o ensaio? (ex: 90 ou 105.5): ").strip().replace(',', '.')
            try:
                tempo = float(tempo_input)
                if tempo <= 0:
                    raise ValueError
                setlist = gerar_setlist_por_tempo(df, tempo_total_minutos=tempo)
                exibir_setlist(setlist)
            except Exception as e:
                print("⚠️ Tempo inválido. Digite um número válido (ex: 90 ou 120.5).")
                print(f"🛠️ Erro técnico: {e}")
        elif escolha == "5":
            if df.empty:
                print("📭 Repertório vazio.")
            else:
                print(df[['titulo', 'autor', 'tempo_min', 'score']])
        elif escolha == "0":
            print("👋 Saindo...")
            break
        else:
            print("⚠️ Opção inválida.")

# Rodar menu
menu()
