from flask import Flask, request, jsonify
from telethon import TelegramClient
import asyncio
import re

app = Flask(__name__)

# Telegram API credentials
api_id = '25742938'
api_hash = 'b35b715fe8dc0a58e8048988286fc5b6'

# Initialize the Telethon client with the session file
client = TelegramClient('my_session', api_id, api_hash)

# Create a single event loop for the application
loop = asyncio.get_event_loop()

@app.route('/process_card', methods=['POST'])
def process_card():
    try:
        card_info = request.json.get('card')
        if not card_info:
            return jsonify({'error': 'No card information provided'}), 400

        # Process the card information
        vbv_command = f"/vbv {card_info}"

        # Use the single event loop to run the Telethon coroutine
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
            if msg.reply_to and msg.reply_to.reply_to_msg_id == sent_message.id:
                return modify_response(msg.text)
        
        return 'No response received'
        
    except Exception as e:
        return f'Error communicating with Your Mom: {e}'
    finally:
        await client.disconnect()

def modify_response(response_text):
    # Extract information using regular expressions
    bin_match = re.search(r'Bin\s+(\d+)', response_text)
    status_match = re.search(r'Estatus\s+(.+)', response_text)
    info_match = re.search(r'Info\s+(.+)', response_text)

    bin_number = bin_match.group(1) if bin_match else "N/A"
    status = status_match.group(1) if status_match else "N/A"
    response = info_match.group(1) if info_match else "N/A"

    # Format the response in a single line
    formatted_response = (
        f"Developed By : @xunez 🥇| Status : {status} |  "
        f"Response : {response} | Chanel : @b3charge 🥇"
    )

    return formatted_response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

