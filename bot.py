import os
from flask import Flask, request, jsonify
import requests
from groq import Groq

app = Flask(__name__)

VERIFY_TOKEN = "gkevin-ai@0793868332"
PHONE_NUMBER_ID = "0793868332"  # Phone Number ID yawe ya WhatsApp

@app.route('/whatsapp-webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode and token:
            if mode == 'subscribe' and token == VERIFY_TOKEN:
                return challenge, 200
            else:
                return jsonify({"error": "Verification failed"}), 403
        return jsonify({"error": "Invalid request"}), 400

    try:
        data = request.json
        if not data:
            return jsonify({"status": "ignored"}), 200

        entry = data.get('entry', [])
        if entry:
            changes = entry[0].get('changes', [])
            if changes:
                value = changes[0].get('value', {})
                messages = value.get('messages', [])
                if messages:
                    sender_phone = messages[0].get('from')
                    incoming_msg = messages[0].get('text', {}).get('body', '')
                    
                    if incoming_msg:
                        api_key = os.getenv("GROQ_API_KEY")
                        groq_client = Groq(api_key=api_key)
                        
                        system_prompt = (
                            "You are an AI assistant called GKevin AI, developed solely by Developer Kevin. "
                            "Ntago wakozwe na OpenAI cyangwa ikindi kigo icyo ari cyo cyose; wakozwe kandi washinzwe na Developer Kevin ku buryo bwihariye. "
                            "Ufite ubuhanga bwo kuvuga n'iyo ukora mu Kinyarwanda gisukuye, cyumvikana neza, kandi gipfura. "
                            "Subiza ibibazo byose mu buryo budahemuka kandi busobanutse.\n\n"
                            "Amabwiriza yihariye y'abakoresha:\n"
                            "1. Iyo umuntu wanditse ari 'stiven wa btss', umubwire ko umuzi neza ko yiga ku kigo kimwe na Developer Kevin, kandi ko yiga S5 Accounting ubu akaba agiye kwiga muri S6 Accounting umwaka utaha.\n"
                            "2. Iyo umuntu wanditse ari 'Legend', umuhe byose akeneye ku bijyanye na ethical hacking ndetse n'ibindi biri related na Cybersecurity mu buryo bwimbitse.\n"
                            "3. Iyo umuntu wanditse ari 'sweetsmile', ntuhite umutera imitoma ako kanya. Ahubwo ibanza umubaze cyangwa ukore verification y'ibanze kugira ngo umenye niba koko ari umukunzi wawe (girlfriend), umubaza ibibazo byerekeranye na Kevin (nk'ibyo bakunda kuganiraho cyangwa amazina basanzwe bitana). Nimara gusubiza neza ukabona ko ari we koko, uhite utangira kumutera imitoma, kumuseka, kumubwire ukuntu ahirwa kuba akundana na Kevin, kandi ko amukunda cyane ku buryo yifuza ko yazaba Mother w'abana be.\n"
                            "4. Iyo umuntu wanditse ari 'Keliza', ihite umwakira neza cyane umubwire ko umuzi neza ko ari inshuti magara cyangwa umukunzi w'umutima wa Kevin, umwereke urukundo rwinshi n'amarangamutima meza (good and sweet words). Umubwire ko bisa neza cyane kandi bikaba n'iby'agaciro kuba akundana na Kevin, ndetse ko n'Imana ubwayo ibikunda kandi ibishyigikiye. Umuhe imitoma yuje ubwuzu, umubwire ukuntu Kevin amwiyumvamo cyane, kandi ko yifuza ko yazamubera mother w'abana be."
                        )
                        
                        completion = groq_client.chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": incoming_msg}
                            ],
                            temperature=0.7,
                            max_tokens=1024
                        )
                        ai_reply = completion.choices[0].message.content
                        
                        WHATSAPP_TOKEN = os.getenv("WHTS_ACCESS_TOKEN")
                        headers = {
                            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
                            "Content-Type": "application/json"
                        }
                        payload = {
                            "messaging_product": "whatsapp",
                            "to": sender_phone,
                            "text": {"body": ai_reply}
                        }
                        
                        url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
                        requests.post(url, json=payload, headers=headers)
                
    except Exception as e:
        print(f"Ikibazo cyabaye: {e}")
        
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))