from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from sqlalchemy import CheckConstraint, Date, Enum, func, literal_column
from sqlalchemy.sql import select
from flask_login import LoginManager
from enum import Enum as PyEnum
import re

from config import bcrypt, db


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    _password_hash = db.Column(db.String)
    admin = db.Column(db.String, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    recipes = db.relationship('Recipe', back_populates='user')

    serialize_rules = ('-recipes',)

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))

    @validates('email')
    def validate_email(self, key, email):
        users = User.query.all()
        emails = [user.email for user in users]
        if not email:
            raise ValueError('Email must be provided')
        elif email in emails:
            raise ValueError('This email is already registered to an account - please log in.')
        elif not re.search('@', email):
            raise ValueError('Must be a valid email')
        return email

    @validates('password')
    def validate_password(self, key, password):
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long.')
        elif not re.search('[!@#$%^&*]', password):
            raise ValueError('Password must contain at least one special character.')
        return password
        
    @validates('first_name')
    def validate_first_name(self, key, value):
        if not value:
            raise ValueError('First name must be provided')
        return value
    

    def __repr__(self):
        return f'USER: ID: {self.id}, Name {self.name}, Email: {self.email}'



class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    user = db.relationship('User', back_populates='recipes')
    recipe_ingredients = db.relationship('RecipeIngredient', back_populates='recipe')
    recipe_category = db.relationship('RecipeCategory', back_populates='recipe')

    serialize_rules = ('-user', '-recipe_ingredients', '-recipe_category')



class Ingredient(db.Model, SerializerMixin):
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    recipe_ingredients = db.relationship('RecipeIngredient', back_populates='ingredient')

    serialize_rules = ('-recipe_ingredients',)


class RecipeIngredient(db.Model, SerializerMixin):
    __tablename__ = 'recipeingredients'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'))
    quantity = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    recipe = db.relationship('Recipe', back_populates='recipe_ingredients')
    ingredient = db.relationship('Ingredient', back_populates='recipe_ingredients')

    serialize_rules = ('-recipe', '-ingredient')


class Category(db.Model, SerializerMixin):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    recipe_category = db.relationship('RecipeCategory', back_populates='category')

    serialize_rules = ('-recipe_category')



class RecipeCategory(db.Model, SerializerMixin):
    __tablename__ = 'recipecategories'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    recipe = db.relationship('Recipe', back_populates='recipe_category')
    category = db.relationship('Category', back_populates='recipe_category')

    serialize_rules = ('-recipe', '-category')

