import encrypt
import json

def main():
    while True:
        a = input("command: ")
        if a == "gen":
            print(encrypt.generate_key())
        elif a == "get":
            print(encrypt.get_key())
        elif a == "enc":
            s = input("string: ")
            try:
                s = dict(s)
            except:
                print("excp")
            enc = encrypt.encrypt_string(s)
            dec = encrypt.decrypt_string(enc)
            
            print(enc)
            print(dec)
            
        elif a == "dec":
            s = input("string: ")
            print(encrypt.decrypt_string(s))
        
        
if __name__ == "__main__":
    main()