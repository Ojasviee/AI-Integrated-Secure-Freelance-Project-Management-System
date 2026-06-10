from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from database import db
from models import User, Project
import bcrypt

app = Flask(__name__)
CORS(app)

# CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///freelanceai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'

db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

# ---------------- HOME ----------------
@app.route('/')
def home():
    return jsonify({"message": "Backend Running Successfully"})


# ---------------- REGISTER ----------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 400

    hashed = bcrypt.hashpw(
        data['password'].encode('utf-8'),
        bcrypt.gensalt()
    )

    user = User(
        username=data['username'],
        password=hashed.decode('utf-8'),
        role=data['role']
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"})


# ---------------- LOGIN ----------------
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    user = User.query.filter_by(username=data['username']).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if bcrypt.checkpw(data['password'].encode('utf-8'),
                      user.password.encode('utf-8')):

        token = create_access_token(identity=user.username)

        return jsonify({
            "token": token,
            "role": user.role
        })

    return jsonify({"message": "Invalid credentials"}), 401


# ---------------- CREATE PROJECT (AI ENGINE) ----------------
@app.route('/create-project', methods=['POST'])
def create_project():

    data = request.json

    budget = int(data['budget'])
    text = (data['title'] + " " + data['description']).lower()
    deadline = data['deadline'].lower()

    trust_score = 100
    reasons = []

    # --- budget
    if budget < 1000:
        trust_score -= 40
        reasons.append("Very low budget")

    elif budget < 3000:
        trust_score -= 20
        reasons.append("Budget may be insufficient")

    # --- urgency
    urgency_words = ["urgent", "asap", "immediately", "today", "tomorrow"]
    for w in urgency_words:
        if w in text:
            trust_score -= 15
            reasons.append(f"Urgency keyword: {w}")

    # --- deadline
    if "today" in deadline or "tomorrow" in deadline:
        trust_score -= 25
        reasons.append("Very short deadline")

    # --- risky keywords
    risky = [
        "banking", "crypto", "wallet", "admin access",
        "database access", "hack", "bypass",
        "full system", "ecommerce platform"
    ]

    for w in risky:
        if w in text:
            trust_score -= 10
            reasons.append(f"Sensitive keyword: {w}")

    # clamp
    trust_score = max(0, min(trust_score, 100))

    # risk level
    if trust_score >= 80:
        risk = "Low"
    elif trust_score >= 50:
        risk = "Medium"
    else:
        risk = "High"

    ai_reason = " | ".join(reasons) if reasons else "Clean project"

    project = Project(
        title=data['title'],
        description=data['description'],
        budget=budget,
        deadline=data['deadline'],
        client_name=data['client_name'],
        trust_score=trust_score,
        risk_level=risk,
        ai_reason=ai_reason
    )

    db.session.add(project)
    db.session.commit()

    return jsonify({
        "message": "Project created successfully",
        "trust_score": trust_score,
        "risk_level": risk,
        "ai_reason": ai_reason
    })


# ---------------- GET PROJECTS ----------------
@app.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()

    return jsonify([
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "budget": p.budget,
            "deadline": p.deadline,
            "client_name": p.client_name,
            "trust_score": p.trust_score,
            "risk_level": p.risk_level,
            "ai_reason": p.ai_reason
        }
        for p in projects
    ])


# ---------------- DELETE ----------------
@app.route('/delete-project/<int:id>', methods=['DELETE'])
def delete_project(id):
    project = Project.query.get(id)

    if not project:
        return jsonify({"message": "Not found"}), 404

    db.session.delete(project)
    db.session.commit()

    return jsonify({"message": "Deleted"})


if __name__ == '__main__':
    app.run(debug=True)