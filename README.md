
# Tech Challenge – Otimização de Layout de Escritório com Algoritmo Genético

## 📌 Descrição do Problema

Este projeto resolve o problema de planejamento espacial em ambientes de escritório. O objetivo é alocar mesas de diferentes tamanhos dentro de uma planta realista (60x40 unidades), respeitando restrições físicas (paredes, banheiro) e operacionais (espaço para circulação e cadeiras), de forma a otimizar a ocupação e distribuição.

## 🧠 Abordagem Utilizada

- Implementação de um **algoritmo genético** para gerar layouts válidos e otimizados.
- Leitura da planta e elementos fixos via `planta_config_realista.json`.
- Mesas são móveis e posicionadas respeitando margens mínimas.
- A **função de fitness** penaliza colisões e favorece layouts bem distribuídos.
- Crossover e mutação preservam elementos fixos e respeitam regras.
- Visualização via Matplotlib com renderização da planta final.

## 🧪 Resultados

- O algoritmo encontra soluções viáveis em poucas gerações.
- Layouts são visualmente compreensíveis e respeitam todas as restrições.
- Convergência do fitness demonstrada graficamente.

## 📚 Conclusão

- Abordagem aplicável a qualquer cenário de space planning realista.
- Estrutura de código modular e expansível.
- Pode ser adaptado para incluir mais restrições (ex: iluminação, janelas, equipes).

## 🔗 Links
- 🎥 **Vídeo explicativo:** [](#)


```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## ⚙️ Como rodar o projeto localmente
uvicorn app.main:app --reload