# Models go here
from peewee import *
import datetime

db = SqliteDatabase(":memory:")


class BaseModel(Model):
    class Meta:
        database = db


class Tag(BaseModel):
    name = CharField(unique=True)


class Product(BaseModel):
    name = CharField(index=True)
    description = CharField(index=True)
    price_per_unit = FloatField()
    quantity_in_stock = IntegerField()
    tags = ManyToManyField(Tag, backref="tags")


class Address(BaseModel):
    streetname = CharField()
    house_number = IntegerField()


class User(BaseModel):
    name = CharField()
    address = ForeignKeyField(Address)
    billing_information = ForeignKeyField(Address)
    products_owned = ManyToManyField(Product, backref="products_owned")


class Transaction(BaseModel):
    purchased_products = ForeignKeyField(Product, backref="products")
    purchased_date = DateField(default=datetime.datetime.now)
    buyer_id = ForeignKeyField(User, backref="buyer_id")
    quantity = IntegerField(default=1)


ProductTags = Product.tags.get_through_model()
ProductsOwners = User.products_owned.get_through_model()


def create_tables():
    with db:
        db.create_tables(
            [User, Tag, Product, Transaction, Address, ProductTags, ProductsOwners],
            safe=True,
        )
