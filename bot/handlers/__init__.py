from ..handlers.user.commands import router as commands
from ..handlers.user.auxiliary import router as auxiliary
from ..handlers.user.examples import router as examples

routers = [
    commands,
    auxiliary,
    examples
]