from .auth_controller import router as auth_router
from .product_controller import router as product_router
from .order_controller import router as order_router
from .blacklist_controller import router as blacklist_router

__all__ = ["auth_router", "product_router", "order_router", "blacklist_router"]
