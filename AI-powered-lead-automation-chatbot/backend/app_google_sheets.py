from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import requests
from dotenv import load_dotenv
import json
import re
import phonenumbers
from models import score_lead

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("AI Chatbot Leads").sheet1

load_dotenv()
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")

sessions = {}

translations = {
    "en": {
        "questions": [
            "What's your name?",
            "Which industry are you in?",
            "What is your estimated budget? (Eg.10000)",
            "Which service are you looking for?",
            "What's your email address?",
            "Which country are you from?",
            "What’s your phone number?(Eg.+91 8925649937)"
        ],
        "thank_you": "Thanks {name}! 🎉 We'll contact you soon at {email}.",
        "service_options": ["Website", "Mobile App", "SEO", "Branding", "Marketing"]
    },
    # ... other languages like "hi", "ta" same as before, extended with country/phone ...
    "hi": {
        "questions": [
            "आपका नाम क्या है?",
            "आप किस उद्योग में हैं?",
            "आपका अनुमानित बजट क्या है?",
            "आप कौन सी सेवा चाहते हैं?",
            "आपका ईमेल पता क्या है?",
            "आप किस देश से हैं?",
            "आपका फोन नंबर क्या है?(Eg.+91 8925649937)"
        ],
        "thank_you": "धन्यवाद {name}! हम आपसे जल्द ही संपर्क करेंगे {email} पर।",
        "service_options": ["वेबसाइट", "मोबाइल ऐप", "एसईओ", "ब्रांडिंग", "मार्केटिंग"]
    },
    "ta": {
        "questions": [
            "உங்கள் பெயர் என்ன?",
            "நீங்கள் எந்த தொழிலில் இருக்கிறீர்கள்?",
            "உங்கள் மதிப்பிடப்பட்ட பட்ஜெட் என்ன?",
            "எந்த சேவையை நீங்கள் தேடுகிறீர்கள்?",
            "உங்கள் மின்னஞ்சல் முகவரி என்ன?",
            "நீங்கள் எந்த நாட்டைச் சேர்ந்தவர்?",
            "உங்க போன் நம்பர் என்ன?(Eg.+91 8925649937)"
        ],
        "thank_you": "நன்றி {name}! நாங்கள் விரைவில் {email} முகவரியில் தொடர்புகொள்வோம்.",
        "service_options": ["வலைத்தளம்", "மொபைல் ஆப்", "எஸ்இஓ", "பிராண்டிங்", "மார்க்கெட்டிங்"]
    }
}

def send_email_notification(data):
    sender_email = os.getenv("SENDER_EMAIL")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    subject = "🚀 New Lead Captured!"
    body = f"""
    <h3>New Lead Details</h3>
    <ul>
        <li><b>Name:</b> {data['name']}</li>
        <li><b>Industry:</b> {data['industry']}</li>
        <li><b>Budget:</b> {data['budget']}</li>
        <li><b>Service:</b> {data['service']}</li>
        <li><b>Email:</b> {data['email']}</li>
        <li><b>Country:</b> {data['country']}</li>
        <li><b>Phone:</b> {data['phone']}</li>
    </ul>
    """
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("📩 Admin email sent successfully!")
    except Exception as e:
        print("❌ Failed to send admin email:", e)

def send_email_to_lead(data):
    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    lead_email = data['email']
    subject = "🎉 Thanks for contacting us!"
    body = f"""
    <p>Hi {data['name']},</p>
    <p>Thanks for reaching out to us! We're excited to help you with your <b>{data['service']}</b> needs in the <b>{data['industry']}</b> industry.</p>
    <p>Our team will get in touch with you shortly. If you have any questions, feel free to reply to this email.</p>
    <br>
    <p>Best Regards,<br><b>AI Chatbot Team</b></p>
    """
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = lead_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, lead_email, msg.as_string())
        server.quit()
        print("📧 Email sent to lead successfully!")
    except Exception as e:
        print("❌ Failed to send email to lead:", e)

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_phone(phone, country):
    try:
        parsed = phonenumbers.parse(phone, country.upper())
        return phonenumbers.is_valid_number(parsed)
    except:
        return False

@app.route('/chat', methods=['POST'])
def chat():
    req = request.json
    user_input = req['message']
    session_id = req.get('session_id', 'default_user')
    lang = req.get('lang', 'en')

    if session_id not in sessions:
        sessions[session_id] = {'step': 0, 'data': {}, 'lang': lang, 'retry': False}

    session = sessions[session_id]
    session['lang'] = lang
    questions = translations[lang]["questions"]
    keys = ["name", "industry", "budget", "service", "email", "country", "phone"]
    step = session['step']
    data = session['data']

    if step > 0 and step <= len(keys):
        key = keys[step - 1]

        if key == "email" and not is_valid_email(user_input):
            session['retry'] = True
            return jsonify({'response': "❌ That doesn't look like a valid email. Please try again.", 'options': []})
        elif key == "phone":
            country = data.get("country", "US")
            if not is_valid_phone(user_input, country):
                session['retry'] = True
                return jsonify({'response': "📞 Please enter a valid phone number (with country code).", 'options': []})
        elif key == "budget":
            budget_input = user_input.replace(",", "").replace("$", "").strip()
            if not budget_input.isdigit():
                session['retry'] = True
                return jsonify({'response': "❌ Please enter your estimated budget as a number (e.g., 10000):", 'options': []})
            user_input = budget_input

        session['data'][key] = user_input
        session['retry'] = False

    response = ""
    options = []

    if step < len(questions):
        if session['retry']:
            response = questions[step - 1]
        else:
            if keys[step] == "service":
                name = data.get("name", "")
                industry = data.get("industry", "")
                response = f"Thanks {name}, {industry} is a booming industry! Let's get your {user_input} needs sorted.\n" + questions[step]
                options = translations[lang]["service_options"]
            else:
                response = questions[step]
            session['step'] += 0 if session['retry'] else 1
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['lead_score'] = score_lead(data)

        try:
            budget_num = int(data.get("budget", "0"))
            if budget_num < 5000:
                response += "\nDon't worry, we’ve got great solutions for any budget!"
            elif budget_num < 15000:
                response += "\nThat's a smart budget! We’ll make sure you get the best value."
            else:
                response += "\nAwesome! You’re looking for premium solutions—we’ve got you covered."
        except:
            pass

        response += "\n" + translations[lang]["thank_you"].format(name=data['name'], email=data['email'])

        send_email_notification(data)
        send_email_to_lead(data)

        sheet.append_row([
            data.get('name', ''),
            data.get('industry', ''),
            data.get('budget', ''),
            data.get('service', ''),
            data.get('email', ''),
            data.get('country', ''),
            data.get('phone', ''),
            data['lead_score'],
            timestamp
        ])

        payload = {
            "properties": {
                "email": data['email'],
                "firstname": data['name'],
                "industry": data['industry'],
                "budget": data['budget'],
                "service": data['service'],
                "phone": data['phone'],
                "country": data['country'],
                "lead_score": str(data['lead_score']),
                "bot_channel": "Website Chatbot"
            }
        }

        headers = {
            "Authorization": f"Bearer {HUBSPOT_API_KEY}",
            "Content-Type": "application/json"
        }

        res = requests.post("https://api.hubapi.com/crm/v3/objects/contacts", json=payload, headers=headers)

        if res.status_code == 409:
            contact_id = json.loads(res.text).get('message').split(":")[-1].strip()
            update_url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
            update_res = requests.patch(update_url, json={"properties": payload["properties"]}, headers=headers)
            print("🔁 HubSpot Update Response:", update_res.status_code, update_res.text)
        else:
            print("📅 HubSpot Response:", res.status_code, res.text)

        sessions.pop(session_id)

    return jsonify({'response': response, 'options': options})

@app.route('/leads', methods=['GET'])
def get_leads():
    records = sheet.get_all_records()
    return jsonify(records)

if __name__ == '__main__':
    app.run(debug=True)
