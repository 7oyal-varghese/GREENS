from django.urls import path
from .views import home,add_product,product_list,add_to_cart, view_cart, increase_quantity, decrease_quantity, remove_from_cart,checkout,order_success,admin_orders

urlpatterns = [
    path('', home, name='home'),
    path("add-product/", add_product, name="add_product"),
    path("products/", product_list, name="product_list"),
    path("add-to-cart/<str:product_id>/", add_to_cart, name="add_to_cart"),
    path("cart/", view_cart, name="view_cart"),
    path("cart/increase/<str:product_id>/", increase_quantity, name="increase_quantity"),
    path("cart/decrease/<str:product_id>/", decrease_quantity, name="decrease_quantity"),
    path("cart/remove/<str:product_id>/", remove_from_cart, name="remove_from_cart"),
    path("checkout/", checkout, name="checkout"),
    path("order-success/", order_success, name="order_success"),
    path("dashboard/orders/", admin_orders, name="admin_orders"),






]
