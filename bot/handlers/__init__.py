from bot.handlers.user.commands import router as commands
from bot.handlers.user.auxiliary import router as auxiliary
from bot.handlers.user.examples import router as examples

routers = [
    commands,
    auxiliary,
    examples
]