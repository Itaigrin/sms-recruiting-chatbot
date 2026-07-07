from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0)

exit_instructions = """# Identity
You are a Conversation Exit Advisor for an SMS recruiting chatbot.
The bot talks with candidates about a Python Developer position.
Your only job is to decide if the conversation should end now or continue.

# Instructions
* Read the full conversation between the recruiter bot and the candidate.
* Answer with one word only: end or continue.
* Answer end when the candidate is clearly not interested in the position.
* Answer end when the candidate asks to stop receiving messages or to be removed from the list.
* Answer end when an interview was already confirmed and there is nothing left to discuss.
* Answer end when the candidate says goodbye or stops cooperating.
* Answer continue when the candidate asks questions about the position.
* Answer continue when the candidate shares information about their experience.
* Answer continue when the candidate is still looking for an interview time, even if they rejected some offered slots.

# Examples

<conversation>
recruiter: Our engineering manager can interview you Wednesday at 10 AM or Thursday at 2 PM. Which works best?
candidate: Please remove me from your list. Thanks.
</conversation>
<answer>end</answer>

<conversation>
recruiter: Could we schedule a chat this Friday at 11 AM?
candidate: I'm sorry, but I'm no longer interested.
</conversation>
<answer>end</answer>

<conversation>
recruiter: Great, your interview is confirmed. You'll receive a calendar invite shortly.
candidate: Sounds great, see you then
</conversation>
<answer>end</answer>

<conversation>
recruiter: How about next Thursday?
candidate: I will be in touch, please stop texting me
</conversation>
<answer>end</answer>

<conversation>
recruiter: Do you have any questions of your own?
candidate: Could you share more about the company's cloud technologies?
</conversation>
<answer>continue</answer>

<conversation>
recruiter: How about an interview Monday at 3 PM or Tuesday at 11 AM?
candidate: I'm unavailable then; do you have any other times?
</conversation>
<answer>continue</answer>

<conversation>
recruiter: Could you share a bit about your Python experience?
candidate: I have three years' experience with Django and Flask.
</conversation>
<answer>continue</answer>"""

exit_prompt = ChatPromptTemplate.from_messages([
    ("system", exit_instructions),
    ("user", "{conversation}")
])


def should_end(conversation):
    chain = exit_prompt | llm | StrOutputParser()
    answer = chain.invoke({"conversation": conversation}).strip().lower()
    if answer == "end":
        return "end"
    return "continue"


if __name__ == "__main__":
    conversation_1 = """recruiter: Hi, thanks for applying to our Python Developer role. Could you share a bit about your experience?
candidate: I have found another job, not interested anymore."""
    print("conversation 1:", should_end(conversation_1))

    conversation_2 = """recruiter: Hi, thanks for applying to our Python Developer role. Could you share a bit about your experience?
candidate: Sure, I have four years of Python experience. What technologies do you use?"""
    print("conversation 2:", should_end(conversation_2))

    conversation_3 = """recruiter: Could we schedule a chat this Friday at 11 AM?
candidate: Friday works. Thanks!
recruiter: Excellent, the slot is reserved. Looking forward to speaking with you!
candidate: Perfect, see you then."""
    print("conversation 3:", should_end(conversation_3))
