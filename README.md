# 🎨 Visualizador de Grafos Rosa

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Dash](https://img.shields.io/badge/Dash-2.14.0-pink.svg)](https://dash.plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Um visualizador de grafos interativo e estiloso com foco em algoritmos de busca (BFS e DFS). Desenvolvido com Dash e Cytoscape, este projeto permite criar, editar e visualizar grafos de forma intuitiva, com cores vibrantes e animações passo a passo dos algoritmos.

## ✨ Funcionalidades

- **Criação de Grafos**: Adicione vértices clicando na área de trabalho ou usando o botão "V"
- **Conexões**: Conecte vértices clicando em dois vértices sequencialmente ou usando o formulário
- **Orientação**: Suporte a grafos direcionados e não direcionados
- **Peso nas Arestas**: Adicione e edite pesos nas conexões
- **Algoritmos de Busca**: Execute BFS (Busca em Largura) e DFS (Busca em Profundidade)
- **Visualização Passo a Passo**: Controle manual da execução dos algoritmos
- **Auto Execução**: Execute todo o algoritmo automaticamente
- **Import/Export**: Salve e carregue grafos em formato texto
- **Atalhos de Teclado**: 
  - `V`: Adicionar novo vértice
  - `Backspace`: Deletar elemento selecionado

## 🎨 Cores e Estilo

- Tema rosa característico com gradientes suaves
- Destaques visuais para vértices durante a execução dos algoritmos:
  - 🟡 **Amarelo**: Vértice atual
  - 🔵 **Azul**: Vértices já visitados
  - 🟢 **Verde**: Vértices na fila/pilha
  - 💗 **Rosa**: Vértices não visitados

## 🚀 Como Executar

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/visualizador-grafos.git
cd visualizador-grafos