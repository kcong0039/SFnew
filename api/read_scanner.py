import requests
import json
import ast

# Airtable API config
API_KEY = "patYTVmRlbjgZsLyK.36e936cecbe99037db01f5a35b2cb1052c25ccaaba84347f541e4100ab2073a2"
BASE_ID = "appqkpDOLvi6AESlN"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

kitchen_setup_table = "tblNZQiFdZQzoLkVt"
client_servings_table = "tblVwpvUmsTS2Se51"

# Airtable table endpoints
CLIENT_SERVINGS_URL = f"https://api.airtable.com/v0/{BASE_ID}/{client_servings_table}"
KITCHEN_SETUP_URL    = f"https://api.airtable.com/v0/{BASE_ID}/{kitchen_setup_table}"


def fetch_kitchen_setup(station_prefix, dish_name):
    """
    Fetch and return an ordered list of allowed ingredients for a given station and dish.
    """
    ingredients = []
    params = {}

    while True:
        resp = requests.get(KITCHEN_SETUP_URL, headers=HEADERS, params=params)
        if resp.status_code != 200:
            raise RuntimeError(f"Airtable error: {resp.text}")
        data = resp.json()

        for record in data.get("records", []):
            fields = record.get("fields", {})
            stations = fields.get("Station", [])
            if not isinstance(stations, list):
                stations = [stations]

            ingredient = fields.get("Ingredient")
            sequence   = fields.get("Sequence", 0)
            dish       = fields.get("Dish Name")

            if dish != dish_name:
                continue

            for st in stations:
                if isinstance(st, str) and st.lower().endswith(station_prefix.lower()):
                    if ingredient:
                        ingredients.append((ingredient, sequence))
                    break

        if "offset" in data:
            params["offset"] = data["offset"]
        else:
            break

    # sort by sequence and dedupe
    ingredients.sort(key=lambda x: x[1])
    seen = set()
    ordered = []
    for ingr, seq in ingredients:
        if ingr not in seen:
            seen.add(ingr)
            ordered.append(ingr)
    return ordered


def fetch_client_servings(order_id):
    """
    Fetch the Airtable client servings record matching the given order ID.
    """
    params = {}
    while True:
        resp = requests.get(CLIENT_SERVINGS_URL, headers=HEADERS, params=params)
        if resp.status_code != 200:
            raise RuntimeError(f"Airtable error: {resp.text}")
        data = resp.json()
        for record in data.get("records", []):
            fields   = record.get("fields", {})
            record_id = str(fields.get("#"))
            if record_id == order_id:
                return fields  # return the fields dict directly
        if "offset" in data:
            params["offset"] = data["offset"]
        else:
            break
    return {}


def process_scan(raw_code):
    """
    Main scanning logic. Takes the raw barcode string, fetches data, and returns a JSON-ready dict.
    """
    # parse prefix letters and numeric portion
    prefix   = ''.join([c for c in raw_code if c.isalpha()])
    order_id = ''.join([c for c in raw_code if c.isdigit()])[1:]

    if not prefix or not order_id:
        raise ValueError(f"Invalid scan format: {raw_code}")

    # fetch serving record
    fields = fetch_client_servings(order_id)
    if not fields:
        raise LookupError(f"No record found for order {order_id}")

    dish = fields.get("Dish")[0] if isinstance(fields.get("Dish"), list) else fields.get("Dish")

    # fetch allowed ingredients
    allowed = fetch_kitchen_setup(prefix, dish)

    # parse modified recipe details
    raw_details = fields.get("Modified Recipe Details", "{}")
    try:
        recipe_details = ast.literal_eval(raw_details)
    except Exception:
        recipe_details = {}

    ingredients = []
    for ingr in allowed:
        if ingr in recipe_details:
            grams   = recipe_details[ingr]
            portion = f"{round(grams,2)}g" if isinstance(grams, (int,float)) else "—"
            name    = ' '.join(ingr.split(' ')[1:]) if ' ' in ingr else ingr
            ingredients.append({"name": name, "portion": portion})

    # dietary restrictions
    notes = fields.get("Nutrition Notes", [])
    if isinstance(notes, str):
        notes = [notes]
    dietary = [n.strip() for n in notes]

    return {
        "clientName": fields.get("Customer Name", []),
        "mealType":   fields.get("Order Type (from Linked OrderItem)", []),
        "dishName":   fields.get("Dish", []),
        "dishNumber": int(order_id),
        "stationNumber": f"Station {prefix}",
        "barcodeNumber": raw_code,
        "ingredients": ingredients,
        "dietaryRestrictions": dietary,
    }


if __name__ == "__main__":
    print("🔄 Ready to scan barcodes (Ctrl+C to stop)...")
    try:
        while True:
            raw = input("Scan a barcode: ").strip()
            try:
                result = process_scan(raw)
                print(json.dumps(result, indent=2))
            except Exception as err:
                print(f"❌ {err}")
    except KeyboardInterrupt:
        print("\n🛑 Scanner stopped.")
