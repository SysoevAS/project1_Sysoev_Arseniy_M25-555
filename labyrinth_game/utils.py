"""Вспомогательные функции: описание комнат, помощь, загадки, случайности."""

import math

from .constants import (
    COMMANDS,
    EVENT_PROBABILITY_MODULO,
    RANDOM_EVENT_TYPES,
    ROOMS,
    TRAP_DANGER_MODULO,
    TRAP_DEATH_THRESHOLD,
)


def describe_current_room(game_state: dict) -> None:
    """Вывести описание текущей комнаты, предметов и выходов."""
    room_name = game_state.get("current_room")
    room = ROOMS.get(room_name, {})
    print()
    print(f"== {room_name.upper()} ==")
    print(room.get("description", ""))

    items = room.get("items", [])
    if items:
        print("Заметные предметы:", ", ".join(items))

    exits = room.get("exits", {})
    if exits:
        directions = ", ".join(sorted(exits.keys()))
        print("Выходы:", directions)

    if room.get("puzzle") is not None:
        print("Кажется, здесь есть загадка (используйте команду solve).")


def show_help(commands: dict | None = None) -> None:
    """Показать доступные команды игроку."""
    print("\nДоступные команды:")
    mapping = commands or COMMANDS
    for command, description in mapping.items():
        print(f" {command:<16} - {description}")


def pseudo_random(seed: int, modulo: int) -> int:
    """Простой псевдослучайный генератор на основе синуса."""
    if modulo <= 0:
        return 0
    x = math.sin(seed * 12.9898) * 43758.5453
    frac = x - math.floor(x)
    return int(frac * modulo)


def trigger_trap(game_state: dict) -> None:
    """Сработавшая ловушка: потеря предмета или потенциальная смерть."""
    print("\nЛовушка активирована! Пол под ногами начинает дрожать...")
    inventory = game_state.get("player_inventory", [])
    if inventory:
        index = pseudo_random(game_state.get("steps_taken", 0), len(inventory))
        lost_item = inventory.pop(index)
        print(f"Вы едва удерживаете равновесие и роняете предмет: {lost_item}.")
        return

    roll = pseudo_random(game_state.get("steps_taken", 0), TRAP_DANGER_MODULO)
    if roll < TRAP_DEATH_THRESHOLD:
        print("Пол внезапно проваливается. Вы падаете в яму. Игра окончена.")
        game_state["game_over"] = True
    else:
        print("Вы чудом удерживаетесь на краю и выживаете.")


def random_event(game_state: dict) -> None:
    """Случайные события при перемещении по лабиринту."""
    steps = game_state.get("steps_taken", 0)
    trigger_value = pseudo_random(steps, EVENT_PROBABILITY_MODULO)
    if trigger_value != 0:
        return

    event_type = pseudo_random(steps + 1, RANDOM_EVENT_TYPES)
    current_room_name = game_state.get("current_room")
    room = ROOMS.get(current_room_name, {})
    inventory = game_state.get("player_inventory", [])

    if event_type == 0:
        # Находка монеты
        print("\nВы замечаете на полу старую монетку.")
        if "coin" not in room.get("items", []):
            room.setdefault("items", []).append("coin")
    elif event_type == 1:
        # Испуг
        print("\nГде-то рядом раздается странный шорох.")
        if "sword" in inventory:
            print("Вы сжимаете меч, и существо в темноте отступает.")
    else:
        # Потенциальная ловушка
        if current_room_name == "trap_room" and "torch" not in inventory:
            print("\nВы чувствуете, что пол под ногами подозрительно пружинит...")
            trigger_trap(game_state)


def solve_puzzle(game_state: dict) -> None:
    """Попытаться решить загадку в текущей комнате."""
    room_name = game_state.get("current_room")
    room = ROOMS.get(room_name, {})
    puzzle = room.get("puzzle")

    if puzzle is None:
        print("Загадок здесь нет.")
        return

    question, answer = puzzle
    print()
    print(question)
    user_answer = input("Ваш ответ: ").strip().lower()
    expected = answer.strip().lower()

    valid_answers = {expected}
    if expected == "7":
        valid_answers.add("")

    if user_answer in valid_answers:
        print("Верно! Вы разгадали загадку.")
        room["puzzle"] = None

        inventory = game_state.get("player_inventory", [])

        if room_name == "hall":
            if "treasure_key" not in inventory:
                inventory.append("treasure_key")
                print("Вы находите маленький ключ от сокровищницы.")
        elif room_name == "library":
            if "mysterious_amulet" not in inventory:
                inventory.append("mysterious_amulet")
                print("Вы находите странный амулет среди свитков.")
        elif room_name == "trap_room":
            print("Некоторые плиты перестают щелкать. Ловушка вроде бы успокоилась.")
    else:
        print("Неверно. Попробуйте снова.")
        if room_name == "trap_room":
            trigger_trap(game_state)


def attempt_open_treasure(game_state: dict) -> None:
    """Попытка открыть сундук с сокровищами."""
    room_name = game_state.get("current_room")
    if room_name != "treasure_room":
        print("Здесь нечего открывать.")
        return

    room = ROOMS.get(room_name, {})
    items = room.get("items", [])
    inventory = game_state.get("player_inventory", [])

    if "treasure_chest" not in items:
        print("Сундука здесь уже нет.")
        return

    if "treasure_key" in inventory:
        print(
            "\nВы применяете найденный ключ, и замок щёлкает. "
            "Сундук открыт!"
        )
        items.remove("treasure_chest")
        print("В сундуке оказывается сокровище. Вы победили!")
        game_state["game_over"] = True
        return

    print(
        "\nСундук заперт. Можно попытаться взломать его, введя код."
    )
    choice = input("Ввести код? (да/нет): ").strip().lower()
    if choice != "да":
        print("Вы отступаете от сундука.")
        return

    puzzle = room.get("puzzle")
    if puzzle is None:
        print("Код уже был подобран раньше.")
        return

    question, answer = puzzle
    print(question)
    user_code = input("Код: ").strip().lower()
    expected = answer.strip().lower()
    valid_answers = {expected}
    if expected == "7":
        valid_answers.add("семь")

    if user_code in valid_answers:
        print("Код верный! Замок открывается.")
        items.remove("treasure_chest")
        room["puzzle"] = None
        print("Вы видите гору золота и драгоценностей. Вы победили!")
        game_state["game_over"] = True
    else:
        print("Код неверный. Сундук остаётся закрытым.")
