// frontend/src/constants/cardTypes.js

export const CARD_TYPES = {
  // Money cards
  COLLECT_MONEY: 'COLLECT_MONEY',
  PAY_MONEY: 'PAY_MONEY',
  COLLECT_FROM_ALL: 'COLLECT_FROM_ALL',
  PAY_EACH_PLAYER: 'PAY_EACH_PLAYER',

  // Movement cards
  ADVANCE_TO_GO: 'ADVANCE_TO_GO',
  ADVANCE_TO_PROPERTY: 'ADVANCE_TO_PROPERTY',
  ADVANCE_TO_RAILROAD: 'ADVANCE_TO_RAILROAD',
  MOVE_BACK: 'MOVE_BACK',
  GO_TO_JAIL: 'GO_TO_JAIL',

  // Special cards
  GET_OUT_OF_JAIL: 'GET_OUT_OF_JAIL',
  STREET_REPAIRS: 'STREET_REPAIRS',
  GENERAL_REPAIRS: 'GENERAL_REPAIRS',
};

export const CARD_METADATA = {
  [CARD_TYPES.COLLECT_MONEY]: {
    emoji: '💰',
    color: '#48bb78',
    label: '💰 Collect Money',
    isPositive: true,
  },
  [CARD_TYPES.PAY_MONEY]: {
    emoji: '💸',
    color: '#fc8181',
    label: '💸 Pay Money',
    isPositive: false,
  },
  [CARD_TYPES.COLLECT_FROM_ALL]: {
    emoji: '🎁',
    color: '#4fd1c5',
    label: '🎁 Collect from All',
    isPositive: true,
  },
  [CARD_TYPES.PAY_EACH_PLAYER]: {
    emoji: '💸',
    color: '#fc8181',
    label: '💸 Pay Each Player',
    isPositive: false,
  },
  [CARD_TYPES.ADVANCE_TO_GO]: {
    emoji: '🏃',
    color: '#63b3ed',
    label: '🏃 Advance to GO',
    isPositive: true,
  },
  [CARD_TYPES.ADVANCE_TO_PROPERTY]: {
    emoji: '🏠',
    color: '#b794f4',
    label: '🏠 Advance to Property',
    isPositive: true,
  },
  [CARD_TYPES.ADVANCE_TO_RAILROAD]: {
    emoji: '🚂',
    color: '#f6ad55',
    label: '🚂 Advance to Railroad',
    isPositive: true,
  },
  [CARD_TYPES.MOVE_BACK]: {
    emoji: '🔙',
    color: '#fc8181',
    label: '🔙 Move Back',
    isPositive: false,
  },
  [CARD_TYPES.GO_TO_JAIL]: {
    emoji: '🔒',
    color: '#fc8181',
    label: '🔒 Go to Jail',
    isPositive: false,
  },
  [CARD_TYPES.GET_OUT_OF_JAIL]: {
    emoji: '🆓',
    color: '#b794f4',
    label: '🆓 Get Out of Jail',
    isPositive: true,
  },
  [CARD_TYPES.STREET_REPAIRS]: {
    emoji: '🔧',
    color: '#fc8181',
    label: '🔧 Street Repairs',
    isPositive: false,
  },
  [CARD_TYPES.GENERAL_REPAIRS]: {
    emoji: '🔧',
    color: '#fc8181',
    label: '🔧 General Repairs',
    isPositive: false,
  },
};