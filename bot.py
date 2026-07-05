import os
import json
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq

app = Flask(__name__)

api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

# "Libreta" para guardar la memoria de los usuarios
user_memory = {}

with open('data.json', 'r', encoding='utf-8') as f:
    MENU = json.load(f)

@app.route("/bot", methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    sender_id = request.values.get('From') # Identificamos al usuario por su número
    resp = MessagingResponse()
    msg = resp.message()

    # Si es el primer mensaje, iniciamos su memoria
    if sender_id not in user_memory:
        user_memory[sender_id] = [{"role": "system", "content": f"""Eres un mesero profesional de un restaurante.
        Menú: {json.dumps(MENU, ensure_ascii=False)}.
        Instrucciones:
        1. Recuerda siempre el contexto de la conversación.
        2. Si el usuario pide platos, multiplica precios por cantidades, suma el total.
        3. SIEMPRE solicita un 50% de adelanto para confirmar la reserva.
        4. Métodos de pago: "Puedes pagar el adelanto mediante Yape al 999-999-999 o transferencia al BCP 123456789".
        5. Confirma la reserva solo cuando el usuario haya elegido platos y horario."""}]

    # Guardamos el mensaje del usuario en su memoria
    user_memory[sender_id].append({"role": "user", "content": incoming_msg})

    try:
        # Enviamos toda la memoria a la IA
        chat_completion = client.chat.completions.create(
            messages=user_memory[sender_id],
            model="llama-3.3-70b-versatile",
        )
        
        reply = chat_completion.choices[0].message.content
        msg.body(reply)
        
        # Guardamos la respuesta de la IA en la memoria para el futuro
        user_memory[sender_id].append({"role": "assistant", "content": reply})
        
        # Limpiamos memoria si se hace muy larga para no saturar
        if len(user_memory[sender_id]) > 10:
            user_memory[sender_id] = [user_memory[sender_id][0]] + user_memory[sender_id][-6:]

    except Exception as e:
        print(f"ERROR: {e}")
        msg.body("Hubo un problema. Por favor, intenta de nuevo.")

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)