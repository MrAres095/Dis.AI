class Server():
    def __init__(self, id=0, adminroles=[], allowedroles=[]):
        self.id = id
        self.adminroles = adminroles
        self.allowedroles = allowedroles
        
    def set_admin_roles(self, role):
        if role not in self.adminroles:
            self.adminroles.append(role.id)
        if role not in self.allowedroles:
            self.allowedroles.append(role.id)
                
    def set_allowed_roles(self, *roles):
        for adminrole in self.adminroles:
            if adminrole not in self.allowedroles:
                self.allowedroles.append(adminrole.id)
        for role in roles:
            if role not in self.allowedroles:
                self.allowedroles.append(role.id)
                
        
        