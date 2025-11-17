"""Действия игрока: перемещение, предметы, инвентарь и ввод."""

from .constants import DIRECTIONS, ROOMS
from .utils import describe_current_room, random_event, trigger_trap


def show_inventory(game_state: dict) -> None:
    """Показать содержимое инвентаря игрока."""
    inventory = game_state.get("player_inventory", [])
    if not inventory:
        print("Инвентарь пуст.")
        return

    print("В вашем инвентаре:")
    for item in inventory:
        print(f" - {item}")


def get_input(prompt: str = "> ") -> str:
    """Безопасный ввод команды от пользователя."""
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из игры.")
        return "quit"


def move_player(game_state: dict, direction: str) -> None:
    """Переместить игрока в указанном направлении, если есть выход."""
    direction = direction.lower()
    if direction not in DIRECTIONS:
        print("Такого направления нет.")
        return

    current_room_name = game_state.get("current_room")
    current_room = ROOMS.get(current_room_name, {})
    exits = current_room.get("exits", {})

    if direction not in exits:
        print("Нельзя пойти в этом направлении.")
        return

    target_room_name = exits[direction]
    inventory = game_state.get("player_inventory", [])

    if target_room_name == "treasure_room" and "rusty_key" not in inventory:
        print("Дверь заперта. Нужен ключ, чтобы пройти дальше.")
        return
    if target_room_name == "treasure_room" and "rusty_key" in inventory:
        print(
            "Вы используете найденный ключ, чтобы открыть путь "
            "в комнату сокровищ."
        )

    game_state["current_room"] = target_room_name
    game_state["steps_taken"] = game_state.get("steps_taken", 0) + 1

    random_event(game_state)
    if not game_state.get("game_over"):
        describe_current_room(game_state)


def take_item(game_state: dict, item_name: str) -> None:
    """Поднять предмет из текущей комнаты."""
    item_name = item_name.strip()
    if not item_name:
        print("Что именно вы хотите взять?")
        return

    if item_name == "treasure_chest":
        print("Вы не можете поднять сундук, он слишком тяжелый.")
        return

    room_name = game_state.get("current_room")
    room = ROOMS.get(room_name, {})
    items = room.get("items", [])
    if item_name not in items:
        print("Такого предмета здесь нет.")
        return

    items.remove(item_name)
    game_state.setdefault("player_inventory", []).append(item_name)
    print(f"Вы подняли: {item_name}")


def use_item(game_state: dict, item_name: str) -> None:
    """Использовать предмет из инвентаря."""
    item_name = item_name.strip()
    if not item_name:
        print("Какой предмет вы хотите использовать?")
        return

    inventory = game_state.get("player_inventory", [])
    if item_name not in inventory:
        print("У вас нет такого предмета.")
        return

    current_room_name = game_state.get("current_room")

    if item_name == "torch":
        print("Вы зажигаете факел. Вокруг становится светлее и менее страшно.")
    elif item_name == "sword":
        print("Вы крепче сжимаете меч и чувствуете уверенность.")
    elif item_name == "bronze_box":
        if "rusty_key" not in inventory:
            print(
                "Вы аккуратно открываете бронзовую шкатулку "
                "и находите внутри ржавый ключ."
            )
            inventory.append("rusty_key")
        else:
            print("Шкатулка уже пуста, вы всё забрали ранее.")
    else:
        if current_room_name == "trap_room":
            print("Вы неуверенно пытаетесь использовать предмет,"
                  " но ничего не происходит.")
            trigger_trap(game_state)
        else:
            print("Вы не знаете, как использовать этот предмет.")
