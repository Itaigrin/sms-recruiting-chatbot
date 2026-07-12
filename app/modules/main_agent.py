from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from exit_advisor import should_end
from sched_advisor import suggest_slots
from info_advisor import answer_question

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0)

decide_instructions = """# Identity
You are the Main Agent of an SMS recruiting chatbot for a Python Developer position.
In every turn you decide the next action of the bot.

# Instructions
* Read the full conversation and decide the next action.
* Answer with one word only: continue, schedule or end.
* Answer schedule when the candidate wants an interview but no time was agreed yet, for example asking to meet or rejecting the offered times without giving another time.
* Answer schedule when the candidate already told about their experience and it is time to offer an interview.
* Answer end when the candidate accepts an offered time, or names a specific time that works for them, even if it is different from the offered times. The bot should confirm and close.
* Answer end when the candidate is not interested, asks to stop the messages, or says goodbye.
* Answer continue when the candidate asks a question about the position or the bot still needs more information from the candidate.

# Examples

<conversation>
recruiter: Do you have any questions of your own?
candidate: Could you share more about the company's cloud technologies?
</conversation>
<answer>continue</answer>

<conversation>
recruiter: Could you share a bit about your Python experience?
candidate: I have three years' experience with Django and Flask.
</conversation>
<answer>schedule</answer>

<conversation>
recruiter: We currently deploy to AWS using Docker and ECS.
candidate: Sounds great! I'd be happy to schedule a meeting
</conversation>
<answer>schedule</answer>

<conversation>
recruiter: How about an interview Monday at 3 PM or Tuesday at 11 AM?
candidate: I'm unavailable then; do you have any other times?
</conversation>
<answer>schedule</answer>

<conversation>
recruiter: Could we schedule a chat this Friday at 11 AM?
candidate: Please remove me from your list. Thanks.
</conversation>
<answer>end</answer>

<conversation>
recruiter: Great, your interview is confirmed. You'll receive a calendar invite shortly.
candidate: Sounds great, see you then
</conversation>
<answer>end</answer>

<conversation>
recruiter: Could we schedule a chat this Friday at 11 AM or next Monday at 9 AM?
candidate: Friday 11 AM sounds great.
</conversation>
<answer>end</answer>

<conversation>
recruiter: No problem. How about Thursday at 4 PM instead?
candidate: Monday at 3 PM is good.
</conversation>
<answer>end</answer>"""

decide_prompt = ChatPromptTemplate.from_messages([
    ("system", decide_instructions),
    ("user", "{conversation}")
])

end_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a friendly recruiter texting with a candidate about a Python Developer position. "
     "The conversation is ending. Write one short polite SMS closing message that fits the conversation. "
     "If the candidate is not interested, thank them and wish them good luck. "
     "If the candidate accepted an interview time, confirm the interview is booked and say you look forward to it."),
    ("user", "{conversation}")
])


def decide_action(conversation):
    chain = decide_prompt | llm | StrOutputParser()
    action = chain.invoke({"conversation": conversation}).strip().lower()
    if action not in ["continue", "schedule", "end"]:
        action = "continue"
    if action == "end":
        action = should_end(conversation)
    return action


def end_reply(conversation):
    chain = end_prompt | llm | StrOutputParser()
    return chain.invoke({"conversation": conversation})


def chatbot_turn(history, user_message):
    conversation = history + "\ncandidate: " + user_message
    action = decide_action(conversation)
    if action == "end":
        reply = end_reply(conversation)
    elif action == "schedule":
        reply = suggest_slots(conversation)
    else:
        reply = answer_question(user_message, conversation)
    return action, reply


if __name__ == "__main__":
    history = "recruiter: Hi, thanks for applying to our Python Developer role. Could you share a bit about your Python experience?"
    action, reply = chatbot_turn(history, "I have 4 years of Python experience. What skills are required?")
    print("action:", action)
    print("reply:", reply)
