from django.db import models

class CardType(models.TextChoices):
    """Community Chest card types"""
    COLLECT_MONEY = 'COLLECT_MONEY', 'Collect Money'
    PAY_MONEY = 'PAY_MONEY', 'Pay Money'
    ADVANCE_TO_GO = 'ADVANCE_TO_GO', 'Advance to GO'
    GO_TO_JAIL = 'GO_TO_JAIL', 'Go to Jail'
    GET_OUT_OF_JAIL = 'GET_OUT_OF_JAIL', 'Get Out of Jail'
    COLLECT_FROM_ALL = 'COLLECT_FROM_ALL', 'Collect from All Players'
    STREET_REPAIRS = 'STREET_REPAIRS', 'Street Repairs'