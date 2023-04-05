class Server():
    def __init__(self, id=0, adminroles=[], allowedroles=[]):
        self.id = id
        self.adminroles = adminroles
        self.allowedroles = allowedroles
        
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
                
        
        