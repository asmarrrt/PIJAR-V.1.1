from flask_wtf import FlaskForm
from wtforms import EmailField,PasswordField,StringField
from wtforms.validators import DataRequired,Email,Length,EqualTo
class LoginForm(FlaskForm):
    email=EmailField("Email",validators=[DataRequired(),Email()])
    password=PasswordField("Password",validators=[DataRequired()])
class RegisterForm(FlaskForm):
    full_name=StringField("Nama lengkap",validators=[DataRequired(),Length(min=2,max=150)])
    email=EmailField("Email",validators=[DataRequired(),Email(),Length(max=255)])
    password=PasswordField("Password",validators=[DataRequired(),Length(min=8,max=128)])
    confirm_password=PasswordField("Konfirmasi password",validators=[DataRequired(),EqualTo("password")])
