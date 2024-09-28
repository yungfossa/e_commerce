from admin import Admin
from seller import Seller
from user import User

admin = Admin.login("admin@shopsphere.com", "changeme")
admin.reset_db()
admin.add_category("Food")
admin.add_category("Drugs")
admin.add_category("Garden")

products = [
    (
        "Pot",
        "Not the drug",
        "https://media.istockphoto.com/id/1298515744/it/foto/vaso-di-fiori-vuoto.jpg?s=1024x1024&w=is&k=20&c=zuJOZd4I7w9gn_8Q_KeDM_kqApZ6GGtZfjejITph7OI=",
        "Garden",
        [
            (("sales@amazon.com", "changeme"), (10, 19.99, "new")),
        ],
    ),
    (
        "Flowers",
        "A flower",
        "https://media.istockphoto.com/id/526039805/it/foto/lucky-bamb%C3%B9.jpg?s=2048x2048&w=is&k=20&c=z2MXWWcWpyyw1G8uoqJ5YFV30cHdZJ_Hvxz9t4OjPcA=",
        "Garden",
        [
            (("sales@amazon.com", "changeme"), (5, 39.99, "new")),
        ],
    ),
    (
        "Meat",
        "Mlmlml",
        "https://media.istockphoto.com/id/1162717440/it/foto/pila-di-cubetti-di-manzo-isolati-su-bianco.jpg?s=2048x2048&w=is&k=20&c=izUSXR_n7absKOtGBRdPT7gg1E_9lAlshtdoiG9JU1w=",
        "Food",
        [
            (("sales@amazon.com", "changeme"), (100, 9.85, "new")),
            (("sales@google.com", "changeme"), (1, 99.99, "new")),
        ],
    ),
    (
        "Watr",
        "Mlmlml?",
        "https://media.istockphoto.com/id/614012030/cs/fotografie/mlad%C3%A1-%C5%BEena-pije-sklenici-vody.jpg?s=2048x2048&w=is&k=20&c=WdAEQoAMlC5e0PMr4o8hQ_uE0ufiEd0q5y83q1rBiwk=",
        "Food",
        [
            (("sales@google.com", "changeme"), (1, 99.99, "new")),
        ],
    ),
]

for name, description, image, category, listings in products:
    (product, _) = admin.add_product(name, description, image, category)
    product_id = product["id"]

    for listing in listings:
        ((email, password), (count, price, quality)) = listing

        seller = Seller.login(email, password)
        (lr, _) = seller.create_listing(product_id, count, price, quality)
        listing_id = lr["id"]

customer = User.create("bar@gmail.com", "Password1?", "bar", "bar")
review = customer.create_review(
    product_id, listing_id, "Not great", "Not terrible", "3"
)

# customer = User.force_login("foo@gmail.com", "Password1?").create_review(
#     product_id, listing_id, "Not great", "Not terrible", "5"
# )
