import easyocr, fitz, cv2, os
from certReader import *

image_path = "signature.png"
reader = easyocr.Reader(['fr'])

def sign_definition(image_path):
  img = cv2.imread(image_path)
  os.remove(image_path)
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  _, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
  rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 30))
  dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
  contours, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
  for i, cnt in enumerate(contours):
    x, y, w, h = cv2.boundingRect(cnt)
    contour_img = img[y:y+h, x:x+w]
    cv2.imwrite(f"{i}_{image_path}", contour_img)

def lireSignature(pdf_path, image_path=image_path):
  doc = fitz.open(pdf_path)
  page = doc.load_page(0)
  pix = page.get_pixmap(dpi=270, clip=page.rect)
  pix.save(image_path)
  sign_definition(image_path)
  doc.close()

def lireCaractere(image_path):
  results = reader.readtext(image_path)
  text = ''
  for result in results:
    text += ' ' + result[1]
  return text

import easyocr, fitz, cv2, os
from certReader import *

image_path = "signature.png"
reader = easyocr.Reader(['fr'])

def sign_definition(image_path):
  img = cv2.imread(image_path)
  os.remove(image_path)
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  _, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
  rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 30))
  dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
  contours, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
  for i, cnt in enumerate(contours):
    x, y, w, h = cv2.boundingRect(cnt)
    contour_img = img[y:y+h, x:x+w]
    cv2.imwrite(f"{i}_{image_path}", contour_img)

def lireSignature(pdf_path, image_path=image_path):
  doc = fitz.open(pdf_path)
  page = doc.load_page(0)
  pix = page.get_pixmap(dpi=270, clip=page.rect)
  pix.save(image_path)
  sign_definition(image_path)
  doc.close()

def lireCaractere(image_path):
  results = reader.readtext(image_path)
  text = ''
  for result in results:
    text += ' ' + result[1]
  return text
