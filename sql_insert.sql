
INSERT INTO Individu (nom, prenom, adresse, telephone, email) 
VALUES ('TALALI', 'Zakaria', '10 rue de la paix', '0606060606', 'Z4R4p@gmail.com'),
      ('SANDT', 'Timothe', '11 rue de la paix', '0606060607', 'Z4R5p@gmail.com'),
      ('MIGUET', 'Maxime', '12 rue de la paix', '0606060608', 'Z4R6p@yahoo.fr'),
      ('DE CHEZ CARGLASS', 'Olivier', '13 rue de Carglass', '0310051515', 'carglass@carglass.com'),
      ('DUPONT', 'Martin', '33 avenue des champs Elychgées', '0366662900', 'dupont.dupond@gmail.com');



INSERT INTO Piece (type_piece, prix) 
VALUES ('roue', 10.00),
      ('roue', 10.00),
      ('roue', 10.00),
      ('roue', 10.00),
      ('boulon', 5.00),
      ('boulon', 5.00),
      ('boulon', 5.00),
      ('boulon', 5.00),
      ('frein', 20.00),
      ('frein', 20.00),
      ('frein', 20.00),
      ('pedale', 15.00),
      ('pedale', 15.00),
      ('pedale', 15.00),
      ('suspension', 50.00),
      ('suspension', 50.00),
      ('batterie', 100.00),
      ('moteur', 200.00);
      


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



