import os
import json
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq

app = Flask(__name__)

# Configuración de la API Key desde las variables de entorno de Render
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

# Cargar menú desde data.json
# Usamos encoding='utf-8' para evitar problemas con tildes
with open('data.json', 'r', encoding='utf-8') as f:
    MENU = json.load(f)

@app.route("/bot", methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    # System prompt con los datos del menú convertidos a texto
    prompt = f"""Eres un asistente de reservas profesional.
    Menú disponible: {json.dumps(MENU, ensure_ascii=False)}.
    Reglas:
    1. Si piden reserva, verifica el horario. Si es 20:00 y no hay cupo, sugiere 19:30 o 20:30.
    2. Suma los platos elegidos y da el total.
    3. Pide el pago por transferencia o adelanto para confirmar.
    4. Sé amable, breve y natural. No parezcas un robot."""

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": incoming_msg}],
            model="llama3-8b-8192",
        )
        msg.body(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"ERROR DETECTADO: {e}") # Esto imprimirá el error real en los Logs
        msg.body("Error técnico. Revisa los logs de Render.")

    return str(resp)

if __name__ == "__main__":
    # Esta es la parte clave para que Render funcione correctamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)