# MEMORY.md — Contexto Arquitetural e Memória de Trabalho

<p align="center">
  <a href="#-português">🇧🇷 Português</a> •
  <a href="#-english">🇺🇸 English</a>
</p>

---

## 🇧🇷 Português

> Documento de continuidade do projeto **Sistema_TG**. Serve para qualquer pessoa (ou IA) retomar o trabalho sem precisar reconstruir o raciocínio do zero. Não é documentação de usuário final (isso é o [`README.md`](README.md)) — é contexto de **decisões, arquitetura e estado**.

---

## 1. O que é o projeto

Sistema de escala automática (rodízio) de **Atirador de Ronda** e **Comandante da Guarda do Dia** para um pelotão de **Tiro de Guerra (TG)**. É, ao mesmo tempo:

1. Uma ferramenta funcional de sorteio/gestão de escala de guarda.
2. Um exercício pedagógico de lógica de programação estruturada/procedural em Python, com restrições rígidas definidas em [`ia/Prompt Python.md`](ia/Prompt%20Python.md).

Arquivo único de aplicação: **`ia/sistema_escala.py`** (~980 linhas). Sem dependências externas — apenas biblioteca padrão (`tkinter`, `random`).

---

## 2. Restrições pedagógicas (não negociáveis)

Definidas em `ia/Prompt Python.md`, vindas de antes desta sessão. Qualquer mudança futura no código **precisa respeitar**:

- **Proibido usar `class`** — paradigma 100% procedural. Estado em variáveis globais, manipulado por funções com `global`.
- Funções nativas/métodos de alto nível (`random.choice`, `random.sample`, `sorted`, `dict.get`, list comprehensions, `f-string`, etc.) são permitidos, **mas todo uso precisa de comentário** explicando o que a função faz por baixo dos panos e qual algoritmo manual ela substitui.
- Funções de regra de negócio devem ter docstring no formato **DADO / QUANDO / ENTÃO**.
- O fluxo deve evidenciar as três estruturas de Böhm-Jacopini via comentários: `# SEQUÊNCIA`, `# SELEÇÃO`, `# REPETIÇÃO`.
- Interface: `tkinter` + `tkinter.ttk` (`ttk.Style` para tema nativo). Validação de entrada e tratamento de erro via `messagebox`.

Essas regras foram seguidas em todas as etapas (1, 2 e 3) e devem continuar sendo seguidas.

---

## 3. Arquitetura do código (`ia/sistema_escala.py`)

O arquivo é organizado em seções marcadas com comentários `# ====...====`, nesta ordem:

| Seção | Conteúdo |
|---|---|
| **Estruturas de dados globais** | Constantes de tamanho + vetores + ponteiros + estado do dia + histórico |
| **Paleta e estilo visual** | Cores, fontes, `configurar_estilo()`, `criar_stat_card()` |
| **Funções de geração de dados padrão** | Bancos de nomes + `gerar_pessoas_aleatorias()` |
| **Funções de regra de negócio** | `selecionar_comandante_do_dia()`, `selecionar_atirador_ronda()` (lógica pura, sem tkinter) |
| **Funções de tarefas do dia** | Banco de tarefas + `sortear_tarefas_do_dia()` |
| **Funções de interface** | Callbacks dos botões (dependem de widgets globais criados em `main()`) |
| **Montagem da interface gráfica** | `main()` — cria a janela, aplica estilo, monta os 4 blocos da tela |

### 3.1 Estado global (variáveis-chave)

```python
TAMANHO_PELOTAO = 38        # atiradores SEM elegibilidade a comando
TAMANHO_COMANDANTES = 12    # atiradores elegíveis a comando
# efetivo real total = 38 + 12 = 50 (os dois vetores são disjuntos)

vetor_pelotao = []          # nomes, tamanho TAMANHO_PELOTAO
vetor_comandantes = []      # nomes, tamanho TAMANHO_COMANDANTES

ponteiro_ronda = 0          # índice cíclico em vetor_pelotao
ponteiro_comandante = 0     # índice cíclico em vetor_comandantes

dia_atual = 0                # contador de dias já escalados
dia_aberto = False           # True entre "Gerar Novo Dia" e "Fechar o Dia"
historico_escalas = []       # lista de dicts, um por dia (ver 3.2)
```

### 3.2 Esquema de um dia em `historico_escalas`

Cada dia é um **dicionário** (não tupla — decisão tomada na Etapa 3 para acomodar múltiplos campos com nomes claros):

```python
{
    "dia": int,
    "comandante": str,
    "ronda": str,
    "tarefas": [str, str, str],       # 3 tarefas sorteadas
    "fechado": bool,                  # False até "Fechar o Dia" ser confirmado
    "faltantes": [str],               # ex.: ["Comandante (Nome)", "Ronda (Nome)"]
    "observacao": str,                # texto livre do registro de falta
    "item_id": str,                   # id do item na Treeview principal, p/ atualizar depois
}
```

### 3.3 Telas (janelas)

- **Janela principal** (`main()`): 4 blocos — vetores de entrada, painel de estado (cards), ações do dia, histórico (Treeview com coluna de status colorida).
- **`abrir_janela_tarefas()`** (Toplevel): mostra as 3 tarefas do dia atual.
- **`abrir_janela_registro_falta(registro)`** (Toplevel, `grab_set()`): checkboxes de quem faltou + campo de observação livre. Ao confirmar, chama `concluir_fechamento_dia()`.
- **`abrir_janela_relatorio()`** (Toplevel): tabela completa do rodízio + resumo de faltas por pessoa (dict de contagem) + botão de exportação para `.txt` (`filedialog.asksaveasfilename`).

### 3.4 Fluxo de um dia

```
Carregar Vetores → [Gerar Novo Dia] → dia_aberto = True
                        ↓
              (sorteia comandante, ronda, 3 tarefas)
                        ↓
                 [Ver Tarefas do Dia] (opcional, quantas vezes quiser)
                        ↓
                  [Fechar o Dia] → pergunta "ocorreu bem?"
                        ├─ Sim → fecha direto, dia_aberto = False
                        └─ Não → abre janela de falta → confirma → fecha, dia_aberto = False
                        ↓
              (só agora "Gerar Novo Dia" é liberado de novo)
```

**Decisão importante**: `gerar_novo_dia()` bloqueia a geração de um novo dia enquanto `dia_aberto == True`. Isso é intencional (ver seção 4) e não é um bug.

---

## 4. Decisões de design e o porquê (não óbvio pelo código)

| Decisão | Motivo |
|---|---|
| `TAMANHO_PELOTAO` = 38 (não 50) | Os 12 comandantes elegíveis são um **subconjunto** dos 50 atiradores reais, não pessoas à parte. Efetivo total = 38 + 12 = 50. Corrigido na Etapa 2 a pedido do usuário. |
| Nomes sorteados nunca se repetem entre `vetor_pelotao` e `vetor_comandantes` | Reflete que é o mesmo efetivo de 50 pessoas reais — `gerar_nomes_padrao_comandantes()` recebe os nomes já usados no pelotão como exclusão. |
| tkinter/ttk puro, sem `customtkinter` | Escolha explícita do usuário (perguntado via clarificação) — zero dependências externas, mesmo abrindo mão de um visual ainda mais "flat/moderno". |
| Paleta verde-oliva + dourado, **sem** brasão/emblema oficial do Exército | Escolha explícita do usuário — usar só paleta e estilo "inspirado", evitando reproduzir símbolo oficial em sistema não institucional. |
| Falta apenas registra observação livre (não sorteia substituto automático) | Escolha explícita do usuário — manter a lógica de ponteiros intocada; a decisão de quem substitui fica com o humano, registrada em texto. |
| `historico_escalas` migrou de lista de tuplas para lista de dicts (Etapa 3) | Tuplas posicionais ficariam ilegíveis com 8 campos por dia; dict não viola a restrição de "sem `class`" (é estrutura nativa). |
| Treeview usa tags de **status** (aberto/ok/falta) coloridas em vez de zebra striping | Depois da Etapa 3, status por dia é uma informação mais útil visualmente do que striping alternado — as duas coisas competiam pela mesma tag, então zebra foi removida. |
| `Gerar Novo Dia` bloqueado até `Fechar o Dia` | Mantém o registro de faltas consistente — não dá pra "pular" o fechamento e perder o rastro do dia anterior. |
| Branch `mudancas` como área de trabalho, `master` como checkpoint | Pedido explícito do usuário no início da sessão: medo de mudanças desagradarem, queria sempre um ponto seguro de volta. Ver seção 5. |

---

## 5. Fluxo de trabalho Git usado neste projeto

Estabelecido a pedido do usuário e mantido consistentemente:

- **`master`** — sempre igual ao `origin/master`. É o **checkpoint estável**, nunca recebe commits diretos de trabalho em progresso.
- **`mudancas`** — branch de trabalho. Todo ajuste solicitado é commitado aqui primeiro.
- Quando o usuário aprova o resultado (testou e gostou):
  1. Commit na `mudancas` com mensagem `Etapa N: descrição` (corpo detalhado + rodapé `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`).
  2. `git checkout master && git merge mudancas --ff-only` (sempre fast-forward, nunca há divergência real).
  3. `git push origin master`.
  4. `git checkout mudancas` de novo, pronta para o próximo ajuste.

**Histórico de etapas até agora:**

| Commit (master) | Etapa | Conteúdo |
|---|---|---|
| `3b3ee14` | Etapa 1 (pré-sessão) | Sistema de escala inicial (ronda e comandante da guarda) |
| `24f2945` | Etapa 1 (desta sessão) → visual | Redesign visual: interface tática, paleta militar |
| `24f2945` | Etapa 2 | Nomes aleatórios + correção do efetivo (38+12=50) |
| `45f2b2e` | Etapa 3 | Tarefas do dia, fechamento com registro de falta, relatório do rodízio |

> Nota: a Etapa 1 do redesign visual e a Etapa 2 (nomes/efetivo) foram commitadas juntas em `24f2945` como "Etapa 2" — o redesign visual em si ficou num commit anterior (`38bdd73` na branch `mudancas`, incorporado ao fast-forward).

---

## 6. Estado atual (o que já existe)

- ✅ Interface gráfica com identidade visual militar (tema escuro, verde-oliva + dourado).
- ✅ Geração de nomes aleatórios brasileiros, sem repetição entre pelotão e comandantes.
- ✅ Modelo de efetivo correto (38 + 12 = 50).
- ✅ Seleção cíclica por ponteiros (comandante e ronda), sem coincidência entre os dois no mesmo dia.
- ✅ Sorteio de 3 tarefas do dia por pessoa escalada.
- ✅ Fechamento do dia com pergunta de "ocorreu bem?" e registro de falta (quem + observação livre).
- ✅ Bloqueio de novo dia até o atual ser fechado.
- ✅ Relatório do rodízio completo (tabela + resumo de faltas + exportação `.txt`).
- ✅ `README.md` bilíngue (PT/EN) completo.

## 7. Pontos em aberto / possíveis próximos passos

Não implementados, não decididos — apenas registrados para não perder o fio:

- **Licença do projeto**: nenhuma foi definida ou solicitada. Não presumir uma sem perguntar ao usuário.
- **Screenshots no README**: não incluídos (nenhuma captura de tela real foi gerada com sucesso durante a sessão — tentativas via PowerShell esbarraram em permissão de leitura fora do diretório de trabalho).
- Qualquer nova funcionalidade deve passar pelo mesmo padrão: **perguntar antes de decisões de arquitetura/regra de negócio não triviais**, implementar na `mudancas`, testar a GUI antes de reportar como concluído, só então commitar + merge + push a pedido explícito do usuário.

---

## 8. Convenções a manter em qualquer edição futura

- Nunca introduzir `class`.
- Nunca adicionar dependência externa sem perguntar (o projeto é, por escolha, 100% biblioteca padrão).
- Comentar todo uso de função/método nativo de alto nível não trivial.
- Manter os comentários `SEQUÊNCIA` / `SELEÇÃO` / `REPETIÇÃO` nos blocos de controle de fluxo novos.
- Manter a paleta de cores definida no topo do arquivo (`COR_*`, `FONTE_*`) em vez de valores soltos — qualquer novo widget deve reutilizar essas constantes.
- Seguir o fluxo de git da seção 5: trabalhar na `mudancas`, só ir para `master`/GitHub quando o usuário aprovar explicitamente.

---

## 🇺🇸 English

> Continuity document for the **Sistema_TG** project. It lets anyone (or any AI) pick up the work without reconstructing the reasoning from scratch. This is not end-user documentation (that's [`README.md`](README.md)) — it's context on **decisions, architecture, and current state**.

---

## 1. What the project is

Automatic guard-duty rotation system for **Patrol Shooter** and **Guard Commander of the Day**, for a Brazilian **Tiro de Guerra (TG)** platoon. It's simultaneously:

1. A functional roster-drawing/management tool.
2. A structured/procedural programming-logic teaching exercise in Python, under strict constraints defined in [`ia/Prompt Python.md`](ia/Prompt%20Python.md).

Single application file: **`ia/sistema_escala.py`** (~980 lines). No external dependencies — standard library only (`tkinter`, `random`).

---

## 2. Pedagogical constraints (non-negotiable)

Defined in `ia/Prompt Python.md`, predating this session. Any future change to the code **must respect**:

- **`class` is forbidden** — 100% procedural paradigm. State lives in global variables, manipulated by functions using `global`.
- High-level built-in functions/methods (`random.choice`, `random.sample`, `sorted`, `dict.get`, list comprehensions, f-strings, etc.) are allowed, **but every use needs a comment** explaining what it does under the hood and which manual algorithm it replaces.
- Business-rule functions must carry a **GIVEN / WHEN / THEN**-style docstring.
- The flow must make the three Böhm–Jacopini structures explicit via comments: `# SEQUÊNCIA` (Sequence), `# SELEÇÃO` (Selection), `# REPETIÇÃO` (Repetition) — kept in Portuguese in the code itself, matching the original spec's language.
- UI: `tkinter` + `tkinter.ttk` (`ttk.Style` for native theming). Input validation and error handling via `messagebox`.

These rules were followed through all stages (1, 2, and 3) and must keep being followed.

---

## 3. Code architecture (`ia/sistema_escala.py`)

The file is organized into sections marked with `# ====...====` comments, in this order:

| Section | Contents |
|---|---|
| **Global data structures** | Size constants + rosters + pointers + day state + history |
| **Visual palette and style** | Colors, fonts, `configurar_estilo()`, `criar_stat_card()` |
| **Default data generation functions** | Name banks + `gerar_pessoas_aleatorias()` |
| **Business rule functions** | `selecionar_comandante_do_dia()`, `selecionar_atirador_ronda()` (pure logic, no tkinter) |
| **Daily task functions** | Task bank + `sortear_tarefas_do_dia()` |
| **Interface functions** | Button callbacks (depend on global widgets created in `main()`) |
| **GUI assembly** | `main()` — builds the window, applies the style, assembles the screen's 4 blocks |

### 3.1 Global state (key variables)

```python
TAMANHO_PELOTAO = 38        # shooters WITHOUT command eligibility
TAMANHO_COMANDANTES = 12    # command-eligible shooters
# real total headcount = 38 + 12 = 50 (the two rosters are disjoint)

vetor_pelotao = []          # names, size TAMANHO_PELOTAO
vetor_comandantes = []      # names, size TAMANHO_COMANDANTES

ponteiro_ronda = 0          # cyclic index into vetor_pelotao
ponteiro_comandante = 0     # cyclic index into vetor_comandantes

dia_atual = 0                # count of days already scheduled
dia_aberto = False           # True between "Generate New Day" and "Close the Day"
historico_escalas = []       # list of dicts, one per day (see 3.2)
```

### 3.2 Schema of one day in `historico_escalas`

Each day is a **dictionary** (not a tuple — a decision made in Stage 3 to accommodate several clearly-named fields):

```python
{
    "dia": int,
    "comandante": str,
    "ronda": str,
    "tarefas": [str, str, str],       # 3 tasks drawn
    "fechado": bool,                  # False until "Close the Day" is confirmed
    "faltantes": [str],               # e.g. ["Comandante (Name)", "Ronda (Name)"]
    "observacao": str,                # free-text note from the absence record
    "item_id": str,                   # id of the row in the main Treeview, used to update it later
}
```

### 3.3 Screens (windows)

- **Main window** (`main()`): 4 blocks — input rosters, status panel (cards), day actions, history (Treeview with a colored status column).
- **`abrir_janela_tarefas()`** (Toplevel): shows the current day's 3 tasks.
- **`abrir_janela_registro_falta(registro)`** (Toplevel, `grab_set()`): checkboxes for who was absent + free-text note field. On confirm, calls `concluir_fechamento_dia()`.
- **`abrir_janela_relatorio()`** (Toplevel): full rotation table + per-person absence summary (a counting dict) + export-to-`.txt` button (`filedialog.asksaveasfilename`).

### 3.4 Day flow

```
Load Rosters → [Generate New Day] → dia_aberto = True
                        ↓
          (draws commander, patrol shooter, 3 tasks)
                        ↓
              [View Day's Tasks] (optional, any number of times)
                        ↓
              [Close the Day] → asks "did everything go fine?"
                        ├─ Yes → closes directly, dia_aberto = False
                        └─ No → opens absence window → confirm → closes, dia_aberto = False
                        ↓
          (only now is "Generate New Day" unlocked again)
```

**Important decision**: `gerar_novo_dia()` blocks generating a new day while `dia_aberto == True`. This is intentional (see section 4), not a bug.

---

## 4. Design decisions and why (not obvious from the code alone)

| Decision | Reason |
|---|---|
| `TAMANHO_PELOTAO` = 38 (not 50) | The 12 command-eligible shooters are a **subset** of the 50 real shooters, not separate people. Total headcount = 38 + 12 = 50. Fixed in Stage 2 at the user's request. |
| Drawn names never repeat between `vetor_pelotao` and `vetor_comandantes` | Reflects that it's the same real 50-person headcount — `gerar_nomes_padrao_comandantes()` receives the platoon's already-used names as an exclusion list. |
| Plain tkinter/ttk, no `customtkinter` | Explicit user choice (asked via clarification) — zero external dependencies, even at the cost of a less "flat/modern" look. |
| Olive-green + gold palette, **no** official Army coat of arms/emblem | Explicit user choice — palette and "inspired" styling only, avoiding reproducing an official symbol in a non-institutional system. |
| Absences only record a free-text note (no automatic substitute draw) | Explicit user choice — keeps the pointer logic untouched; the decision of who substitutes stays with the human, recorded as text. |
| `historico_escalas` moved from a list of tuples to a list of dicts (Stage 3) | Positional tuples would be unreadable with 8 fields per day; a dict doesn't violate the "no `class`" constraint (it's a native structure). |
| Treeview uses colored **status** tags (open/ok/absence) instead of zebra striping | After Stage 3, per-day status is more visually useful than alternating stripes — the two competed for the same tag, so zebra striping was removed. |
| `Generate New Day` blocked until `Close the Day` | Keeps the absence record consistent — you can't "skip" closing and lose track of the previous day. |
| `mudancas` branch as the working area, `master` as the checkpoint | Explicit user request at the start of the session: afraid changes might turn out badly, wanted a safe point to always fall back to. See section 5. |

---

## 5. Git workflow used in this project

Established at the user's request and kept consistent throughout:

- **`master`** — always equal to `origin/master`. The **stable checkpoint**, never receives direct work-in-progress commits.
- **`mudancas`** — working branch. Every requested change is committed here first.
- Once the user approves the result (tested it and liked it):
  1. Commit on `mudancas` with message `Etapa N: description` (detailed body + `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>` footer).
  2. `git checkout master && git merge mudancas --ff-only` (always a fast-forward, no real divergence).
  3. `git push origin master`.
  4. `git checkout mudancas` again, ready for the next change.

**Stage history so far:**

| Commit (master) | Stage | Content |
|---|---|---|
| `3b3ee14` | Stage 1 (pre-session) | Initial scheduling system (patrol and guard commander) |
| `24f2945` | Stage 1 (this session) → visual | Visual redesign: tactical UI, military palette |
| `24f2945` | Stage 2 | Random names + headcount fix (38+12=50) |
| `45f2b2e` | Stage 3 | Daily tasks, closing flow with absence record, rotation report |

> Note: the visual redesign (Stage 1) and the names/headcount fix (Stage 2) were committed together in `24f2945` as "Etapa 2" — the visual redesign itself sits in an earlier commit (`38bdd73` on the `mudancas` branch), carried along by the fast-forward.

---

## 6. Current state (what already exists)

- ✅ GUI with a military visual identity (dark theme, olive-green + gold).
- ✅ Random Brazilian name generation, no repeats between platoon and commanders.
- ✅ Correct headcount model (38 + 12 = 50).
- ✅ Cyclic pointer-based selection (commander and patrol), no same-day overlap between the two.
- ✅ Draw of 3 daily tasks per scheduled person.
- ✅ Day-closing flow with a "did everything go fine?" question and absence recording (who + free-text note).
- ✅ New day blocked until the current one is closed.
- ✅ Full rotation report (table + absence summary + `.txt` export).
- ✅ Bilingual (PT/EN) `README.md`.

## 7. Open points / possible next steps

Not implemented, not decided — recorded only so the thread isn't lost:

- **Project license**: none defined or requested. Do not assume one without asking the user.
- **Screenshots in the README**: not included (no real screenshot was successfully generated during the session — PowerShell attempts ran into read-permission restrictions outside the working directory).
- Any new feature should follow the same pattern: **ask before non-trivial architecture/business-rule decisions**, implement on `mudancas`, test the GUI before reporting it as done, only then commit + merge + push at the user's explicit request.

---

## 8. Conventions to keep in any future edit

- Never introduce `class`.
- Never add an external dependency without asking (the project is, by choice, 100% standard library).
- Comment every non-trivial use of a high-level built-in function/method.
- Keep the `SEQUÊNCIA` / `SELEÇÃO` / `REPETIÇÃO` comments on new control-flow blocks.
- Keep using the color palette defined at the top of the file (`COR_*`, `FONTE_*`) instead of loose values — any new widget should reuse those constants.
- Follow the git workflow from section 5: work on `mudancas`, only go to `master`/GitHub when the user explicitly approves.
