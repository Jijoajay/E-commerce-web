from flask import Flask, render_template, request, redirect, url_for, flash, abort
from sqlalchemy.orm import relationship
from form import ContactFrom, LoginForm, RegisterForm, ProductForm, SearchBar, QuantityForm, AddressForm
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, UserMixin, login_user, logout_user
from functools import wraps
from flask_gravatar import Gravatar
import stripe

app = Flask(__name__)
app.config['SECRET_KEY'] = '1234'
Bootstrap(app)

# stripe api_key
app.config[
    'STRIPE_PUBLIC_KEY'] = "pk_test_51No0dvSJ3G54P1mWngbUjowDqPnkPXisiwUSmxzSaN5EpW9SJaEQpfFGuQPxpNBwMjYpANrCCwzuHEy0Jqw8sYPw00JRN94VKh"
app.config[
    'STRIPE_API_KEY'] = "sk_test_51No0dvSJ3G54P1mW5EShkwMsialXkmB0TpxKyuh6y2c9bSHI0996lFjDsUUY0tmCtz0BhpimCZs8RAu8Of7SZz0w00BYPOiUFB"
my_domain = ' http://127.0.0.1:909'

# db connection
app.config['SQLALCHsEMY_DATABASE_URI'] = 'sqlite:///store_website.db'
db = SQLAlchemy(app)  # initialized the flask into the database

# login connection
login_manager = LoginManager(app)


@login_manager.user_loadder
def load_user(user_id):
    return StoreUser.query.get(int(user_id))


@app.context_processor
def base():
    form = SearchBar()
    return dict(searched_form=form)


# create search function
@app.route('/search', methods=['POST'])
def search():
    form = SearchBar()
    if form.validate_on_submit():
        searched = request.form.get('search')
        searched_product = ProductInfo.query.filter(ProductInfo.product_name.ilike(f"%{searched}%")).all()
        return render_template("search.html", form=form, search=searched,searched=searched_product)


# adding profile img to users
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None
                    )


class StoreUser(UserMixin, db.Model):
    __tablename__ = "store_user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    carts = relationship("CartInfo", back_populates="user")
    favourites = relationship("FavouriteInfo", back_populates="user")
    address_detail = relationship("AddressDetail", back_populates="user")
    product = relationship("ProductInfo", back_populates="user")


class ProductInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(250), nullable=False)
    product_price = db.Column(db.Integer, nullable=False)
    original_price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey("store_user.id"), nullable=False)
    user = relationship("StoreUser", back_populates="product")


class CartInfo(db.Model):
    __tablename__ = "cart_info"
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(250), nullable=False)
    product_price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    cart_user_id = db.Column(db.Integer, db.ForeignKey("store_user.id"), nullable=False)
    user = relationship('StoreUser', back_populates="carts")


class FavouriteInfo(db.Model):
    __tablename__ = "favourite_info"
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(250), nullable=False)
    product_price = db.Column(db.Integer, nullable=False)
    original_price = db.Column(db.Integer, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    favour_user_id = db.Column(db.Integer, db.ForeignKey('store_user.id'), nullable=False)
    user = relationship('StoreUser', back_populates="favourites")


class AddressDetail(db.Model):
    __tablename__ = "address_detail"
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(250), nullable=False)
    last_name = db.Column(db.String(250), nullable=False)
    street_address = db.Column(db.String(250), nullable=False)
    city = db.Column(db.String(250), nullable=False)
    state = db.Column(db.String(250), nullable=False)
    pin_code = db.Column(db.Integer(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('store_user.id'), nullable=False)
    user = relationship('StoreUser', back_populates="address_detail")


with app.app_context():
    db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@app.route('/', methods=['POST', 'GET'])
def home():
    result = db.session.execute(db.select(StoreUser.id))
    users = result.scalar()
    return render_template('index.html', current_user=current_user)


@app.route('/about')
def about():
    return render_template('about.html', current_user=current_user)


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    form = ContactFrom()
    if request.method == 'POST':
        new_contact = {
            'name': request.form['name'],
            'email': request.form['email'],
            'number': request.form['number'],
            'message': request.form['message']
        }
        flash('The message sent successfully')
        return render_template('contact.html')
    return render_template('contact.html', form=form, current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_pass = db.session.execute(db.select(StoreUser).where(StoreUser.password == request.form['password']))
        password = user_pass.scalar()
        result = db.session.execute(db.select(StoreUser).where(StoreUser.email == request.form['email']))
        user = result.scalar()
        if not user:
            flash('first please register the account')
            return redirect(url_for('register'))
        elif not password:
            print(password)
            flash('please enter the correct password')
        else:
            login_user(user)
            flash(f'Welcome {current_user.name}')
            return redirect(url_for('home'))
    return render_template('login.html', form=form, current_user=current_user)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        result = db.session.execute(db.select(StoreUser).where(StoreUser.email == request.form['email']))
        user = result.scalar()
        if user:
            flash("this account is already exists..please sign in..")
        else:
            new_user = StoreUser(
                name=request.form['name'],
                email=request.form['email'],
                password=request.form['password']
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
    return render_template('register.html', form=form, current_user=current_user)


@app.route('/log-out')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/add', methods=['POST', 'GET'])
@admin_only
def add():
    form = ProductForm()
    if request.method == 'POST':
        new_product = ProductInfo(
            product_name=request.form['name'],
            product_price=request.form['price'],
            original_price=request.form['og_price'],
            img_url=request.form['img_url'],
            category=request.form['category'],
            user_id=current_user.id
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('product'))
    return render_template('add.html', form=form, current_user=current_user)


@app.route('/edit/<int:post_id>', methods=['POST', 'GET'])
@admin_only
def edit(post_id):
    post = db.get_or_404(ProductInfo, post_id)
    form = ProductForm(
        product_name=post.product_name,
        product_price=post.product_price,
        img_url=post.img_url
    )
    if request.method == 'POST':
        post.product_name = request.form['name']
        post.product_price = request.form['price']
        original_price = request.form['og_price']
        post.img_url = request.form['img_url']
        db.session.commit()
        return redirect(url_for('product', post_id=post.id))
    return render_template('add.html', form=form, is_edit=True, current_user=current_user)


@app.route('/delete/<int:post_id>')
@admin_only
def delete(post_id):
    delete_post = db.get_or_404(ProductInfo, post_id)
    db.session.delete(delete_post)
    db.session.commit()
    return redirect(url_for('product', post_id=post_id))


@app.route('/view/<int:post_id>', methods=['POST', 'GET'])
def view(post_id):
    # getting the particular product by post_id
    post = db.get_or_404(ProductInfo, post_id)
    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        print(f'{quantity};view-quantity')
        new_item = ProductInfo(
            product_name=post.product_name,
            product_price=post.product_price,
            quantity=quantity
        )
        db.session.add(new_item)
        db.session.commit()
        flash("product added to the cart")
        print("current quantity:", quantity)
        return redirect(url_for('product'))
    return render_template("view.html", post=post, current_user=current_user)


@app.route('/products', methods=['GET', 'POST'])
def product():
    result = db.session.execute(db.select(ProductInfo))
    post = result.scalars().all()
    return render_template('product.html', all_post=post, current_user=current_user)


# adding cart to the web


@app.route('/cart_add/<int:post_id>', methods=['GET', 'POST'])
def cart_add(post_id):
    cart_post = db.get_or_404(ProductInfo, post_id)
    new_item = CartInfo(
        product_name=cart_post.product_name,
        product_price=cart_post.product_price,
        quantity=cart_post.quantity,
        cart_user_id=current_user.id
    )
    print("new_item.cart_user_id:", new_item.cart_user_id)
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('product'))


@app.route('/cart_read')
def cart_read():
    user_id = current_user.id
    cart_items = CartInfo.query.filter_by(cart_user_id=user_id).all()
    product_name = [item.product_name for item in cart_items]
    print(f'{product_name:}cart_read')
    total = sum(item.product_price * item.quantity for item in cart_items)
    return render_template('cart.html', total_amount=total, cart=cart_items, current_user=current_user)


@app.route('/cart_delete/<int:post_id>')
def cart_delete(post_id):
    delete_post = CartInfo.query.get_or_404(post_id)
    db.session.delete(delete_post)
    db.session.commit()
    return redirect(url_for('cart_read'))


@app.route('/favourites')
def favourites():
    favor_items = FavouriteInfo.query.filter_by(favour_user_id=current_user.id).all()
    return render_template('favourites.html', all_post=favor_items, current_user=current_user)


@app.route('/add_favourite/<int:post_id>', methods=['POST', 'GET'])
def add_to_favor(post_id):
    productt = db.get_or_404(ProductInfo, post_id)
    new_favor = FavouriteInfo(
        product_name=productt.product_name,
        product_price=productt.product_price,
        img_url=productt.img_url,
        original_price=productt.original_price,
        quantity=productt.quantity,
        favour_user_id=current_user.id)
    db.session.add(new_favor)
    db.session.commit()
    return redirect(url_for('product'))
    # flash("the product added to the favourite")


@app.route('/favor_delete/<int:post_id>')
def favor_delete(post_id):
    delete_post = FavouriteInfo.query.get_or_404(post_id)
    db.session.delete(delete_post)
    db.session.commit()
    return redirect(url_for('favourites'))


@app.route('/user_account', methods=['POST', 'GET'])
def customers():
    print(current_user.email)
    return render_template('customer.html', current_user=current_user)


@app.route('/address', methods=['POST', 'GET'])
def address():
    form = AddressForm()
    if form.validate_on_submit():
        user_address = AddressDetail(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            street_address=request.form['street_address'],
            city=request.form['city'],
            state=request.form['state'],
            pin_code=request.form['pin_code'],
            user_id=current_user.id
        )
        db.session.add(user_address)
        db.session.commit()
        flash('successfully saved the address')
        return redirect(url_for("customers"))
    return render_template('address.html', form=form)


@app.route('/address_read')
def address_read():
    address = AddressDetail.query.filter_by(user_id=current_user.id).all()
    return render_template('address_read.html', users_address=address)


@app.route('/address_edit/<int:post_id>')
def address_edit(post_id):
    post = db.get_or_404(AddressDetail, post_id)
    form = AddressForm(
        first_name=post.first_name,
        last_name=post.last_name,
        street_address=post.street_address,
        city=post.city,
        state=post.state,
        pin_code=post.pin_code,
    )
    if request.method == 'POST':
        post.first_name = request.form['first_name']
        post.last_name = request.form['last_name']
        post.street_address = request.form['street_address']
        post.city = request.form['city']
        post.state = request.form['state']
        post.pin_code = request.form['pin_code']
        db.session.commit()
        return redirect(url_for('customers', post_id=post.id))
    return render_template('address.html', is_edit=True, form=form)


@app.route('/address_delete/<int:post_id>')
def address_delete(post_id):
    post_to_delete = db.get_or_404(AddressDetail, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('address_read'))


@app.route('/payment')
def payment():
    return render_template('payment.html')


@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/cancel')
def cancel():
    return render_template("cancel.html")


@app.route('/checkout-session')
def checkout_session():
    stripe.api_key = app.config['STRIPE_API_KEY']
    user_id = current_user.id
    cart_items = CartInfo.query.filter_by(cart_user_id=user_id).all()
    total = sum(item.product_price for item in cart_items)
    total_quantity = sum(item.quantity for item in cart_items)
    product_name = [item.product_name for item in cart_items]

    if len(product_name) > 1:
        product_id = stripe.Product.create(name="nike shoes")
    else:
        product_id = stripe.Product.create(name=product_name[0])

    print(product_id)
    price_id = stripe.Price.create(
        unit_amount=total * 100,
        currency="inr",
        product=product_id,
    )
    session = stripe.checkout.Session.create(
        line_items=[{
            'price': price_id,
            'quantity': total_quantity,
        }],
        mode='payment',
        success_url='https://127.0.0.1:909/success',
        cancel_url='https://127.0.0.1:909/cancel'
    )
    return redirect(session.url, code=303)


@app.route('/sneakers')
def sneakers():
    product = ProductInfo.query.filter_by(category="sneakers").all()
    print(product)
    return render_template("sneakers.html", all_post=product)


@app.route('/high-tops')
def high_tops():
    post = ProductInfo.query.filter_by(category="hightops").all()
    return render_template("hightops.html", all_post=post)


@app.route('/sports')
def sports():
    post = ProductInfo.query.filter_by(category="sports").all()
    return render_template("sports.html", all_post=post)


if __name__ == '__main__':
    app.run(debug=True, port=909)
