from sklearn.preprocessing import LabelEncoder
from keras_facenet import FaceNet
from sklearn.svm import SVC
import numpy as np
import base64, cv2

model = SVC(kernel='linear', probability=True)
encoder = LabelEncoder()
embedder = FaceNet()

class FACELOADING:
  def __init__(self, data):
    self.data = data
    self.X = []
    self.Y = []

  def base64ToImg(self, base64_string):
    image_data = base64.b64decode(base64_string)
    np_arr = np.frombuffer(image_data, np.uint8)
    return cv2.cvtColor(cv2.imdecode(np_arr, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB) 

  def load_classes(self):
    for element in self.data:
      self.X.append(self.base64ToImg(element["picture"]))
      self.Y.append(element["person"])
    return np.asarray(self.X), np.asarray(self.Y)

def get_trainset(conn):
  cursor = conn.cursor()
  query = 'SELECT * FROM trainset;'
  cursor.execute(query)
  rows = cursor.fetchall()
  cursor.close()
  conn.close()
  data = []
  for row in rows:
    data.append({
      "id": row[0],
      "person": row[1],
      "picture": row[2],
    })
  return data

def get_embedding(face_img):
  face_img = face_img.astype('float32') # 3D(160x160x3)
  face_img = np.expand_dims(face_img, axis=0)
  # 4D (Nonex160x160x3)
  yhat = embedder.embeddings(face_img)
  return yhat[0] # 512D image (1x1x512)

def get_trained_model(data):
  try:
    faceloading = FACELOADING(data)
    X, Y = faceloading.load_classes()

    EMBEDDED_X = []
    for img in X:
      EMBEDDED_X.append(get_embedding(img))
    EMBEDDED_X = np.asarray(EMBEDDED_X)
    encoder.fit(Y)
    Y_ENCODDED = encoder.transform(Y)
    model.fit(EMBEDDED_X, Y_ENCODDED)
    return model, encoder
  except Exception as e:
    print(e)
    return None, None

def predict_face(face, model, encoder):
  if not face.all() == None:
    face_embed = get_embedding(face)
    test_im = [face_embed]
    ypreds = model.predict(test_im)
    res = model.predict_proba(test_im)[0]
    prob = res[0] - res[1]
    return encoder.inverse_transform(ypreds)[0], prob
  return "No face detected !"