import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# โหลดค่าตัวแปรจากไฟล์ .env
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # จำกัดขนาดไฟล์อัปโหลดสูงสุด 10 MB

API_KEY = os.getenv("AIFORTHAI_API_KEY") 

# หน้าแรกสุดสำหรับแสดงหน้ารอโหลด
@app.route('/')
def index():
    return render_template('screen.html')

# หน้าเมนูหลัก
@app.route('/menu.html')
def menu():
    return render_template('menu.html')

# หน้า 1: แปลไทย -> จีน
@app.route('/th-to-cn.html')
def page_th_to_cn():
    return render_template('th-to-cn.html')

# หน้า 2: แปลจีน -> ไทย
@app.route('/cn-to-th.html')
def page_cn_to_th():
    return render_template('cn-to-th.html')

# หน้า 3: ตรวจจับบุคคลในภาพ
@app.route('/detect.html')
def page_detect():
    return render_template('detect.html')

# API Route 1: ระบบแปลภาษาจีน -> ไทย (Xiaofan)
@app.route('/api/translate', methods=['POST'])
def translate_zh_th():
    data = request.get_json()
    text = data.get('text', '').strip()

    if not text:
        return jsonify({'error': 'กรุณากรอกข้อความภาษาจีนที่ต้องการแปล'}), 400
    
    if len(text) > 5000:
        return jsonify({'error': 'ข้อความยาวเกินกำหนด (สูงสุด 5,000 ตัวอักษร)'}), 400

    url = "https://api.aiforthai.in.th/xiaofan-zh-th"
    payload = json.dumps({
        "input": text,
        "src": "zh",
        "trg": "th"
    })
    headers = {
        'apikey': API_KEY,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'เชื่อมต่อ API แปลภาษาไม่สำเร็จ: {str(e)}'}), 500

# ✅ API Route ใหม่ (เพิ่มใน Phase 1): ระบบแปลภาษาไทย -> จีน (Xiaofan)
@app.route('/api/translate-th-zh', methods=['POST'])
def translate_th_zh():
    data = request.get_json()
    text = data.get('text', '').strip()

    if not text:
        return jsonify({'error': 'กรุณากรอกข้อความภาษาไทยที่ต้องการแปล'}), 400
    
    # ตรวจสอบความยาวไม่เกิน 5,000 ตัวอักษรตามข้อกำหนด API
    if len(text) > 5000:
        return jsonify({'error': 'ข้อความยาวเกินกำหนด (สูงสุด 5,000 ตัวอักษร)'}), 400

    url = "https://api.aiforthai.in.th/xiaofan-zh-th"
    payload = json.dumps({
        "input": text,
        "src": "th",
        "trg": "zh"
    })
    headers = {
        'apikey': API_KEY,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'เชื่อมต่อ API แปลภาษาไทย-จีนไม่สำเร็จ: {str(e)}'}), 500

# API Route 2: ระบบระบุตำแหน่งบุคคลในภาพ (Human Detect)
@app.route('/api/human-detect', methods=['POST'])
def human_detect():
    if 'image' not in request.files:
        return jsonify({'error': 'ไม่พบไฟล์รูปภาพที่อัปโหลด'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'ยังไม่ได้เลือกไฟล์รูปภาพ'}), 400

    filename_lower = file.filename.lower()
    if not (filename_lower.endswith('.jpg') or filename_lower.endswith('.jpeg')):
        return jsonify({'error': 'รองรับเฉพาะไฟล์รูปภาพนามสกุล .jpg หรือ .jpeg เท่านั้น'}), 400

    url = "https://api.aiforthai.in.th/person/human_detect/"
    headers = {
        'Apikey': API_KEY
    }
    data = {
        'json_export': 'true',
        'img_export': 'true'
    }
    files = {
        'src_img': (file.filename, file.stream, file.content_type)
    }

    try:
        response = requests.post(url, files=files, headers=headers, data=data, timeout=20)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'เชื่อมต่อ API ตรวจจับบุคคลไม่สำเร็จ: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)