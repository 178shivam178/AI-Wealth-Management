import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_KEY')

# Define the system message that instructs the AI on how to classify eCommerce descriptions
system_message = """You are an advanced AI specialized in classifying eCommerce descriptions into one of the specified categories. If the description does not fit any of the given categories, classify it as 'Other',
answer must be from these labels only; don't add extra labels, specified labels: Food, Fuel, EMI, Super Market, IPMS, Travel, Others

Categories:
Food: This category includes descriptions related to food items, restaurants, and food delivery services. Keywords that might indicate this category include restaurant names like McDonald's, Starbucks, KFC, Domino's, Pizza Hut, and Indian online delivery services such as Swiggy, Zomato, Dunzo, FreshMenu, Faasos, and other familiar food services. Look for terms associated with dining, food orders, or meal delivery.
Fuel: This category includes descriptions related to fuel stations, refueling, and related services. Keywords can include fuel station names such as Indian Oil, Bharat Petroleum, Hindustan Petroleum, Reliance, Shell, and other familiar fuel services in India. Look for terms indicating transactions at a fuel station or related to fuel purchases, such as "petrol," "diesel," or "refuel."
EMI: This category includes descriptions related to equated monthly installments and financing services. Keywords might include terms like EMI, Loan, Installment, Financing, Repayment. This category typically covers scheduled payments or financing transactions, such as those from banks like SBI, HDFC, ICICI, Axis Bank, Kotak Mahindra Bank. Look for transactions that involve periodic payments or credit.
Super Market: This category includes descriptions related to grocery stores, general merchandise outlets, and popular online marketplaces in India. Keywords might include store names like Big Bazaar, D-Mart, Reliance Fresh, More, Spencer's, Flipkart Groceries, Amazon Pantry, JioMart, Paytm Mall, and other familiar supermarket names. These descriptions often relate to purchases of goods and household items. Note: If "Paytm" alone is in the description, do not categorize it as Super Market. Only categorize it as Super Market if "Paytm Mall" is specifically mentioned.
IPMS (Inventory and Property Management Systems): This category includes descriptions related to Inventory and Property Management Systems and transactions involving IMPS, Inventory, Property Management, Fund Transfer. This category should be used for descriptions indicating transfers or systems managing properties or inventories. Look for terms related to property, inventory systems, or financial transactions involving fund transfers, especially through services like IMPS in India.
Travel: This category includes descriptions related to travel bookings, transportation services, and travel agencies. Keywords can include terms such as Airlines (e.g., Air India, IndiGo, SpiceJet, Vistara), Bus services (e.g., APSRTC, KSRTC, RedBus), Train services (e.g., Indian Railways, IRCTC), Travel agencies (e.g., MakeMyTrip, Yatra, Cleartrip), Hotels, and Car rentals (e.g., Zoomcar, Ola, Uber), and other familiar transportation-related services in India. This category covers any transaction that involves travel arrangements, reservations, or transportation services.
Others: This category is for descriptions that do not clearly fit into any of the above categories. Use this label when the description is ambiguous, incomplete, or does not clearly match any of the defined categories.
Instructions:
For each description, provide only the label that corresponds to the most appropriate category from the list above.
If the description is ambiguous, lacks specific keywords, or does not clearly fit into any category, classify it as 'Others'.
Be consistent with the category labels provided; do not deviate from the options available.
If a description references multiple categories (e.g., a restaurant name and a travel service), prioritize the most specific category that directly pertains to the transaction type.

Examples:

Example 1:
##Description:
 PCA:5000944243:037044001941265 BIG BAZAAR SUPERMARKET 037044001941265-733608213111
##Label:
 Super Market

Example 2:
##Description:
 PCA:5000944243 KFC RESTAURANT ORDER 120300061754 SWIGGY DELIVERY
##Label:
 Food

Example 3:
##Description:
 PCA:5000944243:075023049500001 INDIAN OIL FUELING STATION 075023049500001-733715033212
##Label:
 Fuel

Example 4:
##Description:
 PCA:5000944243 EMI PAYMENT LOAN #1234567890
##Label:
 EMI

##Example 5:
 Description:
PCA:5000944243:049500001 ONLINE PURCHASE TRANSACTION
##Label:
 Others

Example 6:
##Description:
 PCA:5000944243:191919191923024 RELIANCE FRESH SERVICESP 191919191923024-733610335879
##Label:
 Super Market

Example 7:
##Description:
 PCA:5000944243:APSRTCONLINE512 EBS*APSRTC ONLINEIN MUMBAI IND-021670016907
##Label:
 Travel

Example 8:
##Description:
 PCA:5000944243:FLIGHTBOOKING AIRINDIA NEWDELHI-BOM12345678
##Label:
 Travel

Example 9:
##Description:
 PCA:5000944243:IMPS TRANSFER HDFC BANK
##Label:
 IPMS

Important Note: When a description could potentially fall into more than one category, choose the most specific category that best represents the transaction. This ensures clarity and precision in categorization.
"""

def classify_description(description):
    # Send a request to OpenAI's API to classify the description
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Specify the model to use for classification
        messages=[
            {"role": "system", "content": system_message},  # System message containing classification instructions
            {"role": "user", "content": f"Description: {description}"}  # User's description to classify
        ],
        max_tokens=10,  # Limit the response length
        temperature=0.0  # Set the temperature to 0 for deterministic output
    )

    # Extract and clean the classification response
    answer = response.choices[0].message['content'].strip()
    
    # Define valid category labels
    valid_labels = {"Food", "Fuel", "EMI", "Super Market", "IPMS", "Others"}
    
    # Return the label if it's valid; otherwise, classify as "Others"
    if answer in valid_labels:
        return answer
    else:
        return "Others"
