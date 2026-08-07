// frontend/src/components/Game/CardDisplay.js
import React from 'react';
import './CardDisplay.css';

const CardDisplay = ({ card, onClose }) => {
  if (!card) return null;

  // ✅ Use card type directly
  const getEmoji = (type) => {
    const emojis = {
      'COLLECT_MONEY': '💰',
      'PAY_MONEY': '💸',
      'ADVANCE_TO_GO': '🏃',
      'GO_TO_JAIL': '🔒',
      'GET_OUT_OF_JAIL': '🆓',
      'COLLECT_FROM_ALL': '🎁',
      'STREET_REPAIRS': '🔧',
    };
    return emojis[type] || '📬';
  };

  const getCardColor = (type) => {
    const colors = {
      'COLLECT_MONEY': '#4caf50',
      'PAY_MONEY': '#f44336',
      'ADVANCE_TO_GO': '#2196f3',
      'GO_TO_JAIL': '#ff9800',
      'GET_OUT_OF_JAIL': '#9c27b0',
      'COLLECT_FROM_ALL': '#00bcd4',
      'STREET_REPAIRS': '#ff5722',
    };
    return colors[type] || '#607d8b';
  };

  const getTypeLabel = (type) => {
    const labels = {
      'COLLECT_MONEY': '💰 Collect Money',
      'PAY_MONEY': '💸 Pay Money',
      'ADVANCE_TO_GO': '🏃 Advance to GO',
      'GO_TO_JAIL': '🔒 Go to Jail',
      'GET_OUT_OF_JAIL': '🆓 Get Out of Jail',
      'COLLECT_FROM_ALL': '🎁 Collect from All',
      'STREET_REPAIRS': '🔧 Street Repairs',
    };
    return labels[type] || type;
  };

  return (
    <div className="card-overlay" onClick={onClose}>
      <div className="card-modal" style={{ borderColor: getCardColor(card.type) }}>
        <div className="card-header" style={{ background: getCardColor(card.type) }}>
          <div className="card-type-badge">{getTypeLabel(card.type)}</div>
        </div>
        <div className="card-body">
          <p className="card-description">{card.description}</p>
          {card.amount > 0 && (
            <p className={`card-amount ${card.type === 'PAY_MONEY' ? 'negative' : 'positive'}`}>
              {card.type === 'PAY_MONEY' ? '-' : '+'} ${card.amount}
            </p>
          )}
        </div>
        <div className="card-footer">
          <button className="card-footer-button" onClick={onClose}>Got it!</button>
        </div>
      </div>
    </div>
  );
};

export default CardDisplay;
