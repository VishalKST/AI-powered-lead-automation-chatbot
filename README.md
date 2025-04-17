# AI-Powered Chatbot for Lead Automation
This project is an AI-powered lead automation chatbot designed to streamline and enhance the process of lead capture, qualification, and customer relationship management. Built using Python and Flask, the chatbot engages website visitors in real-time, collects essential lead details, and seamlessly integrates with HubSpot CRM for automated lead.

## 🌟 Features

- Multilingual Support (English, Hindi, Tamil)
- Collects name, industry, budget, service, email, country, and phone number
- Validates email and phone number formats
- Sends leads to Google Sheets and HubSpot CRM
- Email notification to admin and thank-you email to lead
- Lead scoring via `models.py`

## 🔧 Tech Stack:

- Backend: Python, Flask
- Frontend: HTML, CSS (chatbot UI)
- Database: Google Sheets (optional for logging)
- CRM: HubSpot API
- Analytics: Power BI / Google Data Studio
- Hosting: Localhost or cloud deployment



# **To Run the code**

_[Open and read the "Read Me.txt" in the folder for more details.]_

pip install -r requirements.txt

Create a Google Cloud Service Account

Create .env File [Can you the "generate_env.py" to do so]

Run python app.py in CMD

Then open index.html from the frontend folder

After that in HubSpot the lead details are visible


# Output
- ChatBot Interface
![Screenshot 2025-04-18 011426](https://github.com/user-attachments/assets/7c50411a-40ad-4584-8505-ffa08970533e)
- Google sheet
![Screenshot 2025-04-18 011239](https://github.com/user-attachments/assets/34288173-7997-4c9a-bf70-11a05496c978)
- HubSpot (CRM Website)
![Screenshot 2025-04-18 011826](https://github.com/user-attachments/assets/4e5a2e4f-0f8f-46b4-9223-845137b96eee)
