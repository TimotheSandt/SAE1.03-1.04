-- SAE1.03-1.04
-- Groupe S1C2
-- Groupe SAE 22
--
-- SANDT Timothe - MIGUET Maxime - TALALI Zakaria

DROP TABLE IF EXISTS utilise;
DROP TABLE IF EXISTS loue;
DROP TABLE IF EXISTS Reparation;
DROP TABLE IF EXISTS Velo;
DROP TABLE IF EXISTS Categorie_velo;
DROP TABLE IF EXISTS Etat;
DROP TABLE IF EXISTS Type_reparation;
DROP TABLE IF EXISTS Piece;
DROP TABLE IF EXISTS Individu;



CREATE TABLE Individu(
   identifiant_individu INT AUTO_INCREMENT,
   nom VARCHAR(50),
   prenom VARCHAR(50),
   adresse VARCHAR(255),
   telephone VARCHAR(10),
   email VARCHAR(50),
   PRIMARY KEY(identifiant_individu)
);

CREATE TABLE Piece(
   code_piece INT AUTO_INCREMENT,
   type_piece VARCHAR(50),
   PRIMARY KEY(code_piece)
);

CREATE TABLE Type_reparation(
   code_type_reparation INT AUTO_INCREMENT,
   libelle_type_reparation VARCHAR(50),
   PRIMARY KEY(code_type_reparation)
);

CREATE TABLE Etat(
   code_etat INT AUTO_INCREMENT,
   libelle_etat VARCHAR(50),
   PRIMARY KEY(code_etat)
);

CREATE TABLE Categorie_velo(
   code_categorie_velo INT AUTO_INCREMENT,
   libelle_categorie_velo VARCHAR(50),
   PRIMARY KEY(code_categorie_velo)
);

CREATE TABLE Velo(
   code_velo INT AUTO_INCREMENT,
   libelle_velo VARCHAR(50),
   code_categorie_velo INT NOT NULL,
   code_etat INT NOT NULL,
   PRIMARY KEY(code_velo),
   FOREIGN KEY(code_categorie_velo) REFERENCES Categorie_velo(code_categorie_velo),
   FOREIGN KEY(code_etat) REFERENCES Etat(code_etat)
);

CREATE TABLE Reparation(
   code_reparation INT AUTO_INCREMENT,
   date_reparation DATE,
   duree_reparation INT,
   description_reparation TEXT,
   code_type_reparation INT NOT NULL,
   code_velo INT NOT NULL,
   identifiant_individu INT NOT NULL,
   PRIMARY KEY(code_reparation),
   FOREIGN KEY(code_type_reparation) REFERENCES Type_reparation(code_type_reparation),
   FOREIGN KEY(code_velo) REFERENCES Velo(code_velo),
   FOREIGN KEY(identifiant_individu) REFERENCES Individu(identifiant_individu)
);

CREATE TABLE loue(
   identifiant_individu_bailleur INT,
   identifiant_individu_locataire INT,
   code_velo INT,
   JJMMAAAA DATE,
   duree INT,
   prix DECIMAL(19,4),
   PRIMARY KEY(identifiant_individu_bailleur, identifiant_individu_locataire, code_velo, JJMMAAAA),
   FOREIGN KEY(identifiant_individu_bailleur) REFERENCES Individu(identifiant_individu),
   FOREIGN KEY(identifiant_individu_locataire) REFERENCES Individu(identifiant_individu),
   FOREIGN KEY(code_velo) REFERENCES Velo(code_velo)
);

CREATE TABLE utilise(
   code_piece INT,
   code_reparation INT,
   date_utilisation DATE,
   quantite INT,
   PRIMARY KEY(code_piece, code_reparation),
   FOREIGN KEY(code_piece) REFERENCES Piece(code_piece),
   FOREIGN KEY(code_reparation) REFERENCES Reparation(code_reparation)
);

SHOW TABLES;



-- Individu;
-- Piece;
-- Type_reparation;
-- Etat;
-- Categorie_velo;
-- Velo;
-- Reparation;
-- loue;
-- utilise;

INSERT INTO Individu (nom, prenom, adresse, telephone, email) 
VALUES ('TALALI', 'Zakaria', '10 rue de la paix', '0606060606', 'Z4R4p@example.com'),
      ('SANDT', 'Timothe', '11 rue de la paix', '0606060607', 'Z4R5p@example.com'),
      ('MIGUET', 'Maxime', '12 rue de la paix', '0606060608', 'Z4R6p@example.com'),
      ('DE CHEZ CARGLASS', 'Olivier', '13 rue de Carglass', '0310051515', 'carglass@carglass.com');


INSERT INTO Piece (type_piece) 
VALUES ('Roue'),
      ('Chaine'),
      ('Boulon'),
      ('Pédale'),
      ('Suspension'),
      ('Frein'),
      ('Batterie'),
      ('Moteur');


INSERT INTO Type_reparation (libelle_type_reparation) 
VALUES ('Crevaison'),
      ('Suspension'),
      ('Frein'),
      ('Pédalier'),
      ('Changement de batterie'),
      ('Entretien');


INSERT INTO Etat (libelle_etat)
VALUES ('Très mauvais'),
      ('Mauvais'),
      ('Moyen'),
      ('Bon'),
      ('Très bon'),
      ('Neuf');


INSERT INTO Categorie_velo (libelle_categorie_velo) 
VALUES ('VTT'),
      ('MTB'),
      ('BMX'),
      ('Vélo éléctrique'),
      ('Vélo de course'),
      ('Vélo de ville');


INSERT INTO Velo (libelle_velo, code_categorie_velo, code_etat) 
VALUES ('Jean-pierre bike', 1, 1),
      ('biket', 2, 3),
      ('carglass', 6, 5),
      ('velo', 4, 5);


INSERT INTO Reparation (date_reparation, duree_reparation, description_reparation, code_type_reparation, code_velo, identifiant_individu) 
VALUES ('2022-01-01', 1, NULL, 4, 1, 1),
      ('2022-02-02', 3, 'description', 2, 2, 2),
      ('2023-03-03', 1, 'description', 3, 2, 1),
      ('2024-04-04', 5, 'La batterie était mauvaise, elle a été remplacé', 5, 4, 4);

INSERT INTO loue (identifiant_individu_bailleur, identifiant_individu_locataire, code_velo, JJMMAAAA, duree, prix) 
VALUES (4, 2, 1, '2022-01-01', 1, 5.00),
      (4, 1, 4, '2023-01-01', 21, 130.00),
      (4, 4, 3, '2024-01-01', 31, 1500.00),
      (4, 3, 2, '2025-01-01', 354464, -5800.00);


INSERT INTO utilise (code_piece, code_reparation, date_utilisation, quantite) 
VALUES (4, 1, '2022-01-01', 2),
      (5, 2, '2022-02-02', 1),
      (6, 3, '2023-03-03', 2),
      (7, 4, '2024-04-04', 1);