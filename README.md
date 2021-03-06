# Automatisation MPLS et MPLSVPN

  # 1. Objectif de script
L'objectif de ce script est d'automatiser la génération de configuration MPLS et MPLS VPN pour une architecture réseau GNS3.
Pour ce faire, nous avons opté pour une solution pas nécessairement optimale dans le sens où ce n'est pas ce qui se fait en entreprise mais cette solution convient parfaitement aux erchitecture réseau GNS3.
Le script permet de générer les configurations des routeurs sur base de description de la topologie, puis de les pousser respectivement dans les bons fichiers du projet GNS3.
  # 2. Fonctionnement
Le scprit est pour l'instant composé de 5 principaux fichiers.
- **generateConfigFile.py** : Permet la génération des fichiers de configuration
- **main.py** : est le point d'entrée du script
- **cfg.py** : Permet de définir l'ensemble des constantes nécessaire au fonctionnement su programme (AS, PROJECT_DIR)
- **utils.py**: Définition de fonction utilitaires
- **data.v2.json** : Définition de notre topologie GNS3 sous format json
  # 3. Lancement
Pour le lancement du script, il est  nécessaire de:
- Créer votre topologie GNS3
- Définir votre topologie GNS3 dans le fichier data.json
- Dans le fichier cfg.py, définir le chemin du projet et le numéro d'AS de votre réseau de coeur

Il y'a deux principales options pour lancer le script:
- **reset** : Permet de remettre les routeurs dans leurs configurations initiales
- **deploy** : Permet de deployer l'ensemble des configurations pour les routeurs déclarés et leurs configurations déclarées dans le data.json
