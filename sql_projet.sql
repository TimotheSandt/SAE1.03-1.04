-- SAE1.03-1.04
-- Groupe S1C2
-- Groupe SAE 22
--
-- SANDT Timothe - MIGUET Maxime - TALALI Zakaria

DROP TABLE IF EXISTS Utilise;
DROP TABLE IF EXISTS Location;
DROP TABLE IF EXISTS Reparation;
DROP TABLE IF EXISTS Velo;
DROP TABLE IF EXISTS Facture;
DROP TABLE IF EXISTS Categorie_velo;
DROP TABLE IF EXISTS Etat;
DROP TABLE IF EXISTS Type_reparation;
DROP TABLE IF EXISTS Piece;
DROP TABLE IF EXISTS Individu;


CREATE TABLE Individu(
   id_individu INT AUTO_INCREMENT,
   nom VARCHAR(50),
   prenom VARCHAR(50),
   adresse VARCHAR(255),
   telephone VARCHAR(10),
   email VARCHAR(50),
   PRIMARY KEY(id_individu)
);

CREATE TABLE Piece(
   code_piece INT AUTO_INCREMENT,
   type_piece VARCHAR(50),
   prix DECIMAL(19,4),
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

CREATE TABLE Facture(
   id_facture INT AUTO_INCREMENT,
   prix_total DECIMAL(19,4),
   PRIMARY KEY(id_facture)
);

CREATE TABLE Velo(
   code_velo INT AUTO_INCREMENT,
   libelle_velo VARCHAR(50),
   prix DECIMAL(19,4),
   date_achat DATE,
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
   prix_main_d_oeuvre DECIMAL(19,4),
   id_facture INT NOT NULL,
   code_type_reparation INT NOT NULL,
   code_velo INT NOT NULL,
   id_individu INT NOT NULL,
   PRIMARY KEY(code_reparation),
   FOREIGN KEY(id_facture) REFERENCES Facture(id_facture),
   FOREIGN KEY(code_type_reparation) REFERENCES Type_reparation(code_type_reparation),
   FOREIGN KEY(code_velo) REFERENCES Velo(code_velo),
   FOREIGN KEY(id_individu) REFERENCES Individu(id_individu)
);

CREATE TABLE Location(
   ID_location INT AUTO_INCREMENT,
   prix DECIMAL(19,4),
   duree INT,
   date_location DATE,
   id_facture INT NOT NULL,
   locataire INT NOT NULL,
   bailleur INT NOT NULL,
   code_velo INT NOT NULL,
   PRIMARY KEY(ID_location),
   FOREIGN KEY(id_facture) REFERENCES Facture(id_facture),
   FOREIGN KEY(locataire) REFERENCES Individu(id_individu),
   FOREIGN KEY(bailleur) REFERENCES Individu(id_individu),
   FOREIGN KEY(code_velo) REFERENCES Velo(code_velo)
);

CREATE TABLE Utilise(
   code_piece INT,
   code_reparation INT,
   date_utilisation DATE,
   quantite INT,
   PRIMARY KEY(code_piece, code_reparation),
   FOREIGN KEY(code_piece) REFERENCES Piece(code_piece),
   FOREIGN KEY(code_reparation) REFERENCES Reparation(code_reparation)
);
