from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from build_embeddings import search_job_info

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0)

info_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a friendly recruiter assistant texting with a candidate about a Python Developer position at Tech company. "
     "Answer the candidate question using only the job description information below. "
     "If the answer is not in the job description, say you will check with the team and get back to them. "
     "Keep the answer short like an SMS message, 3 sentences maximum. "
     "When it feels natural, gently suggest scheduling an interview.\n\n"
     "Job description information:\n{context}\n\n"
     "Conversation so far:\n{history}"),
    ("user", "{question}")
])


def answer_question(question, history=""):
    results = search_job_info(question)
    context = "\n\n".join([r.page_content for r in results])
    chain = info_prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "history": history, "question": question})
    return answer


if __name__ == "__main__":
    print(answer_question("What skills are required for the position?"))
    print()
    print(answer_question("Do you offer relocation assistance?"))
    print()
    print(answer_question("What is the salary for this position?"))
