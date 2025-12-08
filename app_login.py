import bcrypt
import json

USER_FILE = "users_data.json"

class AuthSystem:
    def __init__(self):
        self.session_user = None

    def load_users(self):
        try:
            with open(USER_FILE, 'r') as f:
                return json.load(f)['users']
        except FileNotFoundError:
            print("Erreur : Fichier d'utilisateurs non trouvé.")
            return []
        except json.JSONDecodeError:
            print("Erreur : Format JSON invalide dans le fichier utilisateur.")
            return []

    def login(self, username_input, password_input):
        
        users = self.load_users()
        
        user_record = next((u for u in users if u['username'] == username_input), None)
        
        if not user_record:
            return False, "Nom d'utilisateur ou mot de passe invalide."
        
        stored_hash_bytes = user_record['password_hash'].encode('utf-8')
        password_input_bytes = password_input.encode('utf-8')
        
        try:
            if bcrypt.checkpw(password_input_bytes, stored_hash_bytes):
                self.session_user = {
                    "username": user_record['username'],
                    "role": user_record['role'],
                    "is_authenticated": True
                }
                return True, f"Connexion réussie ! Bienvenue {username_input}."
            else:
                return False, "Nom d'utilisateur ou mot de passe invalide."

        except ValueError:
            return False, "Erreur de vérification (hachage corrompu)."

    def logout(self):
        """Déconnecte l'utilisateur."""
        self.session_user = None
        return "Déconnexion réussie."

    def access_admin_panel(self):
        """Exemple de contrôle d'accès."""
        if self.session_user and self.session_user['is_authenticated'] and self.session_user['role'] == 'admin':
            return "Accès accordé : Ceci est le panneau d'administration !"
        else:
            return "Accès refusé. Vous devez être connecté en tant qu'administrateur."

if __name__ == "__main__":
    
    auth_app = AuthSystem()
    
    print("\n--- TEST 1 : Connexion Réussie ---")
    user = input("Nom d'utilisateur : ")
    pwd = input("Mot de passe : ")
    
    success, message = auth_app.login(user, pwd)
    print(message)
    print("Statut de la session :", auth_app.session_user)
    print(auth_app.access_admin_panel())
    
    print("\n--- TEST 2 : Tentative Échouée ---")
    success_fail, message_fail = auth_app.login("mon_admin", "mauvais_mot_de_passe")
    print(message_fail)
    
    print("\n--- TEST 3 : Déconnexion ---")
    print(auth_app.logout())
    print(auth_app.access_admin_panel())
