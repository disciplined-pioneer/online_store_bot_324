from ..handlers.user.commands import router as commands
from ..handlers.user.auxiliary import router as auxiliary
from ..handlers.user.examples import router as examples
from ..handlers.user.make_order import router as make_order
from ..handlers.user.paintings_metal import router as paintings_metal

routers = [
    commands,
    auxiliary,
    make_order,
    paintings_metal,
    examples
]