# Poker Vision Lab

Um assistente estratégico de poker Texas Hold'em em formato PWA (Progressive Web App), projetado com uma interface mobile-first e um backend Python robusto para cálculo de equity em tempo real.

![Poker Vision Lab Screenshot](https://i.imgur.com/your-screenshot-url.png) <!-- Adicione um screenshot aqui depois -->

## Principais Funcionalidades

- **Interface Visual Mobile-First:** Abandona campos de texto em favor de um seletor de cartas 100% visual e tátil, ideal para uso rápido em dispositivos móveis.
- **Cálculo de Equity (Monte Carlo):** A aplicação calcula a probabilidade estatística de vitória ("Equity") contra um número configurável de oponentes, rodando uma simulação Monte Carlo no backend para não sobrecarregar o dispositivo do usuário.
- **Sugestões Estratégicas:** Com base na equity e em regras de pré-flop, o sistema oferece uma sugestão de aposta direta (Ex: "Fortíssimo (Aumentar/Raise)", "Cuidado (Check/Fold)").
- **Análise Pré-Flop (Fórmula de Chen):** Utiliza a Fórmula de Chen para dar uma avaliação numérica instantânea da força da mão inicial, permitindo decisões rápidas nas primeiras rodadas.
- **Arquitetura Cliente-Servidor:** Toda a lógica pesada é processada por um servidor Python (Flask), garantindo que a interface do usuário permaneça leve, rápida e responsiva.

## Como Executar Localmente

**Pré-requisitos:**
- Python 3.x
- `pip` e `venv`

**1. Clone o Repositório:**
```bash
git clone https://github.com/lucas-andrade-barbosa/poker-vision-lab.git
cd poker-vision-lab
```

**2. Configure o Backend (Ambiente Virtual):**
```bash
# Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

**3. Inicie o Servidor:**
```bash
python app.py
```

**4. Acesse a Aplicação:**
Abra seu navegador e acesse `http://127.0.0.1:8080`.

## Arquitetura

- **Frontend:** HTML5, CSS3, JavaScript puro. Responsável pela renderização da interface, captura das interações do usuário e comunicação com a API.
- **Backend:** Python com o micro-framework Flask. Responsável por servir os arquivos do frontend e expor a API de cálculo.
- **API:** Um único endpoint (`/api/evaluate`) que recebe a mão do jogador, as cartas da mesa e o número de jogadores, retornando um JSON com a análise completa (equity, força da mão, sugestão).
- **Lógica de Poker:** Utiliza a biblioteca `deuces` para uma avaliação de mãos de alta performance, essencial para as simulações.

## Limitações Atuais e Roadmap Futuro

- **Range de Oponentes:** A simulação assume que os oponentes podem ter quaisquer duas cartas (range 100% aleatório), o que não reflete um jogo real onde os ranges são mais restritos.
- **Falta de Contexto:** As sugestões não consideram fatores cruciais como posição na mesa, tamanho do pote (pot odds) ou o stack dos jogadores.

O próximo passo natural para o projeto é evoluir a inteligência do backend para considerar essas variáveis, tornando as sugestões ainda mais precisas e contextuais.
