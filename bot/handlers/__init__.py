from ..handlers.user.commands import router as commands
from ..handlers.user.auxiliary import router as auxiliary
from ..handlers.user.examples import router as examples
from ..handlers.user.make_order import router as make_order

routers = [
    commands,
    auxiliary,
    make_order,
    examples
]