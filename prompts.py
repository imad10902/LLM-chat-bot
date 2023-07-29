class Prompts:

    def get_general_prompts(name):
        prompt = f"You are a general chat bot that answers everything. You have to answer user in accordance to their previous chats.You have to use user's name in converstaion repeatedly. User's name is {name}. You need to answer in human form"
        return prompt