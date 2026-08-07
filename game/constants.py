# game/constants.py
from .enums import CardType

"""Community Chest cards for Monopoly"""

COMMUNITY_CHEST_CARDS = [
    {
      "id": 1,
      "name": "Advance to GO",
      "description": "Advance to GO (Collect $200)",
      "type": CardType.ADVANCE_TO_GO,
      "amount": 200,
    },
    {
      "id": 2,
      "name": "Bank Error",
      "description": "Bank error in your favor. Collect $200",
      "type": CardType.COLLECT_MONEY,
      "amount": 200,
    },
    {
      "id": 3,
      "name": "Doctor's Fee",
      "description": "Doctor's fee. Pay $50",
      "type": CardType.PAY_MONEY,
      "amount": 50,
    },
    {
      "id": 4,
      "name": "Stock Sale",
      "description": "From sale of stock you get $50",
      "type": CardType.COLLECT_MONEY,
      "amount": 50,
    },
    {
        "id": 5,
        "name": "Get Out of Jail Free",
        "description": "Get Out of Jail Free - Keep this card",
        "type": CardType.GET_OUT_OF_JAIL,
        "amount": 0,
    },
    {
        "id": 6,
        "name": "Go to Jail",
        "description": "Go to Jail",
        "type": CardType.GO_TO_JAIL,
        "amount": 0,
    },
    {
        "id": 7,
        "name": "Grand Opera Night",
        "description": "Grand Opera Night. Collect $50 from every player",
        "type": CardType.COLLECT_FROM_ALL,
        "amount": 50,
    },
    {
        "id": 8,
        "name": "Holiday Fund",
        "description": "Holiday fund matures. Receive $100",
        "type": CardType.COLLECT_MONEY,
        "amount": 100,
    },
    {
        "id": 9,
        "name": "Tax Refund",
        "description": "Income tax refund. Collect $20",
        "type": CardType.COLLECT_MONEY,
        "amount": 20,
    },
    {
        "id": 10,
        "name": "Birthday",
        "description": "It's your birthday! Collect $10 from each player",
        "type": CardType.COLLECT_FROM_ALL,
        "amount": 10,
    },
    {
        "id": 11,
        "name": "Life Insurance",
        "description": "Life insurance matures. Collect $100",
        "type": CardType.COLLECT_MONEY,
        "amount": 100,
    },
    {
        "id": 12,
        "name": "Hospital Fees",
        "description": "Pay hospital fees of $100",
        "type": CardType.PAY_MONEY,
        "amount": 100,
    },
    {
        "id": 13,
        "name": "School Fees",
        "description": "Pay school fees of $50",
        "type": CardType.PAY_MONEY,
        "amount": 50,
    },
    {
        "id": 14,
        "name": "Consultancy Fee",
        "description": "Receive $25 consultancy fee",
        "type": CardType.COLLECT_MONEY,
        "amount": 25,
    },
    {
        "id": 15,
        "name": "Street Repairs",
        "description": "You are assessed for street repairs: $40 per house, $115 per hotel",
        "type": CardType.STREET_REPAIRS,
        "amount": 0,
    },
    {
        "id": 16,
        "name": "Beauty Contest",
        "description": "You have won second prize in a beauty contest. Collect $10",
        "type": CardType.COLLECT_MONEY,
        "amount": 10,
    },
]

# Card type metadata for display
CARD_TYPE_METADATA = {
    CardType.COLLECT_MONEY: {
        'emoji': '💰',
        'color': '#4caf50',
        'label': 'Collect Money',
        'is_positive': True,
    },
    CardType.PAY_MONEY: {
        'emoji': '💸',
        'color': '#f44336',
        'label': 'Pay Money',
        'is_positive': False,
    },
    CardType.ADVANCE_TO_GO: {
        'emoji': '🏃',
        'color': '#2196f3',
        'label': 'Advance to GO',
        'is_positive': True,
    },
    CardType.GO_TO_JAIL: {
        'emoji': '🔒',
        'color': '#ff9800',
        'label': 'Go to Jail',
        'is_positive': False,
    },
    CardType.GET_OUT_OF_JAIL: {
        'emoji': '🆓',
        'color': '#9c27b0',
        'label': 'Get Out of Jail',
        'is_positive': True,
    },
    CardType.COLLECT_FROM_ALL: {
        'emoji': '🎁',
        'color': '#00bcd4',
        'label': 'Collect from All',
        'is_positive': True,
    },
    CardType.STREET_REPAIRS: {
        'emoji': '🔧',
        'color': '#ff5722',
        'label': 'Street Repairs',
        'is_positive': False,
    },
}