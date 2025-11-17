#!/usr/bin/env python3
"""Точка входа в игру «Лабиринт сокровищ»."""

from .constants import COMMANDS, DIRECTIONS
from .player_actions import (
    get_input,
    move_player,
    show_inventory,
    take_item,
    use_item,
)
from .utils import (
    attempt_open_treasure,
    describe_current_room,
    show_help,
    solve_puzzle,
)


def process_command(game_state: dict, command_line: str) -> None:
    """Разобрать и выполнить команду пользователя."""
    command_line = command_line.strip()
    if not command_line:
        return

    parts = command_line.split()
    cmd = parts[0].lower()
    arg = " ".join(parts[1:])

    # Движение по односложным командам (north/south/...)
    if cmd in DIRECTIONS and not arg:
        move_player(game_state, cmd)
        return

    match cmd:
        case "go":
            if not arg:
                print("Укажите направление (north/south/east/west).")
            else:
                move_player(game_state, arg)
        case "look":
            describe_current_room(game_state)
        case "inventory":
            show_inventory(game_state)
        case "take":
            if not arg:
                print("Что вы хотите взять?")
            else:
                take_item(game_state, arg)
        case "use":
            if not arg:
                print("Что вы хотите использовать?")
            else:
                use_item(game_state, arg)
        case "solve":
            current_room = game_state.get("current_room")
            if current_room == "treasure_room":
                attempt_open_treasure(game_state)
            else:
                solve_puzzle(game_state)
        case "help":
            show_help(COMMANDS)
        case "quit" | "exit":
            print("Вы решили покинуть лабиринт. Игра окончена.")
            game_state["game_over"] = True
        case _:
            print("Неизвестная команда. Введите 'help' для списка команд.")


def main() -> None:
    """Запустить главный игровой цикл."""
    game_state = {
        "player_inventory": [],
        "current_room": "entrance",
        "game_over": False,
        "steps_taken": 0,
    }

    print("Добро пожаловать в Лабиринт сокровищ!")
    describe_current_room(game_state)

    while not game_state.get("game_over"):
        command_line = get_input("> ")
        if command_line.strip().lower() in ("quit", "exit"):
            print("Вы решили покинуть лабиринт. Игра окончена.")
            break

        process_command(game_state, command_line)


if __name__ == "__main__":
    main()
