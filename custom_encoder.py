from decimal import Decimal
from json import JSONEncoder as BaseJSONEncoder

class CustomJSONEncoder(BaseJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)
