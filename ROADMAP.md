# ROADMAP.md — Sistema de Escala Automática (Tiro de Guerra)

<p align="center">
  <a href="#-português">🇧🇷 Português</a> •
  <a href="#-english">🇺🇸 English</a>
</p>

---

## 🇧🇷 Português

> Planejamento de versões e funcionalidades do projeto. É um projeto pessoal/pedagógico sem prazos fixos — os itens abaixo estão ordenados por prioridade sugerida, não por data. Itens do backlog são ideias, não compromissos. Qualquer item marcado como decisão de arquitetura ou regra de negócio deve ser confirmado com o usuário antes de ser implementado (ver [`MEMORY.md`](MEMORY.md), seção 8).

**Legenda:** ✅ Concluído · 🔜 Próximo passo sugerido · 💡 Ideia em backlog (não priorizada)

---

### v1.0 — MVP atual ✅ (concluído)

A base funcional do sistema, entregue em 3 etapas nesta sessão:

- ✅ Redesign visual com identidade militar (tema escuro, verde-oliva + dourado).
- ✅ Geração de nomes aleatórios brasileiros, sem repetição entre os vetores.
- ✅ Correção do modelo de efetivo (38 atiradores + 12 comandantes = 50 pessoas reais).
- ✅ Sorteio de 3 tarefas do dia por pessoa escalada.
- ✅ Fluxo de fechamento do dia com registro de falta (quem + observação livre).
- ✅ Relatório do rodízio com resumo de faltas e exportação em `.txt`.
- ✅ `README.md` e `MEMORY.md` bilíngues (PT/EN).

---

### v1.1 — Persistência e robustez 🔜 (próximo passo sugerido)

Hoje **todo o estado é perdido ao fechar o programa** (vetores, ponteiros, histórico do rodízio) — a única forma de guardar algo é exportar o relatório em `.txt` manualmente antes de fechar. Esta é a lacuna mais importante do sistema atual.

- 🔜 **Salvar/carregar estado em arquivo** (ex.: JSON) — vetores, ponteiros e `historico_escalas` persistidos entre execuções.
- 🔜 **Editar/corrigir um dia já registrado** — hoje não há como consertar um erro de digitação numa observação ou numa falta marcada errada, por exemplo.
- 🔜 **Testes automatizados** para as funções de regra de negócio que são lógica pura (sem tkinter): `selecionar_comandante_do_dia`, `selecionar_atirador_ronda`, `gerar_pessoas_aleatorias`, `sortear_tarefas_do_dia`.

---

### v1.2 — Refinamentos de interface e usabilidade

- 💡 Banco de tarefas editável pela própria interface (adicionar/remover tarefas do sorteio, hoje é uma lista fixa no código).
- 💡 Busca/filtro no histórico e no relatório (por nome, por status, por intervalo de dias).
- 💡 Atalhos de teclado para as ações mais usadas (gerar dia, fechar dia).
- 💡 Empacotamento como executável (ex.: PyInstaller), pra rodar sem precisar de Python instalado.

---

### v2.0 — Expansão de escopo

- 💡 Suporte a **múltiplos pelotões/turmas** no mesmo sistema (hoje é um único efetivo fixo).
- 💡 Estatísticas e gráficos (ex.: evolução de faltas ao longo do rodízio, ranking de tarefas mais sorteadas).
- 💡 Exportação em outros formatos (PDF, CSV), além do `.txt` atual.
- 💡 Sorteio de substituto automático em caso de falta, como alternativa **opcional/configurável** ao registro manual atual (a decisão vigente foi manter só o registro livre — ver `MEMORY.md`).

---

### Backlog geral (não priorizado)

- 💡 Definir uma licença para o projeto (hoje não há nenhuma definida).
- 💡 Adicionar screenshots reais da interface ao `README.md`.
- 💡 Internacionalizar a interface do sistema em si (hoje só a documentação é bilíngue; os textos da tela são só em português, propositalmente, já que o público é o TG brasileiro).
- 💡 Alternância entre tema escuro (atual) e um tema claro.

---

## 🇺🇸 English

> Version and feature planning for the project. This is a personal/pedagogical project with no fixed deadlines — the items below are ordered by suggested priority, not by date. Backlog items are ideas, not commitments. Any item that implies an architecture or business-rule decision must be confirmed with the user before implementation (see [`MEMORY.md`](MEMORY.md), section 8).

**Legend:** ✅ Done · 🔜 Suggested next step · 💡 Backlog idea (unprioritized)

---

### v1.0 — Current MVP ✅ (done)

The system's functional baseline, delivered in 3 stages during this session:

- ✅ Visual redesign with a military identity (dark theme, olive-green + gold).
- ✅ Random Brazilian name generation, no repeats across the two rosters.
- ✅ Headcount model fix (38 shooters + 12 commanders = 50 real people).
- ✅ Draw of 3 daily tasks per scheduled person.
- ✅ Day-closing flow with absence recording (who + free-text note).
- ✅ Rotation report with absence summary and `.txt` export.
- ✅ Bilingual (PT/EN) `README.md` and `MEMORY.md`.

---

### v1.1 — Persistence and robustness 🔜 (suggested next step)

Right now **all state is lost when the program closes** (rosters, pointers, rotation history) — the only way to keep anything is to manually export the report to `.txt` before closing. This is the current system's most important gap.

- 🔜 **Save/load state to a file** (e.g. JSON) — rosters, pointers, and `historico_escalas` persisted across runs.
- 🔜 **Edit/fix an already-recorded day** — there's currently no way to correct, say, a typo in a note or a wrongly-checked absence.
- 🔜 **Automated tests** for the business-rule functions that are pure logic (no tkinter): `selecionar_comandante_do_dia`, `selecionar_atirador_ronda`, `gerar_pessoas_aleatorias`, `sortear_tarefas_do_dia`.

---

### v1.2 — UI and usability refinements

- 💡 Task bank editable from the interface itself (add/remove tasks from the draw pool — currently a fixed list in the code).
- 💡 Search/filter in the history and the report (by name, status, or day range).
- 💡 Keyboard shortcuts for the most-used actions (generate day, close day).
- 💡 Packaging as a standalone executable (e.g. PyInstaller), to run without a Python install.

---

### v2.0 — Scope expansion

- 💡 Support for **multiple platoons/classes** in the same system (currently a single fixed headcount).
- 💡 Statistics and charts (e.g. absence trends over the rotation, most-drawn-task ranking).
- 💡 Export to other formats (PDF, CSV), in addition to the current `.txt`.
- 💡 Automatic substitute draw on absence, as an **optional/configurable** alternative to the current manual record (the current decision was to keep only the free-text log — see `MEMORY.md`).

---

### General backlog (unprioritized)

- 💡 Define a license for the project (none is defined today).
- 💡 Add real interface screenshots to `README.md`.
- 💡 Internationalize the system's own interface (today only the documentation is bilingual; on-screen text is Portuguese-only, intentionally, since the audience is the Brazilian TG program).
- 💡 Toggle between the current dark theme and a light theme.
