from ecommerceapi.models.product import Product
from ecommerceapi.schemas.product import ProductSerializedOut


def serialize_product(product: Product) -> ProductSerializedOut:
    return ProductSerializedOut(
        id=product.id,
        name=product.name,
        price=float(product.price) if product.price is not None else None,
        starts_with_a=product.name.startswith("A"),
    )
