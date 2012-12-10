try:
    from transaction import *
except ImportError:

    def commit():
        return get_transaction().commit()
