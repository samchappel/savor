# Standard library imports
from random import randint, choice as rc

# Remote library imports
from faker import Faker

# Local imports
from app import app
from models import db, User, Recipe, Ingredient, RecipeIngredient, Category, RecipeCategory

if __name__ == '__main__':
    fake = Faker()

    with app.app_context():
        # Deleting all records
        print("Deleting all records...")
        RecipeCategory.query.delete()
        RecipeIngredient.query.delete()
        Category.query.delete()
        Ingredient.query.delete()
        Recipe.query.delete()
        User.query.delete()

        # Seeding Users
        print("Seeding Users...")
        users = []
        for _ in range(50):  # Seeding 50 users
            user = User(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password_hash=fake.password(),
            )
            users.append(user)
            db.session.add(user)
        db.session.commit()

        # Seeding Recipes
        print("Seeding Recipes...")
        recipes = []
        for _ in range(100):  # Seeding 100 recipes
            recipe = Recipe(
                name=fake.unique.sentence(),
                description=fake.text(),
                user_id=rc(users).id
            )
            recipes.append(recipe)
            db.session.add(recipe)
        db.session.commit()

        # Seeding Ingredients
        print("Seeding Ingredients...")
        ingredients = ["Eggs", "Milk", "Flour", "Sugar", "Butter", "Baking Powder", "Salt", "Vanilla Extract", "Chocolate", "Yeast"]
        for ingredient in ingredients:
            db.session.add(Ingredient(name=ingredient))
        db.session.commit()

        # Fetching seeded ingredients
        seeded_ingredients = Ingredient.query.all()

        # Seeding RecipeIngredients
        print("Seeding RecipeIngredients...")
        for _ in range(200):  # Seeding 200 recipe-ingredient relationships
            ri = RecipeIngredient(
                recipe_id=rc(recipes).id,
                ingredient_id=rc(seeded_ingredients).id,
                quantity=f"{randint(1, 5)} {rc(['cups', 'tablespoons', 'teaspoons', 'pieces'])}"
            )
            db.session.add(ri)
        db.session.commit()

        # Seeding Categories
        print("Seeding Categories...")
        categories = ["Dessert", "Main Course", "Appetizer", "Beverage", "Snack", "Breakfast", "Lunch", "Dinner", "Brunch", "Salad"]
        for category in categories:
            db.session.add(Category(name=category))
        db.session.commit()

        # Fetching seeded categories
        seeded_categories = Category.query.all()

        # Seeding RecipeCategories
        print("Seeding RecipeCategories...")
        for _ in range(150):  # Seeding 150 recipe-category relationships
            rc_entry = RecipeCategory(
                recipe_id=rc(recipes).id,
                category_id=rc(seeded_categories).id
            )
            db.session.add(rc_entry)
        db.session.commit()

        print("Seeding finished!")