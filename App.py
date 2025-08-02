from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_config import db
from google.cloud import firestore

app = Flask(__name__)
CORS(app)

@app.route('/api/orders', methods=['POST'])
def add_order():
    data = request.get_json()
    phone = data.get('phone')  
    cart_items = data.get('cart')

    print("Received cart_items:", cart_items)
    print("User phone:", phone)

    if not phone or not cart_items:
        return jsonify({'error': 'Missing phone or cart items'}), 400

    if not isinstance(cart_items, list) or not all(isinstance(item, dict) for item in cart_items):
        return jsonify({'error': 'Cart must be a list of item dictionaries.'}), 400

    user_ref = db.collection('users').document(phone)
    user_doc = user_ref.get()

    if not user_doc.exists:
        return jsonify({'error': f"User with phone '{phone}' not found."}), 404

    try:
        order_data = {
            'items': cart_items
        }

        user_ref.update({
            'orders': firestore.ArrayUnion([order_data]),
            'cart': [] 
        })

        print("Order placed successfully.")
        return jsonify({'message': 'Order placed successfully'}), 200

    except Exception as e:
        print('Firestore Error:', e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['POST'])
def add_or_update_user():
    data = request.get_json()
    required_fields = ["name", "phone", "address", "cart"]
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields."}), 400

    phone = data['phone'].strip()

    if not phone:
        return jsonify({"error": "Phone number is required and cannot be empty."}), 400

    user_ref = db.collection('users').document(phone)
    user_doc = user_ref.get()

    if user_doc.exists:
        existing = user_doc.to_dict()
        existing_cart = existing.get("cart", [])
        new_cart = data["cart"]

        cart_dict = {item["name"]: item for item in existing_cart}
        for item in new_cart:
            cart_dict[item["name"]] = item
        merged_cart = list(cart_dict.values())

        user_ref.update({
            "name": data["name"],
            "address": data["address"],
            "cart": merged_cart
        })
    else:
        user_ref.set({
            "name": data["name"],
            "phone": phone,
            "address": data["address"],
            "cart": data["cart"],
            "orders": []
        })

    return jsonify({"message": "User data updated.", "user_id": phone}), 201

@app.route('/api/signin', methods=['POST'])
def sign_in():
    data = request.get_json()
    required_fields = ["phone", "name", "address"]
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields."}), 400

    phone = data["phone"]
    user_ref = db.collection('users').document(phone)
    user_doc = user_ref.get()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        return jsonify({
            "name": user_data.get("name", ""),
            "phone": phone,
            "address": user_data.get("address", ""),
            "cart": user_data.get("cart", [])
        }), 200
    else:
        user_ref.set({
            "name": data["name"],
            "phone": phone,
            "address": data["address"],
            "cart": [],
            "orders": []
        })
        return jsonify({
            "name": data["name"],
            "phone": phone,
            "address": data["address"],
            "cart": []
        }), 201


@app.route('/api/users/<phone>', methods=['GET'])
def get_user(phone):
    phone = phone.strip()
    if not phone:
        return jsonify({"error": "Phone number required"}), 400

    user_ref = db.collection('users').document(phone)
    user_doc = user_ref.get()

    if user_doc.exists:
        return jsonify(user_doc.to_dict()), 200
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/api/reservations', methods=['POST'])
def add_or_update_reservation():
    data = request.get_json()
    required_fields = ["name", "phone", "date", "time", "guests"]

    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required reservation fields."}), 400

    phone = data["phone"].strip()
    if not phone:
        return jsonify({"error": "Phone number cannot be empty."}), 400

    reservation_ref = db.collection("reservations").document(phone)

    reservation_ref.set({
        "name": data["name"],
        "phone": phone,
        "date": data["date"],
        "time": data["time"],
        "guests": int(data["guests"]),
    })

    return jsonify({"message": "Reservation successfully added/updated!"}), 201


if __name__ == '__main__':
    app.run(debug=True)
