from admin import Admin
from seller import Seller

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
        (10, 19.99, "new"),
    ),
    (
        "Flowers",
        "A flower",
        "https://media.istockphoto.com/id/526039805/it/foto/lucky-bamb%C3%B9.jpg?s=2048x2048&w=is&k=20&c=z2MXWWcWpyyw1G8uoqJ5YFV30cHdZJ_Hvxz9t4OjPcA=",
        "Garden",
        (5, 39.99, "used"),
    ),
    (
        "Meat",
        "Mlmlml",
        "https://media.istockphoto.com/id/1162717440/it/foto/pila-di-cubetti-di-manzo-isolati-su-bianco.jpg?s=2048x2048&w=is&k=20&c=izUSXR_n7absKOtGBRdPT7gg1E_9lAlshtdoiG9JU1w=",
        "Food",
        (100, 9.85, "used"),
    ),
]

seller = Seller.login("sales@amazon.com", "changeme")
for name, description, image, category, listing in products:
    (count, price, quality) = listing

    (product, _) = admin.add_product(name, description, image, category)

    product_id = product["product_id"]
    seller.create_listing(product_id, count, price, quality)
