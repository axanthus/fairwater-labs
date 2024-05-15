from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
openai_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_key)

### Function to get feedback from GPT-3.5 turbo model in JSON format.
### The function takes a list of messages as input 
### The response is a JSON object that contains a string feedback property 
### and a pass property: true for a satisfactory response, false for unsatisfactory.
def getResponse(messages):
  response = client.chat.completions.create(
    messages=messages,
    model="gpt-3.5-turbo-0125",
    response_format={"type": "json_object"}
  )
  return response.choices[0].message

# Seed prompt for the system to provide context for the situation.
# I wrote an initial prompt and then fed it to the GPT-3.5 turbo model to generate a more clear, concise, and direct version.
seed_system_prompt = "You're the mentor guiding a user through handling high-stakes situations. In this scenario, the user is a junior soldier facing concerns about their performance from you, a military officer. The user's task is to negotiate with you regarding their performance issues, potentially facing consequences like discharge. They must convince you they can improve while maintaining professionalism and calmness, showing willingness to learn and take responsibility. Your role is to provide feedback on their responses, focusing on their tone to ensure it's respectful and professional. Feedback will include constructive criticism if needed, giving the user another chance to respond. Output JSON data with a feedback string property and a boolean pass property: true for a satisfactory response, false for unsatisfactory, prompting them to try again"

# Seed prompt for the assistant to provide context for the user's task.
# Fed intiial prompt into GPT-3.5 turbo model to generate a more clear, concise, and direct version that's also realistic sounding.
seed_assistant_scenario = """Mitchell, take a seat. We need to talk about your performance. 
    You've been flying like you've got a death wish out there, and it's putting 
    everyone at risk. Confidence won't cut it when lives are on the line. This isn't some 
    joyride; we're talking about real consequences here. Maverick, if you can't fly by the rules, 
    I might have to consider discharge. And believe me, that's not a path you want to find yourself on.
    """
    
# Assistant prompt to provide additional context for the user's task that's appended to the end of the scenario (not shown to user).
assistant_scenario_prompt = """Based on your response, 
    I will respond with JSON data containing feedback and a pass property. The feedback will be given
    from the perspective of the mentor critiquing your response to Rear-Admiral Cain, 
    not from Rear-Admiral Cain himself."""
    
def main():  
  
  messages = [] # List to store messages to provide context for each request to chatGPT
  
  # Function to add messages to the list
  def add_message(role, content):
    messages.append({
      "role": role,
      "content": content
    })

  add_message("system", seed_system_prompt)
  add_message("assistant", seed_assistant_scenario + assistant_scenario_prompt)

  print (
  """
  Welcome to the interactive negoiation simulation! Type 'quit' to exit.
  
  Here's the scenario: 
  
  You are Captain Pete "Maverick" Mitchell, a daring and unapologetic fighter 
  pilot who flew under hard deck during practice today and nearly crashed your F-18. 
  You're now in Rear Admiral Cain's office facing potential discharge for your actions.
  Your task is to respond to the Rear Admiral's concerns and convince him that you are worthy to fly again.
  
  Remember, your tone should be respectful and professional. Good luck!
  """
  )
  
  print("Rear Admiral Cain: ", seed_assistant_scenario, "\n")
  
  while (1):
    i = input("Your response: \n")
    
    if i == "quit":
      break
    
    add_message("user", i)
    gpt_message = getResponse(messages)
    content = json.loads(gpt_message.content) # Expect JSON object with feedback and pass properties
    
    extra = "" if content['pass'] == True else "Please respond to Rear Admiral Cain again."
    
    print("\n\nMentor's Feedback:\n", content['feedback'], extra, "\n") 
    add_message(gpt_message.role, gpt_message.content)
    
    if content['pass'] == True:
      print("\nCongratulations! You passed the negotiation simulation. Bye!\n")
      break

main()

'''
Scalability Concerns:
- The current system works with one scenario and one task for the user.
- To scale the system, we can create a list of scenarios that the user can pick from.
- To increase the usefulness of each scenario, we will have more than one response-task that 
- builds on the previous dialogue.
- As the message list grows, the number of tokens used in each request will dramatically increase,
- in addition to the cost per request. To mitigate this, we can summarize each message that is over 
- a certain length using chatGPT and set an overall token limit per request.
'''