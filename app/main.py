import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

from main_agent import chatbot_turn

opening_message = "Hi, thanks for applying to our Python Developer role. Could you share a bit about your Python experience?"


def run_chat():
    print("SMS Recruiting Bot (type quit to stop)")
    print("\nBot:", opening_message)
    history = "recruiter: " + opening_message
    while True:
        user_message = input("\nYou: ")
        if user_message == "quit":
            break
        action, reply = chatbot_turn(history, user_message)
        history = history + "\ncandidate: " + user_message + "\nrecruiter: " + reply
        print("\nBot:", reply)
        if action == "end":
            print("\n(the conversation has ended)")
            break


if __name__ == "__main__":
    run_chat()
