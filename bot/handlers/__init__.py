from .user.order import router as order
from .user.commands import router as commands
from .user.auxiliary import router as auxiliary
from .user.examples import router as examples
from .user.custom_engraving import router as custom_engraving
from .user.paintings_metal import router as paintings_metal
from .user.pick_up_point import router as pick_up_point

routers = [
    commands,
    custom_engraving,
    paintings_metal,
    order,
    pick_up_point,
    examples,
    auxiliary,
]