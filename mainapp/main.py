from flask import render_template, request, session, redirect, jsonify
from mainapp import app, utils
from mainapp.filters import *
from mainapp import login
from mainapp.models import User
from flask_login import login_user, login_manager


@app.route("/")
def index():
    categories = ["ALL", "VĂN HỌC", "KINH TẾ", "SÁCH THIẾU NHI", "SÁCH NGOẠI NGỮ"]
    kw = request.args.get("keyword")
    if kw:
        result = []
        for cat in categories:
            if cat in categories(kw) >= 0:
                result.append(cat)
    else:
        result = categories
    return render_template('index.html', categories=result)


@app.route("/<int:id>")
def index2(id):
    if id == 1:
        return render_template('index.html', categories=["VĂN HỌC", "KINH TẾ"])
    else:
        return render_template('index.html', categories=["SÁCH THIẾU NHI", "SÁCH NGOẠI NGỮ"])


@app.route('/products')
def product_list():
    books = utils.read_book()
    return render_template('product-list.html', books=books)


@app.route('/product-economic')
def product_list_economic():
    books = utils.read_book()
    return render_template('product-economy.html', books=books)


@app.route('/product-literature')
def product_list_literature():
    books = utils.read_book()
    return render_template('product-literature.html', books=books)


@login.user_loader
def get_user(user_id):
    return User.query.get(user_id)  # select * from User where id = userid


@app.route('/login', methods=['get', 'post'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter(User.username == username,
                                 User.password == password).first()
        if user:
            login_user(user=user)
    return redirect('/admin')  # neu method = get


@app.route('/api/cart', methods=['get', 'post'])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    data = request.json
    id = str(data.get('id'))
    name = data.get('name')
    price = data.get('price')

    if id in cart:
        cart[id]['quantity'] = cart[id]['quantity']+1
    else:
        cart[id] = {
            "id": id,
            "name": name,
            "price": price,
            "quantity": 1
        }
    session['cart'] = cart

    total_quan, total_amount = utils.cart_starts(cart)
    # return jsonify({
    #     "total_amount": total_amount,
    #     "total_quantity": total_quan,
    #     "cart": cart
    # })
    return jsonify({
        "total_amount": total_amount,
        "total_quantity": total_quan
    })


@app.route('/pay')
def payment():
    total_quan, total_amount = utils.cart_starts(session.get('cart'))
    return render_template("payment.html", total_amount=total_amount, total_quan=total_quan)


@app.route('/api/pay', methods=['post'])
def pay():
    if 'cart' in session and session['cart']:
        utils.add_receipt(cart=session['cart'])
        del session['cart']

        return jsonify({'message': 'Đã thanh toán'})

    return jsonify({'message': 'failed'})


@app.route('/api/cart/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    if 'cart' in session:
        cart = session['cart']
        if item_id in cart:
            del cart[item_id]
            session['cart'] = cart

            return jsonify({'err_msg': 'Thanh cong',
                            'code': 200,
                            'item_id': item_id
                            })

    return jsonify({'err_msg': 'that bai', 'code': 500})


@app.route('/api/cart/<item_id>', methods=['post'])
def update_item(item_id):
    if 'cart' in session:
        cart = session['cart']
        # du lieu gui len tu bo dy cua ham fetch
        data = request.json
        if item_id in cart and 'quantity' in data:
            cart[item_id]['quantity'] = int(data['quantity'])
            session['cart'] = cart
            total_quan, total_amount = utils.cart_starts(session.get('cart'))
            return jsonify({'err_msg': 'Thanh cong',
                            'code': 200,
                            'total_quantity': total_quan,
                            'total_amount': total_amount
                            })

        return jsonify({'err_msg': 'that bai', 'code': 500})


if __name__ == "__main__":
    from mainapp.admin_module import *
    app.run(debug=True)
