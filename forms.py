from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,SelectField,IntegerField
from wtforms.validators import DataRequired
from vrbs import AppVariables
class LoginForm(FlaskForm):
     username = StringField('Username', validators=[DataRequired()])
     password= PasswordField('Password',validators=[DataRequired()])
     submit=SubmitField('Sign In')


class UpdateForm(FlaskForm):
    pl=AppVariables.productlist
    p2=AppVariables.locationlist
    productname=SelectField('Select Product', choices=pl, validators=[DataRequired()])
    location=SelectField('Select Location', choices=p2, validators=[DataRequired()])
    quantity=IntegerField('Quantity',validators=[DataRequired()])      
    submit=SubmitField('Add')

class RemoveForm(FlaskForm):
    pl=AppVariables.productlist
    p2=AppVariables.locationlist
    productname=SelectField('Select Product', choices=pl, validators=[DataRequired()])
    #location=SelectField('Select Location', choices=p2, validators=[DataRequired()])
    quantity=IntegerField('Quantity',validators=[DataRequired()])      
    submit=SubmitField('Remove')

class ViewForm(FlaskForm):
	what_to_display=SelectField('Select Filter',choices=[('1','All Contents'),('2', 'By Location'), ('3', 'By Category'), ('4', 'By Expiry')])
	submit=SubmitField('View')

class LogoutForm(FlaskForm):
    logoutbutton=SubmitField('Log Out')

class ShoppingListForm(FlaskForm):
    x=SelectField('View by', choices=[('0', 'Quantity'),('1','Expiry')])
    submit=SubmitField('View')
