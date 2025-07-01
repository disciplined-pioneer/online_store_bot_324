from bot.handlers.user.commands import router as commands
from bot.handlers.user.auxiliary import router as auxiliary

routers = [
    commands,
    auxiliary
]