__winc_id__ = "d7b474e9b3a54d23bca54879a4f1855b"
__human_name__ = "Betsy Webshop"

from thefuzz import fuzz
from models import *


def search(term: str) -> list:
    search_result = []
    results = Product.select()
    for product in results:
        print(product.name, (fuzz.partial_ratio(term.lower(), product.name.lower())))
        print(
            product.description,
            (fuzz.partial_ratio(term.lower(), product.description.lower())),
        )
        if fuzz.partial_ratio(term.lower(), product.name) > 70:
            search_result.append(product.name)
        elif fuzz.partial_ratio(term.lower(), product.description) > 70:
            search_result.append(product.name)
    return search_result


def list_user_products(user_id: int) -> list:
    data = User.get_by_id(user_id)
    return [product.name for product in data.products_owned]


def list_products_per_tag(tag_id: int) -> list:
    result = (
        Product.select(Product, Tag, ProductTags)
        .join(ProductTags, JOIN.LEFT_OUTER)
        .join(Tag, JOIN.LEFT_OUTER)
        .where(Tag.id == tag_id)
    )
    return [product.name for product in result]


def add_product_to_catalog(
    user_id, name: str, description: str, price: float, quantity: int, tags: list
) -> None:
    product = Product.create(
        name=name,
        description=description,
        price_per_unit=price,
        quantity_in_stock=quantity,
    )
    for tag in tags:
        item, _ = Tag.get_or_create(name=tag)
        product.tags.add(item)
    User.get_by_id(user_id).products_owned.add(product)
    return None


def update_stock(product_id: int, new_quantity: int) -> None:
    try:
        product = Product.get_by_id(product_id)
        product.quantity_in_stock = new_quantity
        product.save()
    except:
        print("Product id not found!")
    return None


def purchase_product(product_id: int, buyer_id: int, quantity=1) -> None:
    current_product = Product.get_by_id(product_id)
    if current_product.quantity_in_stock >= quantity:
        current_product.quantity_in_stock -= quantity
        current_product.save()
        Transaction.create(
            purchased_products=product_id, buyer_id=buyer_id, quantity=quantity
        )
        User.get_by_id(buyer_id).products_owned.add(product_id)
    else:
        print("Not enough in stock")
    return None


def remove_product(product_id: str) -> None:
    try:
        Product.get_by_id(product_id).delete_instance()
    except:
        print("No product find for this product id!")
    return None


def create_user(
    name: str, address: list[str, int], billing_address: list[str, int] = []
) -> None:
    home_address, _ = Address.get_or_create(
        streetname=address[0], house_number=address[1]
    )
    if billing_address != []:
        bil_address, _ = Address.get_or_create(
            streetname=billing_address[0], house_number=billing_address[1]
        )
    else:
        bil_address = home_address
    User.get_or_create(name=name, address=home_address, billing_information=bil_address)
    return None


def create_product(
    name: str, description: str, price: float, quantity: int, tags: list
) -> None:
    product = Product.create(
        name=name,
        description=description,
        price_per_unit=price,
        quantity_in_stock=quantity,
    )
    for tag in tags:
        item, _ = Tag.get_or_create(name=tag)
        product.tags.add(item)
    return None


# if __name__ == "__main__":
# create_tables()
# db.connect()
# db.close()
