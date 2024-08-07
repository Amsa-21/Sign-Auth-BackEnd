from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
from flask_cors import CORS
from functions import *
import json, uuid

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.json.sort_keys = False

BASE_FOLDER = "D:/SNT/.database/"
clean()

# model, encoder = refresh_model()

@app.route('/')
def hello():
  return "<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Flask API Running...</h1></div>"

@app.route('/metadatafrompdf', methods=['POST'])
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
  name = getNameFromCode(member_json['countryNameIssuer'])
  insert_query = 'INSERT INTO ownTrustList (codeCountryRegion, hLocation, cName) VALUES (%s, %s, %s)'
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(insert_query, (member_json['countryNameIssuer'], name, member_json['organizationNameIssuer']))
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
  try:
    users = get_data_from_table("users")
    username = request.json.get('email')
    password = request.json.get('password')
    for user in (users):
      if user["email"].lower() == username.lower() and user["password"] == password:
        token = generate_token()
        return jsonify({"success": True, "userToken": token, "username": user["prenom"] + " " + user["nom"], "telephone": user["telephone"], "role": user["role"]})
    return jsonify({"success": False, "error": "Invalid credentials"})
  except Exception as e:
    return jsonify({"success": False, "error": "No database connexion"})

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
  res = faceScan(filename)
  conn = get_db_connection()
  cursor = conn.cursor()
  try:
    req = "INSERT INTO users (nom, prenom, date, email, password, telephone, organisation, poste, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(req, (member_json['nom'].upper(), member_json['prenom'].capitalize(), member_json['date'], member_json['email'].capitalize(), member_json['password'], member_json['numero'], member_json['organisation'].capitalize(), member_json['poste'].capitalize(), "User"))  
    identity = f"{member_json['prenom'].capitalize()} {member_json['nom'].upper()} {member_json['numero']}"
    frames2db(identity, res, cursor)
    conn.commit()
    cursor.close()
    conn.close()
  except Exception as e:
    cursor.close()
    conn.close()
    return jsonify({"success": False, "error": str(e)})
  create_PKCS(identity, member_json['email'].capitalize(), f"{member_json['prenom'].capitalize()} {member_json['nom'].upper()}", member_json['organisation'].capitalize())
  return jsonify({"success": True})

@app.route('/editUser', methods=['POST'])
def editUser():
  member = request.form['member']
  member_json = json.loads(member)
  conn = get_db_connection()
  cursor = conn.cursor()
  try:
    req = "UPDATE users SET nom = %s, prenom = %s, date = %s, email = %s, password = %s, telephone = %s, organisation = %s, poste = %s, role = %s WHERE id = %s;"
    cursor.execute(req, (member_json['nom'].upper(), member_json['prenom'].capitalize(), member_json['date'], member_json['email'].capitalize(), member_json['password'], member_json['telephone'], member_json['organisation'].capitalize(), member_json['poste'].capitalize(), member_json['role'].capitalize(), member_json['id']))
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

@app.route('/predict', methods=['POST'])
def predict():
  face_img = request.form['image']
  if model is not None:
    face, person = prediction(face_img, model, encoder, refresh=False)
    if face:
      face = "data:image/jpg;base64," + face
      return jsonify({"success": True, "person": person, "face": face})
  return jsonify({"success": True, "person": "No model trained", "face": None})

@app.route('/signPDF', methods=['POST'])
async def sign():
  id = request.form['id']
  user = request.form['user']
  code = request.form['code']
  img = request.form['image']
    
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM public."signRequest" WHERE id = %s', (id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    for row in rows:
      if row:
        filename = rf"{BASE_FOLDER}{row[1]}"
        cursign = row[9]
        numsigners = row[8]
    certs = get_data_from_table("certificates")
    for cert in  certs:
      if user == cert["person"] and code == cert["digit"]:
        ident, success = await signPdf(pdf_path=filename, certificate=cert["certificate"], private_key=cert["private_key"])
        if success:
          savePicture(ident, img)
          with open(filename, "rb") as file:
            data = base64.b64encode(file.read()).decode('utf-8')
          clean()
          conn = get_db_connection()
          cursor = conn.cursor()
          cursor.execute('UPDATE public."signRequest" set cursign = %s, status = %s WHERE id = %s', (int(cursign)+1, (int(cursign)+1)//int(numsigners), id))
          conn.commit()
          cursor.close()
          conn.close()
          return jsonify({"success": True, "pdfdata": data})
        clean()
        return jsonify({"success": False, "error": "Signature déjà présente !"})
    clean()
    return jsonify({"success": False, "error": "Code invalide !"})
  except Exception as e:
    cursor.close()
    conn.close()
    clean()
    return jsonify({"success": False, "error": str(e)})

@app.route('/addRequest', methods=['POST'])
def addRequest():
  file = request.files['fichier']
  user = request.form['demandeur']
  t=user.split(' ')
  filename = f"Demande-{t[0]}_{t[1]}_{uuid.uuid4()}.pdf"
  file.save(f"{BASE_FOLDER}{filename}")
  signers = request.form['signataires']
  obj = request.form['objet']
  comment = request.form['commentaire']
  date = datetime.datetime.now(datetime.UTC).strftime('%H:%M:%S %d/%m/%Y')
  signer = [user.strip() for user in signers.split(',')]
  insert_query = 'INSERT INTO public."signRequest" (filename, person, signers, object, comment, date, status, nbresign, cursign) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(insert_query, (filename, user, signer, obj, comment, date, 0, len(signer), 0))
    conn.commit()
  except Exception as e:
    cursor.close()
    conn.close()
    return jsonify({"success": False, "error": str(e)})
  cursor.close()
  conn.close()
  return jsonify({"success": True})

@app.route('/allRequest', methods=['GET'])
def allRequest():
  data = get_data_from_table("signRequest")
  return jsonify({"success": True, "result": data})

@app.route('/deleteRequest', methods=['DELETE'])
def deleteRequest():
  id = request.args.get('id')
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM public."signRequest" WHERE id = %s', (id,))
    rows = cursor.fetchall()
    cursor.execute('DELETE FROM public."signRequest" WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    for row in rows:
      if row:
        filename = row[1]
        os.remove(rf"{BASE_FOLDER}{filename}")
  except Exception as e:
    cursor.close()
    conn.close()
    return jsonify({"success": False, "error": str(e)})
  data = get_data_from_table("signRequest")
  return jsonify({"success": True, "result": data})

@app.route('/refuseRequest', methods=['POST'])
def refuseRequest():
  id = request.args.get('id')
  conn = get_db_connection()
  cursor = conn.cursor()
  try:
    req = 'Update public."signRequest" set status = 2 WHERE id = %s'
    cursor.execute(req, (id,))
    conn.commit()
    cursor.close()
    conn.close()
  except Exception as e:
    cursor.close()
    conn.close()
    return jsonify({"success": False, "error": str(e)})
  data = get_data_from_table("signRequest")
  return jsonify({"success": True, "result": data})

@app.route('/getPDF', methods=['POST'])
def getPDF():
  id = request.args.get('id')
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM public."signRequest" WHERE id = %s', (id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    filename = rf"{BASE_FOLDER}{rows[0][1]}"
    with open(filename, "rb") as file:
      data = base64.b64encode(file.read()).decode('utf-8')
  except Exception as e:
    cursor.close()
    conn.close()
    return jsonify({"success": False, "error": str(e)})
  return jsonify({"success": True, "result": data})

""" 
TODO
Mailing
Contrôle sur les signataires Vérification des signatures """

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port='8080')
