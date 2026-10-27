## **Project Overview**

A real-time multiplayer Monopoly game, driven entirely by its backend. There is no UI: every action is a REST call or a WebSocket message, and any client (curl, a script, a bot, a test) can play.

---

## **Tech Stack**

- **Backend:** Django, DRF, Channels, Daphne
- **Database:** MySQL (see `config/settings.py`)
- **Channel layer:** in-memory (dev), Redis (prod)

---

## **API**

All endpoints except login/register require `Authorization: Token <key>`.

### REST

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/auth/register/` | Create an account |
| POST | `/api/auth/login/` | Get a token |
| POST | `/api/auth/logout/` | Invalidate the token |
| GET | `/api/auth/me/` | Current user |
| GET | `/api/user/profile/` | Player profile |
| GET | `/api/games/` | Your games |
| POST | `/api/games/create/` | Create a game |
| GET | `/api/games/<id>/` | Game details |
| POST | `/api/games/<id>/join/` | Join a game |
| POST | `/api/games/<id>/start/` | Start a game |

### WebSocket

Connect to `ws://<host>/ws/game/<game_id>/?token=<key>`. Close codes: `4001` auth failure, `4003` not a player in this game.

Send JSON `{"action": "<name>", ...}`. Actions: `roll_dice`, `start_game`, `end_turn`, `buy_property`, `game_state`, `build_house`, `sell_house`, `pay_bail`, `use_jail_card`, `leave_game`.

The server sends `{"type": "<event>", "data": ...}`. Events: `game_state`, `game_started`, `game_update`, `dice_rolled`, `property_purchased`, `house_built`, `turn_ended`, `bail_paid`, `jail_card_used`, `game_left`, and `error` (with `message`).

---

## **Running**

```
pip install -r requirements.txt
python manage.py migrate
python manage.py init_board
daphne -p 8001 config.asgi:application
```

---

## **Roadmap**

- [x]  Django + DRF setup, token authentication
- [x]  Models: Game, Player, GamePlayer, Square, Property
- [x]  Game APIs: create, join, start, leave
- [x]  Channels + Daphne, game consumer
- [x]  Dice, movement, property purchase, rent, taxes, Pass GO
- [x]  Chance and Community Chest
- [x]  Railroads, utilities, jail (bail, doubles, 3 turns)
- [x]  Houses & hotels: buy house, sell house
- [x]  Bankruptcy, game over & winner
- [ ]  Testing (unit, integration)
- [ ]  Docker & Redis setup
- [ ]  Production deployment
