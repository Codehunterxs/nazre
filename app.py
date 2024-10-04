from flask import Flask, request, jsonify
from telethon import TelegramClient
import asyncio

app = Flask(__name__)

# Telegram API credentials
api_id = '25742938'
api_hash = 'b35b715fe8dc0a58e8048988286fc5b6'

# Initialize the Telethon client with the session file
client = TelegramClient('my_session', api_id, api_hash)

@app.route('/process_card', methods=['POST'])
def process_card():
    try:
        card_info = request.json.get('card')
        if not card_info:
            return jsonify({'error': 'No card information provided'}), 400

        # Process the card information
        vbv_command = f"/vbv {card_info}"

        # Use asyncio to run the Telethon coroutine
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(send_and_receive(vbv_command))

        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': f'Internal server error: {e}'}), 500

async def send_and_receive(message):
    try:
        # Start the client using the session file
        await client.start()
        
        # Use the group's ID to get the entity
        group_id = -4593530179  # Make sure to use the negative sign
        entity = await client.get_entity(group_id)
        
        # Send message to the group
        sent_message = await client.send_message(entity, message)
        
        # Wait for a few seconds to allow the bot to reply
        await asyncio.sleep(5)  # Adjust the delay as needed
        
        # Fetch messages from the group and filter by reply_to_msg_id
        response = await client.get_messages(entity, limit=10)
        for msg in response:
            if msg.reply_to_msg_id == sent_message.id:
                return modify_response(msg.text)
        
        return 'No response received'
        
    except Exception as e:
        return f'Error communicating with group: {e}'
    finally:
        await client.disconnect()

def modify_response(response_text):
    # Replace specific words in the response
    replacements = {
        "Datos": "[火]  𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐃",
        "Gracias": "𝐁𝐘",
        "Braintree": "@xunez",
        "Usuario": "[火]",
        "change_is_constant_x420": "𝐒𝐏𝐀𝐂𝐄",
        "FREE": " 𝐀𝐔𝐓𝐎𝐌𝐀𝐓𝐈𝐎𝐍"
    }
    
    for word, replacement in replacements.items():
        response_text = response_text.replace(word, replacement)
    
    return response_text

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

