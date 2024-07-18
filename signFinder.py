import easyocr, fitz, cv2, os
from certReader import *

reader = easyocr.Reader(['fr'])

def sign_definition(pix):
  tab = []
  gray = cv2.cvtColor(pix, cv2.COLOR_BGR2GRAY)
  _, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
  rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 30))
  dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
  contours, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
  for i, cnt in enumerate(contours):
    x, y, w, h = cv2.boundingRect(cnt)
    contour_img = pix[y:y+h, x:x+w]
    tab.append(contour_img)
  return tab

def lireSignature(pdf_path):
  doc = fitz.open(pdf_path)
  page = doc.load_page(0)
  pix = page.get_pixmap(dpi=270, clip=page.rect)
  doc.close()
  pix.save("pix_image.png")
  pix = cv2.imread("pix_image.png")
  os.remove("pix_image.png")
  tab = sign_definition(pix)
  return tab

def lireCaractere(img):
  cv2.imwrite("image_path.png", cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
  results = reader.readtext("image_path.png")
  os.remove("image_path.png")
  text = ''
  for result in results:
    text += ' ' + result[1]
  return text
