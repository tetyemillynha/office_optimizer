
# Tech Challenge – Otimização de Layout de Escritório com Algoritmo Genético

## 📌 Descrição do Problema

Este projeto tem como objetivo aplicar um **Algoritmo Genético (GA)** para resolver o problema de **layout de um escritório**, otimizando a posição de mesas dentro de uma planta com restrições físicas, como paredes e banheiro, e regras de espaçamento.

A solução visa evitar sobreposições entre elementos móveis, respeitar áreas fixas e distribuir as mesas de forma eficiente dentro do ambiente de trabalho.

## 🧠 Problema

Dado um escritório com:
- Tamanho fixo (60x40 unidades);
- Elementos fixos (paredes, banheiro, porta do banheiro);
- Mesas móveis com dimensões variadas (10x3 ou 20x3);
- Restrições como:
  - Nenhuma sobreposição entre mesas;
  - Distância mínima entre os elementos;
  - Proibição de invadir áreas fixas;

## 🎯 Objetivo

Organizar automaticamente as mesas móveis dentro de um escritório de 60x40 unidades:
- **Evitar sobreposição** com paredes, banheiro ou entre mesas;
- **Manter espaço para cadeiras** ao redor das mesas;
- **Maximizar o aproveitamento do espaço** e manter distância adequada entre mesas;
- **Gerar uma solução otimizada** de forma automática, simulando gerações de evolução com um algoritmo genético.

## 🧬 Algoritmo Genético

O algoritmo segue os seguintes passos:

1. **Inicialização:** gera uma população de layouts aleatórios;
2. **Avaliação:** cada layout recebe um valor de fitness com base em colisões, densidade, centralidade e capacidade de cadeiras;
3. **Seleção:** usa torneio para selecionar os melhores indivíduos;
4. **Crossover:** combina partes de dois layouts para gerar novos;
5. **Mutação:** altera mesas de forma controlada (posição e rotação);
6. **Parada:** ocorre após alcançar fitness ideal, número máximo de gerações ou estagnação.

## 🏗️ Estrutura do Código

- `OfficeLayoutVisualizer`: classe principal que executa o algoritmo e visualiza o resultado;
- `create_individual`: gera um novo layout aleatório;
- `is_valid_position`: valida se uma mesa pode ser posicionada em determinada área;
- `fitness`: calcula a pontuação do layout;
- `selection`, `crossover`, `mutate`: operadores genéticos;
- `draw`: exibe o layout na tela com cores diferentes para áreas válidas/colididas;
- `run`: executa o loop principal, processando eventos e gerando novas gerações.

## 📐 Restrições Consideradas

- Colisão com:
  - Paredes,
  - Banheiro,
  - Outras mesas.
- Espaço de cadeiras: 1.5 unidades acima/abaixo da mesa.
- Penalidades no fitness para colisões e má distribuição.

## 🎮 Controles

- `Espaço`: Pausar/continuar execução
- `R`: Reiniciar simulação
- `I`: Mostrar/ocultar painel
- `ESC`: Sair

## 🖼️ Visualização

- Verde: Mesa posicionada corretamente
- Vermelho: Mesa em posição inválida
- Azul: Banheiro
- Cinza: Área restrita (paredes)

## 📂 Como Executar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## ⚙️ Como rodar o projeto localmente
```bash
python main.py
```