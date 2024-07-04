import base64, fitz, cv2, os, re, psycopg2, secrets
from mtcnn.mtcnn import MTCNN
from signFinder import *

detector = MTCNN()

def clean():
    for fichier in os.listdir(os.curdir):
        if fichier.endswith(".pdf") or fichier.endswith(".png") or fichier.endswith(".jpg"):
            os.remove(fichier)

def get_db_connection():
    """conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="root",
        port=5432
    )"""
    conn = psycopg2.connect('postgres://avnadmin:AVNS_jJdwHlhkwoHcODhE83V@pg-367c7a2d-amsata2009-bad2.f.aivencloud.com:18480/defaultdb?sslmode=require')
    return conn

def normalize(text):
    return re.sub(r'\W+', ' ', text).lower().strip()

def correlation(json, tab):
    for company in tab:
        issuer_o_normalized = normalize(json["IssuerO"])
        company_name_normalized = normalize(company["nomEntreprise"])
        name_match = issuer_o_normalized == company_name_normalized
        country_match = json["IssuerC"].lower() == company["codePaysRegion"].lower()
        if name_match and country_match:
            return company
    return None

def getNameFromCode(code):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        req = 'SELECT * FROM public."codePaysRegion" WHERE "Code" = %s;'
        cursor.execute(req, (code,))
    except Exception as e:
        cursor.close()
        conn.close()
        return None
    name = cursor.fetchall()
    cursor.close()
    conn.close()
    return name[0][1]

def generate_token():
    return secrets.token_hex(32)

def get_data_from_table(table):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'SELECT * FROM {};'.format(table)
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    data = []
    if table == "ownTrustList":
        for row in rows:
            data.append({
                "id": row[0],
                "codePaysRegion": row[1],
                "emplacementSiegeSocial": row[2],
                "nomEntreprise": row[3],
                "textFind": row[4]
            })
        data.reverse()
    elif table == "users":
        for row in rows:
            data.append({
                "id": row[0],
                "nom": row[1],
                "prenom": row[2],
                "date": row[3],
                "email": row[4],
                "password": row[5],
                "telephone": row[6],
                "organisation": row[7],
                "poste": row[8],
                "role": row[9],
            })
    return data

def find_signature(path):
    signs = {}
    signs = lireSignature_1(path)
    if signs:
        return signs
    data = get_data_from_table("ownTrustList")
    res = autorityFinder(path)
    search = None
    for cert in data:
        if res["IssuerO"] == cert["nomEntreprise"]:
            search = cert["textFind"]
            break
    if search != None:
        lireSignature(path)
        for fichier in [f for f in os.listdir(os.curdir) if f.endswith("_" + image_path)]:
            char = lireCaractere(fichier)
            if search.lower() in char.lower():
                with open(fichier, 'rb') as f:
                    data = f.read()
                data = base64.b64encode(data).decode('utf-8')
                signs[char] = data
    return signs

def sign_definition_1(image_path, widgets):
    original_image = cv2.imread(image_path)
    signs = {}
    if original_image is None:
        raise ValueError(f"Failed to load image from {image_path}")
    height, width, _ = original_image.shape
    for i, widget in enumerate(widgets):
        x0, y0, x1, y1 = widget
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(width, x1), min(height, y1)
        if x1 <= x0 or y1 <= y0:
            continue
        cropped_image = original_image[int(y0):int(y1), int(x0):int(x1)]
        if cropped_image.size == 0:
            continue
        cv2.imwrite(f"{i}_{image_path}", cropped_image)
    for fichier in [f for f in os.listdir(os.curdir) if f.endswith("_" + image_path)]:
        with open(fichier, 'rb') as f:
            encoded_data = base64.b64encode(f.read()).decode('utf-8')
        character = lireCaractere(fichier)
        signs[character] = encoded_data
    return signs

def lireSignature_1(pdf_path, image_path="signature.png"):
    widgets = []
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    rect = page.rect
    pix = page.get_pixmap(dpi=270, clip=rect)
    pix.save(image_path)
    page_width, page_height = rect.width, rect.height
    image_height, image_width = pix.height, pix.width

    for widget in page.widgets():
        if widget.field_type_string == "Signature":
            x0, y0, x1, y1 = widget.rect
            x0 = int(x0 / page_width * image_width)
            y0 = int(y0 / page_height * image_height)
            x1 = int(x1 / page_width * image_width)
            y1 = int(y1 / page_height * image_height)
            widgets.append((x0, y0, x1, y1))
    doc.close()
    signs = sign_definition_1(image_path, widgets)
    return signs

def blob_to_mp4(temp_path):
    cap = cv2.VideoCapture(temp_path)
    if not cap.isOpened():
        return None
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    os.remove(temp_path)
    frames = frames[0: -1: len(frames) // 15]
    return frames

def faceDetector(frame):
    faces = detector.detect_faces(frame)
    if faces:
        x, y, w, h = faces[0]['box']
        frame = frame[y:y+h, x:x+w]
        frame = cv2.resize(frame, (160, 160))
        return frame
    return None

def faceScan(data):
    frames = blob_to_mp4(data)
    res = []
    for _, frame in enumerate(frames):
        frame = faceDetector(frame)
        try:
            _, encoded_frame = cv2.imencode('.jpg', frame)
            encoded_frame = base64.b64encode(encoded_frame).decode('utf-8')
            res.append(encoded_frame)
        except:
            pass
    return res

def frames2db(user, res, cursor):
    req = "INSERT INTO trainset (person, picture) VALUES (%s, %s)"
    for pic in res:
        cursor.execute(req, (user, pic))