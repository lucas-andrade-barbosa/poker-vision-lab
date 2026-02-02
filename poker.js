let currentEditingSlot = null;
let selectedCard = { rank: null, suit: null, rankDisplay: null, suitDisplay: null };

const ranks = ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2'];
const rankSolverMap = { 'A': 'A', 'K': 'K', 'Q': 'Q', 'J': 'J', '10': 'T' };

// --- Setup Dinâmico dos Botões ---
document.addEventListener('DOMContentLoaded', () => {
    const rankSelector = document.getElementById('rank-selector');
    ranks.forEach(rank => {
        const button = document.createElement('button');
        button.textContent = rank;
        // Corrigido: Passando 'this' para a função de seleção
        button.onclick = () => selectRank(rank, button);
        rankSelector.appendChild(button);
    });
});

// --- Lógica do Modal ---
function openCardSelector(slotId) {
    const slot = document.getElementById(slotId);
    if (slot.dataset.value) {
        slot.innerHTML = '+';
        delete slot.dataset.value;
        return;
    }
    currentEditingSlot = slotId;
    // Limpa a seleção visual anterior ao abrir o modal
    document.querySelectorAll('#suit-selector button, #rank-selector button').forEach(btn => btn.classList.remove('selected'));
    document.getElementById('card-selector-modal').style.display = 'flex';
}

function closeCardSelector() {
    document.getElementById('card-selector-modal').style.display = 'none';
    currentEditingSlot = null;
    selectedCard = { rank: null, suit: null, rankDisplay: null, suitDisplay: null };
}

function selectSuit(suit, suitSymbol, buttonElement) {
    // Gerencia a classe .selected nos naipes
    document.querySelectorAll('#suit-selector button').forEach(btn => btn.classList.remove('selected'));
    if (buttonElement) buttonElement.classList.add('selected');

    selectedCard.suit = suit;
    selectedCard.suitDisplay = suitSymbol;
    if (selectedCard.rank) setCard();
}

function selectRank(rank, buttonElement) {
    // Gerencia a classe .selected nos valores
    document.querySelectorAll('#rank-selector button').forEach(btn => btn.classList.remove('selected'));
    if (buttonElement) buttonElement.classList.add('selected');

    selectedCard.rankDisplay = rank;
    selectedCard.rank = rankSolverMap[rank] || rank; // Converte '10' para 'T' internamente
    if (selectedCard.suit) setCard();
}

function setCard() {
    if (!currentEditingSlot || !selectedCard.rank || !selectedCard.suit) return;
    const slot = document.getElementById(currentEditingSlot);
    const suitClass = `suit-${selectedCard.suit}`;
    slot.innerHTML = `<span class="rank ${suitClass}">${selectedCard.rankDisplay}</span><span class="suit ${suitClass}">${selectedCard.suitDisplay}</span>`;
    slot.dataset.value = selectedCard.rank + selectedCard.suit;
    closeCardSelector();
}

// --- Lógica de Avaliação (Comunicação com Backend) ---
async function evaluateHand() {
    const handResultDiv = document.getElementById('hand-result');
    const equityResultDiv = document.getElementById('equity-result');
    const suggestionResultDiv = document.getElementById('suggestion-result');
    const evaluateBtn = document.getElementById('evaluate-btn');

    handResultDiv.innerHTML = '';
    equityResultDiv.innerHTML = 'Calculando...';
    suggestionResultDiv.innerHTML = '';
    evaluateBtn.disabled = true;

    const myHand = [document.getElementById('hand1').dataset.value, document.getElementById('hand2').dataset.value].filter(c => c);
    const boardCards = [
        document.getElementById('board1').dataset.value, document.getElementById('board2').dataset.value,
        document.getElementById('board3').dataset.value, document.getElementById('board4').dataset.value,
        document.getElementById('board5').dataset.value
    ].filter(c => c);
    const numPlayers = parseInt(document.getElementById('num-opponents').value, 10) + 1;

    if (myHand.length !== 2) {
        equityResultDiv.textContent = 'Selecione as 2 cartas da sua mão.';
        evaluateBtn.disabled = false;
        return;
    }

    try {
        const response = await fetch('/api/evaluate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ my_hand: myHand, board: boardCards, players: numPlayers }),
        });

        const data = await response.json();

        if (!response.ok || !data.ok) {
            // Exibe o erro vindo do backend com "airbag"
            throw new Error(data.error || 'Erro desconhecido no servidor.');
        }

        // Normalização da resposta para compatibilidade
        const r = data.result ?? data;

        const equityText = (typeof r.equity === 'number') ? `${Number(r.equity).toFixed(2)}%` : "—";

        // Renderização segura com fallback para "—"
        handResultDiv.innerHTML = `Força da Mão: <span class="hand-name">${r.hand_strength ?? "—"}</span>`;
        equityResultDiv.textContent = `Sua Chance de Vitória (Equity): ${equityText}`;
        suggestionResultDiv.textContent = `Sugestão Estratégica: ${r.suggestion ?? "—"}`;

    } catch (error) {
        handResultDiv.textContent = '';
        equityResultDiv.textContent = 'Erro ao avaliar a mão.';
        suggestionResultDiv.textContent = error.message;
        console.error('Fetch error:', error);
    } finally {
        evaluateBtn.disabled = false;
    }
}
