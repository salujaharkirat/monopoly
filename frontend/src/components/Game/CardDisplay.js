// frontend/src/components/Game/CardDisplay.js
import React, { useEffect, useState } from 'react';
import { CARD_METADATA, CARD_TYPES } from '../../constants/cardTypes';
import './CardDisplay.css';

const CardDisplay = ({ card, onClose, drawnBy }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Trigger entrance animation
    setTimeout(() => setIsVisible(true), 50);
  }, []);

  if (!card) return null;

  // Determine if it's a Chance or Community Chest card
  const isChance = card.type === 'CHANCE' || card.deck === 'chance';
  const isCommunityChest = card.type === 'COMMUNITY_CHEST' || card.deck === 'community_chest';

  // Get card metadata
  const cardType = card.card_type || card.type;
  const metadata = CARD_METADATA[cardType] || {
    emoji: '📬',
    color: '#607d8b',
    label: cardType || 'Unknown',
    isPositive: false,
  };

  const getAmountDisplay = () => {
    if (!card.amount || card.amount === 0) return null;
    const sign = metadata.isPositive ? '+' : '-';
    const className = metadata.isPositive ? 'amount-positive' : 'amount-negative';
    return (
      <div className={`card-amount ${className}`}>
        {sign} ${card.amount}
      </div>
    );
  };

  const getTypeIcon = () => {
    if (isChance) return '🎴';
    if (isCommunityChest) return '📬';
    return metadata.emoji || '📬';
  };

  const getCardTypeLabel = () => {
    if (isChance) return '🎴 CHANCE';
    if (isCommunityChest) return '📬 COMMUNITY CHEST';
    return metadata.label || 'Unknown';
  };

  const getHeaderColor = () => {
    if (isChance) return 'linear-gradient(135deg, #f6ad55, #dd6b20)';
    if (isCommunityChest) return 'linear-gradient(135deg, #48bb78, #38a169)';
    return metadata.color || '#607d8b';
  };

  // Determine if card has a position change
  const hasPositionChange = card.new_position !== undefined || card.position !== undefined;

  // Get position emoji
  const getPositionEmoji = (pos) => {
    if (pos === 0) return '🏁';
    if (pos === 10) return '🔒';
    if ([5, 15, 25, 35].includes(pos)) return '🚂';
    return '📍';
  };

  // Check if property can be bought
  const canBuy = card.can_buy || false;

  // Check if player went bankrupt
  const isBankrupt = card.bankrupt || false;

  return (
    <div className="card-overlay" onClick={onClose}>
      <div className={`card-modal ${isVisible ? 'visible' : ''}`}>
        {/* Card Header */}
        <div className="card-header" style={{ background: getHeaderColor() }}>
          <div className="card-header-content">
            <span className="card-type-icon">{getTypeIcon()}</span>
            <div className="card-header-text">
              <span className="card-badge">{getCardTypeLabel()}</span>
              <h2>{card.card_name || card.name}</h2>
              {drawnBy && (
                <span className="card-drawn-by">
                  🎯 Drawn by: <strong>{drawnBy}</strong>
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Card Body */}
        <div className="card-body">
          <div className="card-description-wrapper">
            <p className="card-description">{card.description}</p>
          </div>

          {/* Amount Display */}
          {getAmountDisplay()}

          {/* Position Change */}
          {hasPositionChange && (
            <div className="card-position-change">
              <div className="position-change-icon">
                {getPositionEmoji(card.new_position || card.position)}
              </div>
              <div className="position-change-text">
                <span className="position-label">New Position:</span>
                <span className="position-value">
                  {card.property_name ? `${card.property_name} ` : ''}
                  (Square {card.new_position || card.position})
                </span>
              </div>
            </div>
          )}

          {/* Property Purchase */}
          {canBuy && (
            <div className="card-property-buy">
              <div className="buy-icon">🏠</div>
              <div className="buy-text">
                <span className="buy-label">Property Available!</span>
                <span className="buy-price">${card.price}</span>
              </div>
            </div>
          )}

          {/* Bankruptcy Warning */}
          {isBankrupt && (
            <div className="card-bankrupt">
              <div className="bankrupt-icon">💀</div>
              <div className="bankrupt-text">
                <span className="bankrupt-label">⚠️ BANKRUPT!</span>
                <span className="bankrupt-message">{card.message}</span>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="card-footer-actions">
            {canBuy ? (
              <div className="card-actions-row">
                <button className="card-buy-btn" onClick={() => onClose('buy')}>
                  🏠 Buy Property
                </button>
                <button className="card-close-btn" onClick={() => onClose('decline')}>
                  Decline
                </button>
              </div>
            ) : (
              <button className="card-close-btn" onClick={() => onClose('close')}>
                {isBankrupt ? '💀 Game Over' : 'Got it!'}
                <span className="btn-arrow">→</span>
              </button>
            )}
          </div>
        </div>

        {/* Decorative Elements */}
        <div className="card-corner card-corner-tl"></div>
        <div className="card-corner card-corner-tr"></div>
        <div className="card-corner card-corner-bl"></div>
        <div className="card-corner card-corner-br"></div>
      </div>
    </div>
  );
};

export default CardDisplay;