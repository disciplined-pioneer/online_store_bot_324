from .user.commands import router as commands
from .user.auxiliary import router as auxiliary
from .user.examples import router as examples
from .user.custom_engraving import router as custom_engraving
from .user.paintings_metal import router as paintings_metal
from .user.order import router as order

routers = [
    commands,
    auxiliary,
    custom_engraving,
    paintings_metal,
    order,
    examples
]