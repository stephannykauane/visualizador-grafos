# 🎨 Visualizador de Grafos BEEEM Rosa da Stephanny (e do Eduardo)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Dash](https://img.shields.io/badge/Dash-2.14.0-pink.svg)](https://dash.plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Um visualizador de grafos interativo, educativo e MUITO rosa 💖 desenvolvido com foco no aprendizado visual de algoritmos clássicos de grafos.

O projeto permite criar, editar e visualizar grafos dinamicamente, acompanhando passo a passo a execução interna dos algoritmos através de animações, estados visuais e explicações pedagógicas detalhadas.

---

# ✨ Funcionalidades

## 🧩 Manipulação de Grafos

- Criação de vértices por clique
- Conexão interativa entre vértices
- Suporte a grafos:
  - direcionados
  - não direcionados
- Suporte a grafos:
  - ponderados
  - não ponderados
- Edição de pesos das arestas
- Remoção de vértices e arestas
- Importação de grafos
- Exportação de grafos
- Persistência de posições dos vértices
- Interface totalmente interativa

---

# 🔍 Algoritmos Implementados

## ✅ BFS — Busca em Largura

- Execução passo a passo
- Visualização da fila
- Rastreamento de vértices descobertos
- Rastreamento de vértices visitados
- Destaque de arestas percorridas
- Exploração por níveis

---

## ✅ DFS — Busca em Profundidade

- Execução passo a passo
- Visualização da pilha
- Rastreamento de vértices descobertos
- Rastreamento de vértices finalizados
- Exploração em profundidade
- Visualização da recursão de forma iterativa

---

## 🆕 Fluxo Máximo — Ford-Fulkerson com Edmonds-Karp

Implementação pedagógica completa do problema de fluxo máximo.

O algoritmo utiliza:

- Ford-Fulkerson como estratégia geral
- Edmonds-Karp para encontrar caminhos aumentantes usando BFS

A implementação demonstra visualmente:

- BFS sobre o grafo residual
- Caminhos aumentantes
- Capacidades residuais
- Gargalo (bottleneck)
- Atualização de fluxo
- Arestas reversas
- Saturação de arestas
- Fluxo máximo acumulado

---

# 🧠 Arquitetura Pedagógica

A aplicação utiliza um sistema baseado em estados ("steps") para representar cada operação executada pelos algoritmos.

Cada etapa armazena informações completas sobre:

- nó atual
- vizinho analisado
- fila/pilha
- vértices visitados
- vértices descobertos
- vértices finalizados
- arestas percorridas
- capacidades residuais
- caminhos aumentantes
- gargalos
- atualizações de fluxo
- fluxo máximo acumulado

Isso permite:

- execução passo a passo
- replay completo dos algoritmos
- animações educativas
- inspeção visual do estado interno
- acompanhamento detalhado da execução

---

# 🎨 Sistema Visual Dinâmico

O projeto utiliza classes dinâmicas no Cytoscape para representar visualmente o estado dos algoritmos em tempo real.

## Estados visuais implementados

### BFS / DFS

| Cor | Significado |
|---|---|
| 🟡 Amarelo | Nó atual |
| ⚫ Preto | Visitado |
| ⚪ Cinza | Descoberto |
| 🟣 Roxo | Aresta percorrida |
| 🟨 Dourado | Aresta ativa |

---

### Fluxo Máximo

| Cor | Significado |
|---|---|
| 🟢 Verde | Fonte |
| 🔴 Vermelho | Sorvedouro |
| 🟡 Dourado | Caminho aumentante |
| 🔵 Azul | Aresta residual |
| ⚫ Escuro | Aresta saturada |
| 🌫️ Desbotado | Elementos inativos |

---

# 📊 Painel Pedagógico Interativo

Durante a execução dos algoritmos, o sistema exibe:

- fila da BFS
- pilha da DFS
- mapa de pais da BFS
- capacidades residuais
- gargalo encontrado
- atualizações de fluxo
- fluxo máximo acumulado
- estado atual das arestas
- mensagens explicativas automáticas

Cada fase do algoritmo possui explicações textuais detalhadas.

---

# 🔬 Fluxo Máximo — Funcionamento

A implementação do Ford-Fulkerson utiliza Edmonds-Karp com BFS sobre o grafo residual.

O sistema demonstra visualmente:

1. exploração da BFS residual
2. verificação das capacidades residuais
3. descoberta do caminho aumentante
4. reconstrução do caminho usando o mapa de pais
5. cálculo do gargalo
6. envio de fluxo
7. atualização das arestas reversas
8. saturação de arestas
9. cálculo incremental do fluxo máximo

---

# ⚙️ Recursos Técnicos

- Python
- Dash
- Dash Cytoscape
- HTML/CSS
- Sistema de callbacks reativos
- Sistema de estados para animações
- Renderização dinâmica de classes CSS
- Controle automático/manual da execução
- Atualização visual em tempo real

---

# 🚀 Como Executar

## 📋 Pré-requisitos

- Python 3.8+
- pip

---

# 📥 Instalação

Clone o repositório:

```bash
git clone https://github.com/seu-usuario/visualizador-grafos.git
```

Entre na pasta:

```bash
cd visualizador-grafos
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

# ▶️ Executando o Projeto

```bash
python app.py
```

Abra no navegador:

```bash
http://127.0.0.1:8050/
```

---

# ⌨️ Atalhos de Teclado

| Tecla | Ação |
|---|---|
| `V` | Criar vértice |
| `Backspace` | Remover elemento selecionado |

---

# 📂 Estrutura do Projeto

```bash
visualizador-grafos/
│
├── app.py
├── requirements.txt
│
├── algorithms/
│   └── algorithms.py
│
├── callbacks/
├── components/
├── data/
├── assets/
│
└── README.md
```

---

# 💖 Objetivo do Projeto

O principal objetivo deste projeto é transformar algoritmos abstratos em processos visuais e intuitivos.

Em vez de mostrar apenas o resultado final, a aplicação demonstra:

- estado interno dos algoritmos
- estruturas auxiliares
- decisões tomadas durante a execução
- propagação do fluxo
- atualização do grafo residual
- funcionamento das arestas reversas

O foco principal é auxiliar estudantes no aprendizado de algoritmos de grafos de forma visual, interativa e acessível.

---

# 👩‍💻 Autores

Desenvolvido por:

- Stephanny
- Eduardo

---

# 📄 Licença

Este projeto está sob a licença MIT.