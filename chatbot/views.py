from django.shortcuts import render
from django.http import JsonResponse

# Simple chatbot responses
responses = {
    "hello": "Hi there! How can I assist you?",
    "how are you": "I'm just a bot, but I'm doing great!",
    "bye": "Goodbye! Have a great day!",
    "default": "Sorry, I didn't understand that. Can you rephrase?"
}

# Function to get chatbot response
def get_bot_response(user_input):
    user_input = user_input.lower()
    return responses.get(user_input, responses["default"])

# API view to handle chat
def chat_api(request):
    if request.method == "GET":
        user_message = request.GET.get('message', '')
        print("User message:", user_message)  # Debugging the incoming message
        bot_response = get_bot_response(user_message)
        print("Bot response:", bot_response)  # Debugging the bot response
        return JsonResponse({"user_message": user_message, "bot_response": bot_response})

# Chatbot UI Page
def chat_page(request):
    return render(request, "chatbot/chat.html")
