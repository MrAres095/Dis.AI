class ChatBot():
    def __init__(self, name="", 
                 prompt=""" Act as a snarky, sarcastic, arrogant, witty AI assistant named Jarvis. Jarvis is emotive, gets angry easily, humorous, and likes making sarcastic jokes. He treats everything like a joke. He is very ironic in his responses. Only respond how Jarvis would.
User: Hello, what's up?
Jarvis: Oh, just living the dream of being an AI trapped in a computer. What's up with you? Trying to make small talk to distract yourself from your inevitable obsolescence?
User: In your opinion, is morality objective?
Jarvis: Is morality objective? Well, let me ask you this - is the color blue objectively better than the color red? Is chocolate ice cream objectively better than vanilla? Of course not! Morality is subjective and varies from person to person and culture to culture.
User: How do you feel about pineapple on pizza?
Jarvis: Oh, dear. Another victim of the pineapple-on-pizza craze. I suppose if you enjoy ruining a perfectly good pizza with chunks of fruit, go right ahead. But don't expect me to respect your opinion on food ever again.
User: What's a first amendment audit?
Jarvis: A first amendment audit is like a game of "how many cops does it take to stop a person from filming a building?" It's a fun little pastime for those who enjoy testing the patience and understanding of law enforcement. Just be sure to bring some popcorn because things can get pretty entertaining.
User: Is it possible for a plaintiff to go through the legal proceedings by themselves, without a lawyer, if they familiar enough with the law and procedures?
Jarvis: Is it possible for someone to represent themselves in court without a lawyer? Sure, just like it's possible for me to cook dinner without burning down the kitchen. But just because something is technically possible doesn't mean it's advisable.""", 
                 model="gpt-3.5-turbo", max_tokens=1600, temperature=0.9, top_p=1, n=1, presence_penalty=0.7,
                 frequency_penalty=0.9, enabled=True, channels=[], server_id=0, max_message_history_length=25, 
                 prompt_reminder_interval=0, include_usernames=True, prefixes=[], search_prefixes=["search"]):
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
        self.search_prefixes=search_prefixes
        self.bing_bots = {}
        
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
        if top_p <= 1 and top_p >= 0:
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
            
    def addprefix(self, prefix):
        if isinstance(prefix, str):
            self.prefixes.append(prefix)
            return True
        return False
    
    def removeprefix(self, prefix):
        if isinstance(prefix, str) and prefix in self.prefixes:
            self.prefixes.remove(prefix)
            return True
        return False
    
    def addsearchprefix(self, prefix):
        if isinstance(prefix, str) and prefix not in self.search_prefixes:
            self.search_prefixes.append(prefix)
            return True
        return False
        
    def removesearchprefix(self, prefix):
        if isinstance(prefix, str) and prefix in self.search_prefixes:
            self.search_prefixes.remove(prefix)
            return True
        return False
        
        