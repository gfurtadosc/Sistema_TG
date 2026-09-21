"""
Sistema de Escala Automática - Atirador de Ronda e Comandante da Guarda do Dia

Paradigma: 100% procedural (sem uso de `class`).
Interface gráfica: tkinter + tkinter.ttk (ttk.Style para estilo nativo).
"""

import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ============================================================
# ESTRUTURAS DE DADOS GLOBAIS (vetores e ponteiros)
# ============================================================
# O efetivo real do pelotão é de 50 atiradores. Os 12 comandantes elegíveis
# são um subconjunto desses 50 (não pessoas à parte), por isso o vetor do
# pelotão guarda apenas os 38 atiradores sem elegibilidade a comando:
# TAMANHO_PELOTAO + TAMANHO_COMANDANTES = 50 (efetivo total).
TAMANHO_PELOTAO = 38         # Tamanho fixo do vetor de atiradores sem elegibilidade a comando
TAMANHO_COMANDANTES = 12     # Tamanho fixo do vetor de atiradores elegíveis a comandante

vetor_pelotao = []          # Vetor de atiradores (sem elegibilidade a comando) em ordem de formatura
vetor_comandantes = []      # Vetor de atiradores elegíveis a comandante da guarda

ponteiro_ronda = 0          # Aponta a próxima posição a servir no vetor_pelotao
ponteiro_comandante = 0     # Aponta a próxima posição a servir no vetor_comandantes

dia_atual = 0                # Contador sequencial de dias de instrução já escalados
dia_aberto = False           # Indica se o dia atual já foi gerado mas ainda não foi fechado
historico_escalas = []       # Lista de dicionários com os dados completos de cada dia já escalado


# ============================================================
# PALETA E ESTILO VISUAL (identidade militar: verde-oliva + dourado)
# ============================================================
COR_FUNDO = "#10160D"          # Fundo principal da janela (quase preto esverdeado)
COR_PAINEL = "#1B2515"         # Fundo dos "cards"/painéis
COR_PAINEL_CLARO = "#26331C"   # Fundo de campos de entrada (Text)
COR_BORDA = "#3C4A2A"          # Bordas discretas
COR_OLIVA = "#4B5320"          # Verde-oliva (cor tradicional do Exército)
COR_OLIVA_CLARO = "#5E6B2C"    # Verde-oliva em estado "hover"
COR_DOURADO = "#C9A24B"        # Dourado (destaque, cor de insígnias militares)
COR_DOURADO_CLARO = "#DFBE72"  # Dourado em estado "hover"
COR_TEXTO = "#EDEAE0"          # Texto principal sobre fundo escuro
COR_TEXTO_SEC = "#9FAE8C"      # Texto secundário/rótulos
COR_TEXTO_ESCURO = "#14190D"   # Texto escuro sobre fundo dourado

COR_STATUS_OK_BG = "#1E2E17"       # Fundo de linha/dia fechado sem faltas
COR_STATUS_FALTA_BG = "#332018"    # Fundo de linha/dia fechado com falta registrada
COR_STATUS_FALTA_TXT = "#E1A98F"   # Texto de destaque sobre fundo de falta

FONTE_FAMILIA = "Segoe UI"
FONTE_BASE = (FONTE_FAMILIA, 10)
FONTE_BASE_NEGRITO = (FONTE_FAMILIA, 10, "bold")
FONTE_TITULO = (FONTE_FAMILIA, 19, "bold")
FONTE_TITULO_JANELA = (FONTE_FAMILIA, 14, "bold")
FONTE_SUBTITULO = (FONTE_FAMILIA, 9)
FONTE_SECAO = (FONTE_FAMILIA, 10, "bold")
FONTE_STAT_ROTULO = (FONTE_FAMILIA, 8, "bold")
FONTE_STAT_VALOR = (FONTE_FAMILIA, 17, "bold")


def configurar_estilo(estilo):
    # SEQUÊNCIA: define o tema base e sobrescreve suas cores com a paleta militar
    estilo.theme_use("clam")

    estilo.configure("TFrame", background=COR_FUNDO)
    estilo.configure("TLabel", background=COR_FUNDO, foreground=COR_TEXTO, font=FONTE_BASE)

    # "Cards" (LabelFrame) com borda dourada fina, simulando painéis táticos
    estilo.configure(
        "Card.TLabelframe",
        background=COR_PAINEL,
        bordercolor=COR_DOURADO,
        borderwidth=1,
        relief="solid",
    )
    estilo.configure(
        "Card.TLabelframe.Label",
        background=COR_PAINEL,
        foreground=COR_DOURADO,
        font=FONTE_SECAO,
    )

    # Botão primário: ação principal do fluxo, em destaque dourado
    estilo.configure(
        "Primary.TButton",
        background=COR_DOURADO,
        foreground=COR_TEXTO_ESCURO,
        font=FONTE_BASE_NEGRITO,
        padding=(16, 9),
        borderwidth=0,
        relief="flat",
    )
    estilo.map(
        "Primary.TButton",
        background=[("active", COR_DOURADO_CLARO), ("disabled", COR_BORDA)],
        foreground=[("disabled", COR_TEXTO_SEC)],
    )

    # Botão secundário: ação de apoio, em verde-oliva
    estilo.configure(
        "Secondary.TButton",
        background=COR_OLIVA,
        foreground=COR_TEXTO,
        font=FONTE_BASE_NEGRITO,
        padding=(16, 9),
        borderwidth=0,
        relief="flat",
    )
    estilo.map("Secondary.TButton", background=[("active", COR_OLIVA_CLARO)])

    # Treeview (histórico) em tema escuro com cabeçalho em destaque
    estilo.configure(
        "Treeview",
        background=COR_PAINEL,
        fieldbackground=COR_PAINEL,
        foreground=COR_TEXTO,
        rowheight=30,
        font=FONTE_BASE,
        borderwidth=0,
    )
    estilo.configure(
        "Treeview.Heading",
        background=COR_OLIVA,
        foreground=COR_TEXTO,
        font=FONTE_BASE_NEGRITO,
        relief="flat",
    )
    estilo.map(
        "Treeview",
        background=[("selected", COR_DOURADO)],
        foreground=[("selected", COR_TEXTO_ESCURO)],
    )

    # Barra de rolagem discreta, alinhada à paleta
    estilo.configure(
        "Vertical.TScrollbar",
        background=COR_OLIVA,
        troughcolor=COR_FUNDO,
        bordercolor=COR_FUNDO,
        arrowcolor=COR_TEXTO,
        relief="flat",
    )


def criar_stat_card(pai, rotulo_texto, destaque=True):
    # Monta um "card" de estatística (rótulo pequeno + valor em destaque)
    card = tk.Frame(pai, bg=COR_PAINEL, highlightthickness=1, highlightbackground=COR_BORDA)
    tk.Label(card, text=rotulo_texto, bg=COR_PAINEL, fg=COR_TEXTO_SEC, font=FONTE_STAT_ROTULO).pack(
        anchor="w", padx=14, pady=(12, 0)
    )
    fonte_valor = FONTE_STAT_VALOR if destaque else FONTE_BASE_NEGRITO
    cor_valor = COR_DOURADO if destaque else COR_TEXTO
    valor = tk.Label(card, text="-", bg=COR_PAINEL, fg=cor_valor, font=fonte_valor)
    valor.pack(anchor="w", padx=14, pady=(0, 12))
    return card, valor


# ============================================================
# FUNÇÕES DE GERAÇÃO DE DADOS PADRÃO
# ============================================================
NOMES_PROPRIOS = [
    "João", "Pedro", "Lucas", "Gabriel", "Matheus", "Rafael", "Bruno", "Carlos",
    "Daniel", "Eduardo", "Felipe", "Gustavo", "Henrique", "Igor", "Kaique",
    "Leonardo", "Marcos", "Nicolas", "Otávio", "Paulo", "Rodrigo", "Samuel",
    "Thiago", "Vinícius", "Wesley", "André", "Breno", "Caio", "Diego", "Fábio",
]  # Banco de nomes próprios para sorteio

SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves",
    "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho",
    "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa", "Rocha",
    "Dias", "Monteiro", "Cardoso", "Reis", "Araújo", "Castro", "Andrade",
    "Nascimento", "Moreira",
]  # Banco de sobrenomes para sorteio


def gerar_pessoas_aleatorias(quantidade, nomes_ja_usados):
    """
    DADO um banco de nomes próprios e sobrenomes
    QUANDO o sistema precisa sortear um vetor de nomes completos
    ENTÃO retorna `quantidade` nomes distintos entre si e distintos de
    `nomes_ja_usados`, simulando o efetivo real de atiradores do pelotão.
    """
    nomes_sorteados = []

    # REPETIÇÃO: continua sorteando até atingir a quantidade solicitada
    while len(nomes_sorteados) < quantidade:
        # Usa random.choice() para sortear um nome próprio e um sobrenome do banco,
        # substituindo um cálculo manual de índice aleatório com random.random()
        primeiro_nome = random.choice(NOMES_PROPRIOS)
        sobrenome = random.choice(SOBRENOMES)
        nome_completo = f"{primeiro_nome} {sobrenome}"

        # SELEÇÃO: só aceita o nome sorteado se ele ainda não foi usado em nenhum
        # dos dois vetores. Usa o operador `in` para checar pertencimento na lista,
        # substituindo um loop manual de comparação nome a nome.
        if nome_completo not in nomes_ja_usados and nome_completo not in nomes_sorteados:
            nomes_sorteados.append(nome_completo)

    return nomes_sorteados


def gerar_nomes_padrao_pelotao():
    # SEQUÊNCIA: sorteia os atiradores sem elegibilidade a comando
    return gerar_pessoas_aleatorias(TAMANHO_PELOTAO, [])


def gerar_nomes_padrao_comandantes(nomes_pelotao):
    # SEQUÊNCIA: sorteia os atiradores elegíveis a comando, excluindo quem já
    # foi sorteado para o vetor do pelotão (mesmo efetivo, vetores disjuntos)
    return gerar_pessoas_aleatorias(TAMANHO_COMANDANTES, nomes_pelotao)


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
# FUNÇÕES DE TAREFAS DO DIA (sorteio)
# ============================================================
TAREFAS_DISPONIVEIS = [
    "Ronda perimetral às 06h00",
    "Ronda perimetral às 12h00",
    "Ronda perimetral às 18h00",
    "Inspeção de armamento antes da instrução",
    "Conferência do material de intendência",
    "Fiscalização da entrada e saída de instruendos",
    "Hasteamento da Bandeira Nacional",
    "Arriamento da Bandeira Nacional",
    "Supervisão da ordem unida no pátio",
    "Verificação dos extintores de incêndio",
    "Inspeção de higiene do alojamento",
    "Apoio à instrução de tiro no estande",
    "Controle de acesso à sala de aula",
    "Vistoria do material de primeiros socorros",
    "Organização da fila do rancho",
    "Checagem do quadro de avisos",
]  # Banco de tarefas típicas de um dia de Tiro de Guerra

QTD_TAREFAS_POR_DIA = 3


def sortear_tarefas_do_dia():
    # Usa random.sample() para sortear tarefas sem repetição dentro do mesmo dia,
    # substituindo um loop manual de sorteio com verificação de duplicidade
    return random.sample(TAREFAS_DISPONIVEIS, QTD_TAREFAS_POR_DIA)


# ============================================================
# FUNÇÕES DE INTERFACE (dependem dos widgets criados em main())
# ============================================================
def restaurar_padrao():
    # SEQUÊNCIA: sorteia o pelotão primeiro, depois os comandantes (excluindo
    # quem já foi sorteado para o pelotão, já que é o mesmo efetivo de 50)
    nomes_pelotao = gerar_nomes_padrao_pelotao()
    nomes_comandantes = gerar_nomes_padrao_comandantes(nomes_pelotao)

    # SEQUÊNCIA: limpa e repreenche as caixas de texto com os nomes sorteados
    txt_pelotao.delete("1.0", tk.END)
    txt_pelotao.insert(tk.END, "\n".join(nomes_pelotao))

    txt_comandantes.delete("1.0", tk.END)
    txt_comandantes.insert(tk.END, "\n".join(nomes_comandantes))


def carregar_vetores():
    """
    DADO que o sistema é iniciado no primeiro dia de instrução
    QUANDO os vetores de atiradores e de comandantes elegíveis são carregados
    ENTÃO o ponteiro_ronda aponta para a posição 0 do vetor de 50 e o
    ponteiro_comandante aponta para a posição 0 do vetor de 12.
    """
    global vetor_pelotao, vetor_comandantes, ponteiro_ronda, ponteiro_comandante
    global dia_atual, dia_aberto, historico_escalas

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
    dia_aberto = False
    historico_escalas = []

    for linha in arvore_historico.get_children():  # REPETIÇÃO: limpa o histórico exibido na tela
        arvore_historico.delete(linha)

    btn_novo_dia.config(state=tk.NORMAL)
    btn_fechar_dia.config(state=tk.DISABLED)
    atualizar_painel_estado()
    messagebox.showinfo("Sistema Iniciado", "Vetores carregados com sucesso. Ponteiros reiniciados na posição 0.")


def gerar_novo_dia():
    global dia_atual, dia_aberto

    # SELEÇÃO: impede gerar escala sem os vetores carregados
    if not vetor_pelotao or not vetor_comandantes:
        messagebox.showwarning(
            "Vetores não carregados",
            "Carregue os vetores de atiradores e comandantes antes de gerar uma nova escala."
        )
        return

    # SELEÇÃO: impede iniciar um novo dia enquanto o dia atual ainda está em aberto
    if dia_aberto:
        messagebox.showwarning(
            "Dia em aberto",
            "Feche o dia atual (botão 'Fechar o Dia') antes de gerar um novo dia."
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

    tarefas_do_dia = sortear_tarefas_do_dia()

    item_id = arvore_historico.insert(
        "", tk.END,
        values=(dia_atual, comandante_do_dia, atirador_ronda_do_dia, "Em aberto"),
        tags=("status_aberto",),
    )
    arvore_historico.yview_moveto(1.0)  # Rola a visualização até o registro mais recente

    # Cada dia vira um dicionário com todos os dados relevantes (mais legível
    # que uma tupla posicional, já que agora há vários campos por dia)
    historico_escalas.append({
        "dia": dia_atual,
        "comandante": comandante_do_dia,
        "ronda": atirador_ronda_do_dia,
        "tarefas": tarefas_do_dia,
        "fechado": False,
        "faltantes": [],
        "observacao": "",
        "item_id": item_id,
    })

    dia_aberto = True
    btn_novo_dia.config(state=tk.DISABLED)
    btn_fechar_dia.config(state=tk.NORMAL)

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

    registro = historico_escalas[-1]  # Consulta o último dia registrado
    messagebox.showinfo(
        f"Escala do Dia {registro['dia']}",
        f"Comandante da Guarda do Dia: {registro['comandante']}\n"
        f"Atirador de Ronda do Dia: {registro['ronda']}"
    )


def abrir_janela_tarefas():
    # SELEÇÃO: só é possível consultar tarefas se já existir ao menos um dia gerado
    if not historico_escalas:
        messagebox.showinfo(
            "Tarefas do Dia", "Nenhum dia foi gerado ainda. Clique em 'Gerar Novo Dia' primeiro."
        )
        return

    registro = historico_escalas[-1]

    janela_tarefas = tk.Toplevel()
    janela_tarefas.title(f"Tarefas do Dia {registro['dia']}")
    janela_tarefas.configure(bg=COR_FUNDO)
    janela_tarefas.geometry("480x420")
    janela_tarefas.minsize(420, 360)

    tk.Label(
        janela_tarefas, text=f"TAREFAS DO DIA {registro['dia']}",
        bg=COR_FUNDO, fg=COR_DOURADO, font=FONTE_TITULO_JANELA,
    ).pack(pady=(18, 4))
    tk.Label(
        janela_tarefas,
        text=f"Comandante da Guarda: {registro['comandante']}\nAtirador de Ronda: {registro['ronda']}",
        bg=COR_FUNDO, fg=COR_TEXTO, font=FONTE_BASE, justify="left",
    ).pack(pady=(0, 14))

    frame_lista = tk.Frame(janela_tarefas, bg=COR_PAINEL, highlightthickness=1, highlightbackground=COR_BORDA)
    frame_lista.pack(fill="both", expand=True, padx=18, pady=(0, 18))

    for tarefa in registro["tarefas"]:  # REPETIÇÃO: lista cada tarefa sorteada para o dia
        tk.Label(
            frame_lista, text=f"☐  {tarefa}",
            bg=COR_PAINEL, fg=COR_TEXTO, font=FONTE_BASE, anchor="w", justify="left",
        ).pack(fill="x", padx=14, pady=6)


def concluir_fechamento_dia():
    global dia_aberto

    historico_escalas[-1]["fechado"] = True
    dia_aberto = False
    btn_novo_dia.config(state=tk.NORMAL)
    btn_fechar_dia.config(state=tk.DISABLED)
    atualizar_painel_estado()


def abrir_janela_registro_falta(registro):
    janela_falta = tk.Toplevel()
    janela_falta.title(f"Registrar Falta — Dia {registro['dia']}")
    janela_falta.configure(bg=COR_FUNDO)
    janela_falta.geometry("460x420")
    janela_falta.minsize(420, 400)
    janela_falta.grab_set()  # Trava a interação com a janela principal até este registro ser concluído

    tk.Label(
        janela_falta, text=f"REGISTRO DE FALTA — DIA {registro['dia']}",
        bg=COR_FUNDO, fg=COR_DOURADO, font=FONTE_TITULO_JANELA,
    ).pack(pady=(18, 10))

    tk.Label(
        janela_falta, text="Quem faltou hoje?",
        bg=COR_FUNDO, fg=COR_TEXTO_SEC, font=FONTE_STAT_ROTULO,
    ).pack(anchor="w", padx=20)

    var_faltou_comandante = tk.BooleanVar(value=False)
    var_faltou_ronda = tk.BooleanVar(value=False)

    tk.Checkbutton(
        janela_falta, text=f"Comandante da Guarda ({registro['comandante']})",
        variable=var_faltou_comandante, bg=COR_FUNDO, fg=COR_TEXTO,
        selectcolor=COR_PAINEL_CLARO, activebackground=COR_FUNDO, activeforeground=COR_TEXTO,
        font=FONTE_BASE,
    ).pack(anchor="w", padx=28, pady=(6, 2))

    tk.Checkbutton(
        janela_falta, text=f"Atirador de Ronda ({registro['ronda']})",
        variable=var_faltou_ronda, bg=COR_FUNDO, fg=COR_TEXTO,
        selectcolor=COR_PAINEL_CLARO, activebackground=COR_FUNDO, activeforeground=COR_TEXTO,
        font=FONTE_BASE,
    ).pack(anchor="w", padx=28, pady=(2, 14))

    tk.Label(
        janela_falta, text="O que pode ser feito / o que foi feito a respeito da falta?",
        bg=COR_FUNDO, fg=COR_TEXTO_SEC, font=FONTE_STAT_ROTULO,
    ).pack(anchor="w", padx=20)

    txt_observacao = tk.Text(
        janela_falta, height=6,
        bg=COR_PAINEL_CLARO, fg=COR_TEXTO, insertbackground=COR_TEXTO,
        relief="flat", highlightthickness=1, highlightbackground=COR_BORDA,
        highlightcolor=COR_DOURADO, font=FONTE_BASE, padx=8, pady=8,
    )
    txt_observacao.pack(fill="both", expand=True, padx=20, pady=(6, 14))

    def confirmar_falta():
        faltantes = []  # SEQUÊNCIA: monta a lista de quem faltou com base nos checkboxes marcados
        if var_faltou_comandante.get():
            faltantes.append(f"Comandante ({registro['comandante']})")
        if var_faltou_ronda.get():
            faltantes.append(f"Ronda ({registro['ronda']})")

        # SELEÇÃO: exige ao menos uma falta marcada, já que o usuário indicou que algo deu errado
        if not faltantes:
            messagebox.showwarning(
                "Nenhuma falta marcada",
                "Marque ao menos um atirador que faltou, ou feche a janela e responda 'Sim' no fechamento do dia."
            )
            return

        registro["faltantes"] = faltantes
        registro["observacao"] = txt_observacao.get("1.0", tk.END).strip()

        status_texto = "Fechado — Falta: " + ", ".join(faltantes)
        arvore_historico.item(
            registro["item_id"],
            values=(registro["dia"], registro["comandante"], registro["ronda"], status_texto),
            tags=("status_falta",),
        )

        janela_falta.destroy()
        concluir_fechamento_dia()

    frame_botoes_falta = tk.Frame(janela_falta, bg=COR_FUNDO)
    frame_botoes_falta.pack(pady=(0, 16))
    ttk.Button(frame_botoes_falta, text="Confirmar", style="Primary.TButton", command=confirmar_falta).pack()


def fechar_dia():
    # SELEÇÃO: só é possível fechar se houver um dia realmente em aberto
    if not historico_escalas or not dia_aberto:
        messagebox.showinfo("Fechar o Dia", "Não há nenhum dia em aberto para fechar.")
        return

    registro = historico_escalas[-1]

    ocorreu_bem = messagebox.askyesno(
        f"Fechamento do Dia {registro['dia']}",
        "Tudo ocorreu bem hoje? O comandante da guarda e o atirador de ronda escalados compareceram normalmente?"
    )

    # SELEÇÃO: se tudo ocorreu bem, fecha o dia direto; senão, abre a janela de registro de falta
    if ocorreu_bem:
        arvore_historico.item(
            registro["item_id"],
            values=(registro["dia"], registro["comandante"], registro["ronda"], "Fechado — OK"),
            tags=("status_ok",),
        )
        concluir_fechamento_dia()
    else:
        abrir_janela_registro_falta(registro)


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
        registro = historico_escalas[-1]
        lbl_comandante_valor.config(text=registro["comandante"])
        lbl_ronda_valor.config(text=registro["ronda"])
    else:
        lbl_comandante_valor.config(text="-")
        lbl_ronda_valor.config(text="-")


def abrir_janela_relatorio():
    # SELEÇÃO: só é possível gerar relatório se houver ao menos um dia registrado
    if not historico_escalas:
        messagebox.showinfo(
            "Relatório do Rodízio",
            "Nenhum dia foi gerado ainda. Gere ao menos um dia antes de consultar o relatório."
        )
        return

    janela_relatorio = tk.Toplevel()
    janela_relatorio.title("Relatório do Rodízio")
    janela_relatorio.configure(bg=COR_FUNDO)
    janela_relatorio.geometry("860x620")
    janela_relatorio.minsize(760, 540)

    tk.Label(
        janela_relatorio, text="★ RELATÓRIO DO RODÍZIO ★",
        bg=COR_FUNDO, fg=COR_DOURADO, font=FONTE_TITULO_JANELA,
    ).pack(pady=(18, 2))
    tk.Label(
        janela_relatorio, text=f"Total de dias registrados: {len(historico_escalas)}",
        bg=COR_FUNDO, fg=COR_TEXTO_SEC, font=FONTE_SUBTITULO,
    ).pack(pady=(0, 14))

    frame_tabela = tk.Frame(janela_relatorio, bg=COR_FUNDO)
    frame_tabela.pack(fill="both", expand=True, padx=16)

    colunas_relatorio = ("dia", "comandante", "ronda", "tarefas", "status")
    tabela = ttk.Treeview(frame_tabela, columns=colunas_relatorio, show="headings", height=12)
    tabela.heading("dia", text="Dia")
    tabela.heading("comandante", text="Comandante")
    tabela.heading("ronda", text="Ronda")
    tabela.heading("tarefas", text="Tarefas do Dia")
    tabela.heading("status", text="Status")
    tabela.column("dia", width=45, anchor="center")
    tabela.column("comandante", width=140, anchor="center")
    tabela.column("ronda", width=140, anchor="center")
    tabela.column("tarefas", width=260, anchor="w")
    tabela.column("status", width=170, anchor="center")
    tabela.tag_configure("status_ok", background=COR_STATUS_OK_BG, foreground=COR_TEXTO)
    tabela.tag_configure("status_falta", background=COR_STATUS_FALTA_BG, foreground=COR_STATUS_FALTA_TXT)
    tabela.tag_configure("status_aberto", background=COR_PAINEL_CLARO, foreground=COR_TEXTO_SEC)

    contagem_faltas = {}  # Dicionário nome -> quantidade de faltas, usado no resumo abaixo

    for registro in historico_escalas:  # REPETIÇÃO: percorre todos os dias já registrados
        tarefas_resumo = "; ".join(registro["tarefas"])

        # SELEÇÃO: define o texto e a cor de status conforme o estado do dia
        if not registro["fechado"]:
            status_texto = "Em aberto"
            tag = "status_aberto"
        elif registro["faltantes"]:
            status_texto = "Falta: " + ", ".join(registro["faltantes"])
            tag = "status_falta"
        else:
            status_texto = "OK"
            tag = "status_ok"

        tabela.insert(
            "", tk.END,
            values=(registro["dia"], registro["comandante"], registro["ronda"], tarefas_resumo, status_texto),
            tags=(tag,),
        )

        for nome_faltante in registro["faltantes"]:  # REPETIÇÃO: acumula as faltas por nome
            # Usa dict.get() com valor padrão 0 para incrementar o contador,
            # substituindo uma checagem manual "if chave in dicionario" antes de somar
            contagem_faltas[nome_faltante] = contagem_faltas.get(nome_faltante, 0) + 1

    barra = ttk.Scrollbar(frame_tabela, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=barra.set)
    tabela.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")

    tk.Label(
        janela_relatorio, text="RESUMO DE FALTAS",
        bg=COR_FUNDO, fg=COR_DOURADO, font=FONTE_SECAO,
    ).pack(anchor="w", padx=16, pady=(16, 4))

    frame_resumo = tk.Frame(janela_relatorio, bg=COR_PAINEL, highlightthickness=1, highlightbackground=COR_BORDA)
    frame_resumo.pack(fill="x", padx=16, pady=(0, 12))

    # SELEÇÃO: só exibe a lista de faltas se houver ao menos uma registrada
    if contagem_faltas:
        # Usa sorted() com key=lambda para ordenar do nome com mais faltas para o com menos,
        # substituindo um algoritmo manual de ordenação (ex.: bubble sort)
        faltas_ordenadas = sorted(contagem_faltas.items(), key=lambda item: item[1], reverse=True)
        for nome, quantidade in faltas_ordenadas:  # REPETIÇÃO: lista cada nome com sua contagem
            tk.Label(
                frame_resumo, text=f"{nome}  —  {quantidade} falta(s)",
                bg=COR_PAINEL, fg=COR_TEXTO, font=FONTE_BASE, anchor="w",
            ).pack(fill="x", padx=14, pady=4)
    else:
        tk.Label(
            frame_resumo, text="Nenhuma falta registrada até o momento.",
            bg=COR_PAINEL, fg=COR_TEXTO_SEC, font=FONTE_BASE,
        ).pack(padx=14, pady=10)

    def exportar_relatorio_txt():
        caminho_escolhido = filedialog.asksaveasfilename(
            title="Exportar Relatório do Rodízio",
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt")],
            initialfile="relatorio_rodizio.txt",
        )
        # SELEÇÃO: interrompe a exportação se o usuário cancelar a caixa de diálogo
        if not caminho_escolhido:
            return

        linhas = ["RELATÓRIO DO RODÍZIO — TIRO DE GUERRA", "=" * 50, ""]
        for registro in historico_escalas:  # REPETIÇÃO: percorre os dias novamente para montar o texto
            linhas.append(f"Dia {registro['dia']}")
            linhas.append(f"  Comandante da Guarda: {registro['comandante']}")
            linhas.append(f"  Atirador de Ronda: {registro['ronda']}")
            linhas.append(f"  Tarefas: {'; '.join(registro['tarefas'])}")

            # SELEÇÃO: escolhe a linha de status conforme o estado do dia
            if not registro["fechado"]:
                linhas.append("  Status: Em aberto")
            elif registro["faltantes"]:
                linhas.append(f"  Status: Falta — {', '.join(registro['faltantes'])}")
                linhas.append(f"  Observação: {registro['observacao']}")
            else:
                linhas.append("  Status: OK")
            linhas.append("")

        linhas.append("RESUMO DE FALTAS")
        if contagem_faltas:
            for nome, quantidade in sorted(contagem_faltas.items(), key=lambda item: item[1], reverse=True):
                linhas.append(f"  {nome}: {quantidade} falta(s)")
        else:
            linhas.append("  Nenhuma falta registrada.")

        with open(caminho_escolhido, "w", encoding="utf-8") as arquivo:
            # Usa join() para concatenar as linhas com quebra de linha entre elas,
            # substituindo a concatenação manual de string dentro de um loop de escrita
            arquivo.write("\n".join(linhas))

        messagebox.showinfo("Exportação concluída", f"Relatório salvo em:\n{caminho_escolhido}")

    ttk.Button(
        janela_relatorio, text="Exportar Relatório (.txt)",
        style="Primary.TButton", command=exportar_relatorio_txt,
    ).pack(pady=(0, 18))


# ============================================================
# MONTAGEM DA INTERFACE GRÁFICA
# ============================================================
def main():
    global txt_pelotao, txt_comandantes, arvore_historico, btn_novo_dia, btn_fechar_dia
    global lbl_dia_valor, lbl_ponteiro_ronda_valor, lbl_ponteiro_comandante_valor
    global lbl_comandante_valor, lbl_ronda_valor

    janela = tk.Tk()
    janela.title("Sistema de Escala Automática — Tiro de Guerra")
    janela.geometry("1000x760")
    janela.minsize(900, 680)
    janela.configure(bg=COR_FUNDO)

    estilo = ttk.Style()
    configurar_estilo(estilo)

    # --------------------------------------------------------
    # Cabeçalho institucional
    # --------------------------------------------------------
    frame_header = tk.Frame(janela, bg=COR_PAINEL)
    frame_header.pack(fill="x")
    tk.Label(
        frame_header,
        text="★  SISTEMA DE ESCALA AUTOMÁTICA  ★",
        bg=COR_PAINEL, fg=COR_DOURADO, font=FONTE_TITULO,
    ).pack(pady=(18, 2))
    tk.Label(
        frame_header,
        text="ATIRADOR DE RONDA  ·  COMANDANTE DA GUARDA DO DIA  —  TIRO DE GUERRA",
        bg=COR_PAINEL, fg=COR_TEXTO_SEC, font=FONTE_SUBTITULO,
    ).pack(pady=(0, 16))
    tk.Frame(janela, bg=COR_DOURADO, height=2).pack(fill="x")

    container = ttk.Frame(janela, padding=16)
    container.pack(fill="both", expand=True)

    # --------------------------------------------------------
    # Bloco 1: Carregamento dos vetores
    # --------------------------------------------------------
    frame_vetores = ttk.LabelFrame(
        container, text="VETORES DE ENTRADA  (um nome por linha)", style="Card.TLabelframe"
    )
    frame_vetores.pack(fill="x", pady=(0, 14))

    corpo_vetores = tk.Frame(frame_vetores, bg=COR_PAINEL)
    corpo_vetores.pack(fill="both", expand=True, padx=4, pady=4)

    frame_vetor_pelotao = tk.Frame(corpo_vetores, bg=COR_PAINEL)
    frame_vetor_pelotao.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    tk.Label(
        frame_vetor_pelotao, text=f"PELOTÃO  ({TAMANHO_PELOTAO} atiradores)",
        bg=COR_PAINEL, fg=COR_TEXTO_SEC, font=FONTE_STAT_ROTULO,
    ).pack(anchor="w", pady=(0, 6))
    txt_pelotao = tk.Text(
        frame_vetor_pelotao, width=32, height=10,
        bg=COR_PAINEL_CLARO, fg=COR_TEXTO, insertbackground=COR_TEXTO,
        relief="flat", highlightthickness=1, highlightbackground=COR_BORDA,
        highlightcolor=COR_DOURADO, font=FONTE_BASE, padx=8, pady=8,
    )
    txt_pelotao.pack(fill="both", expand=True)

    frame_vetor_comandantes = tk.Frame(corpo_vetores, bg=COR_PAINEL)
    frame_vetor_comandantes.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    tk.Label(
        frame_vetor_comandantes, text=f"COMANDANTES ELEGÍVEIS  ({TAMANHO_COMANDANTES} atiradores)",
        bg=COR_PAINEL, fg=COR_TEXTO_SEC, font=FONTE_STAT_ROTULO,
    ).pack(anchor="w", pady=(0, 6))
    txt_comandantes = tk.Text(
        frame_vetor_comandantes, width=32, height=10,
        bg=COR_PAINEL_CLARO, fg=COR_TEXTO, insertbackground=COR_TEXTO,
        relief="flat", highlightthickness=1, highlightbackground=COR_BORDA,
        highlightcolor=COR_DOURADO, font=FONTE_BASE, padx=8, pady=8,
    )
    txt_comandantes.pack(fill="both", expand=True)

    corpo_vetores.columnconfigure(0, weight=1)
    corpo_vetores.columnconfigure(1, weight=1)

    frame_botoes_vetores = tk.Frame(corpo_vetores, bg=COR_PAINEL)
    frame_botoes_vetores.grid(row=1, column=0, columnspan=2, pady=(0, 10))
    ttk.Button(
        frame_botoes_vetores, text="Restaurar Nomes Padrão",
        style="Secondary.TButton", command=restaurar_padrao,
    ).pack(side="left", padx=6)
    ttk.Button(
        frame_botoes_vetores, text="Carregar Vetores / Iniciar Sistema",
        style="Primary.TButton", command=carregar_vetores,
    ).pack(side="left", padx=6)

    # --------------------------------------------------------
    # Bloco 2: Painel de estado atual (exibição em tempo real)
    # --------------------------------------------------------
    tk.Label(
        container, text="ESTADO ATUAL DO SISTEMA",
        bg=COR_FUNDO, fg=COR_DOURADO, font=FONTE_SECAO,
    ).pack(anchor="w", pady=(0, 8))

    linha_stats_principal = tk.Frame(container, bg=COR_FUNDO)
    linha_stats_principal.pack(fill="x", pady=(0, 8))
    linha_stats_principal.columnconfigure(0, weight=1)
    linha_stats_principal.columnconfigure(1, weight=1)
    linha_stats_principal.columnconfigure(2, weight=1)

    card_dia, lbl_dia_valor = criar_stat_card(linha_stats_principal, "DIA DE INSTRUÇÃO")
    card_dia.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

    card_comandante, lbl_comandante_valor = criar_stat_card(linha_stats_principal, "COMANDANTE DA GUARDA DO DIA")
    card_comandante.grid(row=0, column=1, padx=8, sticky="nsew")

    card_ronda, lbl_ronda_valor = criar_stat_card(linha_stats_principal, "ATIRADOR DE RONDA DO DIA")
    card_ronda.grid(row=0, column=2, padx=(8, 0), sticky="nsew")

    linha_stats_ponteiros = tk.Frame(container, bg=COR_FUNDO)
    linha_stats_ponteiros.pack(fill="x", pady=(0, 14))
    linha_stats_ponteiros.columnconfigure(0, weight=1)
    linha_stats_ponteiros.columnconfigure(1, weight=1)

    card_ponteiro_ronda, lbl_ponteiro_ronda_valor = criar_stat_card(
        linha_stats_ponteiros, "ponteiro_ronda", destaque=False
    )
    card_ponteiro_ronda.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

    card_ponteiro_comandante, lbl_ponteiro_comandante_valor = criar_stat_card(
        linha_stats_ponteiros, "ponteiro_comandante", destaque=False
    )
    card_ponteiro_comandante.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

    # --------------------------------------------------------
    # Bloco 3: Ações do dia
    # --------------------------------------------------------
    frame_acoes = tk.Frame(container, bg=COR_FUNDO)
    frame_acoes.pack(fill="x", pady=(0, 14))

    btn_novo_dia = ttk.Button(
        frame_acoes, text="Gerar Novo Dia",
        style="Primary.TButton", command=gerar_novo_dia, state=tk.DISABLED,
    )
    btn_novo_dia.pack(side="left", padx=(0, 8))

    btn_fechar_dia = ttk.Button(
        frame_acoes, text="Fechar o Dia",
        style="Primary.TButton", command=fechar_dia, state=tk.DISABLED,
    )
    btn_fechar_dia.pack(side="left", padx=(0, 8))

    ttk.Button(
        frame_acoes, text="Consultar Escala do Dia",
        style="Secondary.TButton", command=consultar_escala_do_dia,
    ).pack(side="left", padx=(0, 8))

    ttk.Button(
        frame_acoes, text="Ver Tarefas do Dia",
        style="Secondary.TButton", command=abrir_janela_tarefas,
    ).pack(side="left", padx=(0, 8))

    ttk.Button(
        frame_acoes, text="Relatório do Rodízio",
        style="Secondary.TButton", command=abrir_janela_relatorio,
    ).pack(side="left")

    # --------------------------------------------------------
    # Bloco 4: Histórico de escalas (Treeview)
    # --------------------------------------------------------
    frame_historico = ttk.LabelFrame(container, text="HISTÓRICO DE ESCALAS", style="Card.TLabelframe")
    frame_historico.pack(fill="both", expand=True)

    corpo_historico = tk.Frame(frame_historico, bg=COR_PAINEL)
    corpo_historico.pack(fill="both", expand=True, padx=4, pady=4)

    colunas = ("dia", "comandante", "ronda", "status")
    arvore_historico = ttk.Treeview(corpo_historico, columns=colunas, show="headings", height=10)
    arvore_historico.heading("dia", text="Dia")
    arvore_historico.heading("comandante", text="Comandante da Guarda")
    arvore_historico.heading("ronda", text="Atirador de Ronda")
    arvore_historico.heading("status", text="Status")
    arvore_historico.column("dia", width=60, anchor="center")
    arvore_historico.column("comandante", width=220, anchor="center")
    arvore_historico.column("ronda", width=220, anchor="center")
    arvore_historico.column("status", width=200, anchor="center")
    arvore_historico.tag_configure("status_aberto", background=COR_PAINEL_CLARO, foreground=COR_TEXTO_SEC)
    arvore_historico.tag_configure("status_ok", background=COR_STATUS_OK_BG, foreground=COR_TEXTO)
    arvore_historico.tag_configure("status_falta", background=COR_STATUS_FALTA_BG, foreground=COR_STATUS_FALTA_TXT)

    barra_rolagem = ttk.Scrollbar(corpo_historico, orient="vertical", command=arvore_historico.yview)
    arvore_historico.configure(yscrollcommand=barra_rolagem.set)

    arvore_historico.pack(side="left", fill="both", expand=True, padx=(4, 0), pady=4)
    barra_rolagem.pack(side="right", fill="y", pady=4)

    # Preenche os campos de texto com os nomes padrão já na abertura do sistema
    restaurar_padrao()

    janela.mainloop()


if __name__ == "__main__":
    main()
