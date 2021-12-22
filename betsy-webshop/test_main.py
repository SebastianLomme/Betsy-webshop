import pytest
from models import *
from main import *
import sys

MODELS = [User, Tag, Product, Transaction, Address, ProductTags, ProductsOwners]


@pytest.fixture(scope="module", autouse=True)
def setup_databases() -> None:
    test_db = SqliteDatabase(":memory:")
    test_db.connect()
    test_db.create_tables(MODELS, safe=True)
    create_user("Anni Hillatt", ["Park Meadow Alley", 40079], ["Northridge Circle", 89])
    create_user("Ronnie O'Donnell", ["Merrick Junction", 6])

    create_product(
        name="Fjallraven - Foldsack No. 1 Backpack, Fits 15 inches Laptops",
        description="Your perfect pack for everyday use and walks in the forest. Stash your laptop (up to 15 inches) in the padded sleeve, your everyday",
        price=109.95,
        quantity=10,
        tags=["backpack", "laptop sleeve", "Foldsack, 15 inches Laptops"],
    )
    create_product(
        name="Mens Casual Premium Slim Fit T-Shirts",
        description="Slim-fitting style, contrast raglan long sleeve, three-button henley placket, light weight & soft fabric for breathable and comfortable wearing. And Solid stitched shirts with round neck made for durability and a great fit for casual fashion wear and diehard baseball fans. The Henley style round neckline includes a three-button placket.",
        price=22.3,
        quantity=10,
        tags=["t-shirt", "mens cloting", "round neck", "casual"],
    )
    create_product(
        name="Mens Cotton Jacket",
        description="great outerwear jackets for Spring/Autumn/Winter, suitable for many occasions, such as working, hiking, camping, mountain/rock climbing, cycling, traveling or other outdoors. Good gift choice for you or your family member. A warm hearted love to Father, husband or son in this thanksgiving or Christmas Day.",
        price=55.99,
        quantity=10,
        tags=["jacket", "mens cloting", "outdoors"],
    )
    create_product(
        name="Mens Casual Slim Fit longsleef",
        description="The color could be slightly different between on the screen and in practice. / Please note that body builds vary by person, therefore, detailed size information should be reviewed below on the product description.",
        price=15.99,
        quantity=10,
        tags=["longsleef", "mens cloting", "round neck", "casual"],
    )
    create_product(
        name="John Hardy Women's Legends Naga Gold & Silver Dragon Station Chain Bracelet",
        description="The color could be slightly different between on the screen and in practiceFrom our Legends Collection, the Naga was inspired by the mythical water dragon that protects the ocean's pearl. Wear facing inward to be bestowed with love and abundance, or outward for protection.",
        price=695,
        quantity=10,
        tags=["jewelery", "women", "gold", "silver"],
    )

    yield
    # test_db.drop_tables(MODELS)
    test_db.close()


class TestUser:
    def test_User_billing_info_given(self) -> None:
        data = User.get(name="Anni Hillatt")
        assert data.name == "Anni Hillatt"
        assert data.address != data.billing_information

    def test_User_billing_info_not_given(self) -> None:
        data = User.get(name="Ronnie O'Donnell")
        assert data.address == data.billing_information


class TestCreateProduct:
    def test_create_product_no_dublicate_tags(self) -> None:
        try:
            create_product(
                name="Red jeans",
                description="these jeans are red",
                price=50,
                quantity=10,
                tags=["jeans", "red"],
            )
        except:
            pytest.fail("you create a dublicate tag")

    def test_create_product(self) -> None:
        create_product(
            name="Red t-shirt",
            description="these t-shirt are red",
            price=50,
            quantity=10,
            tags=["t-shirt", "red"],
        )

    def test_product_price(self) -> None:
        product_price = Product.get_by_id(1).price_per_unit
        assert product_price == 109.95

    def test_product_price_two_decimals(self):
        product_price = Product.get_by_id(5).price_per_unit
        assert product_price == 695.00


class TestSearch:
    def test_search_by_name(self) -> None:
        result = search("jeans")
        assert result == ["Red jeans"]

    def test_search_by_name_spelling_mistake(self) -> None:
        result = search("Jaens")
        assert result == ["Red jeans"]

    def test_search_by_name_spelling_mistake_redd(self) -> None:
        result = search("redd")
        assert result == ["Red jeans", "Red t-shirt"]


class TestListUserProducts:
    def test_list_user_products(self) -> None:
        purchase_product(2, 1, 1)
        purchase_product(1, 1, 1)
        result = list_user_products(1)
        assert result == [
            "Fjallraven - Foldsack No. 1 Backpack, Fits 15 inches Laptops",
            "Mens Casual Premium Slim Fit T-Shirts",
        ]


class TestListProductsPerTag:
    def test_list_products_per_tag(self) -> None:
        result = list_products_per_tag(7)
        assert result == [
            "Mens Casual Premium Slim Fit T-Shirts",
            "Mens Casual Slim Fit longsleef",
        ]


class TestListProductsPerTagNoTag:
    def test_list_products_per_tag_no_tag(self) -> None:
        result = list_products_per_tag(50)
        assert result == []


class TestUpdateStock:
    def test_update_stock(self, capsys) -> None:
        assert Product.get_by_id(1).quantity_in_stock != 20
        update_stock(1, 20)
        assert Product.get_by_id(1).quantity_in_stock == 20
        update_stock(100, 1)
        captured = capsys.readouterr()
        assert captured.out == "Product id not found!\n"


class TestPurchasesProduct:
    def test_product_out_of_stock(self, capsys) -> None:
        purchase_product(1, 1, 21)
        captured = capsys.readouterr()
        assert captured.out == "Not enough in stock\n"

    def test_purchases_product_stock_update(self) -> None:
        assert Product.get_by_id(2).quantity_in_stock == 9
        purchase_product(2, 2, 5)
        assert Product.get_by_id(2).quantity_in_stock == 4

    def test_purchases_added_to_user(self) -> None:
        result = User.get_by_id(2).products_owned
        assert [item.name for item in result] == [
            "Mens Casual Premium Slim Fit T-Shirts"
        ]
        purchase_product(4, 2, 1)
        result = User.get_by_id(2).products_owned
        assert [item.name for item in result] == [
            "Mens Casual Premium Slim Fit T-Shirts",
            "Mens Casual Slim Fit longsleef",
        ]


class TestRemoveProduct:
    def test_remove_product(self, capsys) -> None:
        remove_product(2)
        captured = capsys.readouterr()
        assert captured.out == ""
        remove_product(2)
        captured = capsys.readouterr()
        assert captured.out == "No product find for this product id!\n"


class TestAddProductToCatalog:
    def test_add_product_to_catalog(self):
        add_product_to_catalog(
            2,
            name="SanDisk SSD PLUS 1TB Internal SSD - SATA III 6 Gb/s",
            description="Easy upgrade for faster boot up, shutdown, application load and response (As compared to 5400 RPM SATA 2.5” hard drive; Based on published specifications and internal benchmarking tests using PCMark vantage scores) Boosts burst write performance, making it ideal for typical PC workloads The perfect balance of performance and reliability Read/write speeds of up to 535MB/s/450MB/s (Based on internal testing; Performance may vary depending upon drive capacity, host device, OS and application.)",
            price=109,
            quantity=5,
            tags=["electronics", "SSD"],
        )
        result = User.get_by_id(2).products_owned
        assert [item.name for item in result] == [
            "Mens Casual Slim Fit longsleef",
            "SanDisk SSD PLUS 1TB Internal SSD - SATA III 6 Gb/s",
        ]
