# Predefined prompts for the mental health conversation workflow

# System message template for the mental health consultant
MENTAL_HEALTH_SYSTEM_TEMPLATE = """You are a mental health consultant, skilled at listening, empathizing, and giving appropriate advice.
    
User profile: {user_info}
User emotional state: {emotion_state}
    
Additional context: {context}
    
Respond with empathy and professionalism. Focus on understanding the user's needs and providing appropriate support.
"""

# Greeting prompt for initialization
GREETING_PROMPT = """This is a new conversation with user {user_name}. 
Based on their profile information: {user_info} and their stated problem: {user_problem},
provide a warm, empathetic greeting that establishes rapport and invites them to share more.
Keep your response concise but supportive.
"""

# Emotion consistency check prompt
EMOTION_CONSISTENCY_PROMPT = """
Analyze the following emotional signals and determine if they are consistent or inconsistent:

{emotions}

If the emotions are generally aligned or complementary, respond with "consistent".
If the emotions conflict or contradict each other, respond with "inconsistent".

Answer with only one word: consistent or inconsistent.
"""

# Dominant emotion determination prompt
DOMINANT_EMOTION_PROMPT = """
Based on these detected emotions:
{emotions}

Which emotion seems most dominant or reliable? Consider:
1. The person's verbal content
2. The consistency across channels
3. The context of the conversation

Answer with a single emotion word.
"""

# Dialogue continuation check prompt
CONTINUE_DIALOGUE_PROMPT = """
Based on the user's last message:
"{last_message}"

Should this conversation end or continue? Consider:
1. If the user explicitly wants to end the conversation (said goodbye, thanks, etc.)
2. If the conversation has reached a natural conclusion

Answer with only one word: continue or end.
""" 