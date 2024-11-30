
INSERT INTO Individu (nom, prenom, adresse, telephone, email) 
VALUES ('TALALI', 'Zakaria', '10 rue de la paix', '0606060606', 'Z4R4p@gmail.com'),
      ('SANDT', 'Timothe', '11 rue de la paix', '0606060607', 'Z4R5p@gmail.com'),
      ('MIGUET', 'Maxime', '12 rue de la paix', '0606060608', 'Z4R6p@yahoo.fr'),
      ('DE CHEZ CARGLASS', 'Olivier', '13 rue de Carglass', '0310051515', 'carglass@carglass.com'),
      ('DUPONT', 'Martin', '33 avenue des champs Elychgées', '0366662900', 'dupont.dupond@gmail.com');


INSERT INTO Type_piece (libelle_type_piece) 
VALUES ('Roue'),
      ('Chaine'),
      ('Boulon'),
      ('Pédale'),
      ('Suspension'),
      ('Frein'),
      ('Batterie'),
      ('Moteur');


INSERT INTO Piece (libelle_piece, code_type_piece) 
VALUES ('roue', 1),
      ('roue', 1),
      ('Boulon', 3),
      ('Boulon', 3),
      ('Frein', 6),
      ('Frein', 6),
      ('Frein', 6),
      ('Frein', 6),
      ('Pédale', 4),
      ('Pédale', 4),
      ('Chaine', 2),
      ('Batterie', 7);
      


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



INSERT INTO Utilise (code_piece, code_reparation, date_utilisation) 
VALUES (9, 1, '2022-01-01'),
      (10, 1, '2022-01-01'),
      (5, 3, '2023-03-03'),
      (12, 4, '2024-04-04');

