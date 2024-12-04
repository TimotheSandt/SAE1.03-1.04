
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


INSERT INTO Velo (libelle_velo, prix, date_achat, code_categorie_velo, code_etat) 
VALUES ('Jean-pierre bike', 150, '2022-01-01', 1, 1),
      ('biket', 100, '2022-01-01', 2, 3),
      ('carglass', 50, '2022-01-01', 6, 5),
      ('velo', 100, '2022-01-01', 4, 5);


INSERT INTO Facture (prix_total)
VALUES (30.00),
      (34.00),
      (546.00),
      (150.00),
      (35.00),
      (65.00),
      (75.00),
      (121.00),
      (25.00);

INSERT INTO Reparation (date_reparation, duree_reparation, description_reparation, prix_main_d_oeuvre, id_facture, code_type_reparation, code_velo, id_individu) 
VALUES ('2022-01-01', 2, 'Changement de roue', 10.00, 1, 1, 1, 1),
      ('2024-07-08', 4, NULL, 50.00, 4, 5, 4, 2),
      ('2024-07-23', 1, NULL, 25.00, 5, 5, 4, 2);

INSERT INTO Utilise (code_piece, code_reparation, date_utilisation)
VALUES (2, 1, '2022-01-01'),
      (3, 1, '2022-01-01'),
      (17, 2, '2024-07-08'),
      (1, 3, '2024-07-23');

INSERT INTO Location (duree, date_location, id_facture, locataire, bailleur, code_velo)
VALUES (2, '2024-09-03', 2, 2, 5, 4),
      (90, '2025-01-01', 3, 3, 5, 2),
      (10, '2025-06-01', 6, 4, 5, 2),
      (15, '2025-06-05', 7, 5, 4, 1),
      (20, '2025-05-01', 8, 4, 5, 1),
      (3, '2025-05-05', 9, 5, 4, 3);
