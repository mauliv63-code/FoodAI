import os
import json
import logging
import random
from datetime import datetime
from collections import Counter, deque

# ============================================================
# OPTIONAL CLAUDE AI
# ============================================================

try:
    import anthropic
    ANTHROPIC_SDK_AVAILABLE = True
except ImportError:
    ANTHROPIC_SDK_AVAILABLE = False


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    filename="foodai.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ============================================================
# CUSTOM EXCEPTIONS
# ============================================================

class FoodAIError(Exception):
    pass


class FoodNotFoundError(FoodAIError):
    pass


class OutOfStockError(FoodAIError):
    pass


class InvalidQuantityError(FoodAIError):
    pass


class InvalidPriceError(FoodAIError):
    pass


class EmptyCartError(FoodAIError):
    pass


class InvalidChoiceError(FoodAIError):
    pass


class AIRecommendationError(FoodAIError):
    pass


class PaymentError(FoodAIError):
    pass


# ============================================================
# FOOD CLASS
# ============================================================

class Food:

    def __init__(
        self,
        food_id,
        name,
        category,
        price,
        rating,
        vegetarian,
        spicy,
        stock,
        description=""
    ):

        if price <= 0:
            raise InvalidPriceError(
                f"Invalid price for {name}"
            )

        if stock < 0:
            raise ValueError(
                f"Stock cannot be negative for {name}"
            )

        self.id = food_id
        self.name = name
        self.category = category
        self.price = price
        self.rating = rating
        self.vegetarian = vegetarian
        self.spicy = spicy
        self.stock = stock
        self.description = description

    def display(self):

        veg = "VEG" if self.vegetarian else "NON-VEG"
        spice = "SPICY" if self.spicy else "MILD"

        print(
            f"{self.id:3} | "
            f"{self.name:30} | "
            f"{self.category:12} | "
            f"₹{self.price:<4} | "
            f"⭐ {self.rating} | "
            f"{veg:7} | "
            f"{spice:5} | "
            f"Stock: {self.stock}"
        )


# ============================================================
# MENU
# 160+ REAL MENU ITEMS
# ============================================================

class Menu:

    def __init__(self):

        self.foods = {}

        food_data = [

            # =================================================
            # PIZZAS
            # =================================================

            ("Margherita Pizza", "Pizza", 249, 4.6, True, False, 15),
            ("Farmhouse Pizza", "Pizza", 299, 4.7, True, False, 12),
            ("Paneer Tikka Pizza", "Pizza", 299, 4.8, True, True, 14),
            ("Cheese Burst Pizza", "Pizza", 329, 4.7, True, False, 10),
            ("Veggie Supreme Pizza", "Pizza", 319, 4.6, True, True, 13),
            ("Corn Cheese Pizza", "Pizza", 269, 4.4, True, False, 18),
            ("Mushroom Pizza", "Pizza", 289, 4.5, True, False, 15),
            ("Jalapeno Cheese Pizza", "Pizza", 299, 4.6, True, True, 12),
            ("Spicy Paneer Pizza", "Pizza", 319, 4.7, True, True, 11),
            ("Mexican Green Wave Pizza", "Pizza", 309, 4.5, True, True, 14),
            ("Chicken Tikka Pizza", "Pizza", 349, 4.8, False, True, 15),
            ("Chicken Pepperoni Pizza", "Pizza", 379, 4.8, False, True, 10),
            ("BBQ Chicken Pizza", "Pizza", 359, 4.7, False, True, 13),
            ("Chicken Cheese Pizza", "Pizza", 339, 4.6, False, False, 14),
            ("Peri Peri Chicken Pizza", "Pizza", 369, 4.8, False, True, 12),
            ("Double Cheese Pizza", "Pizza", 289, 4.5, True, False, 16),
            ("Olive Garden Pizza", "Pizza", 319, 4.4, True, False, 10),
            ("Spicy Corn Pizza", "Pizza", 279, 4.3, True, True, 17),
            ("Garlic Mushroom Pizza", "Pizza", 299, 4.6, True, False, 13),
            ("Cheese Paneer Pizza", "Pizza", 319, 4.7, True, False, 12),

            # =================================================
            # BIRYANI
            # =================================================

            ("Chicken Biryani", "Biryani", 220, 4.8, False, True, 20),
            ("Veg Biryani", "Biryani", 180, 4.5, True, True, 18),
            ("Paneer Biryani", "Biryani", 240, 4.7, True, True, 15),
            ("Egg Biryani", "Biryani", 210, 4.6, False, True, 14),
            ("Hyderabadi Chicken Biryani", "Biryani", 280, 4.9, False, True, 15),
            ("Mutton Biryani", "Biryani", 330, 4.8, False, True, 10),
            ("Kolkata Chicken Biryani", "Biryani", 270, 4.6, False, False, 11),
            ("Lucknowi Chicken Biryani", "Biryani", 290, 4.7, False, False, 12),
            ("Mushroom Biryani", "Biryani", 210, 4.5, True, True, 13),
            ("Soya Chaap Biryani", "Biryani", 230, 4.6, True, True, 10),
            ("Chicken Dum Biryani", "Biryani", 310, 4.9, False, True, 12),
            ("Paneer Dum Biryani", "Biryani", 260, 4.7, True, True, 14),
            ("Egg Dum Biryani", "Biryani", 240, 4.5, False, True, 13),
            ("Spicy Veg Biryani", "Biryani", 190, 4.4, True, True, 17),
            ("Chicken Keema Biryani", "Biryani", 320, 4.7, False, True, 9),

            # =================================================
            # BURGERS
            # =================================================

            ("Cheese Burger", "Burger", 199, 4.4, True, False, 10),
            ("Chicken Burger", "Burger", 229, 4.6, False, False, 14),
            ("Veg Supreme Burger", "Burger", 219, 4.5, True, False, 12),
            ("Paneer Burger", "Burger", 239, 4.7, True, True, 13),
            ("Spicy Paneer Burger", "Burger", 249, 4.7, True, True, 11),
            ("Chicken Cheese Burger", "Burger", 259, 4.7, False, False, 12),
            ("Peri Peri Chicken Burger", "Burger", 269, 4.8, False, True, 14),
            ("Crispy Chicken Burger", "Burger", 249, 4.6, False, False, 13),
            ("Double Chicken Burger", "Burger", 299, 4.7, False, True, 9),
            ("Mushroom Burger", "Burger", 229, 4.4, True, False, 12),
            ("Mexican Veg Burger", "Burger", 219, 4.5, True, True, 14),
            ("BBQ Chicken Burger", "Burger", 279, 4.7, False, True, 10),
            ("Tandoori Paneer Burger", "Burger", 249, 4.6, True, True, 12),
            ("Aloo Tikki Burger", "Burger", 149, 4.3, True, False, 20),
            ("Spicy Chicken Burger", "Burger", 259, 4.7, False, True, 11),

            # =================================================
            # NOODLES
            # =================================================

            ("Hakka Noodles", "Noodles", 160, 4.3, True, True, 16),
            ("Chicken Noodles", "Noodles", 190, 4.5, False, True, 13),
            ("Schezwan Noodles", "Noodles", 180, 4.6, True, True, 15),
            ("Veg Chowmein", "Noodles", 170, 4.4, True, False, 16),
            ("Chicken Chowmein", "Noodles", 210, 4.6, False, True, 14),
            ("Paneer Noodles", "Noodles", 200, 4.5, True, True, 13),
            ("Singapore Noodles", "Noodles", 190, 4.5, True, True, 12),
            ("Garlic Noodles", "Noodles", 170, 4.4, True, False, 15),
            ("Chilli Garlic Noodles", "Noodles", 190, 4.6, True, True, 13),
            ("Egg Noodles", "Noodles", 180, 4.4, False, True, 14),
            ("Peri Peri Noodles", "Noodles", 200, 4.6, True, True, 12),
            ("Manchurian Noodles", "Noodles", 210, 4.5, True, True, 11),
            ("Schezwan Chicken Noodles", "Noodles", 220, 4.7, False, True, 13),
            ("Mushroom Noodles", "Noodles", 190, 4.4, True, False, 12),
            ("Triple Schezwan Noodles", "Noodles", 250, 4.8, False, True, 10),

            # =================================================
            # PASTA
            # =================================================

            ("White Sauce Pasta", "Pasta", 220, 4.5, True, False, 15),
            ("Red Sauce Pasta", "Pasta", 210, 4.4, True, False, 16),
            ("Arrabbiata Pasta", "Pasta", 230, 4.6, True, True, 13),
            ("Alfredo Pasta", "Pasta", 250, 4.7, True, False, 12),
            ("Paneer Pasta", "Pasta", 240, 4.6, True, False, 13),
            ("Chicken Alfredo Pasta", "Pasta", 290, 4.8, False, False, 11),
            ("Chicken Arrabbiata Pasta", "Pasta", 280, 4.7, False, True, 10),
            ("Cheese Pasta", "Pasta", 210, 4.5, True, False, 14),
            ("Mushroom Alfredo Pasta", "Pasta", 260, 4.6, True, False, 11),
            ("Spicy Penne Pasta", "Pasta", 220, 4.4, True, True, 15),
            ("Creamy Tomato Pasta", "Pasta", 230, 4.5, True, False, 12),
            ("Peri Peri Chicken Pasta", "Pasta", 290, 4.8, False, True, 10),
            ("Mexican Pasta", "Pasta", 240, 4.6, True, True, 13),
            ("Garlic Parmesan Pasta", "Pasta", 250, 4.7, True, False, 11),
            ("Chicken Cheese Pasta", "Pasta", 280, 4.7, False, False, 12),

            # =================================================
            # WRAPS
            # =================================================

            ("Veg Wrap", "Wrap", 149, 4.3, True, False, 20),
            ("Paneer Wrap", "Wrap", 189, 4.6, True, True, 17),
            ("Spicy Paneer Wrap", "Wrap", 199, 4.7, True, True, 15),
            ("Chicken Wrap", "Wrap", 209, 4.5, False, False, 18),
            ("Chicken Tikka Wrap", "Wrap", 229, 4.7, False, True, 15),
            ("Peri Peri Chicken Wrap", "Wrap", 239, 4.8, False, True, 13),
            ("Mexican Veg Wrap", "Wrap", 179, 4.4, True, True, 16),
            ("Cheese Corn Wrap", "Wrap", 169, 4.4, True, False, 14),
            ("Mushroom Wrap", "Wrap", 179, 4.3, True, False, 15),
            ("BBQ Chicken Wrap", "Wrap", 239, 4.7, False, True, 12),
            ("Tandoori Paneer Wrap", "Wrap", 209, 4.6, True, True, 14),
            ("Egg Wrap", "Wrap", 179, 4.5, False, True, 16),

            # =================================================
            # SANDWICH
            # =================================================

            ("Veg Grilled Sandwich", "Sandwich", 140, 4.3, True, False, 20),
            ("Cheese Sandwich", "Sandwich", 150, 4.4, True, False, 18),
            ("Paneer Sandwich", "Sandwich", 180, 4.6, True, False, 15),
            ("Spicy Paneer Sandwich", "Sandwich", 190, 4.6, True, True, 13),
            ("Chicken Sandwich", "Sandwich", 210, 4.5, False, False, 15),
            ("Chicken Cheese Sandwich", "Sandwich", 230, 4.7, False, False, 12),
            ("Club Sandwich", "Sandwich", 250, 4.7, False, False, 10),
            ("Peri Peri Chicken Sandwich", "Sandwich", 240, 4.8, False, True, 11),
            ("Corn Cheese Sandwich", "Sandwich", 170, 4.5, True, False, 16),
            ("Mushroom Cheese Sandwich", "Sandwich", 190, 4.5, True, False, 13),
            ("Mexican Sandwich", "Sandwich", 200, 4.6, True, True, 12),
            ("Chilli Cheese Toast", "Sandwich", 160, 4.4, True, True, 15),

            # =================================================
            # INDIAN
            # =================================================

            ("Paneer Butter Masala", "Indian", 240, 4.8, True, True, 14),
            ("Shahi Paneer", "Indian", 250, 4.7, True, False, 13),
            ("Kadai Paneer", "Indian", 230, 4.7, True, True, 15),
            ("Palak Paneer", "Indian", 220, 4.6, True, False, 13),
            ("Chole Bhature", "Indian", 180, 4.7, True, True, 18),
            ("Rajma Rice", "Indian", 160, 4.5, True, False, 20),
            ("Dal Makhani Rice", "Indian", 180, 4.6, True, False, 16),
            ("Jeera Rice", "Indian", 120, 4.3, True, False, 22),
            ("Dal Tadka", "Indian", 140, 4.5, True, True, 18),
            ("Aloo Paratha", "Indian", 130, 4.6, True, True, 20),
            ("Paneer Paratha", "Indian", 160, 4.7, True, True, 18),
            ("Masala Dosa", "Indian", 140, 4.7, True, True, 20),
            ("Paneer Dosa", "Indian", 180, 4.6, True, True, 16),
            ("Idli Sambar", "Indian", 100, 4.5, True, False, 25),
            ("Medu Vada", "Indian", 110, 4.5, True, True, 22),
            ("Pav Bhaji", "Indian", 150, 4.6, True, True, 20),
            ("Masala Pav", "Indian", 130, 4.4, True, True, 18),
            ("Paneer Kathi Roll", "Indian", 200, 4.7, True, True, 14),
            ("Chicken Kathi Roll", "Indian", 230, 4.8, False, True, 13),
            ("Tandoori Chicken", "Indian", 280, 4.8, False, True, 12),
            ("Chicken Tikka", "Indian", 260, 4.8, False, True, 13),
            ("Paneer Tikka", "Indian", 220, 4.7, True, True, 15),
            ("Malai Chicken Tikka", "Indian", 280, 4.7, False, False, 11),
            ("Samosa", "Indian", 60, 4.5, True, True, 30),
            ("Paneer Pakora", "Indian", 140, 4.5, True, True, 20),

            # =================================================
            # CHINESE
            # =================================================

            ("Veg Manchurian", "Chinese", 170, 4.5, True, True, 17),
            ("Chicken Manchurian", "Chinese", 220, 4.7, False, True, 14),
            ("Chilli Paneer", "Chinese", 200, 4.7, True, True, 15),
            ("Chilli Chicken", "Chinese", 230, 4.8, False, True, 14),
            ("Honey Chilli Potato", "Chinese", 160, 4.6, True, True, 18),
            ("Spring Rolls", "Chinese", 130, 4.4, True, False, 20),
            ("Chicken Spring Rolls", "Chinese", 180, 4.6, False, True, 16),
            ("Veg Fried Rice", "Chinese", 160, 4.4, True, False, 20),
            ("Chicken Fried Rice", "Chinese", 200, 4.7, False, True, 15),
            ("Schezwan Fried Rice", "Chinese", 180, 4.6, True, True, 17),
            ("Chicken Schezwan Rice", "Chinese", 220, 4.8, False, True, 14),
            ("Paneer Chilli", "Chinese", 210, 4.7, True, True, 13),
            ("Garlic Bread", "Chinese", 120, 4.4, True, False, 25),
            ("Cheese Garlic Bread", "Chinese", 160, 4.7, True, False, 20),

            # =================================================
            # DESSERT
            # =================================================

            ("Chocolate Brownie", "Dessert", 120, 4.7, True, False, 20),
            ("Gulab Jamun", "Dessert", 100, 4.6, True, False, 25),
            ("Rasmalai", "Dessert", 130, 4.7, True, False, 18),
            ("Chocolate Cake", "Dessert", 160, 4.8, True, False, 15),
            ("Red Velvet Cake", "Dessert", 180, 4.8, True, False, 13),
            ("Black Forest Cake", "Dessert", 170, 4.7, True, False, 15),
            ("Cheesecake", "Dessert", 220, 4.8, True, False, 12),
            ("Brownie Sundae", "Dessert", 190, 4.8, True, False, 13),
            ("Chocolate Lava Cake", "Dessert", 180, 4.9, True, False, 14),
            ("Ice Cream Sundae", "Dessert", 160, 4.6, True, False, 18),
            ("Vanilla Ice Cream", "Dessert", 100, 4.4, True, False, 25),
            ("Chocolate Ice Cream", "Dessert", 110, 4.6, True, False, 25),
            ("Strawberry Ice Cream", "Dessert", 110, 4.5, True, False, 23),
            ("Mango Ice Cream", "Dessert", 120, 4.6, True, False, 22),
            ("Kulfi", "Dessert", 100, 4.5, True, False, 24),
            ("Kheer", "Dessert", 90, 4.5, True, False, 20),
            ("Jalebi", "Dessert", 90, 4.6, True, False, 25),
            ("Rasgulla", "Dessert", 90, 4.5, True, False, 25),

            # =================================================
            # BEVERAGES
            # =================================================

            ("Masala Chai", "Beverage", 50, 4.5, True, False, 30),
            ("Cold Coffee", "Beverage", 100, 4.6, True, False, 25),
            ("Chocolate Shake", "Beverage", 140, 4.7, True, False, 20),
            ("Vanilla Shake", "Beverage", 130, 4.5, True, False, 20),
            ("Strawberry Shake", "Beverage", 140, 4.6, True, False, 20),
            ("Mango Shake", "Beverage", 140, 4.7, True, False, 20),
            ("Oreo Shake", "Beverage", 160, 4.8, True, False, 18),
            ("Lemon Soda", "Beverage", 70, 4.4, True, False, 30),
            ("Fresh Lime Water", "Beverage", 60, 4.4, True, False, 30),
            ("Mango Lassi", "Beverage", 100, 4.7, True, False, 25),
            ("Sweet Lassi", "Beverage", 90, 4.6, True, False, 25),
            ("Cold Drink", "Beverage", 60, 4.2, True, False, 30),

            # =================================================
            # SALADS
            # =================================================

            ("Garden Salad", "Salad", 120, 4.3, True, False, 18),
            ("Greek Salad", "Salad", 180, 4.6, True, False, 15),
            ("Paneer Salad", "Salad", 200, 4.6, True, False, 14),
            ("Chicken Salad", "Salad", 220, 4.7, False, False, 13),
            ("Spicy Mexican Salad", "Salad", 170, 4.5, True, True, 15),
            ("Corn Salad", "Salad", 130, 4.4, True, False, 18),
            ("Chickpea Salad", "Salad", 140, 4.5, True, True, 17),
            ("Fruit Salad", "Salad", 120, 4.6, True, False, 20),

            # =================================================
            # SNACKS
            # =================================================

            ("French Fries", "Snacks", 100, 4.5, True, False, 30),
            ("Peri Peri Fries", "Snacks", 120, 4.7, True, True, 28),
            ("Cheese Fries", "Snacks", 150, 4.7, True, False, 25),
            ("Chicken Nuggets", "Snacks", 180, 4.6, False, False, 20),
            ("Cheese Balls", "Snacks", 140, 4.5, True, False, 20),
            ("Veg Momos", "Snacks", 120, 4.6, True, True, 25),
            ("Chicken Momos", "Snacks", 160, 4.7, False, True, 23),
            ("Tandoori Momos", "Snacks", 180, 4.8, False, True, 18),
            ("Paneer Momos", "Snacks", 150, 4.7, True, True, 20),
            ("Cheese Momos", "Snacks", 160, 4.6, True, False, 18),
        ]

        food_id = 1

        for item in food_data:

            name, category, price, rating, vegetarian, spicy, stock = item

            food = Food(
                food_id,
                name,
                category,
                price,
                rating,
                vegetarian,
                spicy,
                stock,
                f"Delicious {name.lower()}."
            )

            self.foods[food_id] = food
            food_id += 1

    # --------------------------------------------------------

    def display(self):

        print("\n" + "=" * 120)
        print("                          FOODAI MENU")
        print("=" * 120)

        for food in self.foods.values():
            food.display()

        print("=" * 120)

    # --------------------------------------------------------

    def search(self, keyword):

        keyword = keyword.lower().strip()

        results = []

        for food in self.foods.values():

            if (
                keyword in food.name.lower()
                or keyword in food.category.lower()
            ):
                results.append(food)

        return results

    # --------------------------------------------------------

    def get_food(self, food_id):

        if food_id not in self.foods:
            raise FoodNotFoundError(
                f"Food ID {food_id} does not exist."
            )

        return self.foods[food_id]

    # --------------------------------------------------------

    def categories(self):

        return sorted(
            set(food.category for food in self.foods.values())
        )


# ============================================================
# AI RECOMMENDATION ENGINE
# ============================================================

class AIRecommendationEngine:

    def __init__(self, menu, use_llm=True):

        self.menu = menu

        self.use_llm = use_llm

        self.client = None

        self.llm_enabled = False

        self.recommendation_history = deque(maxlen=30)

        self.order_history = []

        self.preference_history = []

        # ----------------------------------------------------
        # Claude initialization
        # ----------------------------------------------------

        if (
            self.use_llm
            and ANTHROPIC_SDK_AVAILABLE
            and os.getenv("ANTHROPIC_API_KEY")
        ):

            try:

                self.client = anthropic.Anthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )

                self.llm_enabled = True

                logging.info("Claude AI enabled.")

            except Exception as e:

                logging.error(
                    f"Claude initialization failed: {e}"
                )

        else:

            logging.info(
                "Claude unavailable. Using intelligent local AI."
            )

    # ========================================================
    # BASIC BUDGET EXTRACTION
    # ========================================================

    def extract_budget(self, text):

        import re

        patterns = [
            r"under\s*₹?\s*(\d+)",
            r"below\s*₹?\s*(\d+)",
            r"within\s*₹?\s*(\d+)",
            r"budget\s*(?:is|of)?\s*₹?\s*(\d+)",
            r"₹\s*(\d+)",
            r"rs\.?\s*(\d+)"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text.lower()
            )

            if match:

                return int(match.group(1))

        return None

    # ========================================================
    # RULE-BASED AI
    # ========================================================

    def analyze_preferences(self, text):

        text = text.lower()

        preferences = {

            "vegetarian": None,

            "spicy": None,

            "budget": self.extract_budget(text),

            "categories": [],

            "cheap": False,

            "high_rating": False,

            "filling": False,

            "light": False,

            "sweet": False,

            "healthy": False,

            "protein": False
        }

        # ----------------------------------------------------
        # Vegetarian
        # ----------------------------------------------------

        if any(
            word in text
            for word in [
                "vegetarian",
                "veg",
                "no chicken",
                "no meat",
                "no non veg"
            ]
        ):
            preferences["vegetarian"] = True

        elif any(
            word in text
            for word in [
                "non vegetarian",
                "non-vegetarian",
                "chicken",
                "mutton",
                "meat",
                "non veg"
            ]
        ):
            preferences["vegetarian"] = False

        # ----------------------------------------------------
        # Spice
        # ----------------------------------------------------

        if any(
            word in text
            for word in [
                "spicy",
                "hot",
                "very spicy",
                "chilli",
                "schezwan",
                "peri peri"
            ]
        ):
            preferences["spicy"] = True

        elif any(
            word in text
            for word in [
                "mild",
                "not spicy",
                "less spicy",
                "non spicy"
            ]
        ):
            preferences["spicy"] = False

        # ----------------------------------------------------
        # Categories
        # ----------------------------------------------------

        category_keywords = {

            "Pizza": [
                "pizza"
            ],

            "Biryani": [
                "biryani"
            ],

            "Burger": [
                "burger"
            ],

            "Noodles": [
                "noodle",
                "noodles",
                "chowmein"
            ],

            "Pasta": [
                "pasta"
            ],

            "Wrap": [
                "wrap",
                "roll"
            ],

            "Sandwich": [
                "sandwich",
                "toast"
            ],

            "Indian": [
                "indian",
                "dosa",
                "paratha",
                "paneer",
                "tikka",
                "curry",
                "rice"
            ],

            "Chinese": [
                "chinese",
                "manchurian",
                "fried rice",
                "chilli paneer"
            ],

            "Dessert": [
                "dessert",
                "sweet",
                "cake",
                "brownie",
                "ice cream",
                "kulfi",
                "gulab jamun",
                "jalebi",
                "rasmalai"
            ],

            "Beverage": [
                "drink",
                "beverage",
                "shake",
                "coffee",
                "chai",
                "juice",
                "lassi"
            ],

            "Salad": [
                "salad",
                "healthy"
            ],

            "Snacks": [
                "snack",
                "fries",
                "momos",
                "nuggets"
            ]
        }

        for category, keywords in category_keywords.items():

            if any(
                keyword in text
                for keyword in keywords
            ):

                preferences["categories"].append(
                    category
                )

        # ----------------------------------------------------
        # Other intent
        # ----------------------------------------------------

        preferences["cheap"] = any(
            word in text
            for word in [
                "cheap",
                "budget",
                "affordable",
                "inexpensive"
            ]
        )

        preferences["high_rating"] = any(
            word in text
            for word in [
                "best",
                "top rated",
                "highest rated",
                "popular"
            ]
        )

        preferences["filling"] = any(
            word in text
            for word in [
                "filling",
                "hungry",
                "heavy",
                "full meal",
                "proper meal"
            ]
        )

        preferences["light"] = any(
            word in text
            for word in [
                "light",
                "small",
                "quick"
            ]
        )

        preferences["sweet"] = any(
            word in text
            for word in [
                "sweet",
                "dessert",
                "chocolate"
            ]
        )

        preferences["healthy"] = any(
            word in text
            for word in [
                "healthy",
                "light",
                "salad"
            ]
        )

        preferences["protein"] = any(
            word in text
            for word in [
                "protein",
                "protein rich",
                "high protein"
            ]
        )

        return preferences

    # ========================================================
    # CLAUDE INTENT ANALYSIS
    # ========================================================

    def parse_with_llm(self, user_text):

        if not self.llm_enabled:
            return None

        categories = self.menu.categories()

        prompt = f"""
You are the recommendation AI for a food ordering application.

Analyze this customer's request:

"{user_text}"

Available categories:
{categories}

Return ONLY valid JSON.

Use this exact structure:

{{
    "vegetarian": true/false/null,
    "spicy": true/false/null,
    "budget": number/null,
    "categories": [],
    "cheap": true/false,
    "high_rating": true/false,
    "filling": true/false,
    "light": true/false,
    "sweet": true/false,
    "healthy": true/false,
    "protein": true/false
}}

Do not invent categories.
"""

        try:

            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            raw = response.content[0].text.strip()

            # Remove accidental markdown fences

            raw = raw.replace(
                "```json",
                ""
            ).replace(
                "```",
                ""
            ).strip()

            data = json.loads(raw)

            valid_categories = set(
                self.menu.categories()
            )

            data["categories"] = [
                c for c in data.get(
                    "categories",
                    []
                )
                if c in valid_categories
            ]

            return data

        except Exception as e:

            logging.error(
                f"Claude recommendation parsing failed: {e}"
            )

            return None

    # ========================================================
    # USER PROFILE FROM HISTORY
    # ========================================================

    def build_user_profile(self):

        if not self.order_history:
            return {}

        category_count = Counter()
        vegetarian_count = 0
        spicy_count = 0

        for order in self.order_history:

            for item in order["items"]:

                food = item["food"]

                category_count[
                    food.category
                ] += item["quantity"]

                if food.vegetarian:
                    vegetarian_count += item["quantity"]

                if food.spicy:
                    spicy_count += item["quantity"]

        total_items = sum(
            category_count.values()
        )

        profile = {

            "favorite_categories":
                category_count.most_common(5),

            "vegetarian_ratio":
                vegetarian_count / total_items
                if total_items else 0,

            "spicy_ratio":
                spicy_count / total_items
                if total_items else 0
        }

        return profile

    # ========================================================
    # SMART SCORING
    # ========================================================

    def calculate_score(
        self,
        food,
        preferences,
        profile
    ):

        score = 0

        # ----------------------------------------------------
        # Dietary preference
        # ----------------------------------------------------

        if preferences["vegetarian"] is True:

            if food.vegetarian:
                score += 35
            else:
                score -= 50

        elif preferences["vegetarian"] is False:

            if not food.vegetarian:
                score += 35

        else:

            # Learn from history

            vegetarian_ratio = profile.get(
                "vegetarian_ratio",
                0
            )

            if vegetarian_ratio >= 0.75:

                if food.vegetarian:
                    score += 12

            elif vegetarian_ratio <= 0.25:

                if not food.vegetarian:
                    score += 12

        # ----------------------------------------------------
        # Spice
        # ----------------------------------------------------

        if preferences["spicy"] is True:

            if food.spicy:
                score += 25
            else:
                score -= 10

        elif preferences["spicy"] is False:

            if not food.spicy:
                score += 25
            else:
                score -= 10

        # ----------------------------------------------------
        # Category
        # ----------------------------------------------------

        if food.category in preferences["categories"]:

            score += 45

        # ----------------------------------------------------
        # Budget
        # ----------------------------------------------------

        budget = preferences["budget"]

        if budget is not None:

            if food.price <= budget:

                score += 35

                # Better utilization of budget

                percentage = food.price / budget

                score += int(
                    percentage * 10
                )

            else:

                # Penalize foods outside budget

                difference = food.price - budget

                score -= min(
                    60,
                    difference // 5
                )

        # ----------------------------------------------------
        # Cheap request
        # ----------------------------------------------------

        if preferences["cheap"]:

            if food.price <= 150:
                score += 25

            elif food.price <= 200:
                score += 15

            elif food.price <= 250:
                score += 5

        # ----------------------------------------------------
        # Rating
        # ----------------------------------------------------

        if preferences["high_rating"]:

            score += food.rating * 12

        else:

            score += food.rating * 5

        # ----------------------------------------------------
        # Filling
        # ----------------------------------------------------

        if preferences["filling"]:

            filling_categories = {
                "Biryani",
                "Pizza",
                "Pasta",
                "Noodles",
                "Indian",
                "Burger"
            }

            if food.category in filling_categories:

                score += 20

            if food.price >= 180:

                score += 8

        # ----------------------------------------------------
        # Light / healthy
        # ----------------------------------------------------

        if preferences["light"]:

            if food.category in {
                "Salad",
                "Sandwich",
                "Wrap",
                "Beverage"
            }:

                score += 20

            if food.price <= 200:

                score += 8

        # ----------------------------------------------------
        # Sweet
        # ----------------------------------------------------

        if preferences["sweet"]:

            if food.category == "Dessert":
                score += 55

            elif food.category == "Beverage":
                score += 15

            else:
                score -= 20

        # ----------------------------------------------------
        # Healthy
        # ----------------------------------------------------

        if preferences["healthy"]:

            if food.category == "Salad":
                score += 45

            elif food.category in {
                "Wrap",
                "Indian"
            }:
                score += 15

            elif food.category == "Dessert":
                score -= 25

        # ----------------------------------------------------
        # Protein
        # ----------------------------------------------------

        if preferences["protein"]:

            if (
                not food.vegetarian
                or food.category in {
                    "Indian",
                    "Burger",
                    "Wrap",
                    "Salad"
                }
            ):

                score += 18

        # ----------------------------------------------------
        # STOCK
        # ----------------------------------------------------

        if food.stock >= 10:

            score += 5

        elif food.stock <= 3:

            score -= 10

        # ----------------------------------------------------
        # PREVIOUS RECOMMENDATION PENALTY
        #
        # This does NOT ban the item.
        # It only helps the system explore alternatives.
        # ----------------------------------------------------

        recent_ids = list(
            self.recommendation_history
        )

        if food.id in recent_ids:

            position = (
                len(recent_ids)
                - 1
                - recent_ids[::-1].index(food.id)
            )

            # Recently recommended = mild penalty

            score -= max(
                5,
                25 - position * 3
            )

        # ----------------------------------------------------
        # PREVIOUS ORDER BONUS
        #
        # If the customer has actually ordered it before,
        # it becomes slightly more familiar.
        # ----------------------------------------------------

        for order in self.order_history:

            for item in order["items"]:

                if item["food"].id == food.id:

                    score += 5
                    break

        return score

    # ========================================================
    # DIVERSE SELECTION
    # ========================================================

    def select_diverse_items(
        self,
        scored_items,
        count=5
    ):

        selected = []

        used_categories = set()

        # ----------------------------------------------------
        # First pass:
        # Try to give different categories
        # ----------------------------------------------------

        for food, score in scored_items:

            if len(selected) >= count:
                break

            if food.category not in used_categories:

                selected.append(
                    (food, score)
                )

                used_categories.add(
                    food.category
                )

        # ----------------------------------------------------
        # Second pass:
        # Fill remaining positions
        # ----------------------------------------------------

        if len(selected) < count:

            for food, score in scored_items:

                if len(selected) >= count:
                    break

                if food not in [
                    x[0] for x in selected
                ]:

                    selected.append(
                        (food, score)
                    )

        return selected

    # ========================================================
    # MAIN RECOMMENDATION METHOD
    # ========================================================

    def recommend(
        self,
        user_text,
        count=5
    ):

        if not user_text.strip():

            raise AIRecommendationError(
                "Please tell me what kind of food you want."
            )

        # ----------------------------------------------------
        # Try Claude
        # ----------------------------------------------------

        preferences = self.parse_with_llm(
            user_text
        )

        # ----------------------------------------------------
        # Intelligent local fallback
        # ----------------------------------------------------

        if preferences is None:

            preferences = self.analyze_preferences(
                user_text
            )

        self.preference_history.append(
            preferences
        )

        profile = self.build_user_profile()

        scored_items = []

        # ----------------------------------------------------
        # Score EVERY AVAILABLE FOOD
        # ----------------------------------------------------

        for food in self.menu.foods.values():

            if food.stock <= 0:
                continue

            score = self.calculate_score(
                food,
                preferences,
                profile
            )

            scored_items.append(
                (food, score)
            )

        # ----------------------------------------------------
        # Sort by actual relevance
        # ----------------------------------------------------

        scored_items.sort(
            key=lambda x: x[1],
            reverse=True
        )

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # Only use randomness among VERY similar scores.
        #
        # We are NOT randomly selecting the food.
        # ----------------------------------------------------

        if len(scored_items) > 1:

            grouped = []

            i = 0

            while i < len(scored_items):

                base_score = scored_items[i][1]

                group = []

                while (
                    i < len(scored_items)
                    and abs(
                        scored_items[i][1]
                        - base_score
                    ) <= 3
                ):

                    group.append(
                        scored_items[i]
                    )

                    i += 1

                random.shuffle(group)

                grouped.extend(group)

            scored_items = grouped

        # ----------------------------------------------------
        # Diversity selection
        # ----------------------------------------------------

        selected = self.select_diverse_items(
            scored_items,
            count
        )

        # ----------------------------------------------------
        # Save recommendations
        # ----------------------------------------------------

        for food, score in selected:

            self.recommendation_history.append(
                food.id
            )

        return selected, preferences

    # ========================================================
    # LEARN FROM ORDER
    # ========================================================

    def learn_from_order(self, order):

        self.order_history.append(order)

        logging.info(
            "AI learned from completed order."
        )


# ============================================================
# CART
# ============================================================

class Cart:

    def __init__(self):

        self.items = {}

    # --------------------------------------------------------

    def add(self, food, quantity):

        if quantity <= 0:

            raise InvalidQuantityError(
                "Quantity must be greater than zero."
            )

        if food.stock <= 0:

            raise OutOfStockError(
                f"{food.name} is out of stock."
            )

        current_quantity = self.items.get(
            food.id,
            0
        )

        if (
            current_quantity + quantity
            > food.stock
        ):

            raise OutOfStockError(
                f"Only {food.stock} units of "
                f"{food.name} are available."
            )

        self.items[food.id] = (
            current_quantity + quantity
        )

        print(
            f"✓ Added {quantity} x "
            f"{food.name} to cart."
        )

    # --------------------------------------------------------

    def remove(self, food_id):

        if food_id not in self.items:

            raise FoodNotFoundError(
                "Food is not in the cart."
            )

        del self.items[food_id]

        print("✓ Item removed from cart.")

    # --------------------------------------------------------

    def update(self, food, quantity):

        if quantity <= 0:

            raise InvalidQuantityError(
                "Quantity must be greater than zero."
            )

        if quantity > food.stock:

            raise OutOfStockError(
                "Requested quantity exceeds stock."
            )

        self.items[food.id] = quantity

        print("✓ Cart updated.")

    # --------------------------------------------------------

    def subtotal(self, menu):

        total = 0

        for food_id, quantity in self.items.items():

            food = menu.get_food(food_id)

            total += food.price * quantity

        return total

    # --------------------------------------------------------

    def display(self, menu):

        if not self.items:

            print("\n🛒 Your cart is empty.")
            return

        print("\n" + "=" * 70)
        print("                         YOUR CART")
        print("=" * 70)

        for food_id, quantity in self.items.items():

            food = menu.get_food(food_id)

            amount = food.price * quantity

            print(
                f"{food.name:30} "
                f"x {quantity:<3} "
                f"₹{amount}"
            )

        print("-" * 70)

        print(
            f"Subtotal: ₹{self.subtotal(menu)}"
        )

        print("=" * 70)

    # --------------------------------------------------------

    def clear(self):

        self.items.clear()


# ============================================================
# ORDER
# ============================================================

class Order:

    next_order_id = 1000

    def __init__(
        self,
        cart,
        menu,
        customer,
        address,
        payment_method
    ):

        if not cart.items:

            raise EmptyCartError(
                "Cannot create order from empty cart."
            )

        Order.next_order_id += 1

        self.order_id = Order.next_order_id

        self.customer = customer

        self.address = address

        self.payment_method = payment_method

        self.timestamp = datetime.now()

        self.status = "Confirmed"

        self.items = []

        self.total = 0

        for food_id, quantity in cart.items.items():

            food = menu.get_food(food_id)

            self.items.append(
                {
                    "food": food,
                    "quantity": quantity
                }
            )

            self.total += (
                food.price * quantity
            )

    # --------------------------------------------------------

    def display(self):

        print("\n" + "=" * 70)
        print(
            f"                    ORDER #{self.order_id}"
        )
        print("=" * 70)

        print(
            f"Customer : {self.customer}"
        )

        print(
            f"Address  : {self.address}"
        )

        print(
            f"Payment  : {self.payment_method}"
        )

        print(
            f"Status   : {self.status}"
        )

        print(
            f"Time     : "
            f"{self.timestamp.strftime('%d-%m-%Y %I:%M %p')}"
        )

        print("-" * 70)

        for item in self.items:

            food = item["food"]

            quantity = item["quantity"]

            print(
                f"{food.name:30} "
                f"x {quantity:<3} "
                f"₹{food.price * quantity}"
            )

        print("-" * 70)

        print(
            f"TOTAL: ₹{self.total}"
        )

        print("=" * 70)


# ============================================================
# FOODAI APPLICATION
# ============================================================

class FoodAI:

    def __init__(self):

        self.menu = Menu()

        self.ai = AIRecommendationEngine(
            self.menu,
            use_llm=True
        )

        self.cart = Cart()

        self.orders = []

        self.customer_name = ""

        print("\n" + "=" * 70)
        print("                 🤖 FOODAI")
        print("           Intelligent Food Ordering")
        print("=" * 70)

        if self.ai.llm_enabled:

            print(
                "🧠 Claude AI: ENABLED"
            )

        else:

            print(
                "🧠 Smart Local AI: ENABLED"
            )

    # ========================================================
    # GET CUSTOMER DETAILS
    # ========================================================

    def customer_details(self):

        if not self.customer_name:

            name = input(
                "\nEnter your name: "
            ).strip()

            if not name:

                name = "Customer"

            self.customer_name = name

        return self.customer_name

    # ========================================================
    # AI RECOMMENDATION UI
    # ========================================================

    def ai_recommendation(self):

        print("\n" + "=" * 70)

        print(
            "🤖 AI FOOD RECOMMENDER"
        )

        print("=" * 70)

        print(
            "Tell me what you feel like eating."
        )

        print(
            "Examples:"
        )

        print(
            "• spicy vegetarian food under ₹250"
        )

        print(
            "• I want something filling"
        )

        print(
            "• I want a sweet dessert"
        )

        print(
            "• give me a healthy light meal"
        )

        print(
            "• I want chicken biryani"
        )

        request = input(
            "\nYour request: "
        ).strip()

        try:

            recommendations, preferences = (
                self.ai.recommend(request)
            )

            print("\n" + "=" * 90)

            print(
                "🧠 AI RECOMMENDATIONS"
            )

            print("=" * 90)

            for rank, (food, score) in enumerate(
                recommendations,
                1
            ):

                print(
                    f"\n#{rank} "
                    f"{food.name}"
                )

                print(
                    f"   Category : {food.category}"
                )

                print(
                    f"   Price    : ₹{food.price}"
                )

                print(
                    f"   Rating   : ⭐ {food.rating}"
                )

                print(
                    f"   Type     : "
                    f"{'Vegetarian' if food.vegetarian else 'Non-Vegetarian'}"
                )

                print(
                    f"   Spice    : "
                    f"{'Spicy' if food.spicy else 'Mild'}"
                )

                print(
                    f"   AI Match : {score:.1f}"
                )

            print("=" * 90)

            choice = input(
                "\nEnter food ID to add one "
                "(or press Enter to return): "
            ).strip()

            if choice:

                food_id = int(choice)

                food = self.menu.get_food(
                    food_id
                )

                self.cart.add(
                    food,
                    1
                )

        except ValueError:

            print(
                "❌ Please enter a valid number."
            )

        except FoodAIError as e:

            print(
                f"❌ {e}"
            )

        except Exception as e:

            logging.exception(
                "Unexpected AI recommendation error."
            )

            print(
                f"❌ Unexpected error: {e}"
            )

    # ========================================================
    # SEARCH
    # ========================================================

    def search_food(self):

        keyword = input(
            "\nSearch food: "
        ).strip()

        if not keyword:
            return

        results = self.menu.search(
            keyword
        )

        if not results:

            print(
                "❌ No matching food found."
            )

            return

        print("\nSearch Results:")

        for food in results:

            food.display()

    # ========================================================
    # ADD FOOD
    # ========================================================

    def add_food(self):

        try:

            food_id = int(
                input(
                    "\nEnter Food ID: "
                )
            )

            food = self.menu.get_food(
                food_id
            )

            quantity = int(
                input(
                    "Enter quantity: "
                )
            )

            self.cart.add(
                food,
                quantity
            )

        except ValueError:

            print(
                "❌ Please enter numbers only."
            )

        except FoodAIError as e:

            print(
                f"❌ {e}"
            )

    # ========================================================
    # REMOVE FROM CART
    # ========================================================

    def remove_from_cart(self):

        try:

            food_id = int(
                input(
                    "\nEnter Food ID to remove: "
                )
            )

            self.cart.remove(
                food_id
            )

        except ValueError:

            print(
                "❌ Invalid ID."
            )

        except FoodAIError as e:

            print(
                f"❌ {e}"
            )

    # ========================================================
    # UPDATE CART
    # ========================================================

    def update_cart(self):

        try:

            food_id = int(
                input(
                    "\nEnter Food ID: "
                )
            )

            food = self.menu.get_food(
                food_id
            )

            quantity = int(
                input(
                    "New quantity: "
                )
            )

            self.cart.update(
                food,
                quantity
            )

        except ValueError:

            print(
                "❌ Invalid input."
            )

        except FoodAIError as e:

            print(
                f"❌ {e}"
            )

    # ========================================================
    # CHECKOUT
    # ========================================================

    def checkout(self):

        if not self.cart.items:

            raise EmptyCartError(
                "Your cart is empty."
            )

        self.cart.display(
            self.menu
        )

        print("\nPayment Methods")

        print(
            "1. Cash on Delivery"
        )

        print(
            "2. UPI"
        )

        print(
            "3. Card"
        )

        payment_choice = input(
            "\nChoose payment method: "
        ).strip()

        payment_methods = {

            "1": "Cash on Delivery",

            "2": "UPI",

            "3": "Card"
        }

        if payment_choice not in payment_methods:

            raise PaymentError(
                "Invalid payment method."
            )

        payment_method = payment_methods[
            payment_choice
        ]

        customer = self.customer_details()

        address = input(
            "Enter delivery address: "
        ).strip()

        if not address:

            raise ValueError(
                "Address cannot be empty."
            )

        # ----------------------------------------------------
        # Verify stock BEFORE processing order
        # ----------------------------------------------------

        for food_id, quantity in (
            self.cart.items.items()
        ):

            food = self.menu.get_food(
                food_id
            )

            if quantity > food.stock:

                raise OutOfStockError(
                    f"Not enough stock for "
                    f"{food.name}."
                )

        # ----------------------------------------------------
        # Create order
        # ----------------------------------------------------

        order = Order(
            self.cart,
            self.menu,
            customer,
            address,
            payment_method
        )

        # ----------------------------------------------------
        # Reduce stock
        # ----------------------------------------------------

        for food_id, quantity in (
            self.cart.items.items()
        ):

            food = self.menu.get_food(
                food_id
            )

            food.stock -= quantity

        # ----------------------------------------------------
        # Store order
        # ----------------------------------------------------

        self.orders.append(
            order
        )

        # ----------------------------------------------------
        # Teach AI from the order
        # ----------------------------------------------------

        self.ai.learn_from_order(
            {
                "items": order.items,
                "total": order.total
            }
        )

        self.cart.clear()

        order.display()

        print(
            "\n🎉 ORDER PLACED SUCCESSFULLY!"
        )

        logging.info(
            f"Order #{order.order_id} placed."
        )

    # ========================================================
    # ORDER HISTORY
    # ========================================================

    def order_history(self):

        if not self.orders:

            print(
                "\nNo previous orders."
            )

            return

        print("\n" + "=" * 70)

        print(
            "                  ORDER HISTORY"
        )

        print("=" * 70)

        for order in self.orders:

            print(
                f"\nOrder #{order.order_id}"
            )

            print(
                f"Date: "
                f"{order.timestamp.strftime('%d-%m-%Y %I:%M %p')}"
            )

            print(
                f"Total: ₹{order.total}"
            )

            print(
                f"Payment: {order.payment_method}"
            )

            print(
                f"Status: {order.status}"
            )

        print("=" * 70)

    # ========================================================
    # MENU
    # ========================================================

    def show_main_menu(self):

        print("\n" + "=" * 70)

        print(
            "                      FOODAI"
        )

        print("=" * 70)

        print(
            "1. 🍔 View Full Menu"
        )

        print(
            "2. 🤖 AI Food Recommendation"
        )

        print(
            "3. 🔎 Search Food"
        )

        print(
            "4. ➕ Add Food to Cart"
        )

        print(
            "5. 🛒 View Cart"
        )

        print(
            "6. ❌ Remove Item"
        )

        print(
            "7. 🔄 Update Cart"
        )

        print(
            "8. 💳 Checkout"
        )

        print(
            "9. 📦 Order History"
        )

        print(
            "10. 🚪 Exit"
        )

        print("=" * 70)

    # ========================================================
    # MAIN LOOP
    # ========================================================

    def run(self):

        while True:

            try:

                self.show_main_menu()

                choice = input(
                    "\nEnter your choice: "
                ).strip()

                if choice == "1":

                    self.menu.display()

                elif choice == "2":

                    self.ai_recommendation()

                elif choice == "3":

                    self.search_food()

                elif choice == "4":

                    self.add_food()

                elif choice == "5":

                    self.cart.display(
                        self.menu
                    )

                elif choice == "6":

                    self.remove_from_cart()

                elif choice == "7":

                    self.update_cart()

                elif choice == "8":

                    self.checkout()

                elif choice == "9":

                    self.order_history()

                elif choice == "10":

                    print(
                        "\nThank you for using FOODAI! 🤖🍕"
                    )

                    print(
                        "Goodbye!"
                    )

                    break

                else:

                    raise InvalidChoiceError(
                        "Please choose an option "
                        "between 1 and 10."
                    )

            except InvalidChoiceError as e:

                print(
                    f"❌ {e}"
                )

            except KeyboardInterrupt:

                print(
                    "\n\nProgram interrupted."
                )

                break

            except FoodAIError as e:

                print(
                    f"❌ {e}"
                )

                logging.error(
                    str(e)
                )

            except Exception as e:

                logging.exception(
                    "Unexpected application error."
                )

                print(
                    f"❌ Unexpected error: {e}"
                )


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    app = FoodAI()

    app.run()
