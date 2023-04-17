from utils.responses import get_response
from core import ChatBot
class Server():
    def __init__(self, id=0, adminroles=[], allowedroles=[], dailymsgs=0, openai_key=""):
        self.id = id
        self.adminroles = adminroles
        self.allowedroles = allowedroles
        self.dailymsgs=dailymsgs
        self.openai_key=openai_key
        
    async def set_admin_roles(self, roles):
        for role in roles:
            if role not in self.adminroles:
                self.adminroles.append(role)
            if role not in self.allowedroles:
                self.allowedroles.append(role)
                
    async def set_allowed_roles(self, roles):
        for adminrole in self.adminroles:
            if adminrole not in self.allowedroles:
                self.allowedroles.append(adminrole)
        for role in roles:
            if role not in self.allowedroles:
                self.allowedroles.append(role)
                
    async def set_openai_key(self, key):
        key=str(key.strip())
        try:
            response = await get_response(ChatBot.ChatBot(name="temp", prompt=""), message=None, apikey=key)
        except Exception as e:
            print(f"seterr: {e}")
            return False
        
        if response[0] != -3:
            self.openai_key = key
        return response[0] != -3
        
        
        
        