from bson import ObjectId
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .db import products_collection,cart_collection,orders_collection
from datetime import datetime



# Create your views here.
def home(request):
    return render(request,'home.html')



def is_admin(user):
    return user.is_staff

@login_required(login_url='login')
def add_product(request):

    # 🔒 Admin only
    if not request.user.is_staff:
        return redirect("shop")

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        category = request.POST.get("category")
        description = request.POST.get("description")
        image = request.POST.get("image")

        # ✅ Basic validation
        if not name or not price or not category:
            return render(request, "store/add_product.html", {
                "error": "Name, price and category are required"
            })

        # ✅ Prevent null image (fallback)
        if not image:
            image = "https://via.placeholder.com/300x200?text=No+Image"

        product = {
            "name": name,
            "price": int(price),
            "category": category,
            "description": description,
            "image": image,          # ✅ always a string
            "is_available": True,
        }

        products_collection.insert_one(product)
        return redirect("product_list")

    return render(request, "store/add_product.html")



def product_list(request):
    products = list(products_collection.find())

    for product in products:
        product["id"] = str(product["_id"])   # ✅ SAFE for templates

    return render(request, "store/product_list.html", {
        "products": products
    })




@login_required
def add_to_cart(request, product_id):
    user_id = request.user.id
    product = products_collection.find_one({"_id": ObjectId(product_id)})

    if not product:
        return redirect("store")

    cart = cart_collection.find_one({"user_id": user_id})

    if cart:
        # Check if product already in cart
        for item in cart["items"]:
            if item["product_id"] == str(product["_id"]):
                cart_collection.update_one(
                    {"user_id": user_id, "items.product_id": str(product["_id"])},
                    {"$inc": {"items.$.quantity": 1}}
                )
                break
        else:
            cart_collection.update_one(
                {"user_id": user_id},
                {"$push": {
                    "items": {
                        "product_id": str(product["_id"]),
                        "name": product["name"],
                        "price": product["price"],
                        "quantity": 1,
                        "image": product.get("image")
                    }
                }}
            )
    else:
        cart_collection.insert_one({
            "user_id": user_id,
            "items": [{
                "product_id": str(product["_id"]),
                "name": product["name"],
                "price": product["price"],
                "quantity": 1,
                "image": product.get("image")
            }]
        })

    return redirect("view_cart")


@login_required
def view_cart(request):
    cart = cart_collection.find_one({"user_id": request.user.id})
    items = cart["items"] if cart else []

    for item in items:
        item["item_total"] = item["price"] * item["quantity"]

    total = sum(item["item_total"] for item in items)

    return render(request, "store/cart.html", {
        "items": items,
        "total": total
    })

@login_required
def increase_quantity(request, product_id):
    cart_collection.update_one(
        {"user_id": request.user.id, "items.product_id": product_id},
        {"$inc": {"items.$.quantity": 1}}
    )
    return redirect("view_cart")


@login_required
def decrease_quantity(request, product_id):
    cart = cart_collection.find_one({"user_id": request.user.id})

    if not cart:
        return redirect("view_cart")

    for item in cart["items"]:
        if item["product_id"] == product_id:
            if item["quantity"] > 1:
                cart_collection.update_one(
                    {"user_id": request.user.id, "items.product_id": product_id},
                    {"$inc": {"items.$.quantity": -1}}
                )
            else:
                cart_collection.update_one(
                    {"user_id": request.user.id},
                    {"$pull": {"items": {"product_id": product_id}}}
                )
            break

    return redirect("view_cart")

@login_required
def remove_from_cart(request, product_id):
    cart_collection.update_one(
        {"user_id": request.user.id},
        {"$pull": {"items": {"product_id": product_id}}}
    )
    return redirect("view_cart")


def checkoutpage(request):
    return render(request,'store/checkout.html')



@login_required
def checkout(request):
    cart = cart_collection.find_one({"user_id": request.user.id})

    if not cart or not cart.get("items"):
        return redirect("view_cart")

    items = cart["items"]
    total = sum(item["price"] * item["quantity"] for item in items)

    if request.method == "POST":
        address = request.POST.get("address")
        phone = request.POST.get("phone")

        if not address or not phone:
            return render(request, "store/checkout.html", {
                "items": items,
                "total": total,
                "error": "All fields are required"
            })

        order = {
            "user_id": request.user.id,
            "items": items,
            "total_amount": total,
            "address": address,
            "phone": phone,
            "status": "Placed",
            "created_at": datetime.now()
        }

        orders_collection.insert_one(order)

        # 🧹 Clear cart after order
        cart_collection.delete_one({"user_id": request.user.id})

        return redirect("order_success")

    return render(request, "store/checkout.html", {
        "items": items,
        "total": total
    })

@login_required
def order_success(request):
    return render(request, "store/order_success.html")


@login_required
def admin_orders(request):
    if not request.user.is_staff:
        return redirect("home")

    orders = list(orders_collection.find().sort("created_at", -1))

    # Convert ObjectId to string (safe for templates)
    for order in orders:
        order["id"] = str(order["_id"])

    return render(request, "store/view_orders.html", {
        "orders": orders
    })
