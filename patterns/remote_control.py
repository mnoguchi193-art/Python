"""
Remote Control — the Command design pattern with undo support

A remote control button shouldn't know *how* a device works; it just fires a
Command. Each Command knows how to `execute` and how to `undo` itself, so the
remote can keep a history and roll actions back.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


# ── Receivers: the actual devices ─────────────────────────────────────────
class Light:
    def __init__(self, location: str = "Living Room"):
        self.location = location
        self.is_on = False

    def turn_on(self) -> None:
        self.is_on = True
        print(f"{self.location} light is ON")

    def turn_off(self) -> None:
        self.is_on = False
        print(f"{self.location} light is OFF")


class Stereo:
    def __init__(self):
        self.is_on = False
        self.volume = 0

    def turn_on(self) -> None:
        self.is_on = True
        print("Stereo is ON")

    def turn_off(self) -> None:
        self.is_on = False
        print("Stereo is OFF")

    def set_volume(self, level: int) -> None:
        self.volume = level
        print(f"Stereo volume set to {level}")


# ── Command interface ─────────────────────────────────────────────────────
class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...


class NoCommand(Command):
    """Null Object — a do-nothing default so empty slots are safe to press."""

    def execute(self) -> None:
        print("(slot is empty)")

    def undo(self) -> None:
        print("(nothing to undo)")


# ── Concrete commands ─────────────────────────────────────────────────────
class LightOnCommand(Command):
    def __init__(self, light: Light):
        self.light = light

    def execute(self) -> None:
        self.light.turn_on()

    def undo(self) -> None:
        self.light.turn_off()


class LightOffCommand(Command):
    def __init__(self, light: Light):
        self.light = light

    def execute(self) -> None:
        self.light.turn_off()

    def undo(self) -> None:
        self.light.turn_on()


class StereoOnWithVolumeCommand(Command):
    def __init__(self, stereo: Stereo, volume: int = 11):
        self.stereo = stereo
        self.volume = volume
        self._prev_volume = 0
        self._was_on = False

    def execute(self) -> None:
        self._was_on = self.stereo.is_on
        self._prev_volume = self.stereo.volume
        self.stereo.turn_on()
        self.stereo.set_volume(self.volume)

    def undo(self) -> None:
        self.stereo.set_volume(self._prev_volume)
        if not self._was_on:
            self.stereo.turn_off()


class MacroCommand(Command):
    """Run several commands as one button press (e.g. a 'movie mode' scene)."""

    def __init__(self, commands: list[Command]):
        self.commands = commands

    def execute(self) -> None:
        for command in self.commands:
            command.execute()

    def undo(self) -> None:
        for command in reversed(self.commands):
            command.undo()


# ── Invoker: the remote control ───────────────────────────────────────────
class RemoteControl:
    def __init__(self, slots: int = 4):
        self.on_commands: list[Command] = [NoCommand() for _ in range(slots)]
        self.off_commands: list[Command] = [NoCommand() for _ in range(slots)]
        self._history: list[Command] = []

    def set_command(self, slot: int, on: Command, off: Command) -> None:
        self.on_commands[slot] = on
        self.off_commands[slot] = off

    def press_on(self, slot: int) -> None:
        command = self.on_commands[slot]
        command.execute()
        self._history.append(command)

    def press_off(self, slot: int) -> None:
        command = self.off_commands[slot]
        command.execute()
        self._history.append(command)

    def press_undo(self) -> None:
        if not self._history:
            print("(nothing to undo)")
            return
        self._history.pop().undo()

    def __repr__(self) -> str:
        lines = ["RemoteControl:"]
        for i, (on, off) in enumerate(zip(self.on_commands, self.off_commands)):
            lines.append(
                f"  [{i}] on={type(on).__name__}  off={type(off).__name__}"
            )
        return "\n".join(lines)


if __name__ == "__main__":
    living_room = Light("Living Room")
    stereo = Stereo()

    remote = RemoteControl(slots=4)
    remote.set_command(0, LightOnCommand(living_room), LightOffCommand(living_room))
    remote.set_command(
        1,
        StereoOnWithVolumeCommand(stereo, volume=8),
        NoCommand(),  # no dedicated off button for the stereo
    )
    # Slot 2: a "movie mode" macro — dim down to one device + crank the stereo.
    movie_on = MacroCommand(
        [LightOffCommand(living_room), StereoOnWithVolumeCommand(stereo, 5)]
    )
    remote.set_command(2, movie_on, NoCommand())

    print(remote, "\n")

    print("-- Light --")
    remote.press_on(0)
    remote.press_off(0)
    remote.press_undo()  # undoes the off -> light back on

    print("\n-- Stereo --")
    remote.press_on(1)
    remote.press_undo()  # restore previous volume + power state

    print("\n-- Movie mode (macro) --")
    remote.press_on(2)
    remote.press_undo()  # rolls back the whole scene in reverse

    print("\n-- Empty slot --")
    remote.press_on(3)
