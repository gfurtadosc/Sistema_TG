# Sistema de Escala Automática — Tiro de Guerra

Sistema de escala automática (rodízio) de **Atirador de Ronda** e **Comandante da Guarda do Dia**, com interface gráfica em tkinter e identidade visual inspirada no Exército Brasileiro. Feito para o contexto do **Tiro de Guerra (TG)**.

<p align="center">
  <a href="#-português">🇧🇷 Português</a> •
  <a href="#-english">🇺🇸 English</a>
</p>

---

## 🇧🇷 Português

### Sobre o projeto

Este projeto simula o rodízio diário de guarda de um pelotão de Tiro de Guerra: a cada dia de instrução, o sistema seleciona automaticamente um **Comandante da Guarda** (dentre os atiradores elegíveis a comando) e um **Atirador de Ronda** (dentre o restante do efetivo), sorteia as tarefas do dia para os dois, e permite registrar o encerramento do dia — inclusive eventuais faltas.

É também um exercício pedagógico de lógica de programação: todo o código é **100% procedural** (sem uso da palavra-chave `class`), evidenciando as três estruturas fundamentais de controle de fluxo (**Sequência**, **Seleção** e **Repetição** — estruturas de Böhm-Jacopini) através de comentários no código. A especificação original que deu origem a essas regras está em [`ia/Prompt Python.md`](ia/Prompt%20Python.md).

### Funcionalidades

- **Vetores de entrada editáveis**: um campo de texto para os atiradores do pelotão e outro para os comandantes elegíveis (um nome por linha).
- **Geração automática de nomes**: nomes brasileiros aleatórios (nome + sobrenome), sem repetição entre os dois vetores.
- **Seleção cíclica por ponteiros**: a cada novo dia, os ponteiros avançam nos vetores e retornam ao início ao chegar no fim, garantindo rodízio justo.
- **Sorteio de tarefas do dia**: 3 tarefas sorteadas de um banco de tarefas típicas de Tiro de Guerra (rondas, inspeções, hasteamento de bandeira, etc.).
- **Fechamento do dia**: ao final do dia, o sistema pergunta se tudo ocorreu bem; se não, permite registrar quem faltou (comandante e/ou ronda) e uma observação livre sobre o que foi feito a respeito.
- **Relatório do rodízio**: janela com a tabela completa de todos os dias (comandante, ronda, tarefas, status), resumo de faltas por atirador, e exportação do relatório em arquivo `.txt`.
- **Painel de estado em tempo real**: dia atual, próximos da fila (ponteiros), comandante e ronda do dia.
- **Interface visual própria**: paleta verde-oliva e dourado, inspirada no visual militar, sem usar brasões ou símbolos oficiais.

### Requisitos

- **Python 3.8+**
- **tkinter** — já incluso na instalação padrão do Python no Windows e macOS. No Linux (Debian/Ubuntu), pode ser necessário instalar separadamente:
  ```bash
  sudo apt install python3-tk
  ```
- Nenhuma dependência externa (`pip install`) é necessária — o projeto usa apenas a biblioteca padrão do Python (`tkinter`, `random`).

### Como executar

```bash
python ia/sistema_escala.py
```

### Como usar

1. **Restaurar Nomes Padrão** (opcional) — gera 38 nomes de atiradores e 12 nomes de comandantes aleatoriamente, ou edite os campos manualmente (um nome por linha).
2. **Carregar Vetores / Iniciar Sistema** — valida a quantidade de nomes e reinicia os ponteiros do rodízio.
3. **Gerar Novo Dia** — sorteia o comandante da guarda, o atirador de ronda e as 3 tarefas do dia.
4. **Ver Tarefas do Dia** — consulta as tarefas sorteadas para o dia atual.
5. **Fechar o Dia** — confirma se tudo ocorreu bem; caso contrário, registra a falta e uma observação. **Um novo dia só pode ser gerado depois que o dia atual for fechado.**
6. **Relatório do Rodízio** — consulta o histórico completo, o resumo de faltas por atirador e exporta tudo em `.txt`.

### Estrutura do projeto

```
Sistema_TG/
├── ia/
│   ├── sistema_escala.py    # Aplicação principal (lógica + interface tkinter)
│   └── Prompt Python.md     # Especificação/prompt pedagógico original do projeto
├── .gitignore
└── README.md
```

### Paradigma e regras pedagógicas

- **Proibido o uso de `class`** — todo o estado é mantido em variáveis globais e manipulado por funções.
- Uso de funções e métodos nativos de alto nível (`random.choice`, `random.sample`, `sorted`, `dict.get`, list comprehensions, etc.) é permitido, mas cada uso é comentado explicando o que a função faz "por baixo dos panos" e qual algoritmo manual ela substitui.
- As funções de regra de negócio (seleção de comandante e de atirador de ronda) trazem docstrings no formato **DADO / QUANDO / ENTÃO**, evidenciando o comportamento esperado.

### Regras de negócio

- O efetivo real do pelotão é de **50 atiradores**. Os **12 comandantes elegíveis são um subconjunto** desses 50 — não pessoas à parte. Por isso:
  - `vetor_pelotao` tem **38** posições (atiradores sem elegibilidade a comando);
  - `vetor_comandantes` tem **12** posições (atiradores elegíveis a comando);
  - `38 + 12 = 50` (efetivo total).
- A seleção é feita por **ponteiros cíclicos** (`ponteiro_ronda`, `ponteiro_comandante`) que avançam a cada dia e voltam à posição 0 ao chegar ao fim do vetor.
- O **atirador de ronda nunca pode ser a mesma pessoa que o comandante do dia** — se coincidir, o sistema pula para o próximo da fila.
- Um novo dia só pode ser gerado depois que o dia atual estiver **fechado** (com ou sem falta registrada).

---

## 🇺🇸 English

### About

This project simulates the daily guard duty rotation of a Brazilian *Tiro de Guerra* (TG) platoon — a short-term military training program. Each training day, the system automatically selects a **Guard Commander** (from the commander-eligible pool) and a **Patrol Shooter** (from the rest of the platoon), draws the day's tasks for both, and lets the user record the day's closing status — including any absences.

It's also a programming-logic teaching exercise: the entire codebase is **100% procedural** (no `class` keyword is used anywhere), making the three fundamental control-flow structures (**Sequence**, **Selection**, and **Repetition** — Böhm–Jacopini structures) explicit through inline comments. The original spec/prompt that defines these constraints lives in [`ia/Prompt Python.md`](ia/Prompt%20Python.md).

### Features

- **Editable input rosters**: one text box for platoon shooters, another for commander-eligible shooters (one name per line).
- **Automatic name generation**: random Brazilian full names, guaranteed not to repeat across the two rosters.
- **Cyclic pointer-based selection**: each new day advances two pointers through the rosters, wrapping back to the start when the end is reached, ensuring a fair rotation.
- **Daily task draw**: 3 tasks randomly drawn from a bank of typical Tiro de Guerra duties (patrols, inspections, flag ceremony, etc.).
- **Day closing flow**: at the end of the day, the system asks whether everything went fine; if not, it lets the user record who was absent (commander and/or patrol shooter) and a free-text note on what was done about it.
- **Rotation report**: a window with the full day-by-day table (commander, patrol shooter, tasks, status), an absence count summary per shooter, and export of the whole report to a `.txt` file.
- **Real-time status panel**: current day, next-in-line pointers, today's commander and patrol shooter.
- **Custom visual identity**: an olive-green and gold palette inspired by military aesthetics, without reproducing any official coat of arms or emblem.

### Requirements

- **Python 3.8+**
- **tkinter** — bundled with the standard Python installation on Windows and macOS. On Linux (Debian/Ubuntu) it may need to be installed separately:
  ```bash
  sudo apt install python3-tk
  ```
- No external dependencies (`pip install`) are required — the project only uses Python's standard library (`tkinter`, `random`).

### How to run

```bash
python ia/sistema_escala.py
```

### How to use

1. **Restore Default Names** (optional) — randomly generates 38 platoon shooter names and 12 commander names, or edit the fields manually (one name per line).
2. **Load Rosters / Start System** — validates the name counts and resets the rotation pointers.
3. **Generate New Day** — draws the guard commander, the patrol shooter, and the 3 tasks for the day.
4. **View Day's Tasks** — shows the tasks drawn for the current day.
5. **Close the Day** — confirms whether everything went fine; otherwise, records the absence and a note. **A new day can only be generated after the current day is closed.**
6. **Rotation Report** — reviews the full history, the per-shooter absence summary, and exports everything to `.txt`.

### Project structure

```
Sistema_TG/
├── ia/
│   ├── sistema_escala.py    # Main application (business logic + tkinter UI)
│   └── Prompt Python.md     # Original pedagogical spec/prompt for the project
├── .gitignore
└── README.md
```

### Paradigm and pedagogical constraints

- **No `class` keyword allowed** — all state lives in global variables, manipulated by plain functions.
- High-level built-in functions and methods (`random.choice`, `random.sample`, `sorted`, `dict.get`, list comprehensions, etc.) are allowed, but every use is commented explaining what it does under the hood and which manual algorithm it replaces.
- Business-rule functions (commander and patrol shooter selection) carry **GIVEN / WHEN / THEN**-style docstrings that make the expected behavior explicit.

### Business rules

- The platoon's real headcount is **50 shooters**. The **12 commander-eligible shooters are a subset** of those 50 — not separate people. Therefore:
  - `vetor_pelotao` holds **38** entries (shooters without command eligibility);
  - `vetor_comandantes` holds **12** entries (command-eligible shooters);
  - `38 + 12 = 50` (total headcount).
- Selection uses **cyclic pointers** (`ponteiro_ronda`, `ponteiro_comandante`) that advance every day and wrap back to position 0 once they reach the end of the vector.
- The **patrol shooter can never be the same person as that day's commander** — if they match, the system skips to the next one in line.
- A new day can only be generated once the current day has been **closed** (with or without a recorded absence).
