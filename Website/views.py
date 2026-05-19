from flask import Blueprint, render_template, request, flash, jsonify, session, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, Product, Category
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


# --- E-commerce routes ---


@views.route('/shop')
def shop():
    categories = Category.query.order_by(Category.name).all()
    products = Product.query.order_by(Product.name).all()
    return render_template('shop.html', categories=categories, products=products)


@views.route('/category/<int:category_id>')
def category_page(category_id):
    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category.id).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template('category.html', category=category, products=products, categories=categories)


@views.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_page(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        qty = int(request.form.get('quantity', 1))
        cart = session.get('cart', {})
        cart[str(product.id)] = cart.get(str(product.id), 0) + max(1, qty)
        session['cart'] = cart
        flash('Added to cart', category='success')
        return redirect(url_for('views.cart'))
    return render_template('product.html', product=product)


@views.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    data = request.form or request.json or {}
    product_id = data.get('product_id')
    qty = int(data.get('quantity', 1))
    if not product_id:
        return jsonify({'error': 'missing product_id'}), 400
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + max(1, qty)
    session['cart'] = cart
    return jsonify({'success': True, 'cart': cart})


@views.route('/cart')
def cart():
    cart = session.get('cart', {})
    items = []
    total = 0.0
    for pid, qty in cart.items():
        prod = Product.query.get(int(pid))
        if not prod:
            continue
        subtotal = prod.price * qty
        items.append({'product': prod, 'qty': qty, 'subtotal': subtotal})
        total += subtotal
    return render_template('cart.html', items=items, total=total)


@views.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', category='error')
        return redirect(url_for('views.shop'))
    if request.method == 'POST':
        # Simulate payment processing (placeholder)
        name = request.form.get('name')
        card = request.form.get('card')
        if not name or not card:
            flash('Please enter payment details.', category='error')
            return redirect(url_for('views.checkout'))
        # Clear cart
        session['cart'] = {}
        flash('Payment successful! Thank you for your purchase.', category='success')
        return redirect(url_for('views.shop'))
    # show checkout form
    return render_template('checkout.html')