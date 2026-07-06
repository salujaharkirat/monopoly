// frontend/src/components/Game/Dice.js
import React, { useState, useEffect } from 'react';
import './Dice.css';

const Dice = ({ values, isRolling, onRollComplete }) => {
  const [displayValues, setDisplayValues] = useState({ dice1: 1, dice2: 1 });
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (values && isRolling) {
      // Start rolling animation
      setIsAnimating(true);
      
      // Show random values during animation
      const interval = setInterval(() => {
        setDisplayValues({
          dice1: Math.floor(Math.random() * 6) + 1,
          dice2: Math.floor(Math.random() * 6) + 1
        });
      }, 100);

      // Stop animation after 1.5 seconds and show final values
      setTimeout(() => {
        clearInterval(interval);
        setDisplayValues({
          dice1: values.dice1,
          dice2: values.dice2
        });
        setIsAnimating(false);
        if (onRollComplete) {
          onRollComplete(values);
        }
      }, 1500);

      return () => clearInterval(interval);
    } else if (values) {
      setDisplayValues({
        dice1: values.dice1,
        dice2: values.dice2
      });
    }
  }, [values, isRolling, onRollComplete]);

  const getDiceFace = (value) => {
    // Unicode dice faces
    const faces = {
      1: '⚀',
      2: '⚁',
      3: '⚂',
      4: '⚃',
      5: '⚄',
      6: '⚅'
    };
    return faces[value] || '⚀';
  };

  const getDiceStyle = (value) => {
    // Different styles based on value
    const styles = {
      1: { fontSize: '60px' },
      2: { fontSize: '60px' },
      3: { fontSize: '60px' },
      4: { fontSize: '60px' },
      5: { fontSize: '60px' },
      6: { fontSize: '60px' }
    };
    return styles[value] || styles[1];
  };

  if (!values && !isRolling) {
    return (
      <div className="dice-container">
        <div className="dice-placeholder">
          <span className="dice-icon">🎲</span>
          <p className="dice-hint">Roll the dice to start</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dice-container">
      <div className={`dice-wrapper ${isAnimating ? 'rolling' : ''}`}>
        <div className="dice-pair">
          <div className={`dice-face ${isAnimating ? 'rolling-dice' : ''}`}>
            <span style={getDiceStyle(displayValues.dice1)}>
              {getDiceFace(displayValues.dice1)}
            </span>
          </div>
          <div className="dice-plus">+</div>
          <div className={`dice-face ${isAnimating ? 'rolling-dice' : ''}`}>
            <span style={getDiceStyle(displayValues.dice2)}>
              {getDiceFace(displayValues.dice2)}
            </span>
          </div>
        </div>
      </div>
      
      {values && !isAnimating && (
        <div className="dice-result">
          <div className="dice-total">
            <span className="total-label">Total</span>
            <span className="total-value">{values.total}</span>
          </div>
          {values.is_doubles && (
            <div className="doubles-badge">🎯 Doubles!</div>
          )}
          {values.passed_go && (
            <div className="passed-go">💰 Passed GO! +$200</div>
          )}
        </div>
      )}
    </div>
  );
};

export default Dice;