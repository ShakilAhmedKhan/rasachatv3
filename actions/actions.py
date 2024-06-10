from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import sqlite3
from datetime import datetime

class ActionShowProduct(Action):
    def name(self) -> Text:
        return "action_show_product"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        product_name = next(tracker.get_latest_entity_values("product_name"), None)
        if product_name:
            conn = sqlite3.connect('products.db')
            cursor = conn.cursor()
            cursor.execute("SELECT product_name, price, description FROM products WHERE product_name=?", (product_name,))
            result = cursor.fetchone()
            conn.close()

            if result:
                name, price, description = result
                dispatcher.utter_message(text=f"Product: {name}\nPrice: ${price}\nDescription: {description}")
            else:
                dispatcher.utter_message(text="Sorry, I couldn't find any details for that product.")
        else:
            dispatcher.utter_message(text="Please provide the product name.")
        return []

class ActionSuggestProduct(Action):
    def name(self) -> Text:
        return "action_suggest_product"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()
        cursor.execute("SELECT product_name, price, description FROM products ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        conn.close()

        if result:
            product_name, price, description = result
            dispatcher.utter_message(text=f"I suggest {product_name} priced at ${price}. {description}")
        else:
            dispatcher.utter_message(text="Sorry, I couldn't find any products.")
        return []

class ActionOrderProduct(Action):
    def name(self) -> Text:
        return "action_order_product"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        product_name = next(tracker.get_latest_entity_values("product_name"), None)
        if product_name:
            conn = sqlite3.connect('products.db')
            cursor = conn.cursor()
            order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO orders (product_name, order_date) VALUES (?, ?)", (product_name, order_date))
            conn.commit()
            conn.close()
            dispatcher.utter_message(text=f"Order placed for {product_name}.")
        else:
            dispatcher.utter_message(text="Please specify the product name you want to order.")
        return []
