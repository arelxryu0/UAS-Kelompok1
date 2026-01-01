from flask import Flask, render_template, request, redirect, url_for
import cv2
import numpy as np
import os
import time

app = Flask(__name__)

# Konfigurasi Path - Pastikan folder ini ada
UPLOAD_FOLDER = os.path.join('static', 'uploads')
RESULT_FOLDER = os.path.join('static', 'results')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Nama file statis agar mudah dikelola
ORIGINAL_FILENAME = "last_original.png"
RESULT_FILENAME = "last_result.png"

def process_image(filepath, method):
    # Baca gambar (Grayscale untuk morfologi)
    img = cv2.imread(filepath, 0)
    if img is None:
        return None
    
    # Kernel standar 5x5
    kernel = np.ones((5, 5), np.uint8)
    
    if method == "dilasi":
        result = cv2.dilate(img, kernel, iterations=1)
    elif method == "erosi":
        result = cv2.erode(img, kernel, iterations=1)
    elif method == "opening":
        result = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    elif method == "closing":
        result = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    else:
        result = img

    output_path = os.path.join(RESULT_FOLDER, RESULT_FILENAME)
    cv2.imwrite(output_path, result)
    return True

@app.route("/", methods=["GET", "POST"])
def index():
    method = request.form.get("method", "dilasi")
    ts = int(time.time()) # Timestamp untuk cegah cache browser
    
    # Path fisik file
    path_to_original = os.path.join(UPLOAD_FOLDER, ORIGINAL_FILENAME)
    
    # Variabel untuk dikirim ke HTML
    original_url = None
    result_url = None

    # Cek jika file sudah ada di server (agar tetap muncul saat ganti metode)
    if os.path.exists(path_to_original):
        original_url = url_for('static', filename=f'uploads/{ORIGINAL_FILENAME}', v=ts)

    if request.method == "POST":
        file = request.files.get("image")
        
        # JIKA ADA UPLOAD FILE BARU
        if file and file.filename != "":
            ext = os.path.splitext(file.filename)[1].lower()
            
            # Mendukung format TIF dengan konversi otomatis ke PNG
            if ext in ['.tif', '.tiff']:
                temp_path = os.path.join(UPLOAD_FOLDER, "temp" + ext)
                file.save(temp_path)
                img_data = cv2.imread(temp_path)
                if img_data is not None:
                    cv2.imwrite(path_to_original, img_data)
                if os.path.exists(temp_path): os.remove(temp_path)
            else:
                # Format JPG/PNG langsung simpan
                file.save(path_to_original)
            
            # Update URL setelah simpan file baru
            original_url = url_for('static', filename=f'uploads/{ORIGINAL_FILENAME}', v=ts)

        # PROSES GAMBAR JIKA FILE TERSEDIA
        if os.path.exists(path_to_original):
            if process_image(path_to_original, method):
                result_url = url_for('static', filename=f'results/{RESULT_FILENAME}', v=ts)

        return render_template("index.html", 
                               original=original_url, 
                               result=result_url, 
                               method=method)

    return render_template("index.html", 
                           original=original_url, 
                           result=None, 
                           method=method)

@app.route("/reset")
def reset():
    # Hapus semua file di folder upload dan result
    for folder in [UPLOAD_FOLDER, RESULT_FOLDER]:
        for f in os.listdir(folder):
            file_path = os.path.join(folder, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)