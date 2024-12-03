from flask import Flask, request, render_template, redirect, url_for, abort, flash
from flask import session, g
import pymysql.cursors
from datetime import date

from dotenv import load_dotenv
import os

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = 'une cle(token) : grain de sel(any random string)'


load_dotenv()

app = Flask(__name__)
app.config.update(
    TEMPLATES_AUTO_RELOAD=True,
    DB_HOST=os.getenv("DB_HOST"),
    DB_USER=os.getenv("DB_USER"),
    DB_PASSWORD=os.getenv("DB_PASSWORD"),
    DB_NAME=os.getenv("DB_NAME")
)
app.secret_key = os.urandom(256)


def get_db():
    if 'db' not in g:
        g.db =  pymysql.connect(
            host=app.config["DB_HOST"],
            user=app.config["DB_USER"],
            password=app.config["DB_PASSWORD"],
            database=app.config["DB_NAME"],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        # à activer sur les machines personnelles :
        activate_db_options(g.db)
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def activate_db_options(db):
    cursor = db.cursor()
    # Vérifier et activer l'option ONLY_FULL_GROUP_BY si nécessaire
    cursor.execute("SHOW VARIABLES LIKE 'sql_mode'")
    result = cursor.fetchone()
    if result:
        modes = result['Value'].split(',')
        if 'ONLY_FULL_GROUP_BY' not in modes:
            print('MYSQL : il manque le mode ONLY_FULL_GROUP_BY')   # mettre en commentaire
            cursor.execute("SET sql_mode=(SELECT CONCAT(@@sql_mode, ',ONLY_FULL_GROUP_BY'))")
            db.commit()
        else:
            print('MYSQL : mode ONLY_FULL_GROUP_BY  ok')   # mettre en commentaire
    # Vérifier et activer l'option lower_case_table_names si nécessaire
    cursor.execute("SHOW VARIABLES LIKE 'lower_case_table_names'")
    result = cursor.fetchone()
    if result:
        if result['Value'] != '0':
            print('MYSQL : valeur de la variable globale lower_case_table_names differente de 0')   # mettre en commentaire
            cursor.execute("SET GLOBAL lower_case_table_names = 0")
            db.commit()
        else :
            print('MYSQL : variable globale lower_case_table_names=0  ok')    # mettre en commentaire
    cursor.close()



@app.route('/')
def show_accueil():
    return render_template('layout.html')

########### Individu ###########

@app.route('/compte/add', methods=['GET'])
def add_individu():
    return render_template('individu/add_individu.html')


@app.route('/compte/add', methods=['POST'])
def valid_add_individu():
    mycursor = get_db().cursor()
    sql =   ''' INSERT INTO Individu(nom, prenom, adresse, telephone, email)
                VALUES (%s, %s, %s, %s, %s);
            '''
    nom = request.form['nom']
    prenom = request.form['prénom']
    adresse = request.form['adresse']
    telephone = request.form['telephone']
    email = request.form['email']
    values = (nom, prenom, adresse, telephone, email)
    
    mycursor.execute(sql, values)
    get_db().commit()
    return redirect('/')

################################
########### Location ###########
################################

@app.route('/location/show', methods=['GET'])
def show_location():
    mycursor = get_db().cursor()
    sql =   ''' SELECT Location.id_location AS id, ROUND(Location.prix, 2) AS prix, 
                    Location.date_location AS date_debut, 
                    DATE_ADD(Location.date_location, INTERVAL Location.duree DAY) AS date_fin,
                    Velo.libelle_velo AS velo, 
                    CONCAT(loc.nom, ' ', loc.prenom) AS locataire,
                    CONCAT(bai.nom, ' ', bai.prenom) AS bailleur
                FROM Location
                JOIN Velo ON Location.code_velo = Velo.code_velo
                JOIN Individu AS loc ON Location.locataire = loc.id_individu
                JOIN Individu AS bai ON Location.bailleur = bai.id_individu
                ORDER BY date_location;
            '''
    mycursor.execute(sql)

    locations = mycursor.fetchall()
    return render_template('location/show_location.html', locations=locations)



def render_add_location(prix = None, date = None, duree = None, locataire = None, bailleur = None, velo = None):
    location = {
        'prix': prix,
        'date': date,
        'duree': duree,
        'locataire': locataire,
        'bailleur': bailleur,
        'code_velo': velo
    }
    
    mycursor = get_db().cursor()
    sql =   ''' SELECT code_velo, libelle_velo
                FROM Velo
                ORDER BY libelle_velo;
            '''
    mycursor.execute(sql)
    velos = mycursor.fetchall()
    
    sql =   ''' SELECT id_individu AS id, CONCAT(nom, ' ', prenom) AS nom_prenom
                FROM Individu;
            '''
    mycursor.execute(sql)
    individus = mycursor.fetchall()
    
    return render_template('location/add_location.html', velos=velos, individus=individus, location=location)

@app.route('/location/add', methods=['GET'])
def add_location():
    return render_add_location()


def check_date_conflict(velo, date, duree, id_location = None):
    ### recherche des conflits de dates
    mycursor = get_db().cursor()
    sql =   ''' SELECT id_location
                FROM Location
                WHERE (code_velo = %s) AND id_location != %s AND 
                        (
                            ( date_location BETWEEN %s AND DATE_ADD(%s, INTERVAL %s DAY) ) OR
                            ( DATE_ADD(date_location, INTERVAL duree DAY) BETWEEN %s AND DATE_ADD(%s, INTERVAL %s DAY) ) OR
                            ( %s BETWEEN date_location AND DATE_ADD(date_location, INTERVAL duree DAY) ) OR
                            ( DATE_ADD(%s, INTERVAL %s DAY) BETWEEN date_location AND DATE_ADD(date_location, INTERVAL duree DAY) )
                        );
            '''
    # dn = debut nouvelle location, fn = fin nouvelle location, d = debut location, f = fin location
    #
    # Condition de conflit
    #
    # f BETWEEN dn AND fn
    # d BETWEEN dn AND fn
    # dn BETWEEN d AND f
    # fn BETWEEN dn AND d
    
    values = (velo, id_location,
                date, date, duree,
                date, date, duree,
                date, 
                date, duree,            )
    mycursor.execute(sql, values)
    location = mycursor.fetchall()
    has_conflict = len(location) != 0
    return has_conflict

@app.route('/location/add', methods=['POST'])
def valid_add_location():
    prix = request.form['prix']
    date = request.form['date']
    duree = int(request.form['duree']) - 1
    locataire = request.form['locataire']
    bailleur = request.form['bailleur']
    velo = request.form['velo']
    
    
    
    
    if check_date_conflict(velo, date, duree):
        flash("Vélo indisponible durant la location", "danger")
        return render_add_location(prix, date, duree, locataire, bailleur, velo)
    
    
    ### Ajout de la facture
    mycursor = get_db().cursor()
    
    sql =   ''' INSERT INTO Facture(prix_total)
                VALUES (%s);
            '''
    values = (prix,)
    mycursor.execute(sql, values)
    get_db().commit()
    
    mycursor = get_db().cursor()
    sql =   ''' SELECT id_facture
                FROM Facture
                ORDER BY id_facture DESC
                LIMIT 1;
            '''
    mycursor.execute(sql)
    id_facture = mycursor.fetchone()['id_facture']
    
    ### Ajout de la location
    mycursor = get_db().cursor()
    sql =   ''' INSERT INTO Location(prix, date_location, duree, locataire, bailleur, code_velo, id_facture)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            '''
    values = (prix, date, duree, locataire, bailleur, velo, id_facture)
    mycursor.execute(sql, values)
    get_db().commit()
    return redirect(url_for('show_location'))


@app.route('/location/edit/', methods=['GET'])
def edit_location():
    
    # recherche de la location
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql =   ''' SELECT id_location AS id, prix, date_location AS date, duree + 1 AS duree, locataire, bailleur, code_velo, id_facture
                    FROM Location
                WHERE id_location = %s;
            '''
    values = (id,)
    mycursor.execute(sql, values)
    location = mycursor.fetchone()
    
    # recherche des velos
    # mycursor = get_db().cursor()
    sql =   ''' SELECT code_velo, libelle_velo
                FROM Velo
                ORDER BY libelle_velo;
            '''
    mycursor.execute(sql)
    velos = mycursor.fetchall()
    
    # recherche des individus
    sql =   ''' SELECT id_individu AS id, CONCAT(nom, ' ', prenom) AS nom_prenom
                FROM Individu
                ORDER BY nom_prenom;
            '''
    mycursor.execute(sql)
    individus = mycursor.fetchall()
    
    return render_template('location/edit_location.html', location=location, velos=velos, individus=individus)


@app.route('/location/edit', methods=['POST'])
def valid_edit_location():
    id = request.form['id']
    prix = request.form['prix']
    date = request.form['date']
    duree = int(request.form['duree']) - 1
    locataire = request.form['locataire']
    bailleur = request.form['bailleur']
    velo = request.form['velo']
    id_facture = request.form['facture']
    
    
    if check_date_conflict(velo, date, duree, id):
        flash("Vélo indisponible durant la location", "danger")
        return redirect(url_for('edit_location', id=id))
    
    
    ### Modification de la facture
    mycursor = get_db().cursor()
    sql =   ''' UPDATE Facture
                SET prix_total = %s
                WHERE id_facture = %s;
            '''
    values = (prix, id_facture)
    mycursor.execute(sql, values)
    get_db().commit()
    
    ### Modification de la location
    
    mycursor = get_db().cursor()
    sql =   ''' UPDATE Location
                SET prix = %s, date_location = %s, duree = %s, locataire = %s, bailleur = %s, code_velo = %s, id_facture = %s
                WHERE id_location = %s;
            '''
    values = (prix, date, duree, locataire, bailleur, velo, id_facture, id)
    mycursor.execute(sql, values)
    get_db().commit()
    return redirect(url_for('show_location'))

@app.route('/location/delete', methods=['GET'])
def delete_location():
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql =   ''' DELETE FROM Location
                WHERE id_location = %s;
            '''
    values = (id)
    mycursor.execute(sql, values)
    get_db().commit()
    return redirect(url_for('show_location'))

#####################
### État location ###
#####################

def get_individu():
    mycursor = get_db().cursor()
    sql =   ''' SELECT id_individu AS id, CONCAT(nom, ' ', prenom) AS nom_prenom
                FROM Individu
                ORDER BY nom_prenom;
            '''
    mycursor.execute(sql)
    individu = mycursor.fetchall()
    
    return individu


# à faire
def get_best_worst_individu(classification, type_individu):
    assert type_individu in ['locataire', 'bailleur'], "Type d'individu inconnu"
    
    if classification == 'pire':
        ordre = 'ASC'
    elif classification == 'best':
        ordre = 'DESC'
    else:
        raise ValueError("Classification inconnue")
    
    mycursor = get_db().cursor()
    sql =   f''' SELECT Individu.id_individu AS id, CONCAT(Individu.nom, ' ', Individu.prenom) AS nom_prenom, ROUND(SUM(Facture.prix_total), 2) AS montant
                FROM Location
                JOIN Individu ON Location.{type_individu} = Individu.id_individu
                JOIN Facture ON Location.id_facture = Facture.id_facture
                GROUP BY Individu.id_individu, Individu.nom, Individu.prenom
                ORDER BY montant {ordre}
                LIMIT 1;
            '''
    mycursor.execute(sql)
    return mycursor.fetchone()

def render_etat_location(id_individu):
    selection_individus = get_individu()
    
    # recherche de l'individu
    mycursor = get_db().cursor()
    sql =   ''' SELECT Individu.id_individu AS id, CONCAT(Individu.nom, ' ', Individu.prenom) AS nom_prenom
                FROM Individu
                WHERE Individu.id_individu = %s;
            '''
    values = (id_individu,)
    mycursor.execute(sql, values)
    individu = mycursor.fetchone()
    
    # recherche des bailleurs
    mycursor = get_db().cursor()
    sql =   ''' SELECT Individu.id_individu AS id, CONCAT(Individu.nom, ' ', Individu.prenom) AS nom_prenom, COUNT(Individu.id_individu) as nb, ROUND(SUM(Facture.prix_total), 2) AS montant
                FROM Location
                JOIN Individu ON Location.bailleur = Individu.id_individu
                JOIN Facture ON Location.id_facture = Facture.id_facture
                WHERE Location.locataire = %s
                GROUP BY Individu.id_individu, Individu.nom, Individu.prenom;
            '''
    values = (id_individu,)
    mycursor.execute(sql, values)
    bailleur_concerne = mycursor.fetchall()
    
    # recherche des locataires
    mycursor = get_db().cursor()
    sql =   ''' SELECT Individu.id_individu AS id, CONCAT(Individu.nom, ' ', Individu.prenom) AS nom_prenom, COUNT(Individu.id_individu) as nb, ROUND(SUM(Facture.prix_total), 2) AS montant
                FROM Location
                JOIN Individu ON Location.locataire = Individu.id_individu
                JOIN Facture ON Location.id_facture = Facture.id_facture
                WHERE Location.bailleur = %s
                GROUP BY Individu.id_individu, Individu.nom, Individu.prenom;
            '''
    values = (id_individu,)
    mycursor.execute(sql, values)
    locataire_concerne = mycursor.fetchall()
    
    # recherche des velos
    mycursor = get_db().cursor()
    sql =   ''' SELECT Velo.code_velo, Velo.libelle_velo, COUNT(Velo.code_velo) AS nb, SUM(Location.duree + 1) AS duree, ROUND(SUM(Facture.prix_total), 2) AS montant
                FROM Velo
                JOIN Location ON Velo.code_velo = Location.code_velo
                JOIN Facture ON Location.id_facture = Facture.id_facture
                WHERE Location.locataire = %s OR Location.bailleur = %s
                GROUP BY Velo.code_velo, Velo.libelle_velo
                ORDER BY nb DESC;
            '''
    values = (id_individu, id_individu)
    mycursor.execute(sql, values)
    velos_concerne = mycursor.fetchall()
    
    
    mycursor = get_db().cursor()
    sql =   ''' SELECT Location.id_location AS id, ROUND(Location.prix, 2) AS prix, 
                    Location.date_location AS date_debut, 
                    DATE_ADD(Location.date_location, INTERVAL Location.duree DAY) AS date_fin,
                    Velo.libelle_velo AS velo, 
                    CONCAT(bai.nom, ' ', bai.prenom) AS bailleur,
                    CONCAT(loc.nom, ' ', loc.prenom) AS locataire
                FROM Location
                JOIN Velo ON Location.code_velo = Velo.code_velo
                JOIN Individu AS bai ON Location.bailleur = bai.id_individu
                JOIN Individu AS loc ON Location.locataire = loc.id_individu
                WHERE Location.locataire = %s OR Location.bailleur = %s
                ORDER BY date_location;
            '''
    values = (id_individu, id_individu)
    mycursor.execute(sql, values)

    locations = mycursor.fetchall()
    
    
    # recherche  des statistiques
    mycursor = get_db().cursor()
    sql =   ''' SELECT ROUND(SUM(Facture.prix_total), 2) AS montant_total, COUNT(Location.id_location) AS nb, SUM(Location.duree + 1) AS duree_total
                FROM Location
                JOIN Facture ON Location.id_facture = Facture.id_facture
                WHERE Location.locataire = %s
                GROUP BY Location.locataire;
            '''
    values = (id_individu,)
    mycursor.execute(sql, values)
    stat_locataire = mycursor.fetchone()
    
    mycursor = get_db().cursor()
    sql =   ''' SELECT ROUND(SUM(Facture.prix_total), 2) AS montant_total, COUNT(Location.id_location) AS nb, SUM(Location.duree + 1) AS duree_total
                FROM Location
                JOIN Facture ON Location.id_facture = Facture.id_facture
                WHERE Location.bailleur = %s
                GROUP BY Location.bailleur;
            '''
    values = (id_individu,)
    mycursor.execute(sql, values)
    stat_bailleur = mycursor.fetchone()
    
    
    
    return render_template('location/etat_location.html', 
                           individu=individu,
                           selection_individus=selection_individus,
                           locataires=locataire_concerne, bailleurs=bailleur_concerne,
                           velos=velos_concerne, locations=locations, 
                           stat_locataire=stat_locataire, stat_bailleur=stat_bailleur)

@app.route('/location/etat/', methods=['GET'])
def show_etat_location():
    selection_individus = get_individu()
    return render_template('location/etat_location.html', selection_individus=selection_individus, individu=None)

@app.route('/location/etat/', methods=['POST'])
def valid_etat_location():
    individu = request.form.get('selection_individus')
    
    if individu is None:
        return redirect('/location/etat/')
    
    
    if individu == 'best_locataire':
        individu = get_best_worst_individu('best', 'locataire')
    elif individu == 'worst_locataire':
        individu = get_best_worst_individu('pire', 'locataire')
    elif individu == 'best_bailleur':
        individu = get_best_worst_individu('best', 'bailleur')
    elif individu == 'worst_bailleur':
        individu = get_best_worst_individu('pire', 'bailleur')
    
    print(individu)
    return render_etat_location(individu)

##################################
########### Réparation ###########
##################################

@app.route('/reparation/show', methods=['GET'])
def show_reparation():
    mycursor = get_db().cursor()
    sql =   ''' SELECT Reparation.code_reparation AS id, 
                       Reparation.date_reparation AS date, 
                       Reparation.duree_reparation AS duree,
                       Reparation.description_reparation AS description,
                       ROUND(Reparation.prix_main_d_oeuvre, 2) AS prix, 
                       ROUND(Facture.prix_total, 2) AS facture,
                       Type_reparation.libelle_type_reparation AS type_reparation,
                       Velo.libelle_velo AS velo,
                       CONCAT(Individu.prenom, ' ', Individu.nom) AS individu
                FROM Reparation
                JOIN Velo ON Reparation.code_velo = Velo.code_velo
                JOIN Individu ON Reparation.id_individu = Individu.id_individu
                JOIN Type_reparation ON Reparation.code_type_reparation = Type_reparation.code_type_reparation
                JOIN Facture ON Reparation.id_facture = Facture.id_facture
                ORDER BY date;   
            '''
    
    mycursor.execute(sql)

    reparations = mycursor.fetchall()
    return render_template('reparation/show_reparation.html', reparations=reparations)


def render_add_reparation(date = None, duree = None, description = None, prix = None, facture = None, type_reparation = None, velo = None, individu = None):
    reparation = {
        'date': date,
        'duree': duree,
        'description': description,
        'prix': prix,
        'facture': facture,
        'type_reparation': type_reparation,
        'code_velo': velo,
        'individu': individu
    }
    
    mycursor = get_db().cursor()
    sql =   ''' SELECT code_type_reparation, libelle_type_reparation
                FROM Type_reparation;
            '''
    mycursor.execute(sql)
    types_reparation = mycursor.fetchall()

    sql =   ''' SELECT code_velo, libelle_velo
                FROM Velo
                ORDER BY libelle_velo;
            '''
    mycursor.execute(sql)
    velos = mycursor.fetchall()
    
    sql =   ''' SELECT id_individu AS id, CONCAT(nom, ' ', prenom) AS nom_prenom
                FROM Individu;
            '''
    mycursor.execute(sql)
    individus = mycursor.fetchall()
    
    return render_template('reparation/add_reparation.html', velos=velos, individus=individus, reparation=reparation, types_reparation=types_reparation)


@app.route('/reparation/add', methods=['GET'])
def add_reparation():
    return render_add_reparation()



@app.route('/reparation/add', methods=['POST'])
def valid_add_reparation():
    date = request.form['date']
    duree = request.form['duree']
    description = request.form['description']
    prix = request.form['prix']
    type_reparation = request.form['type_reparation']
    velo = request.form['velo']
    individu = request.form['individu']
    # print("date :", date)
    # print("duree :", duree)
    # print("description :", description)
    # print("type_reparation :", type_reparation)
    # print("velo :", velo)
    # print("individu :", individu)

    ### Ajout de la facture
    mycursor = get_db().cursor()
    
    sql =   ''' INSERT INTO Facture(prix_total)
                VALUES (%s);
            '''
    values = (prix,)
    mycursor.execute(sql, values)
    get_db().commit()
    
    mycursor = get_db().cursor()
    sql =   ''' SELECT id_facture
                FROM Facture
                ORDER BY id_facture DESC
                LIMIT 1;
            '''
    mycursor.execute(sql)
    facture = mycursor.fetchone()['id_facture']
    
    ### Ajout de la réparation
    mycursor = get_db().cursor()
    sql =   ''' INSERT INTO Reparation(date_reparation, duree_reparation,
                                       description_reparation, prix_main_d_oeuvre, 
                                       id_facture, code_type_reparation, 
                                       code_velo, id_individu)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            '''
    values = (date, duree, description, prix, facture, type_reparation, velo, individu)
    mycursor.execute(sql, values)
    get_db().commit()
    return redirect(url_for('show_reparation'))


@app.route('/reparation/edit/', methods=['GET'])
def edit_reparation():
    
    # recherche de la réparation
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql =   ''' SELECT code_reparation AS id, 
                       date_reparation AS date, 
                       duree_reparation + 1 AS duree, 
                       description_reparation AS description, 
                       prix_main_d_oeuvre AS prix, 
                       id_facture,
                       code_type_reparation,
                       code_velo, 
                       id_individu
                FROM Reparation
                WHERE code_reparation = %s;
            '''
    values = (id,)
    mycursor.execute(sql, values)
    reparation = mycursor.fetchone()
    
    # recherche des velos
    sql =   ''' SELECT code_velo, libelle_velo
                FROM Velo
                ORDER BY libelle_velo;
            '''
    mycursor.execute(sql)
    velos = mycursor.fetchall()
    
    # recherche des individus
    sql =   ''' SELECT id_individu AS id, CONCAT(nom, ' ', prenom) AS nom_prenom
                FROM Individu
                ORDER BY nom_prenom;
            '''
    mycursor.execute(sql)
    individus = mycursor.fetchall()
    
    # recherche des types de réparation
    sql =   ''' SELECT code_type_reparation, libelle_type_reparation
                FROM Type_reparation;
            '''
    mycursor.execute(sql)
    types_reparation = mycursor.fetchall()
    
    return render_template('reparation/edit_reparation.html', reparation=reparation, velos=velos, individus=individus, types_reparation=types_reparation)


@app.route('/reparation/edit', methods=['POST'])
def valid_edit_reparation():
    id = request.form['id']
    date = request.form['date']
    duree = int(request.form['duree']) - 1
    description = request.form['description']
    prix = request.form['prix']
    id_facture = request.form['facture']
    type_reparation = request.form['type_reparation']
    velo = request.form['velo']
    individu = request.form['individu']
    
    
    ### Modification de la facture
    mycursor = get_db().cursor()
    sql =   ''' UPDATE Facture
                SET prix_total = %s
                WHERE id_facture = %s;
            '''
    values = (prix, id_facture)
    mycursor.execute(sql, values)
    get_db().commit()
    
    
    ### Modification de la réparation
    mycursor = get_db().cursor()
    sql =   ''' UPDATE Reparation
                SET date_reparation = %s,
                    duree_reparation = %s,
                    description_reparation = %s,
                    prix_main_d_oeuvre = %s,
                    id_facture = %s,
                    code_type_reparation = %s,
                    code_velo = %s,
                    id_individu = %s
                WHERE code_reparation = %s;
            ''' 
            
    values = (date, duree, description, prix, id_facture, type_reparation, velo, individu, id)
    mycursor.execute(sql, values)
    get_db().commit()
    return redirect(url_for('show_reparation'))


@app.route('/reparation/delete', methods=['GET'])
def delete_reparation():
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql =   ''' DELETE FROM Reparation
                WHERE code_reparation = %s;
            '''
    values = (id)
    mycursor.execute(sql, values)
    get_db().commit()
    return redirect(url_for('show_reparation'))

#######################
### État réparation ###
#######################


def render_etat_reparation(id_individu):
    selection_individus = get_individu()
    
    # recherche de l'individu
    mycursor = get_db().cursor()
    sql =   ''' SELECT Individu.id_individu AS id, CONCAT(Individu.nom, ' ', Individu.prenom) AS nom_prenom
                FROM Individu
                WHERE Individu.id_individu = %s;
            '''
    values = (id_individu,)
    mycursor.execute(sql, values)
    individus = mycursor.fetchone()
    
    # recherche des types de réparation
    mycursor = get_db().cursor()
    sql =   ''' SELECT Type_reparation.code_type_reparation, Type_reparation.libelle_type_reparation
                FROM Type_reparation
                WHERE Type_reparation.code_type_reparation = %s
            '''
    values = (id_individu,)
    mycursor.execute(sql, values)
    type_reparation_concerne = mycursor.fetchall()
    
    # recherche des velos
    mycursor = get_db().cursor()
    sql =   ''' SELECT Velo.code_velo, Velo.libelle_velo, COUNT(Velo.code_velo) AS nb, SUM(Location.duree + 1) AS duree, ROUND(SUM(Facture.prix_total), 2) AS montant
                FROM Velo
                JOIN Location ON Velo.code_velo = Location.code_velo
                JOIN Facture ON Location.id_facture = Facture.id_facture
                WHERE Location.locataire = %s OR Location.bailleur = %s
                GROUP BY Velo.code_velo, Velo.libelle_velo
                ORDER BY nb DESC;
            '''
    values = (id_individu, id_individu)
    mycursor.execute(sql, values)
    velos_concerne = mycursor.fetchall()
    
    # recherche des réparations
    
    mycursor = get_db().cursor()
    sql =   ''' SELECT Reparation.code_reparation, 
                       Reparation.date_reparation AS date_debut, 
                       Reparation.duree_reparation AS duree, 
                       Reparation.description_reparation AS description, 
                       ROUND(Reparation.prix_main_d_oeuvre, 2) AS prix, 
                       ROUND(Facture.prix_total, 2) AS facture, 
                       Type_reparation.libelle_type_reparation AS type_reparation, 
                       Velo.libelle_velo AS velo, 
                       CONCAT(Individu.prenom, ' ', Individu.nom) AS individu
                FROM Reparation
                JOIN Type_reparation ON Reparation.code_type_reparation = Type_reparation.code_type_reparation
                JOIN Velo ON Reparation.code_velo = Velo.code_velo
                JOIN Individu ON Reparation.id_individu = Individu.id_individu
                JOIN Facture ON Reparation.id_facture = Facture.id_facture
                WHERE Reparation.id_individu = %s
                ORDER BY date_reparation;
            '''
    values = (id_individu, )
    mycursor.execute(sql, values)

    reparations = mycursor.fetchall()
    
    
    # recherche  des statistiques
    mycursor = get_db().cursor()
    sql =   ''' SELECT ROUND(SUM(Facture.prix_total), 2) AS montant_total, COUNT(Reparation.code_reparation) AS nb, SUM(Reparation.duree_reparation + 1) AS duree_total
                FROM Reparation
                JOIN Facture ON Reparation.id_facture = Facture.id_facture
                WHERE Reparation.id_individu = %s
                GROUP BY Reparation.id_individu;
            '''
    values = (id_individu,)
    mycursor.execute(sql, values)
    stat_reparations = mycursor.fetchone()
    
    
    
    return render_template('reparation/etat_reparation.html', 
                           individus=individus,
                           selection_individus=selection_individus,
                           type_reparation_concerne=type_reparation_concerne, 
                           velos_concerne=velos_concerne,
                           reparations=reparations,
                           stat_reparations=stat_reparations,)



@app.route('/reparation/etat/', methods=['GET'])
def show_etat_reparation():
    selection_individus = get_individu()
    return render_template('reparation/etat_reparation.html', selection_individus=selection_individus, individu=None)


@app.route('/reparation/etat/', methods=['POST'])
def valid_etat_reparation():
    individu = request.form.get('selection_individus')
    
    if individu is None:
        return redirect('/reparation/etat/')
    
    return render_etat_reparation(individu)


############################
########### Velo ###########
############################

@app.route('/velo/show', methods=['GET'])
def show_velo():
    mycursor = get_db().cursor()
    sql = '''
        SELECT Velo.code_velo AS id, Velo.libelle_velo, ROUND(Velo.prix, 2) AS prix, Velo.date_achat,
               Categorie_velo.libelle_categorie_velo AS categorie,
               Etat.libelle_etat AS etat
        FROM Velo
        JOIN Categorie_velo ON Velo.code_categorie_velo = Categorie_velo.code_categorie_velo
        JOIN Etat ON Velo.code_etat = Etat.code_etat
        ORDER BY Velo.libelle_velo;
    '''
    mycursor.execute(sql)
    velos = mycursor.fetchall()
    return render_template('velo/show_velo.html', velos=velos)

@app.route('/velo/add', methods=['GET'])
def add_velo():
    mycursor = get_db().cursor()
    sql_categorie = "SELECT code_categorie_velo, libelle_categorie_velo FROM Categorie_velo;"
    sql_etat = "SELECT code_etat, libelle_etat FROM Etat;"
    mycursor.execute(sql_categorie)
    categories = mycursor.fetchall()
    mycursor.execute(sql_etat)
    etats = mycursor.fetchall()
    return render_template('velo/add_velo.html', categories=categories, etats=etats)

@app.route('/velo/add', methods=['POST'])
def valid_add_velo():
    libelle_velo = request.form['libelle_velo']
    prix = request.form['prix']
    date_achat = request.form['date_achat']
    code_categorie_velo = request.form['code_categorie_velo']
    code_etat = request.form['code_etat']
    
    mycursor = get_db().cursor()
    sql = '''
        INSERT INTO Velo (libelle_velo, prix, date_achat, code_categorie_velo, code_etat)
        VALUES (%s, %s, %s, %s, %s);
    '''
    values = (libelle_velo, prix, date_achat, code_categorie_velo, code_etat)
    mycursor.execute(sql, values)
    get_db().commit()
    flash("Vélo ajouté avec succès !", "success")
    return redirect(url_for('show_velo'))

@app.route('/velo/edit', methods=['GET'])
def edit_velo():
    id = request.args.get('id')
    mycursor = get_db().cursor()

    sql_velo = "SELECT * FROM Velo WHERE code_velo = %s;"
    mycursor.execute(sql_velo, (id,))
    velo = mycursor.fetchone()

    sql_categorie = "SELECT code_categorie_velo, libelle_categorie_velo FROM Categorie_velo;"
    mycursor.execute(sql_categorie)
    categories = mycursor.fetchall()

    sql_etat = "SELECT code_etat, libelle_etat FROM Etat;"
    mycursor.execute(sql_etat)
    etats = mycursor.fetchall()

    return render_template('velo/edit_velo.html', velo=velo, categories=categories, etats=etats)

@app.route('/velo/edit', methods=['POST'])
def valid_edit_velo():
    id = request.form['id']
    libelle_velo = request.form['libelle_velo']
    prix = request.form['prix']
    date_achat = request.form['date_achat']
    code_categorie_velo = request.form['code_categorie_velo']
    code_etat = request.form['code_etat']

    mycursor = get_db().cursor()
    sql = '''
        UPDATE Velo
        SET libelle_velo = %s, prix = %s, date_achat = %s, 
            code_categorie_velo = %s, code_etat = %s
        WHERE code_velo = %s;
    '''
    values = (libelle_velo, prix, date_achat, code_categorie_velo, code_etat, id)
    mycursor.execute(sql, values)
    get_db().commit()
    flash("Vélo modifié avec succès !", "success")
    return redirect(url_for('show_velo'))

@app.route('/velo/delete', methods=['GET'])
def delete_velo():
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql = '''DELETE FROM Velo
             WHERE code_velo = %s;'''
    values = (id)  
    mycursor.execute(sql, values)
    get_db().commit()
    flash("Vélo supprimé avec succès !", "success")
    return redirect(url_for('show_velo'))


def render_etat_velo(id_velo):
    selection_velos = get_velos()

    mycursor = get_db().cursor()
    sql = '''
        SELECT Velo.code_velo, Velo.libelle_velo, 
               Categorie_velo.libelle_categorie_velo AS categorie,
               Etat.libelle_etat AS etat
        FROM Velo
        JOIN Categorie_velo ON Velo.code_categorie_velo = Categorie_velo.code_categorie_velo
        JOIN Etat ON Velo.code_etat = Etat.code_etat
        WHERE Velo.code_velo = %s;
    '''
    values = (id_velo,)
    mycursor.execute(sql, values)
    velo = mycursor.fetchone()

    sql = '''
        SELECT Location.id_location AS id, ROUND(Location.prix, 2) AS prix,
               Location.date_location AS date_debut, 
               DATE_ADD(Location.date_location, INTERVAL Location.duree DAY) AS date_fin,
               CONCAT(loc.nom, ' ', loc.prenom) AS locataire,
               CONCAT(bai.nom, ' ', bai.prenom) AS bailleur
        FROM Location
        JOIN Individu AS loc ON Location.locataire = loc.id_individu
        JOIN Individu AS bai ON Location.bailleur = bai.id_individu
        WHERE Location.code_velo = %s
        ORDER BY Location.date_location;
    '''
    mycursor.execute(sql, values)
    locations = mycursor.fetchall()

    sql = '''
        SELECT ROUND(SUM(Location.prix), 2) AS montant_total,
               COUNT(Location.id_location) AS nb_locations,
               SUM(Location.duree) AS duree_totale
        FROM Location
        WHERE Location.code_velo = %s
        GROUP BY Location.code_velo;
    '''
    mycursor.execute(sql, values)
    stats = mycursor.fetchone()

    return render_template(
        'velo/etat_velo.html',
        velo=velo,
        selection_velos=selection_velos,
        locations=locations,
        stats=stats
    )

@app.route('/velo/etat/', methods=['GET'])
def show_etat_velo():
    selection_velos = get_velos()
    return render_template('velo/etat_velo.html', selection_velos=selection_velos, velo=None)

@app.route('/velo/etat/', methods=['POST'])
def valid_etat_velo():
    id_velo = request.form.get('selection_velo')

    if id_velo is None:
        return redirect('/velo/etat/')

    return render_etat_velo(id_velo)

def get_velos():
    mycursor = get_db().cursor()
    sql = ''' SELECT code_velo, libelle_velo FROM Velo ORDER BY libelle_velo; '''
    mycursor.execute(sql)
    return mycursor.fetchall()


#####################

if __name__ == '__main__':
    app.run()
