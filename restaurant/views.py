from django.shortcuts import render

# Create your views here.
from django.http import HttpRequest, HttpResponse
import random
from datetime import datetime, timedelta



def main(request):
    template = 'restaurant/main.html'

    return render(request, template)

def order(request):
    template = 'restaurant/order.html'
    special = random.choice([i for i in DAILY_SPECIAL])

    special_str = DAILY_SPECIAL[special]
    context = {
        'special' : special,
        'special_str' : special_str
    }

    return render(request, template, context)


MEAL_LABELS = {
    'big_mac': 'Big Mac',
    'quarter_pounder': 'Quarter Pounder with Cheese',
    'mcchicken': 'McChicken',
    'filet_o_fish': 'Filet-O-Fish',
    'happy_meal': 'Happy Meal',
}
SIDE_LABELS = {
    'fries': 'Fries',
    'apple_slices': 'Apple Slices',
    'side_salad': 'Side Salad',
    'mozz_sticks': 'Mozzarella Sticks',
}
DRINK_LABELS = {
    'cola': 'Coca-Cola',
    'sprite': 'Sprite',
    'fanta': 'Fanta',
    'iced_tea': 'Iced Tea',
    'water': 'Water',
    'milkshake': 'Milkshake',
}
EXTRA_LABELS = {
    'extra_cheese': 'Extra Cheese',
    'bacon': 'Bacon',
    'lettuce': 'Lettuce',
    'tomato': 'Tomato',
    'onion': 'Onion',
}
DAILY_SPECIAL = {
    'banana_ice_cream' : 'Banana Ice Cream',
    'family_special_combo' : 'Family Special Combo'
}
SIZE = {
    'regular': 'Regular',
    'large': 'Large',
}

# Prices (stored server-side so they can't be tampered with)
MEAL_PRICES = {
    'big_mac': 5.99,
    'quarter_pounder': 6.49,
    'mcchicken': 4.99,
    'filet_o_fish': 5.49,
    'happy_meal': 4.49,
}
SIDE_PRICES = {
    'fries': 1.99,
    'apple_slices': 1.49,
    'side_salad': 2.49,
    'mozz_sticks': 3.49,
}
DRINK_PRICES = {
    'cola': 1.49,
    'sprite': 1.49,
    'fanta': 1.49,
    'iced_tea': 1.49,
    'water': 0.00,
    'milkshake': 2.99,
}
EXTRA_PRICES = {
    'extra_cheese': 0.50,
    'bacon': 1.00,
    'lettuce': 0.25,
    'tomato': 0.25,
    'onion': 0.25,
}
DAILY_SPECIAL_PRICE = {
    'banana_ice_cream' : 2.0,
    'family_special_combo' : 30.0
}
LARGE_UPCHARGE = 1.00


def confirmation(request):
    template = 'restaurant/confirmation.html'
    context = {}

    if request.POST:
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        meal = request.POST.get('meal', '')
        side = request.POST.get('side', '')
        drink = request.POST.get('drink', '')
        daily_special = request.POST.get('daily_special', '')
        extras = request.POST.getlist('extras')
        size = request.POST.get('size', 'regular')
        special_requests = request.POST.get('special_requests', '').strip()

        # Compute total from stored prices
        total = 0.0
        meal_price = MEAL_PRICES.get(meal, 0)
        side_price = SIDE_PRICES.get(side, 0)
        drink_price = DRINK_PRICES.get(drink, 0)
        daily_special_price = DAILY_SPECIAL_PRICE.get(daily_special, 0)
        extras_total = sum(EXTRA_PRICES.get(e, 0) for e in extras)
        size_upcharge = LARGE_UPCHARGE if size == 'large' else 0
        total = meal_price + side_price + drink_price + extras_total + size_upcharge + daily_special_price

        minutes_from_now = random.randint(30, 60)
        ready_datetime = datetime.now() + timedelta(minutes=minutes_from_now)

        context = {
            'name': name,
            'email': email,
            'phone': phone,
            'meal_label': MEAL_LABELS.get(meal, ''),
            'side_label': SIDE_LABELS.get(side, ''),
            'drink_label': DRINK_LABELS.get(drink, ''),
            'extras_labels': [EXTRA_LABELS.get(e, '') for e in extras],
            'size_label': SIZE.get(size, 'Regular'),
            'daily_special_label' : DAILY_SPECIAL.get(daily_special, ''),
            'special_requests': special_requests,
            'ready_time': ready_datetime,
            'meal_price': meal_price,
            'side_price': side_price,
            'drink_price': drink_price,
            'extras_total': extras_total,
            'daily_special_price' : daily_special_price,
            'extras_prices': [(EXTRA_LABELS.get(e, e), EXTRA_PRICES.get(e, 0)) for e in extras],
            'size_upcharge': size_upcharge,
            'total': total,
        }

    return render(request, template, context)