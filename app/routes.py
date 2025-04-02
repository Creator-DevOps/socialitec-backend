from flask import Blueprint, jsonify
from . import db
from sqlalchemy import text

main = Blueprint('main', __name__)

@main.route("/testdb")
def test_db():
    result = db.session.execute(text("SELECT 1"))
    return jsonify({"ok": True, "result": [r[0] for r in result]})
