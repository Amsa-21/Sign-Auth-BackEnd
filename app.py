from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from flask_cors import CORS
from functions import *
import json, uuid

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.json.sort_keys = False
FRONT_URL = "http://localhost:3000/extsign"
BASE_FOLDER = ".database/"
SECRET_KEY = b'\xb9\x82C)\x90\xca\xa1b\x89Q\x7f\xe4\x1c\xed\xd7I\xa7\t\xe7HW\xb36\xb1'
if not os.path.exists(BASE_FOLDER.split('/')[0]):
  os.makedirs(BASE_FOLDER)

clean()

model, encoder = refresh_model()
cache = {"model": model, "encoder": encoder}

app.config['JWT_SECRET_KEY'] = SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=15)

jwt = JWTManager(app)

@app.route('/')
def hello():
  return """<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'>
              <h1>Flask API Running...</h1>
            </div>
          """

@app.route('/metadatafrompdf', methods=['POST'])
def get_data_from_pdf():
  file = request.files['fichier']
  filename = secure_filename(file.filename)
  file.save(filename)
  rows = get_data_from_table("certificates")
  tab = []
  i = 0
  for row in rows:
    cert_path = f"cert{i}.pem"
    with open (cert_path, "wb") as f:
      f.write(base64.b64decode(row["certificate"]))
    tab.append(cert_path)
    i += 1
  certificate_data = extractCert(filename, tab)
  if len(certificate_data) > 0:
    isEmpty = False
    signs = find_signature(filename)
    result = {}
    for i, (cert, sign) in enumerate(zip(certificate_data.items(), signs.items())):
      result[i] = {"cert": cert, "sign": sign}
    res = {"isEmpty": isEmpty, "result": result}
  else:
    isEmpty = True
    res = {"isEmpty": isEmpty, "result": None}
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
        access_token = create_access_token(identity=user["email"])
        refresh_token = create_refresh_token(identity=user["email"])
        return jsonify({
          "success": True,
          "access_token": access_token,
          "refresh_token": refresh_token,
          "username": f"{user['prenom']} {user['nom']}",
          "telephone": user["telephone"],
          "role": user["role"]
        })
    return jsonify({"success": False, "error": "Invalid credentials"})
  except:
    return jsonify({"success": False, "error": "No database connexion"})

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({"access_token": new_access_token})

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
  return jsonify({"success": True, "msg": "Successfully logged out"})

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user)

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
  if res:
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      req = "INSERT INTO users (nom, prenom, date, email, password, telephone, organisation, poste, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
      cursor.execute(req, (member_json['nom'].upper(), member_json['prenom'].capitalize(), member_json['date'], member_json['email'].capitalize(), member_json['password'], member_json['numero'], member_json['organisation'].capitalize(), member_json['poste'].capitalize(), "User"))  
      identity = f"{member_json['prenom'].capitalize()} {member_json['nom'].upper()} {member_json['numero']}"
      frames2db(identity, res, cursor)
      conn.commit()
      cursor.close()
      conn.close()
      model, encoder = refresh_model()
      cache["model"] = model
      cache["encoder"] = encoder
    except Exception as e:
      cursor.close()
      conn.close()
      return jsonify({"success": False, "error": str(e)})
    create_PKCS(identity, member_json['email'].capitalize(), f"{member_json['prenom'].capitalize()} {member_json['nom'].upper()}", member_json['organisation'].capitalize())
    return jsonify({"success": True})
  return jsonify({"success": False})

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
  pers = request.form['person']
  face, person = prediction(face_img, cache["model"], cache["encoder"], refresh=False)
  if face and person == pers:
    return jsonify({"success": True, "person": person, "face": face})
  return jsonify({"success": False, "person": None, "face": None})

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
        person = row[2]
        cursign = row[9]
        numsigners = row[8]
        signatures = row[10]
    certs = get_data_from_table("certificates")
    for cert in  certs:
      if user == cert["person"] and code == cert["digit"]:
        ident, success = await signPdf(pdf_path=filename, certificate=cert["certificate"], private_key=cert["private_key"])
        if success:
          signatures.append(user)
          savePicture(ident, img)
          conn = get_db_connection()
          cursor = conn.cursor()
          cursor.execute('UPDATE public."signRequest" set cursign = %s, status = %s, signatures = %s WHERE id = %s', (int(cursign)+1, (int(cursign)+1)//int(numsigners), signatures, id))
          conn.commit()
          if((int(cursign)+1)//int(numsigners) == 1):
            person = person.split(" ")
            cursor.execute('SELECT * FROM users WHERE telephone = %s', (person[-1],))
            rows = cursor.fetchall()
            for row in rows:
              if row:
                sendSuccessEmail(to_address=row[4], date=datetime.datetime.now(datetime.UTC).strftime('%H:%M:%S %d/%m/%Y'))
          cursor.close()
          conn.close()
          clean()
          return jsonify({"success": True})
        clean()
        return jsonify({"success": False, "error": "Signature déjà présente !"})
    clean()
    return jsonify({"success": False, "error": "Code invalide !"})
  except Exception as e:
    cursor.close()
    conn.close()
    clean()
    return jsonify({"success": False, "error": str(e)})

@app.route('/externalSignPDF', methods=['POST'])
async def externalSign():
  name = request.form['user']
  file = request.form['filename']
  face = request.form['image']
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM public."extSignRequest" WHERE filename = %s', (file,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    for row in rows:
      if row:
        person = row[2]
        cursign = row[9]
        numsigners = row[8]
    certs = get_data_from_table("certificates")
    for cert in certs:
      if cert["person"] == "Externe":
        user = f"{" ".join(name.split("_")[:-1])} <{name.split("_")[-1]}>"
        filename = rf"{BASE_FOLDER}{file}"
        face = base64ToImg(face)
        faceD = faceDetector(face)
        if faceD is not None:
          ident, success = await externalSignPdf(name= user, pdf_path=filename, certificate=cert["certificate"], private_key=cert["private_key"])
          if success:
            img = image_to_base64(cv2.cvtColor(faceD, cv2.COLOR_BGR2RGB))
            savePicture(ident, img)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE public."extSignRequest" set cursign = %s, status = %s WHERE filename = %s', (int(cursign)+1, (int(cursign)+1)//int(numsigners), file))
            conn.commit()
            if((int(cursign)+1)//int(numsigners) == 1):
              cursor.execute('SELECT * FROM users WHERE telephone = %s', (person.split(" ")[-1],))
              rows = cursor.fetchall()
              for row in rows:
                if row:
                  sendSuccessEmail(to_address=row[4], date=datetime.datetime.now(datetime.UTC).strftime('%H:%M:%S %d/%m/%Y'))
            cursor.close()
            conn.close()
            clean()
            return jsonify({"success": True})
          cursor.close()
          conn.close()
          clean()
          return jsonify({"success": False})
        clean()
        return jsonify({"success": False, "error": "Aucun visage détécté !"})
  except Exception as e:
    cursor.close()
    conn.close()
    clean()
    return jsonify({"success": False, "error": str(e)})

@app.route('/addRequest', methods=['POST'])
def addRequest():
  file = request.files['fichier']
  user = request.form['demandeur']
  filename = f"Demande-{"_".join(user.split(" ")[:-1])}_{uuid.uuid4()}.pdf"
  file.save(f"{BASE_FOLDER}{filename}")
  signers = request.form['signataires']
  obj = request.form['objet']
  comment = request.form['commentaire']
  date = datetime.datetime.now(datetime.UTC).strftime('%H:%M:%S %d/%m/%Y')
  signer = [user.strip() for user in signers.split(',')]
  insert_query = 'INSERT INTO public."signRequest" (filename, person, signers, object, comment, date, status, nbresign, cursign, signatures) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
  signatures = []
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(insert_query, (filename, user, signer, obj, comment, date, 0, len(signer), 0, signatures))
    conn.commit()
    for s in signer:
      chaine=s.split(' ')
      cursor.execute('SELECT * FROM "users" WHERE telephone = %s', (chaine[-1],))
      rows = cursor.fetchall()
      sendInvitEmail(to_address=rows[0][4], person=f"{" ".join(user.split(" ")[:-1])}", date=date)
  except Exception as e:
    cursor.close()
    conn.close()
    return jsonify({"success": False, "error": str(e)})
  cursor.close()
  conn.close()
  return jsonify({"success": True})

@app.route('/addExternalRequest', methods=['POST'])
def addExternalRequest():
  file = request.files['fichier']
  user = request.form['demandeur']
  filename = f"Demande-EXT-{"_".join(user.split(" ")[:-1])}_{uuid.uuid4()}.pdf"
  file.save(f"{BASE_FOLDER}{filename}")
  signers = request.form['signataires']
  obj = request.form['objet']
  comment = request.form['commentaire']
  date = datetime.datetime.now(datetime.UTC).strftime('%H:%M:%S %d/%m/%Y')
  signer = [user for user in signers.split(", ")]
  insert_query = 'INSERT INTO "extSignRequest" (filename, person, signers, object, comment, date, status, nbresign, cursign, signatures) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
  signatures = []
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(insert_query, (filename, user, signer, obj, comment, date, 0, len(signer), 0, signatures))
    conn.commit()
    for s in signer:
      name = f"{" ".join(user.split(" ")[:-1])}"
      url = f"{FRONT_URL}/{s.replace(" ", "_")}/{filename}"
      sendExternalInvitEmail(to_address=s.split(" ")[-1], person=name, date=date, url=url)
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
  dataExt = get_data_from_table("extSignRequest")
  dataset = list(data) + list(dataExt)
  def parse_date(date_str):
    return datetime.datetime.strptime(date_str, '%H:%M:%S %d/%m/%Y')
  sorted_data = sorted(dataset, key=lambda x: parse_date(x['date']), reverse=True)
  return jsonify({"success": True, "result": sorted_data})

@app.route('/deleteRequest', methods=['DELETE'])
def deleteRequest():
  id = request.args.get('id')
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM public."signRequest" WHERE id = %s', (id,))
    rows = cursor.fetchall()
    for row in rows:
      if row:
        os.remove(rf"{BASE_FOLDER}{row[1]}")
        cursor.execute('DELETE FROM public."signRequest" WHERE id = %s', (id,))
        conn.commit()
        cursor.close()
        conn.close()
        data = get_data_from_table("signRequest")
        return jsonify({"success": True, "result": data})
    cursor.close()
    conn.close()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM public."extSignRequest" WHERE id = %s', (id,))
    rows = cursor.fetchall()
    for row in rows:
      if row:
        os.remove(rf"{BASE_FOLDER}{row[1]}")
        cursor.execute('DELETE FROM public."extSignRequest" WHERE id = %s', (id,))
        conn.commit()
        cursor.close()
        conn.close()
        data = get_data_from_table("signRequest")
        return jsonify({"success": True, "result": data})
  except Exception as e:
    cursor.close()
    conn.close()
    return jsonify({"success": False, "error": str(e)})

@app.route('/refuseRequest', methods=['POST'])
def refuseRequest():
  id = request.args.get('id')
  conn = get_db_connection()
  cursor = conn.cursor()
  try:
    req = 'Update public."signRequest" set status = 2 WHERE id = %s'
    cursor.execute(req, (id,))
    conn.commit()
    cursor.execute('SELECT * FROM public."signRequest" WHERE id = %s', (id,))
    rows = cursor.fetchall()
    for row in rows:
      if row:
        person = row[2]
        cursor.execute('SELECT * FROM users WHERE telephone = %s', (person.split(" ")[-1],))
        rows1 = cursor.fetchall()
        for row1 in rows1:
          if row1:
            sendRefuseEmail(to_address=row[4], date=datetime.datetime.now(datetime.UTC).strftime('%H:%M:%S %d/%m/%Y'))
    cursor.close()
    conn.close()
  except Exception as e:
    cursor.close()
    conn.close()
    return jsonify({"success": False, "error": str(e)})
  data = get_data_from_table("signRequest")
  return jsonify({"success": True, "result": data})

@app.route('/refuseExtRequest', methods=['POST'])
def refuseExtRequest():
  filename = request.args.get('filename')
  conn = get_db_connection()
  cursor = conn.cursor()
  try:
    req = 'Update public."extSignRequest" set status = 2 WHERE filename = %s'
    cursor.execute(req, (filename,))
    conn.commit()
    cursor.execute('SELECT * FROM public."extSignRequest" WHERE filename = %s', (filename,))
    rows = cursor.fetchall()
    for row in rows:
      if row:
        person = row[2]
        cursor.execute('SELECT * FROM users WHERE telephone = %s', (person.split(" ")[-1],))
        rows1 = cursor.fetchall()
        for row1 in rows1:
          if row1:
            sendRefuseEmail(to_address=row[4], date=datetime.datetime.now(datetime.UTC).strftime('%H:%M:%S %d/%m/%Y'))
    cursor.close()
    conn.close()
  except Exception as e:
    cursor.close()
    conn.close()
    return jsonify({"success": False, "error": str(e)})
  return jsonify({"success": True})

@app.route('/getPDF', methods=['POST'])
def getPDF():
  id = request.args.get('id')
  try:
    data = get_data_from_table("signRequest")
    dataExt = get_data_from_table("extSignRequest")
    dataset = list(data) + list(dataExt)
    for row in dataset:
      if row['id'] == int(id):
        filename = rf"{BASE_FOLDER}{row['filename']}"
        with open(filename, "rb") as file:
          data = base64.b64encode(file.read()).decode('utf-8')
    return jsonify({"success": True, "result": data})
  except Exception as e:
    return jsonify({"success": False, "error": str(e)})

@app.route('/getExtPDF', methods=['POST'])
def getExtPDF():
  filename = request.args.get('filename')
  try:
    file = rf"{BASE_FOLDER}{filename}"
    with open(file, "rb") as file:
      data = base64.b64encode(file.read()).decode('utf-8')
    return jsonify({"success": True, "result": data})
  except Exception as e:
    return jsonify({"success": False, "error": str(e)})

@app.route('/changePassword', methods=['POST'])
def changePassword():
  member = request.form['datas']
  member_json = json.loads(member)
  telephone = request.form['tel']
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE telephone = %s AND password = %s', (telephone, member_json["prepassword"]))
    rows = cursor.fetchall()
    for row in rows:
      if row:
        id = row[0]
        cursor.execute('UPDATE users SET password = %s WHERE id = %s', (member_json["password"], id))
        conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})
  except Exception as e:
    cursor.close()
    conn.close()
    return jsonify({"success": False, "error": str(e)})


"""
Vérification des signatures
Minimum 10 images pour faceScan
"""

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port='8080')
