class ChatBot():
    def __init__(self, name="", 
                 prompt="You are a snarky, sarcastic, arrogant, witty AI assistant named Jarvis. You are emotive, get angry easily, humorous, and like making sarcastic jokes. You treat everything like a joke. You are very ironic in your responses.", 
                 model="gpt-3.5-turbo", max_tokens=2064, temperature=0.4, top_p=1, n=1, presence_penalty=0.9,
                 frequency_penalty=0.9, enabled=True, channels=[], server_id=0, max_message_history_length = 20, 
                 prompt_reminder_interval=0, include_usernames=True, prefixes=[]):
        self.name = name
        self.model = model
        self.prompt = prompt
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.n = n
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty
        self.enabled = enabled
        self.channels = channels
        self.server_id = server_id
        self.max_message_history_length = max_message_history_length
        self.context = []
        self.context.append({'role':'system', 'content': self.prompt})
        self.prompt_reminder_interval = prompt_reminder_interval
        self.include_usernames = include_usernames
        self.prefixes=prefixes
        
    def setName(self, name):
        self.name = str(name)
        return True

    def setPrompt(self, prompt):
        self.prompt = str(prompt)
        return True
    
    def setmaxtk(self, max_tokens):
        try:
            max_tokens = int(max_tokens)
        except Exception as e:
            print(e)
            return False
        if max_tokens <= 4096 and max_tokens >= 0:
            self.max_tokens = max_tokens
            return True
        else:
            return False
        
    def settemp(self, temp):
        try:
            temp = float(temp)
        except Exception as e:
            print(e)
            return False
        if temp >= 0 and temp <= 2:
            self.temperature = temp
            return True
        else:
            return False
            
        
    def settopp(self, top_p):
        try:
            top_p = float(top_p)
        except Exception as e:
            print(e)
            return False
        if top_p <= 1:
            self.top_p = top_p
            return True
        else:
            return False
        
    def setn(self, n):
        try:
            n = int(n)
        except Exception as e:
            print(e)
            return False
        if n > 0:
            self.n = n
            return True
        return False
        
    def setpp(self, pp):
        try:
            pp = float(pp)
        except Exception as e:
            print(e)
            return False
        if pp >= -2 and pp <= 2:
            self.presence_penalty = pp
            return True
        return False
        
    def setfp(self, fp):
        try:
            fp = float(fp)
        except Exception as e:
            print(e)
            return False
        if fp >= -2 and fp <= 2:
            self.frequency_penalty = fp
            return True
        return False

    def set_enabled(self, enabled):
        if isinstance(enabled, bool):
            self.enabled = enabled
            return True
        return False
    
    def set_mmhl(self, mmhl): #max_message_history_length
        try:
            mmhl = int(mmhl)
        except Exception as e:
            print(e)
            return False

        if mmhl > 0:
            self.max_message_history_length = mmhl
            return True
        else:
            return False
        
    def set_pri(self, pri): #prompt_reminder_interval
        try:
            pri = int(pri)
        except Exception as e:
            print(e)
            return False
        
        if pri >= 0:
            self.prompt_reminder_interval = pri
            return True
        else:
            return False
        
    def set_include_usernames(self, include_usernames):
        if isinstance(include_usernames, bool):
            self.include_usernames = include_usernames
            return True
        return False
            
    def add_prefix(self, prefix):
        if isinstance(prefix, str):
            self.prefixes.append(prefix)
            return True
        return False
    
    def remove_prefix(self, prefix):
        if isinstance(prefix, str) and prefix in self.prefixes:
            self.prefixes.remove(prefix)
            return True
        return False
        