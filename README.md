# TD Ransomware

Afin de lancer le ransomware:
* Il faut lancer ```sudo rm -r cnc_data token_data``` afin de supprimer au besoin les précédentes données créées par le ransomware. 

* Ensuite, il faut lancer dans le terminal ```sudo ./run_cnc.sh```. Cela active le CNC. 

* Ensuite, dans un second terminal il faut lancer ```sudo ./run_ransomware.sh```. Le ransomware va s'activer, et va envoyer au CNC : le token, le salt et la clé. 

    Si l'envoi c'est bien passé, un message se terminant par 200, qui est le code de retour de la requete POST (permettant l'envoi des données) s'affiche dans la console du CNC (ainsi que la clé, permettant le déchiffrement des fichiers par la suite). 

Si tout s'est bien passé, un texte vous demandera de renseigner la clé de déchiffrement. Après trois tentatives infructueuses, le ransomware efface tout simplement le token.bin et le salt.bin, et se ferme, vous laissant ainsi avec les données chiffrées, pas déchiffrables. C'est plus sadique que de supprimer les fichiers aha, même si bon, il suffit qu'ils aient, (sur une clé USB par exemple) un des fichiers qui a été chiffré, en clair, et ils peuvent retrouver la clé de déchiffrement. 

Je sais que ce n'est pas optimal et que je pourrrais tout simplement envoyer les fichiers au CNC avant de les supprimer les fichiers.

Pour les envoyer au CNC il faudrait coder une fonction dans le ransomware qui envoie les fichiers en binaire et dans le CNC un fonction qui les écrit en binaire, et on aurait une copie des fichiers de la victime. 

Je m'amuserai donc à essayer cette fonctionnalité dans le futur.



## Questions

### Chiffrement

Q1) Le chiffrement utilisé dans le fichier xorcrypt.py est le chiffrement par flux, qui utilise la fonction XOR entre la clé de chiffrement et la donnée à chiffrer.

Ce chiffrement n'est pas très robuste, tout d'abord, car la clé est répétée, c'est à dire que si une partie de la clé est connue, alors on pourra déchiffrer plusieurs parties du fichier car la clé se répète. De plus, un changement de bit dans les données initiales, entraine un changement dudit bit dans les données chiffrées. Par conséquent, cela peut faciliter le décryptage des fichiers et la découverte de la clé.

<br>

### Génération des secrets

Q2) On n'utilise pas de fonction de hachage, car le hachage d'une donnée donne une empreinte et non une donnée chiffrée. Il existe des types d'attaques (attaque par dictionnaire, attaque par brute force et attaque par tables arc-en-ciel) permettant d'obtenir la même empreinte que celle obtenue en hachant les données. Par conséquent, le hachage n'est pas une méthode sécurisée pour stocker le sel ou la clé de chiffrement.

<br>

### Setup

Q3) Il est préférable de vérifier que le fichier token.bin existe déjà, car cela évite de supprimer le token déjà sauvegardé (token obtenu par dérivation de la clé de déchiffrement). Donc en écrasant le fichier token.bin, on rechiffrerait les fichiers, on rederiverait une nouvelle clé, et cela rendrait impossible le déchiffrement de ces derniers car on aurait perdu la précédente clé de déchiffrement.

<br>

### Vérifier et utiliser la clé

Q4) Pour vérifier et utiliser la clé, on dérive celle saisie par la victime (à l'aide du sel sauvegardé dans sel.bin) et si le token obtenu est identique à celui sauvegardé dans token.bin, alors la clé saisie est la bonne, et on peut déchiffrer les fichiers. 



### Bonus

B2) Casser le chiffrement par flux est plutôt simple. Pour ce faire, nous avons besoin de deux fichiers, un non chiffré et le même fichier chiffré. En effectuant un XOR entre ces deux fichiers, nous obtenons la clé de chiffrement (répétée). Et une fois avec la clé, on peut déchiffrer le reste des fichiers. 

<br>

"Démonstration : "

*fc = fichier chiffré*

*fnc = fichier non chiffré*

*clé = clé de chiffrement*

<br>

fc = fnc ^ clé

fc ^ fnc = fnc ^ clé ^ fnc

clé = fc ^ fnc
 
