from flask import Flask, request, jsonify
from telethon import TelegramClient
import asyncio
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

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
        response = loop.run_until_complete(send_to_group(vbv_command))

        return jsonify({'response': response})
    except Exception as e:
        logging.error(f"Error processing card: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

async def send_to_group(message):
    try:
        # Start the client using the session file
        await client.start()
        
        # Use the group's ID to get the entity
        group_id = -4593530179  # Make sure to use the negative sign
        entity = await client.get_entity(group_id)
        
        # Send message to the group
        sent_message = await client.send_message(entity, message)
        
        # Return confirmation
        return f'Message sent to group: {sent_message.text}'
        
    except Exception as e:
        logging.error(f"Error communicating with group: {e}", exc_info=True)
        return 'Error communicating with group'
    finally:
        await client.disconnect()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
