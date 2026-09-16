"""
Sistema de Escala Automática - Atirador de Ronda e Comandante da Guarda do Dia

Paradigma: 100% procedural (sem uso de `class`).
Interface gráfica: tkinter + tkinter.ttk (ttk.Style para estilo nativo).
"""

import tkinter as tk
from tkinter import ttk, messagebox

# ============================================================
# ESTRUTURAS DE DADOS GLOBAIS (vetores e ponteiros)
# ============================================================
TAMANHO_PELOTAO = 50        # Tamanho fixo do vetor de atiradores do pelotão
TAMANHO_COMANDANTES = 12    # Tamanho fixo do vetor de atiradores elegíveis a comandante

vetor_pelotao = []          # Vetor de 50 posições: atiradores em ordem de formatura
vetor_comandantes = []      # Vetor de 12 posições: atiradores elegíveis a comandante da guarda

ponteiro_ronda = 0          # Aponta a próxima posição a servir no vetor_pelotao
ponteiro_comandante = 0     # Aponta a próxima posição a servir no vetor_comandantes

dia_atual = 0                # Contador sequencial de dias de instrução já escalados
historico_escalas = []       # Lista de tuplas (dia, comandante_do_dia, atirador_ronda_do_dia)


# ============================================================
# FUNÇÕES DE GERAÇÃO DE DADOS PADRÃO
# ============================================================
def gerar_nomes_padrao_pelotao():
    # SEQUÊNCIA + REPETIÇÃO: monta o vetor de 50 atiradores em ordem de formatura
    nomes = []
    for i in range(TAMANHO_PELOTAO):  # REPETIÇÃO: percorre as 50 posições do vetor
        nomes.append(f"Atirador {i + 1:02d}")
    return nomes


def gerar_nomes_padrao_comandantes():
    # SEQUÊNCIA + REPETIÇÃO: monta o vetor de 12 atiradores elegíveis a comandante
    nomes = []
    for i in range(TAMANHO_COMANDANTES):  # REPETIÇÃO: percorre as 12 posições do vetor
        nomes.append(f"Cmt-Curso {i + 1:02d}")
    return nomes


# ============================================================
# FUNÇÕES DE REGRA DE NEGÓCIO (lógica pura, sem tkinter)
# ============================================================
def selecionar_comandante_do_dia():
    """
    DADO que é um novo dia de instrução
    QUANDO o sistema seleciona o comandante da guarda do dia
    ENTÃO o atirador na posição atual do ponteiro_comandante é definido como
    comandante da guarda do dia, e o ponteiro_comandante avança uma posição.
    """
    global ponteiro_comandante

    # SEQUÊNCIA: define o comandante do dia com base na posição atual do ponteiro
    comandante_do_dia = vetor_comandantes[ponteiro_comandante]

    # SELEÇÃO: avança o ponteiro_comandante, reiniciando o ciclo ao chegar ao final do vetor de 12
    if ponteiro_comandante == TAMANHO_COMANDANTES - 1:
        ponteiro_comandante = 0
    else:
        ponteiro_comandante += 1

    return comandante_do_dia


def selecionar_atirador_ronda(comandante_do_dia):
    """
    DADO que o comandante da guarda do dia já foi definido
    QUANDO o sistema seleciona o atirador de ronda do dia
    ENTÃO o atirador na posição atual do ponteiro_ronda é definido como atirador
    de ronda, salvo se ele for o próprio comandante do dia - nesse caso ele é
    pulado e a verificação se repete até achar um atirador diferente do comandante.
    """
    global ponteiro_ronda

    tentativas = 0  # Contador de segurança contra loop infinito em dados inconsistentes

    # REPETIÇÃO: pula atiradores que coincidem com o comandante do dia
    while vetor_pelotao[ponteiro_ronda] == comandante_do_dia:
        # SELEÇÃO: avança o ponteiro_ronda, reiniciando o ciclo ao chegar ao final do vetor de 50
        if ponteiro_ronda == TAMANHO_PELOTAO - 1:
            ponteiro_ronda = 0
        else:
            ponteiro_ronda += 1

        tentativas += 1
        # SELEÇÃO: protege contra vetor inconsistente (ex.: todos os nomes iguais ao comandante)
        if tentativas > TAMANHO_PELOTAO:
            return None

    # SEQUÊNCIA: define o atirador de ronda do dia com base na posição atual do ponteiro
    atirador_ronda_do_dia = vetor_pelotao[ponteiro_ronda]

    # SELEÇÃO: avança o ponteiro_ronda, reiniciando o ciclo ao chegar ao final do vetor de 50
    if ponteiro_ronda == TAMANHO_PELOTAO - 1:
        ponteiro_ronda = 0
    else:
        ponteiro_ronda += 1

    return atirador_ronda_do_dia


# ============================================================
# FUNÇÕES DE INTERFACE (dependem dos widgets criados em main())
# ============================================================
def restaurar_padrao():
    # SEQUÊNCIA: limpa e repreenche as caixas de texto com os nomes padrão gerados
    txt_pelotao.delete("1.0", tk.END)
    txt_pelotao.insert(tk.END, "\n".join(gerar_nomes_padrao_pelotao()))

    txt_comandantes.delete("1.0", tk.END)
    txt_comandantes.insert(tk.END, "\n".join(gerar_nomes_padrao_comandantes()))


def carregar_vetores():
    """
    DADO que o sistema é iniciado no primeiro dia de instrução
    QUANDO os vetores de atiradores e de comandantes elegíveis são carregados
    ENTÃO o ponteiro_ronda aponta para a posição 0 do vetor de 50 e o
    ponteiro_comandante aponta para a posição 0 do vetor de 12.
    """
    global vetor_pelotao, vetor_comandantes, ponteiro_ronda, ponteiro_comandante
    global dia_atual, historico_escalas

    texto_pelotao = txt_pelotao.get("1.0", tk.END).strip()
    texto_comandantes = txt_comandantes.get("1.0", tk.END).strip()

    # Usa split() e list comprehension com filtro `if` para remover linhas em branco,
    # substituindo um laço manual de leitura linha a linha com verificação de vazio.
    linhas_pelotao = [linha.strip() for linha in texto_pelotao.split("\n") if linha.strip() != ""]
    linhas_comandantes = [linha.strip() for linha in texto_comandantes.split("\n") if linha.strip() != ""]

    # SELEÇÃO: valida se a quantidade de nomes corresponde ao tamanho exigido de cada vetor
    if len(linhas_pelotao) != TAMANHO_PELOTAO:
        messagebox.showerror(
            "Erro de Validação",
            f"O vetor do pelotão precisa ter exatamente {TAMANHO_PELOTAO} atiradores "
            f"(foram informados {len(linhas_pelotao)})."
        )
        return

    if len(linhas_comandantes) != TAMANHO_COMANDANTES:
        messagebox.showerror(
            "Erro de Validação",
            f"O vetor de comandantes precisa ter exatamente {TAMANHO_COMANDANTES} atiradores "
            f"(foram informados {len(linhas_comandantes)})."
        )
        return

    vetor_pelotao = linhas_pelotao
    vetor_comandantes = linhas_comandantes

    # Reinicialização do primeiro dia de instrução: ponteiros voltam para a posição 0
    ponteiro_ronda = 0
    ponteiro_comandante = 0
    dia_atual = 0
    historico_escalas = []

    for linha in arvore_historico.get_children():  # REPETIÇÃO: limpa o histórico exibido na tela
        arvore_historico.delete(linha)

    btn_novo_dia.config(state=tk.NORMAL)
    atualizar_painel_estado()
    messagebox.showinfo("Sistema Iniciado", "Vetores carregados com sucesso. Ponteiros reiniciados na posição 0.")


def gerar_novo_dia():
    global dia_atual

    # SELEÇÃO: impede gerar escala sem os vetores carregados
    if not vetor_pelotao or not vetor_comandantes:
        messagebox.showwarning(
            "Vetores não carregados",
            "Carregue os vetores de atiradores e comandantes antes de gerar uma nova escala."
        )
        return

    dia_atual += 1  # SEQUÊNCIA: avança o contador de dias de instrução

    comandante_do_dia = selecionar_comandante_do_dia()
    atirador_ronda_do_dia = selecionar_atirador_ronda(comandante_do_dia)

    # SELEÇÃO: aborta o registro do dia se não foi possível definir um atirador de ronda válido
    if atirador_ronda_do_dia is None:
        dia_atual -= 1
        messagebox.showerror(
            "Erro de Escala",
            "Não foi possível encontrar um atirador de ronda válido para hoje. "
            "Verifique se o vetor do pelotão possui nomes distintos do comandante do dia."
        )
        return

    historico_escalas.append((dia_atual, comandante_do_dia, atirador_ronda_do_dia))
    arvore_historico.insert("", tk.END, values=(dia_atual, comandante_do_dia, atirador_ronda_do_dia))
    arvore_historico.yview_moveto(1.0)  # Rola a visualização até o registro mais recente

    atualizar_painel_estado()


def consultar_escala_do_dia():
    """
    DADO que o comandante da guarda e o atirador de ronda do dia já foram definidos
    QUANDO o usuário consulta a escala do dia
    ENTÃO o sistema exibe os dois nomes designados para aquele dia.
    """
    # SELEÇÃO: só é possível consultar se já existir ao menos um dia escalado
    if not historico_escalas:
        messagebox.showinfo("Escala do Dia", "Nenhuma escala foi gerada ainda. Clique em 'Gerar Novo Dia' primeiro.")
        return

    dia, comandante, ronda = historico_escalas[-1]  # Consulta o último dia registrado
    messagebox.showinfo(
        f"Escala do Dia {dia}",
        f"Comandante da Guarda do Dia: {comandante}\nAtirador de Ronda do Dia: {ronda}"
    )


def atualizar_painel_estado():
    # SEQUÊNCIA: atualiza em tempo real os rótulos com o estado atual do sistema
    lbl_dia_valor.config(text=str(dia_atual))

    if vetor_pelotao:
        lbl_ponteiro_ronda_valor.config(text=f"{ponteiro_ronda}  (próximo: {vetor_pelotao[ponteiro_ronda]})")
    else:
        lbl_ponteiro_ronda_valor.config(text="-")

    if vetor_comandantes:
        lbl_ponteiro_comandante_valor.config(text=f"{ponteiro_comandante}  (próximo: {vetor_comandantes[ponteiro_comandante]})")
    else:
        lbl_ponteiro_comandante_valor.config(text="-")

    # SELEÇÃO: exibe a escala do último dia gerado, se existir
    if historico_escalas:
        _, comandante, ronda = historico_escalas[-1]
        lbl_comandante_valor.config(text=comandante)
        lbl_ronda_valor.config(text=ronda)
    else:
        lbl_comandante_valor.config(text="-")
        lbl_ronda_valor.config(text="-")


# ============================================================
# MONTAGEM DA INTERFACE GRÁFICA
# ============================================================
def main():
    global txt_pelotao, txt_comandantes, arvore_historico, btn_novo_dia
    global lbl_dia_valor, lbl_ponteiro_ronda_valor, lbl_ponteiro_comandante_valor
    global lbl_comandante_valor, lbl_ronda_valor

    janela = tk.Tk()
    janela.title("Escala Automática - Ronda e Comandante da Guarda")
    janela.geometry("860x680")
    janela.minsize(760, 600)

    estilo = ttk.Style()
    estilo.theme_use("clam")  # Estilo nativo consistente entre plataformas

    # --------------------------------------------------------
    # Bloco 1: Carregamento dos vetores
    # --------------------------------------------------------
    frame_vetores = ttk.LabelFrame(janela, text="1. Vetores de Entrada (um nome por linha)")
    frame_vetores.pack(fill="x", padx=10, pady=8)

    frame_vetor_pelotao = ttk.Frame(frame_vetores)
    frame_vetor_pelotao.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
    ttk.Label(frame_vetor_pelotao, text=f"Vetor do Pelotão ({TAMANHO_PELOTAO} atiradores)").pack(anchor="w")
    txt_pelotao = tk.Text(frame_vetor_pelotao, width=32, height=10)
    txt_pelotao.pack(fill="both", expand=True)

    frame_vetor_comandantes = ttk.Frame(frame_vetores)
    frame_vetor_comandantes.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
    ttk.Label(frame_vetor_comandantes, text=f"Vetor de Comandantes Elegíveis ({TAMANHO_COMANDANTES} atiradores)").pack(anchor="w")
    txt_comandantes = tk.Text(frame_vetor_comandantes, width=32, height=10)
    txt_comandantes.pack(fill="both", expand=True)

    frame_vetores.columnconfigure(0, weight=1)
    frame_vetores.columnconfigure(1, weight=1)

    frame_botoes_vetores = ttk.Frame(frame_vetores)
    frame_botoes_vetores.grid(row=1, column=0, columnspan=2, pady=(0, 8))
    ttk.Button(frame_botoes_vetores, text="Restaurar Nomes Padrão", command=restaurar_padrao).pack(side="left", padx=4)
    ttk.Button(frame_botoes_vetores, text="Carregar Vetores / Iniciar Sistema", command=carregar_vetores).pack(side="left", padx=4)

    # --------------------------------------------------------
    # Bloco 2: Painel de estado atual (exibição em tempo real)
    # --------------------------------------------------------
    frame_estado = ttk.LabelFrame(janela, text="2. Estado Atual do Sistema")
    frame_estado.pack(fill="x", padx=10, pady=8)

    ttk.Label(frame_estado, text="Dia de instrução atual:").grid(row=0, column=0, sticky="w", padx=8, pady=4)
    lbl_dia_valor = ttk.Label(frame_estado, text="0", font=("Segoe UI", 10, "bold"))
    lbl_dia_valor.grid(row=0, column=1, sticky="w", padx=8, pady=4)

    ttk.Label(frame_estado, text="ponteiro_ronda:").grid(row=1, column=0, sticky="w", padx=8, pady=4)
    lbl_ponteiro_ronda_valor = ttk.Label(frame_estado, text="-")
    lbl_ponteiro_ronda_valor.grid(row=1, column=1, sticky="w", padx=8, pady=4)

    ttk.Label(frame_estado, text="ponteiro_comandante:").grid(row=2, column=0, sticky="w", padx=8, pady=4)
    lbl_ponteiro_comandante_valor = ttk.Label(frame_estado, text="-")
    lbl_ponteiro_comandante_valor.grid(row=2, column=1, sticky="w", padx=8, pady=4)

    ttk.Label(frame_estado, text="Comandante da Guarda do Dia:").grid(row=0, column=2, sticky="w", padx=8, pady=4)
    lbl_comandante_valor = ttk.Label(frame_estado, text="-", font=("Segoe UI", 10, "bold"))
    lbl_comandante_valor.grid(row=0, column=3, sticky="w", padx=8, pady=4)

    ttk.Label(frame_estado, text="Atirador de Ronda do Dia:").grid(row=1, column=2, sticky="w", padx=8, pady=4)
    lbl_ronda_valor = ttk.Label(frame_estado, text="-", font=("Segoe UI", 10, "bold"))
    lbl_ronda_valor.grid(row=1, column=3, sticky="w", padx=8, pady=4)

    # --------------------------------------------------------
    # Bloco 3: Ações do dia
    # --------------------------------------------------------
    frame_acoes = ttk.Frame(janela)
    frame_acoes.pack(fill="x", padx=10, pady=4)

    btn_novo_dia = ttk.Button(frame_acoes, text="Gerar Novo Dia", command=gerar_novo_dia, state=tk.DISABLED)
    btn_novo_dia.pack(side="left", padx=4)

    ttk.Button(frame_acoes, text="Consultar Escala do Dia", command=consultar_escala_do_dia).pack(side="left", padx=4)

    # --------------------------------------------------------
    # Bloco 4: Histórico de escalas (Treeview)
    # --------------------------------------------------------
    frame_historico = ttk.LabelFrame(janela, text="3. Histórico de Escalas")
    frame_historico.pack(fill="both", expand=True, padx=10, pady=8)

    colunas = ("dia", "comandante", "ronda")
    arvore_historico = ttk.Treeview(frame_historico, columns=colunas, show="headings", height=10)
    arvore_historico.heading("dia", text="Dia")
    arvore_historico.heading("comandante", text="Comandante da Guarda")
    arvore_historico.heading("ronda", text="Atirador de Ronda")
    arvore_historico.column("dia", width=60, anchor="center")
    arvore_historico.column("comandante", width=200, anchor="center")
    arvore_historico.column("ronda", width=200, anchor="center")

    barra_rolagem = ttk.Scrollbar(frame_historico, orient="vertical", command=arvore_historico.yview)
    arvore_historico.configure(yscrollcommand=barra_rolagem.set)

    arvore_historico.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
    barra_rolagem.pack(side="right", fill="y", pady=8)

    # Preenche os campos de texto com os nomes padrão já na abertura do sistema
    restaurar_padrao()

    janela.mainloop()


if __name__ == "__main__":
    main()
