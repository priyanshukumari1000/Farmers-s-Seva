import cv2
import pytesseract
import re
import pypdf
import numpy as np

def ocr_core(img):
    text=pytesseract.image_to_string(img)
    return text

img=cv2.imread('tess.png')

def get_grayscale(image):
    return cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

def remove_noise(image):
    return cv2.medianBlur(image, 5)

# Thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# img = get_grayscale(img)
# img = thresholding(img)
# img = remove_noise(img)

# print(ocr_core(img))

def extract_aadhaar_info(image_path):
    # Load image
    image = cv2.imread(image_path)

    # Resize for better OCR
    scale_percent = 150  # percent of original size
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    image = cv2.resize(image, dim, interpolation=cv2.INTER_CUBIC)

    # Denoise
    image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Run OCR
    raw_text = pytesseract.image_to_string(thresh, lang='eng')

    print("\n===== Extracted Raw Text =====")
    print(raw_text)
    print("================================")

    # Improved name extraction: look for the first plausible name line
    ignore_keywords = ['aadhaar', 'no', 'dob', 'year', 'gender', 'govt', 'government', 'male', 'female', 'address']
    lines = raw_text.split('\n')
    candidate_names = []
    dob_line_idx = None

    # Find DOB line index
    for idx, line in enumerate(lines):
        if re.search(r'DOB|Date of Birth', line, re.IGNORECASE):
            dob_line_idx = idx
            break

    # Collect candidate names
    for idx, line in enumerate(lines):
        clean_line = line.strip()
        if not clean_line:
            continue
        if any(kw in clean_line.lower() for kw in ignore_keywords):
            continue
        if clean_line.isupper() or len(clean_line) < 5:
            continue
        match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', clean_line)
        if match:
            candidate_names.append((idx, match.group(1)))

    # Pick the candidate closest above the DOB line
    name = 'Not found'
    if dob_line_idx is not None and candidate_names:
        # Find the candidate with the highest index less than dob_line_idx
        best = None
        for idx, cand in candidate_names:
            if idx < dob_line_idx:
                best = cand
        if best:
            name = best
        else:
            name = candidate_names[0][1]
    elif candidate_names:
        name = candidate_names[0][1]

    # DOB or Year of Birth
    dob_match = re.search(r'\b(?:DOB|Date of Birth)[^\d]*(\d{2}/\d{2}/\d{4})', raw_text)
    yob_match = re.search(r'\b(?:Year of Birth)[^\d]*(\d{4})', raw_text)

    # Gender (Hindi + English)
    gender_match = re.search(r'\b(MALE|FEMALE|पुरुष|महिला)\b', raw_text, re.IGNORECASE)

    # Extract Aadhaar number
    aadhaar_match = re.search(r'\b\d{4}\s*\d{4}\s*(\d{4})\b', raw_text)
    aadhaar_last_4 = aadhaar_match.group(1) if aadhaar_match else 'Not found'

    return {
        'name': name.strip() if name else 'Not found',
        'dob': dob_match.group(1) if dob_match else (yob_match.group(1) if yob_match else 'Not found'),
        'gender': gender_match.group(1).upper() if gender_match else 'Not found',
        'aadhaar_last_4': aadhaar_last_4
    }

def extract_aadhaar_last_4_from_text(text):
    # Look for patterns like "XXXX XXXX 9008" or "Aadhaar Number : XXXX XXXX 9008"
    match = re.search(r'(?:aadhaar number\s*:)?\s*xxxx\s*xxxx\s*(\d{4})', text.lower())
    return match.group(1) if match else 'Not found'

def extract_consumer_name_from_pdf(pdf_path, aadhaar_name, aadhaar_last_4):
    consumer_name = 'Not found'
    aadhaar_match = False
    try:
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
            
            print("\n===== Raw PDF Text =====")
            print(text)
            print("========================")
            
            # Normalize spaces in both text and name
            normalized_text = ' '.join(text.lower().split())
            normalized_name = ' '.join(aadhaar_name.lower().split())
            
            # Debug prints
            print("\n===== Debug Info =====")
            print("Looking for name:", aadhaar_name)
            print("Looking for Aadhaar last 4:", aadhaar_last_4)
            print("Normalized name:", normalized_name)
            print("Normalized text:", normalized_text)
            print("Is name in text?", normalized_name in normalized_text)
            print("Is Aadhaar number in text?", aadhaar_last_4 in normalized_text)
            print("========================")
            
            # Check if normalized Aadhaar name is present in normalized text
            if normalized_name in normalized_text:
                consumer_name = aadhaar_name
                print(f"Found matching name '{aadhaar_name}' in the document")
            else:
                print(f"Could not find '{aadhaar_name}' in the document")
            
            # Check if Aadhaar last 4 digits are present in text
            if aadhaar_last_4 in normalized_text:
                aadhaar_match = True
                print(f"Found matching Aadhaar number '{aadhaar_last_4}' in the document")
            else:
                print(f"Could not find Aadhaar number '{aadhaar_last_4}' in the document")
                
    except Exception as e:
        print(f"Error extracting consumer name from PDF: {e}")
    return consumer_name, aadhaar_match

# === Example usage ===
if __name__ == "__main__":
    # Extract name from Aadhaar card (riri_old.png)
    aadhaar_image_path = 'riri.png'
    aadhaar_result = extract_aadhaar_info(aadhaar_image_path)
    aadhaar_name = aadhaar_result['name']
    aadhaar_last_4 = aadhaar_result['aadhaar_last_4']
    print("\n===== Extracted Aadhaar Information =====")
    print("Aadhaar Name:", aadhaar_name)
    print("Date of Birth:", aadhaar_result['dob'])
    print("Gender:", aadhaar_result['gender'])
    print("Aadhaar Last 4 Digits:", aadhaar_last_4)

    # Extract consumer/owner name from kusum_bill.pdf
    kusum_bill_pdf_path = 'kusum_bill.pdf'
    kusum_bill_name, kusum_bill_aadhaar_match = extract_consumer_name_from_pdf(kusum_bill_pdf_path, aadhaar_name, aadhaar_last_4)
    print("\n===== Extracted Consumer Name from kusum_bill.pdf =====")
    print("Consumer Name:", kusum_bill_name)
    print("Aadhaar Number Match:", kusum_bill_aadhaar_match)

    # Extract consumer/owner name from kusum_land.pdf
    kusum_land_pdf_path = 'kusum_land.pdf'
    kusum_land_name, kusum_land_aadhaar_match = extract_consumer_name_from_pdf(kusum_land_pdf_path, aadhaar_name, aadhaar_last_4)
    print("\n===== Extracted Consumer Name from kusum_land.pdf =====")
    print("Consumer Name:", kusum_land_name)
    print("Aadhaar Number Match:", kusum_land_aadhaar_match)

    # Compare names
    print("\n===== Name Comparison =====")
    print("Aadhaar Name:", aadhaar_name)
    print("Kusum Bill Name:", kusum_bill_name)
    print("Kusum Land Name:", kusum_land_name)
    if aadhaar_name == kusum_bill_name and aadhaar_name == kusum_land_name:
        print("Names match across all documents.")
    else:
        print("Names do not match across all documents.")

    # Compare Aadhaar numbers
    print("\n===== Aadhaar Number Comparison =====")
    print("Aadhaar Card Last 4:", aadhaar_last_4)
    print("Kusum Bill Match:", kusum_bill_aadhaar_match)
    print("Kusum Land Match:", kusum_land_aadhaar_match)
    if kusum_bill_aadhaar_match and kusum_land_aadhaar_match:
        print("Aadhaar numbers match across all documents.")
    else:
        print("Aadhaar numbers do not match across all documents.")


