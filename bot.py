import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq
import json

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

with open('data.json', 'r') as f:
    MENU = f.read()

@app.route("/bot", methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    prompt = f"""Eres un asistente de reservas profesional.
    Menú disponible: {MENU}.
    Reglas:
    1. Si piden reserva, verifica el horario. Si es 20:00 y no hay cupo, sugiere 19:30 o 20:30.
    2. Suma los platos elegidos y da el total.
    3. Pide el pago por transferencia o adelanto.
    4. Sé amable, breve y natural."""

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": incoming_msg}],
            model="llama3-8b-8192",
        )
        msg.body(chat_completion.choices[0].message.content)
    except Exception as e:
        msg.body("Disculpa, estoy ajustando unos detalles. Intenta en un momento.")

    return str(resp)

if __name__ == "__main__":
    app.run()