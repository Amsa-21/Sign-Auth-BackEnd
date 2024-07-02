from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
from flask_cors import CORS
from functions import *
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.json.sort_keys = False

clean()

@app.route('/')
def hello():
    return "<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Flask API Running...</h1></div>"

@app.route('/metadatafrompdf', methods=['GET', 'POST'])
def get_data_from_pdf():
    file = request.files['fichier']
    filename = secure_filename(file.filename)
    file.save(filename)
    certificate_data = extractCert(filename)
    if len(certificate_data) > 0:
        isEmpty = False
        signs = find_signature(filename)
        res = {"isEmpty": isEmpty, "result": certificate_data, "signature": signs}
    else:
        isEmpty = True
        res = {"isEmpty": isEmpty, "result": {}, "signature": {}}
    clean()
    return jsonify(res)

@app.route('/addMember', methods=['POST'])
def addNewMember():
    member = request.form['member']
    member_json = json.loads(member)
    insert_query = 'INSERT INTO ownTrustList (codeCountryRegion, hLocation, cName, textFind) VALUES (%s, %s, %s, %s)'
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(insert_query, (member_json['codeCountryRegion'].upper(), member_json['hLocation'].capitalize(), member_json['cName'], member_json['textFind']))
        conn.commit()
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "error": str(e)})
    cursor.close()
    conn.close()
    data = get_data_from_table("ownTrustList")
    return jsonify({"success": True, "result": data})

@app.route('/data', methods=['GET'])
def get_data_from_postgres():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM "approvedTrustList";')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    data = []
    for row in rows:
        data.append({
            "codePaysRegion": row[1],
            "emplacementSiegeSocial": row[2],
            "nomEntreprise": row[3]
        })
    return jsonify({"result": data})

@app.route('/ownMember', methods=['GET'])
def getMember():
    data = get_data_from_table("ownTrustList")
    return jsonify({"result": data})

@app.route('/editOne', methods=['POST'])
def editOne():
    member = request.form['member']
    member_json = json.loads(member)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        req = "UPDATE ownTrustList SET codecountryregion = %s, hlocation = %s, cname = %s, textFind = %s WHERE id = %s;"
        cursor.execute(req, (member_json['codeCountryRegion'].upper(), member_json['hLocation'], member_json['cName'], member_json['textFind'], member_json['id']))
        conn.commit()
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "error": str(e)})
    cursor.close()
    conn.close()
    data = get_data_from_table("ownTrustList")
    return jsonify({"success": True, "result": data})

@app.route('/deleteOne', methods=['DELETE'])
def deleteOne():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        req = 'DELETE FROM ownTrustList WHERE id = %s;'
        cursor.execute(req, (id,))
        conn.commit()
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "error": str(e)})
    cursor.close()
    conn.close()
    data = get_data_from_table("ownTrustList")
    return jsonify({"success": True, "result": data})

@app.route('/getPDFInfo', methods=['GET', 'POST'])
def getPDFInfo():
    file = request.files['fichier']
    filename = secure_filename(file.filename)
    file.save(filename)
    data = autorityFinder(filename)
    
    if data:
        isEmpty = False
        tab = get_data_from_table("ownTrustList")
        row = correlation(data, tab)
        if row:
            res = {"isEmpty": isEmpty, "result": data, "correlation": row}
        else:
            res = {"isEmpty": isEmpty, "result": data, "correlation":{}}
    else:
        isEmpty = True
        res = {"isEmpty": isEmpty, "result":{}, "correlation":{}}
    clean()
    return jsonify(res)

@app.route('/addMemberFromAnalysis', methods=['POST'])
def addMemberFromAnalysis():
    member = request.form['member']
    member_json = json.loads(member)
    name = getNameFromCode(member_json['IssuerC'])
    insert_query = 'INSERT INTO ownTrustList (codeCountryRegion, hLocation, cName) VALUES (%s, %s, %s)'
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(insert_query, (member_json['IssuerC'], name, member_json['IssuerO']))
        conn.commit()
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "error": str(e)})
    cursor.close()
    conn.close()
    return jsonify({"success": True, "error": None})

@app.route('/login', methods=['POST'])
def login():
    users = get_data_from_table("users")
    username = request.json.get('username')
    password = request.json.get('password')
    for user in (users):
        if user["username"].lower() == username.lower() and user["password"] == password:
            token = generate_token()
            return jsonify({"success": True, "userToken": token, "username": user["username"], "role": user["role"]})
    return jsonify({"success": False, "error": "Invalid credentials"})

@app.route('/allUsers', methods=['GET'])
def allUsers():
    data = get_data_from_table("users")
    return jsonify({"result": data})

@app.route('/addUser', methods=['POST'])
def addNewUser():
    member = request.form['user']
    video = request.files['file']
    member_json = json.loads(member)
    filename = secure_filename(video.filename)
    video.save(filename)
    faceScan(filename)
    return jsonify({"success": True})

@app.route('/editUser', methods=['POST'])
def editUser():
    member = request.form['member']
    member_json = json.loads(member)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        req = "UPDATE users SET username = %s, email = %s, password = %s, role = %s WHERE id = %s;"
        cursor.execute(req, (member_json['username'].capitalize(), member_json['email'].capitalize(), member_json['password'], member_json['role'].capitalize(), member_json['id']))
        conn.commit()
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "error": str(e)})
    cursor.close()
    conn.close()
    data = get_data_from_table("users")
    return jsonify({"success": True, "result": data})

@app.route('/deleteUser', methods=['DELETE'])
def deleteUser():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        req = 'DELETE FROM users WHERE id = %s;'
        cursor.execute(req, (id,))
        conn.commit()
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "error": str(e)})
    cursor.close()
    conn.close()
    data = get_data_from_table("users")
    return jsonify({"success": True, "result": data})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='8080')
