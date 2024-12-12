from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum
from django.http import JsonResponse
from django.db import transaction
from .models import cartSelection
import pandas as pd
from .models import Product
import csv
import os
import json
from django.conf import settings
from django.contrib.auth.models import User


def load_products():
    products = []
    json_file_path = 'products.json' 

    with open(json_file_path, 'r', encoding='utf-8') as file:
        products = json.load(file) 
    
    return products

def search(request):
    products = []
    json_file_path = 'products.json'  

    with open(json_file_path, newline='', encoding='utf-8') as jsonfile:
        products = json.load(jsonfile)  

    query = request.GET.get('query', '').lower()  
    print(query)
    filtered_products = []

    if query:
        filtered_products = [
            product for product in products
            if query in product['name'].lower() or query in product['description'].lower()
        ]

    return render(request, 'shop/product_page.html', {'products': filtered_products, 'query': query})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')  
        password = request.POST.get('password')  
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user) 
            return redirect('store_selection') 
        else:
            return render(request, 'shop/login_page.html', {'error_message': 'Invalid credentials'})

    return render(request, 'shop/login_page.html')

def products_page(request):
    print("selected1")
    SORTMAPPER = {'name_a_to_z': 'name_asc', 'price_low_to_high': 'price_asc'}
    sort_by = request.POST.get('sort_by', 'name_asc')
    json_file_path = 'products.json'
    products = []


    with open(json_file_path, 'r', encoding='utf-8') as jsonfile:
        products = json.load(jsonfile)

    if sort_by == 'name_asc':
        products = sorted(products, key=lambda x: x['name'].lower())
    elif sort_by == 'price_asc':
        products = sorted(products, key=lambda x: x['price'])
    if request.method == 'POST':
        name = request.POST.get('product_id')
        quantity_selected = int(request.POST.get(f'quantity_{name}', 1))
        for eachProduct in products:
            if name == eachProduct['name']:
                if eachProduct['quantity'] >= quantity_selected:
                    eachProduct['quantity'] -= quantity_selected
                    cartSelection.objects.create(
                        name=name,
                        description=eachProduct['description'],
                        price=eachProduct['price'],
                        quantity=quantity_selected,
                        img = eachProduct["image"]
                    )
                    print(f"Added {quantity_selected} of {name} to the cart.")
                elif eachProduct['quantity'] == 0:
                    print(f"Cannot add {name}: Out of stock.")
                else:
                    print(f"Cannot add {name}: Only {eachProduct['quantity']} available.")
        with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(products, jsonfile, ensure_ascii=False, indent=4)
    total_quantity = cartSelection.objects.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    print(total_quantity)
    return render(request, 'shop/product_page.html', {'products': products, 'sort_by': sort_by, 'cart_count': total_quantity})

def sortby(request):

    SORTMAPPER = {'name_a_to_z':'name_asc', 'price_low_to_high':'price_asc'}
    sort_by = request.POST.get('sort_by')
    products = []
    json_file_path = 'products.json' 
    with open(json_file_path, newline='', encoding='utf-8') as jsonfile:
        products = json.load(jsonfile)  

    if SORTMAPPER.get(sort_by, 'name_asc') == 'name_asc':
        products = sorted(products, key=lambda x: x['name'])
    elif SORTMAPPER.get(sort_by) == 'price_asc':
        products = sorted(products, key=lambda x: x['price'])  

    return render(request, 'shop/product_page.html', {'products': products, 'sort_by': sort_by})

def store_selection(request):
    print("selected")
    SORTMAPPER = {'name_a_to_z': 'name_asc', 'price_low_to_high': 'price_asc'}
    sort_by = request.POST.get('sort_by', 'name_asc')
    json_file_path = 'products.json'
    products = []
    with open(json_file_path, 'r', encoding='utf-8') as jsonfile:
        products = json.load(jsonfile)
    if sort_by == 'name_asc':
        products = sorted(products, key=lambda x: x['name'].lower())
    elif sort_by == 'price_asc':
        products = sorted(products, key=lambda x: x['price'])
    if request.method == 'POST':
        name = request.POST.get('product_id')
        quantity_selected = int(request.POST.get(f'quantity_{name}', 1))
        for eachProduct in products:
            if name == eachProduct['name']:
                if eachProduct['quantity'] >= quantity_selected:
                    eachProduct['quantity'] -= quantity_selected
                    cartSelection.objects.create(
                        name=name,
                        description=eachProduct['description'],
                        price=eachProduct['price'],
                        quantity=quantity_selected,
                        img = eachProduct["image"]
                    )
                    print(f"Added {quantity_selected} of {name} to the cart.")
                elif eachProduct['quantity'] == 0:
                    print(f"Cannot add {name}: Out of stock.")
                else:
                    print(f"Cannot add {name}: Only {eachProduct['quantity']} available.")
        with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(products, jsonfile, ensure_ascii=False, indent=4)
    total_quantity = cartSelection.objects.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    print(total_quantity)
    return render(request, 'shop/product_page.html', {'products': products, 'sort_by': sort_by, 'cart_count': total_quantity})

def update_quantity(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        action = request.POST.get("action")
        try:
            cart_item = cartSelection.objects.get(id=product_id)
        except cartSelection.DoesNotExist:
            return redirect('cart_page') 
        json_file_path = 'products.json'
        with open(json_file_path, 'r', encoding='utf-8') as jsonfile:
            products = json.load(jsonfile)
        product = next((item for item in products if item['name'] == cart_item.name), None)
        if product:
            max_quantity_available = product['quantity']
            product_quantity_change = 0
            if action == "increase" and cart_item.quantity < max_quantity_available:
                product_quantity_change = 1
                cart_item.quantity += 1

            elif action == "decrease" and cart_item.quantity > 1:
                product_quantity_change = -1
                cart_item.quantity -= 1
            elif action == "remove" or (cart_item.quantity == 1 and action == "decrease"):
                product_quantity_change = cart_item.quantity 
                cart_item.delete() 
                for item in products:
                    if item['name'] == cart_item.name:
                        item['quantity'] += product_quantity_change

                with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
                    json.dump(products, jsonfile, ensure_ascii=False, indent=4)
                
                return redirect('cart_page')
            cart_item.save()
            for item in products:
                if item['name'] == cart_item.name:
                    item['quantity'] = int(item['quantity']) 
                    item['quantity'] -= product_quantity_change
            with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(products, jsonfile, ensure_ascii=False, indent=4)

        return redirect('cart_page')

def display_selection(request):
    selections = cartSelection.objects.all()
    return render(request, 'display_selection.html', {'selections': selections})



def cart_page(request):
    selections = cartSelection.objects.all()
    #print(selections)
    total_price = sum(each_selection.price * each_selection.quantity for each_selection in selections)
    #print(total_price)
    return render(request, 'shop/cart.html', {'cart': selections, 'total': total_price})

def thank_you_page(request):
    selections = cartSelection.objects.all()
    items = [{'name': item.name, 'price': item.price} for item in selections]
    #print(items)
    total = sum(float(item.price) for item in selections)
    with transaction.atomic():
        cartSelection.objects.all().delete()
    return render(request, 'shop/thankyou.html', {'items': items, 'total': total})


def logout_user(request):
    logout(request)
    return redirect('login')


def delete_from_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        try:
            cart_item = cartSelection.objects.get(id=product_id)
            cart_item.delete()
        except cartSelection.DoesNotExist:
            pass 
    return redirect('cart_page')