from django.shortcuts import render, get_object_or_404
from .models import Item, Order, OrderItem
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home-page.html"


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"


# @login_required
class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'Object': order,
            }
            return render(self.request, "order_summary.html", context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an activate order")
            return redirect("/")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated to cart")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was added to cart")
            order.items.add(order_item)
            return redirect("core:order-summary")

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to cart")
        return redirect("core:product", slug=slug)


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was remove from your cart")
            return redirect("core:order-summary")
        else:
            # add message saying the user doesnt dave an order
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        # add message the user doesnt have an order
        messages.info(request, "You do not have active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated")
            return redirect("core:order-summary")
        else:
            # add message saying the user doesnt dave an order
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        # add message the user doesnt have an order
        messages.info(request, "You do not have active order")
        return redirect("core:product", slug=slug)


def checkout(request):
    return render(request, "checkout-page.html")
