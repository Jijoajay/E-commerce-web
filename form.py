from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, SearchField, PasswordField, IntegerField, URLField, \
    SelectField
from wtforms.validators import DataRequired, URL


class ContactFrom(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    number = IntegerField('Number', validators=[DataRequired()])
    message = StringField('Enter the message', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Submit', validators=[DataRequired()])
    submit = SubmitField('Submit')


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ProductForm(FlaskForm):
    name = StringField('Shoe Name', validators=[DataRequired()])
    price = StringField('Discounted Price', validators=[DataRequired()])
    og_price = StringField('Original Price', validators=[DataRequired()])
    img_url = URLField('Img_url,', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SearchBar(FlaskForm):
    search = SearchField()
    # submit = SubmitField('Submit')


list = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)


class QuantityForm(FlaskForm):
    quantity = SelectField('Quantity', choices=list)
    cart_submit = SubmitField('Add to Cart')


class AddressForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    street_address = StringField('Street Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    pin_code = IntegerField('Pin code', validators=[DataRequired()])
    submit = SubmitField('Save Address', validators=[DataRequired()])
