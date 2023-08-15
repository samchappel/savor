from flask import  request, make_response, session, abort, jsonify, Flask
from flask_restful import Api, Resource
from flask_login import current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import NotFound, Unauthorized
from models import User, Recipe, Ingredient, RecipeIngredient, Category, RecipeCategory, db
from config import db, api, app, CORS, migrate, bcrypt, load_user, login_manager
import os

from flask_login import LoginManager

login_manager.init_app(app)


class Users(Resource):
    def get(self):
        users = [user.to_dict() for user in User.query.all()]
        return users, 200

    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if User.query.filter_by(email=email).first():
            return {'error': 'Email already in use'}, 409

        new_user = User(email=email, password=password, first_name=first_name, last_name=last_name)
        
        db.session.add(new_user)
        db.session.commit()

        return new_user.to_dict(), 201

api.add_resource(Users, '/users')

class UserByID(Resource):
    def get(self, id):
        user = User.query.filter_by(id=id).first()
        if not user:
            return {'error': 'User not found'}, 404
        return user.to_dict(), 200

    def put(self, id):
        user = User.query.filter_by(id=id).first()
        if not user:
            return {'error': 'User not found'}, 404

        data = request.get_json()
        user.email = data.get('email', user.email)
        user.password = data.get('password', user.password)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        db.session.commit()

        return user.to_dict(), 200

    def delete(self, id):
        user = User.query.filter_by(id=id).first()
        if not user:
            return {'error': 'User not found'}, 404
        db.session.delete(user)
        db.session.commit()
        return {}, 204

api.add_resource(UserByID, '/users/<int:id>')

class Recipes(Resource):
    def get(self):
        recipes = [recipe.to_dict() for recipe in Recipe.query.all()]
        return recipes, 200

    def post(self):
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        user_id = data.get('user_id')
        category_id = data.get('category_id')

        new_recipe = Recipe(title=title, content=content, user_id=user_id, category_id=category_id)
        db.session.add(new_recipe)
        db.session.commit()

        return new_recipe.to_dict(), 201

api.add_resource(Recipes, '/recipes')


class RecipeByID(Resource):
    def get(self, id):
        recipe = Recipe.query.filter_by(id=id).first()
        if not recipe:
            return {'error': 'Recipe not found'}, 404
        return recipe.to_dict(), 200

    def put(self, id):
        recipe = Recipe.query.filter_by(id=id).first()
        if not recipe:
            return {'error': 'Recipe not found'}, 404

        data = request.get_json()
        recipe.title = data.get('title', recipe.title)
        recipe.content = data.get('content', recipe.content)
        recipe.user_id = data.get('user_id', recipe.user_id)
        recipe.category_id = data.get('category_id', recipe.category_id)

        db.session.commit()

        return recipe.to_dict(), 200

    def delete(self, id):
        recipe = Recipe.query.filter_by(id=id).first()
        if not recipe:
            return {'error': 'Recipe not found'}, 404
        db.session.delete(recipe)
        db.session.commit()
        return {}, 204

api.add_resource(RecipeByID, '/recipes/<int:id>')


class Ingredients(Resource):
    def get(self):
        ingredients = [ingredient.to_dict() for ingredient in Ingredient.query.all()]
        return ingredients, 200

    def post(self):
        data = request.get_json()
        name = data.get('name')
        quantity = data.get('quantity')

        new_ingredient = Ingredient(name=name, quantity=quantity)
        db.session.add(new_ingredient)
        db.session.commit()

        return new_ingredient.to_dict(), 201

api.add_resource(Ingredients, '/ingredients')

class IngredientByID(Resource):
    def get(self, id):
        ingredient = Ingredient.query.filter_by(id=id).first()
        if not ingredient:
            return {'error': 'Ingredient not found'}, 404
        return ingredient.to_dict(), 200

    def put(self, id):
        ingredient = Ingredient.query.filter_by(id=id).first()
        if not ingredient:
            return {'error': 'Ingredient not found'}, 404

        data = request.get_json()
        ingredient.name = data.get('name', ingredient.name)
        ingredient.quantity = data.get('quantity', ingredient.quantity)
        db.session.commit()

        return ingredient.to_dict(), 200

    def delete(self, id):
        ingredient = Ingredient.query.filter_by(id=id).first()
        if not ingredient:
            return {'error': 'Ingredient not found'}, 404
        db.session.delete(ingredient)
        db.session.commit()
        return {}, 204

api.add_resource(IngredientByID, '/ingredients/<int:id>')

class RecipeIngredients(Resource):
    def post(self, recipe_id):
        user_id = get_jwt_identity()
        
        data = request.get_json()
        ingredient_id = data.get('ingredient_id')
        
        ingredient = Ingredient.query.filter_by(id=ingredient_id).first()
        if not ingredient:
            return {'error': 'Ingredient not found'}, 404

        recipe = Recipe.query.filter_by(id=recipe_id).first()
        if not recipe:
            return {'error': 'Recipe not found'}, 404

        if recipe.user_id != user_id:
            return {'error': 'Unauthorized'}, 401

        recipe.ingredients.append(ingredient)
        db.session.commit()
        
        return {'message': 'Ingredient added successfully'}, 200

    def delete(self, recipe_id):
        user_id = get_jwt_identity()
        
        data = request.get_json()
        ingredient_id = data.get('ingredient_id')
        
        ingredient = Ingredient.query.filter_by(id=ingredient_id).first()
        if not ingredient:
            return {'error': 'Ingredient not found'}, 404

        recipe = Recipe.query.filter_by(id=recipe_id).first()
        if not recipe:
            return {'error': 'Recipe not found'}, 404

        if recipe.user_id != user_id:
            return {'error': 'Unauthorized'}, 401

        recipe.ingredients.remove(ingredient)
        db.session.commit()
        
        return {'message': 'Ingredient removed successfully'}, 200

api.add_resource(RecipeIngredients, '/recipes/<int:recipe_id>/ingredients')


class Categories(Resource):
    def get(self):
        categories = [category.to_dict() for category in Category.query.all()]
        return categories, 200

    def post(self):
        data = request.get_json()
        name = data.get('name')

        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()

        return new_category.to_dict(), 201

api.add_resource(Categories, '/categories')

class CategoryByID(Resource):
    def get(self, id):
        category = Category.query.filter_by(id=id).first()
        if not category:
            return {'error': 'Category not found'}, 404
        return category.to_dict(), 200

    def put(self, id):
        category = Category.query.filter_by(id=id).first()
        if not category:
            return {'error': 'Category not found'}, 404

        data = request.get_json()
        category.name = data.get('name', category.name)
        db.session.commit()

        return category.to_dict(), 200

    def delete(self, id):
        category = Category.query.filter_by(id=id).first()
        if not category:
            return {'error': 'Category not found'}, 404
        db.session.delete(category)
        db.session.commit()
        return {}, 204

api.add_resource(CategoryByID, '/categories/<int:id>')


class RecipeCategories(Resource):
    def post(self, recipe_id):
        user_id = get_jwt_identity()

        data = request.get_json()
        category_id = data.get('category_id')

        category = Category.query.filter_by(id=category_id).first()
        if not category:
            return {'error': 'Category not found'}, 404

        recipe = Recipe.query.filter_by(id=recipe_id).first()
        if not recipe:
            return {'error': 'Recipe not found'}, 404

        if recipe.user_id != user_id:
            return {'error': 'Unauthorized'}, 401

        recipe.categories.append(category)
        db.session.commit()
        
        return {'message': 'Category added successfully'}, 200

    def delete(self, recipe_id):
        user_id = get_jwt_identity()

        data = request.get_json()
        category_id = data.get('category_id')

        category = Category.query.filter_by(id=category_id).first()
        if not category:
            return {'error': 'Category not found'}, 404

        recipe = Recipe.query.filter_by(id=recipe_id).first()
        if not recipe:
            return {'error': 'Recipe not found'}, 404

        if recipe.user_id != user_id:
            return {'error': 'Unauthorized'}, 401

        recipe.categories.remove(category)
        db.session.commit()
        
        return {'message': 'Category removed successfully'}, 200

api.add_resource(RecipeCategories, '/recipes/<int:recipe_id>/categories')


class Signup(Resource):
     def post(self):
        
        first_name = request.get_json()['first_name']
        last_name = request.get_json()['last_name']
        email = request.get_json()['email']
        password = request.get_json()['password']

        new_user = User(first_name=first_name, last_name=last_name, email=email, admin=False)
        new_user.password_hash = password
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
                
        return new_user.to_dict(), 201

api.add_resource(Signup, '/signup', endpoint='signup')


class Login(Resource):
    def post(self):
        try:
            user = User.query.filter_by(email=request.get_json()['email']).first()
            if user.authenticate(request.get_json()['password']):
                session['user_id'] = user.id
                response = make_response(
                    user.to_dict(),
                    200
                )
                return response
        except:
            abort(401, "Incorrect Email or Password")

api.add_resource(Login, '/login')


class AuthorizedSession(Resource):
    def get(self):
        try:
            user = User.query.filter_by(id=session['user_id']).first()
            response = make_response(
                user.to_dict(),
        
                200
            )
            return response
        except:
            abort(401, "Unauthorized")

api.add_resource(AuthorizedSession, '/authorized')


class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        response = make_response('',204,)
        return response

api.add_resource(Logout, '/logout', endpoint='logout')


@app.errorhandler(NotFound)
def handle_not_found(e):
    response = make_response(
        "Not Found: Sorry the resource you are looking for does not exist",
        404
    )

    return response


class UserRecipes(Resource):
    @jwt_required()
    def get(self, id):
        user_id = get_jwt_identity()
        if user_id != id:
            return {'error': 'Unauthorized'}, 401

        user = User.query.filter_by(id=id).first()
        if not user:
            return {'error': 'User not found'}, 404
        recipes = [recipe.to_dict() for recipe in user.recipes]
        return recipes, 200

api.add_resource(UserRecipes, '/users/<int:id>/recipes')


if __name__ == '__main__':
    app.run(port=5000, debug=True)


