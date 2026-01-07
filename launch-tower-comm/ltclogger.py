'''Kivy takes control of the standard python logger so we invent our own'''
import time
from pathlib import Path

levels = {
    10: "DEBUG",
    15: "VRBOS",
    20: "INFO ",
    25: "TERSE",
    30: "WARN ",
    40: "ERROR",
    50: "CRITL"
}

class __LTCLogger:
    default_level = 20

    def __init__(self):
        self.level = self.default_level
        logdir = Path("logs")
        logdir.mkdir(exist_ok=True)

        basename = "logltc_" + time.strftime("%Y-%m-%dT%H-%M-%S")
        filename = basename

        for i in range(1, 1000):
            try:
                self._log = (logdir / filename).with_suffix(".txt").open('x')
            except FileExistsError:  # noqa: PERF203 I can't see how to satisfy this and not TOCTOU
                filename = f'{basename}_{i:03}'
            else:
                break
        else:
            raise RuntimeError("No valid log filenames")

    def __del__(self):
        self._log.close()

    def set_default_level(self, level):
        self.level = level

    def log(self, text, level):
        if level >= self.level:
            levelname = levels.get(level, level)
            timestamp = time.strftime("%Y-%m-%d %X")
            message = f"{levelname}|{timestamp} | {text}"
            self._log.write(message + '\n')
            print(message)  # noqa: T201


__globallogger = __LTCLogger()


def set_default_level(level):
    __globallogger.set_default_level(level)


def log(text, level=__globallogger.default_level):
    __globallogger.log(text, level)


def debug(text):
    log(text, 10)


def verbose(text):
    log(text, 15)


def info(text):
    log(text, 20)


def terse(text):
    log(text, 25)


def warn(text):
    log(text, 30)


def error(text):
    log(text, 40)


def critical(text):
    log(text, 50)


if __name__ == "__main__":
    log("TEST")
    debug("DEBUG")
    verbose("VERBOSE")
    info("INFO")
    terse("TERSE")
    warn("WARN")
    error("ERROR")
    critical("CRITICAL")
    log("Change default level to 1")
    set_default_level(1)
    log("TEST LEVEL 5", 5)
    log("TEST LEVEL 4", 4)
    log("TEST LEVEL 3", 3)
    log("TEST LEVEL 2", 2)
    log("TEST LEVEL 1", 1)
    log("Invalid level", "Dog")
