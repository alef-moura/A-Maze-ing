# Plano: A-Maze-ing (enunciado v2.3 + régua de avaliação)

## 0. O que realmente decide a nota

A régua é eliminatória: qualquer "No" leva a nota a **0**. Os pontos que derrubam mais gente são:

1. **Crash.** Qualquer exceção não tratada durante a defesa dá 0. Isso inclui Ctrl+C, EOF no `input()`, arquivo inexistente e falta de permissão de escrita.
2. **Arquivos obrigatórios na raiz:** `README.md`, `a_maze_ing.py`, `mazegen-*.tar.gz`/`.whl`, um arquivo de config padrão e tudo o que for preciso para refazer o pacote (`pyproject.toml`).
3. **`flake8` e `mypy`** têm que passar sem erros.
4. **O README precisa ter todas as seções exigidas**, incluindo papéis da equipe, planejamento, ferramentas e uso de IA.
5. **Erros de config:** chave faltando, linha sem `=`, letras no lugar de números, booleano inválido e tupla mal formada.
6. **Arquivo de saída:** tem que passar no validador oficial. O caminho gravado no arquivo tem que ser igual ao que aparece na tela.

**Divergências entre os documentos:**
- A régua (de fev/2026) fala em `mazegen.tar.gz` e `output_validator.py`. O enunciado v2.3 fala em `mazegen-*` e `maze_analyzer.py`. Gere os dois formatos (`mazegen-1.0.0.tar.gz` e o `.whl`) e baixe o script de validação na intra.
- O modo `PERFECT=False` com regras de "Pac-Man" (cantos e centro abertos, laços, poucos becos sem saída) só existe no enunciado. Siga o enunciado.

## 1. Estrutura do repositório

```
amazeing/
├── a_maze_ing.py          # ponto de entrada: parse de args → config → gera → grava → UI
├── config.txt             # config padrão (obrigatória)
├── app/                   # NÃO faz parte do pacote reutilizável
│   ├── config.py          # parse + validação → dataclass MazeConfig
│   ├── output.py          # escrita do arquivo hex
│   └── render.py          # ASCII + cores ANSI + menu interativo
├── mazegen/               # pacote pip reutilizável
│   ├── __init__.py        # exporta MazeGenerator
│   ├── generator.py       # classe MazeGenerator
│   ├── pattern.py         # máscara do "42"
│   └── py.typed
├── docs/
│   └── estudo.html        # guia de estudo para iniciantes (ver seção 10)
├── pyproject.toml         # name = "mazegen", version = "1.0.0"
├── mazegen-1.0.0.tar.gz   # artefatos de build, na raiz
├── mazegen-1.0.0-py3-none-any.whl
├── Makefile
├── README.md
├── LICENSE.md             # MIT, que permite reutilizar e redistribuir
├── .gitignore
└── tests/                 # pytest (não é avaliado, mas é muito útil)
```

**Regra de separação:** o `mazegen` não sabe nada sobre o arquivo de config, o terminal ou o formato de saída. Ele só gera, resolve e expõe a estrutura. Isso cumpre o capítulo VI e ajuda nas modificações pedidas durante a defesa.

## 2. O núcleo: `MazeGenerator`

**Representação:** `grid[y][x]` é um `int` de 0 a 15, com os bits N=1, E=2, S=4, W=8 (bit ligado quer dizer parede fechada). O formato de saída fica direto: `format(cell, "X")`. A convenção de coordenadas é `x` = coluna e `y` = linha, então `ENTRY=0,0` é o canto superior esquerdo.

**Primitiva central:** `_open_wall(x, y, dir)` abre a parede na célula atual **e** a parede oposta na vizinha. Assim a coerência exigida pelo validador é garantida por construção.

**API pública (sugestão):**
```python
gen = MazeGenerator(width=20, height=15, entry=(0, 0), exit=(19, 14),
                    perfect=True, seed=42)
gen.generate()
gen.grid            # list[list[int]]
gen.pattern_cells   # set[tuple[int, int]] (células do "42")
gen.solve()         # str "EESSN..." (caminho mais curto, BFS)
gen.solve_cells()   # list[tuple[int, int]] (para a renderização)
```

**Etapas do `generate()`:**
1. `random.Random(seed)` como instância própria, nunca o `random` global. Isso garante que a mesma seed gere o mesmo labirinto.
2. Começar com todas as células fechadas (`0xF`).
3. **Colocar o "42".** São dois dígitos de 3×5 com 1 coluna de espaço, ou seja, um bloco de 7×5, centralizado. Essas células ficam `0xF` e marcadas como visitadas antes do algoritmo rodar. Se o labirinto for pequeno demais (sugestão: menos de 9×7, para deixar margem), não desenhe o padrão e imprima um aviso no console, como o enunciado pede. **Cuidado:** no modo não-perfeito o centro precisa ser corredor aberto. Desloque o "42" para que a célula central caia fora dele (o espaço entre o 4 e o 2 resolve).
4. **Labirinto perfeito:** Recursive Backtracker (DFS) **iterativo, com pilha explícita**. A versão recursiva estoura o limite de recursão em labirintos grandes, e isso conta como crash. O resultado é uma árvore geradora, portanto existe exatamente um caminho e não há área aberta de 3×3, porque qualquer área assim conteria um ciclo.
5. **Modo não-perfeito (padrão):** gerar o labirinto perfeito e depois **trançar** (braiding). Para cada beco sem saída, abrir uma parede em direção a uma vizinha válida (de preferência outro beco), **somente se isso não criar uma área aberta de 3×3**. Basta checar as janelas 3×3 que contêm a parede alterada. O objetivo é chegar a zero becos, o que vale o bônus; se sobrar algum, que sejam pouquíssimos. Isso cria laços naturalmente, mas confirme que o número de ciclos independentes é ≥ 2 (arestas − células + 1).
6. As bordas externas nunca são abertas, nem na entrada nem na saída.

**Solução:** BFS a partir da entrada, reconstruindo o caminho pelos pais e convertendo em letras N/E/S/W.

**Por que DFS + braiding (isso vai para o README):** é simples de explicar na defesa, o labirinto perfeito sai como árvore por construção e o braiding cuida do modo Pac-Man sem precisar de um segundo algoritmo. Prim ou Kruskal podem entrar depois como bônus ("múltiplos algoritmos", via chave `ALGORITHM=`).

## 3. Config (`app/config.py`)

- Ler com `with open(...)` e capturar `OSError`/`UnicodeDecodeError`. Ignorar linhas vazias e linhas que começam com `#`.
- Usar `split("=", 1)`. Linha sem `=` é erro com número da linha. Chaves são normalizadas com `.upper().strip()` (minúsculas são aceitas).
- **Chaves obrigatórias:** WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT. **Opcionais:** SEED, ALGORITHM e outras.
- **Validações:**
  - **WIDTH/HEIGHT:** `int` > 0, com um teto razoável (ex.: 200).
  - **ENTRY/EXIT:** exatamente dois inteiros separados por `,`, dentro dos limites, diferentes entre si e fora das células do "42".
  - **PERFECT:** aceitar `true`/`false` sem diferenciar maiúsculas; qualquer outro valor é erro.
  - Chave duplicada ou desconhecida: decidir entre aviso e erro, e documentar.
- Cada erro vira uma exceção própria (`ConfigError`). O `main` mostra uma mensagem clara e encerra com `sys.exit(1)`, sem traceback.
- Se não houver SEED, sortear uma e **imprimi-la**, para que o labirinto possa ser reproduzido.

## 4. Saída (`app/output.py`)

```
<HEIGHT linhas de WIDTH dígitos hex>
<linha vazia>
x,y        ← entrada
x,y        ← saída
EESSWN...  ← caminho mais curto
```
Toda linha termina em `\n`. Grave o **primeiro** labirinto gerado, já que a régua confere que ele é o mesmo que aparece na tela. Decida e documente se as regenerações também sobrescrevem o arquivo.

## 5. Visualização e interação (`app/render.py`)

Recomendo **ASCII com cores ANSI**. É menos dependência, mais fácil de depurar e não tem o risco de o MLX não instalar no Mac ou na máquina do avaliador.
- Cada célula ocupa um bloco de caracteres, com paredes desenhadas em `█` ou `+--+`.
- Entrada, saída, caminho e "42" ficam em cores diferentes.
- **Menu com `input()`:** 1) regenerar · 2) mostrar/ocultar caminho · 3) trocar cor das paredes · 4) cor do "42" (opcional) · q) sair.
- Envolver o loop em `try/except (KeyboardInterrupt, EOFError)` para sair limpo.

## 6. Pacote, Makefile e qualidade

**`pyproject.toml`:** usar o backend setuptools e incluir apenas `mazegen` (`[tool.setuptools] packages = ["mazegen"]`). O `README` do pacote traz a mini-documentação de uso.

**Regras do Makefile:**

| Regra | Comando |
|---|---|
| `install` | `pip install -r requirements.txt` (flake8, mypy, build, pytest) |
| `run` | `python3 a_maze_ing.py config.txt` |
| `debug` | `python3 -m pdb a_maze_ing.py config.txt` |
| `clean` | remover `__pycache__`, `.mypy_cache`, `build/`, `dist/`, `*.egg-info` |
| `lint` | `flake8 .` + `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs` |
| `lint-strict` | `flake8 .` + `mypy . --strict` |
| `build` (extra) | `python -m build` e depois copiar `dist/mazegen-*` para a raiz |

Configure o `flake8` para excluir `.venv` e `build` (em `setup.cfg` ou `.flake8`). Todas as funções precisam de type hints e docstrings (Google style).

## 7. Testes (pytest)

- **Coerência das paredes:** para toda célula e vizinha, os bits das paredes compartilhadas batem. A borda é sempre fechada.
- **Conectividade:** um BFS alcança todas as células que não são do "42".
- **Perfeito:** número de passagens abertas = células alcançáveis − 1.
- **Não-perfeito:** ≥ 2 ciclos, cantos e centro abertos, quantidade de becos sem saída (de preferência 0).
- **Áreas abertas:** nenhuma janela 3×3 totalmente aberta.
- **Seed:** a mesma seed gera um `grid` idêntico.
- **Config:** um teste para cada caso de erro da régua.
- Validar com o script oficial em lote: várias seeds × tamanhos × os dois modos.

## 8. Ordem de execução

| Fase | Entrega | Critério de pronto |
|---|---|---|
| 1 | Esqueleto, `.gitignore`, Makefile, `pyproject.toml`, venv | `make lint` passa num projeto vazio |
| 2 | Parser de config e erros | todos os casos da régua dão mensagem, nenhum dá traceback |
| 3 | `MazeGenerator` no modo perfeito, BFS e escrita do arquivo | o validador oficial aprova |
| 4 | Padrão "42" e aviso para labirinto pequeno | os testes de conectividade passam |
| 5 | Modo não-perfeito com braiding e checagem de 3×3 | o validador reporta um tabuleiro jogável |
| 6 | Renderização ASCII e menu | as 3 interações obrigatórias funcionam, Ctrl+C sai limpo |
| 7 | Build do pacote e teste num venv limpo | `pip install mazegen-*.whl` funciona num venv novo |
| 8 | README e LICENSE | checklist da régua seção por seção |
| 9 | Bônus | zero becos sem saída → múltiplos algoritmos → animação |
| 9.5 | Revisão final do guia de estudo (`docs/estudo.html`) | uma pessoa leiga consegue ler os módulos 1–4 sem ajuda, e todo trecho do código aparece em algum conceito |
| 10 | Ensaio da defesa, usando o guia como roteiro de perguntas | simular a régua do zero num `git clone` vazio, e cada integrante responde aos "testes rápidos" sem consultar |

**Em todas as fases de 1 a 8:** acrescentar ao `docs/estudo.html` os conceitos que a fase introduziu, com exemplos do código real.

## 9. Preparação para a defesa

A defesa pode pedir uma modificação rápida, então todos precisam saber explicar:
- o DFS iterativo;
- o braiding e a checagem de 3×3;
- o BFS;
- a codificação em bits.

Exemplos prováveis do que pode ser pedido: trocar o caractere da parede, adicionar uma chave de config ou mudar a cor do caminho.

**Duas decisões que dependem da equipe:**
- **MLX ou ASCII:** recomendo ASCII.
- **Licença:** recomendo MIT.

## 10. Guia de estudo: `docs/estudo.html`

**Objetivo:** um único arquivo HTML que funciona offline (abre com duplo clique, sem internet). Ele explica cada conceito usado no projeto para quem nunca programou e está vendo Python pela primeira vez. Também serve para a preparação da defesa, porque cada pessoa da equipe precisa saber explicar o código.

### Formato de cada conceito

1. **Em uma frase:** o que é, sem jargão.
2. **Analogia do dia a dia:** por exemplo, "uma variável é uma etiqueta colada numa caixa".
3. **Exemplo mínimo em Python:** de 3 a 6 linhas, com comentário em cada linha e a saída esperada.
4. **Onde aparece no projeto:** arquivo e função, por exemplo `mazegen/generator.py → _open_wall`.
5. **Erro comum:** o que costuma dar errado e como reconhecer.
6. **Teste rápido:** uma pergunta com a resposta escondida (`<details>`).

### Trilha de conceitos (na ordem de leitura)

| Módulo | Conceitos |
|---|---|
| **1. Antes do código** | O que é um programa · terminal e comandos · o interpretador Python · rodar `python3 arquivo.py` · o que são arquivos e pastas |
| **2. Python básico** | Variáveis · tipos (`int`, `str`, `bool`, `None`) · operadores · `print` e f-strings · `if/elif/else` · `for`, `while`, `range` · indentação |
| **3. Coleções** | Listas · lista de listas (a grade do labirinto) · tuplas (coordenadas `(x, y)`) · dicionários (a config) · conjuntos (as células do "42") · `deque` (fila) |
| **4. Organizando código** | Funções, parâmetros e `return` · módulos e `import` · `if __name__ == "__main__"` · `sys.argv` · `sys.exit` |
| **5. Objetos** | Classe × objeto (planta × casa) · `__init__` e `self` · métodos · atributos · `@dataclass` · o que é "privado" (`_nome`) |
| **6. Quando algo dá errado** | Exceções · `try/except` · exceções próprias (`ConfigError`) · arquivos com `with` (context manager) · por que um crash zera a nota |
| **7. Código de qualidade** | Type hints · `mypy` · docstrings (PEP 257) · `flake8` e PEP 8 · testes com `pytest` |
| **8. Números por dentro** | Binário · hexadecimal · bits como interruptores · operadores `&`, `\|`, `~`, `<<` · como `0xA` significa "paredes leste e oeste" |
| **9. Labirinto como grafo** | Grade e coordenadas (por que `y` é a linha) · vizinhos · grafo, nó e aresta · árvore · ciclo · árvore geradora = labirinto perfeito |
| **10. Algoritmos** | Aleatoriedade e seed · pilha × fila · recursão e o limite de recursão · DFS (backtracker) · BFS (caminho mais curto) · beco sem saída · braiding · checagem de área 3×3 |
| **11. Interface** | `input()` e loop de menu · códigos de cor ANSI · Ctrl+C (`KeyboardInterrupt`) e `EOFError` |
| **12. Ferramentas do ecossistema** | Git e `.gitignore` · ambiente virtual (venv) · `pip` · pacote, `pyproject.toml`, `.whl` e `.tar.gz` · Makefile · licença de software (MIT) |
| **Glossário** | Todos os termos em ordem alfabética, cada um com link para a seção que o explica |

### Recursos interativos (JavaScript simples, sem dependências)

- **Decodificador de célula:** quatro botões (N/E/S/W) liga/desliga mostram a célula desenhada, o valor binário e o hexadecimal.
- **Animação passo a passo do DFS** numa grade 6×6, com botões "próximo passo", "play" e a pilha visível ao lado.
- **Animação do BFS** no mesmo labirinto, mostrando a fila e a "onda" se espalhando até a saída.
- **Antes e depois do braiding:** os becos sem saída são destacados e depois removidos.
- **Seed:** mesma seed gera o mesmo labirinto, seed diferente gera outro.

### Requisitos do arquivo

- Escrito em português e autocontido: CSS e JS inline, nenhum CDN.
- Menu lateral com a trilha e marcação de "lido" (via `localStorage`, só como conveniência).
- Modo claro e escuro, e legível no celular.
- Blocos de código com destaque de sintaxe feito à mão (classes CSS simples).
- Fica fora do pacote `mazegen` e não interfere no `flake8`/`mypy`. Vale mencionar no README, na seção "Resources".
