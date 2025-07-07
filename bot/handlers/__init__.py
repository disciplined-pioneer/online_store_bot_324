from .user.order import router as order
from .user.commands import router as commands
from .user.auxiliary import router as auxiliary
from .user.examples import router as examples
from .user.custom_engraving import router as custom_engraving
from .user.paintings_metal import router as paintings_metal
from .user.pick_up_point import router as pick_up_point
from .user.my_orders import router as my_orders
from .manager.payment_manager import router as payment_manager
from .admin.admin import router as admin


routers = [
    commands,
    custom_engraving,
    paintings_metal,
    order,
    pick_up_point,
    examples,
    payment_manager,
    my_orders,
    admin,
    auxiliary,
]