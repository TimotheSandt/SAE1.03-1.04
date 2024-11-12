CREATE TABLE Individu(
   identifiant_individu COUNTER,
   nom VARCHAR(50),
   prénom VARCHAR(50),
   adresse VARCHAR(255),
   télephone VARCHAR(10),
   email VARCHAR(50),
   PRIMARY KEY(identifiant_individu)
);

CREATE TABLE Date_réservation(
   JJMMAAAA DATE,
   PRIMARY KEY(JJMMAAAA)
);

CREATE TABLE Pièce(
   code_pièce COUNTER,
   type_pièce VARCHAR(50),
   PRIMARY KEY(code_pièce)
);

CREATE TABLE Type_réparation(
   code_type_réparation COUNTER,
   libellé_type_réparation VARCHAR(50),
   PRIMARY KEY(code_type_réparation)
);

CREATE TABLE Etat(
   code_état COUNTER,
   libellé_état VARCHAR(50),
   PRIMARY KEY(code_état)
);

CREATE TABLE Catégorie_vélo(
   code_catégorie_vélo COUNTER,
   libellé_catégorie_vélo VARCHAR(50),
   PRIMARY KEY(code_catégorie_vélo)
);

CREATE TABLE Vélo(
   code_vélo COUNTER,
   libellé_vélo VARCHAR(50),
   code_catégorie_vélo INT NOT NULL,
   code_état INT NOT NULL,
   PRIMARY KEY(code_vélo),
   FOREIGN KEY(code_catégorie_vélo) REFERENCES Catégorie_vélo(code_catégorie_vélo),
   FOREIGN KEY(code_état) REFERENCES Etat(code_état)
);

CREATE TABLE Réparation(
   code_réparation COUNTER,
   date_réparation DATE,
   description TEXT,
   code_type_réparation INT NOT NULL,
   code_vélo INT NOT NULL,
   identifiant_individu INT NOT NULL,
   PRIMARY KEY(code_réparation),
   FOREIGN KEY(code_type_réparation) REFERENCES Type_réparation(code_type_réparation),
   FOREIGN KEY(code_vélo) REFERENCES Vélo(code_vélo),
   FOREIGN KEY(identifiant_individu) REFERENCES Individu(identifiant_individu)
);

CREATE TABLE loue(
   identifiant_individu_bailleur INT,
   identifiant_individu_locataire INT,
   code_vélo INT,
   JJMMAAAA DATE,
   durée INT,
   prix CURRENCY,
   PRIMARY KEY(identifiant_individu_bailleur, identifiant_individu_locataire, code_vélo, JJMMAAAA),
   FOREIGN KEY(identifiant_individu_bailleur) REFERENCES Individu(identifiant_individu),
   FOREIGN KEY(identifiant_individu_locataire) REFERENCES Individu(identifiant_individu),
   FOREIGN KEY(code_vélo) REFERENCES Vélo(code_vélo),
   FOREIGN KEY(JJMMAAAA) REFERENCES Date_réservation(JJMMAAAA)
);

CREATE TABLE utilise(
   code_pièce INT,
   code_réparation INT,
   date_utilisation DATE,
   quantité INT,
   PRIMARY KEY(code_pièce, code_réparation),
   FOREIGN KEY(code_pièce) REFERENCES Pièce(code_pièce),
   FOREIGN KEY(code_réparation) REFERENCES Réparation(code_réparation)
);
