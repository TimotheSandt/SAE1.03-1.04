from flask import Flask, request, render_template, redirect, url_for, abort, flash
from flask import session, g
import pymysql.cursors

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

########### Location ###########

@app.route('/location/show', methods=['GET'])
def show_location():
    mycursor = get_db().cursor()
    sql =   ''' SELECT Location.ID_location AS ID, Location.prix, Location.date_location AS date, 
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


@app.route('/location/add', methods=['GET'])
def add_location():
    mycursor = get_db().cursor()
    sql =   ''' SELECT code_velo, libelle_velo
                FROM Velo
                ORDER BY libelle_velo;
            '''
    mycursor.execute(sql)
    velos = mycursor.fetchall()
    
    sql =   ''' SELECT id_individu AS ID, CONCAT(nom, ' ', prenom) AS nom_prenom
                FROM Individu;
            '''
    mycursor.execute(sql)
    individus = mycursor.fetchall()
    
    return render_template('location/add_location.html', velos=velos, individus=individus)


@app.route('/location/add', methods=['POST'])
def valid_add_location():
    prix = request.form['prix']
    date = request.form['date']
    duree = request.form['duree']
    locataire = request.form['locataire']
    bailleur = request.form['bailleur']
    velo = request.form['velo']
    
    mycursor = get_db().cursor()
    sql =   ''' INSERT INTO Location(prix, date_location, duree, locataire, bailleur, code_velo)
                VALUES (%s, %s, %s, %s, %s);
            '''
    values = (prix, date, duree, locataire, bailleur, velo)
    mycursor.execute(sql, values)
    get_db().commit()
    return redirect(url_for('show_location'))


@app.route('/location/edit/', methods=['GET'])
def edit_location():
    
    # recherche de la location
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql =   ''' SELECT ID_location AS ID, prix, date_location AS date, duree, locataire, bailleur, code_velo
                FROM Location
                WHERE ID = %s;
            '''
    values = (id)
    mycursor.execute(sql, values)
    location = mycursor.fetchone()
    
    # recherche des velos
    mycursor = get_db().cursor()
    sql =   ''' SELECT code_velo, libelle_velo
                FROM Velo
                ORDER BY libelle_velo;
            '''
    mycursor.execute(sql)
    velos = mycursor.fetchall()
    
    # recherche des individus
    sql =   ''' SELECT id_individu AS ID, CONCAT(nom, ' ', prenom) AS nom_prenom
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
    duree = request.form['duree']
    locataire = request.form['locataire']
    bailleur = request.form['bailleur']
    velo = request.form['velo']
    
    mycursor = get_db().cursor()
    sql =   ''' UPDATE Location
                SET prix = %s, date_location = %s, duree = %s, locataire = %s, bailleur = %s, code_velo = %s
                WHERE ID_location = %s;
            '''
    values = (prix, date, duree, locataire, bailleur, velo, id)
    mycursor.execute(sql, values)
    get_db().commit()
    return redirect(url_for('show_location'))

@app.route('/location/delete', methods=['POST'])
def delete_location():
    id = request.form['id']
    mycursor = get_db().cursor()
    sql =   ''' DELETE FROM Location
                WHERE ID_location = %s;
            '''
    values = (id)
    mycursor.execute(sql, values)
    get_db().commit()
    return redirect(url_for('show_location'))

########### Reparation ###########

@app.route('/reparation/show', methods=['GET'])
def show_reparation():
    mycursor = get_db().cursor()
    sql =   ''' SELECT reparation.code_reparation AS id, 
                       reparation.date_reparation AS date, 
                       reparation.duree_reparation AS duree,
                       reparation.description_reparation AS description,
                       reparation.prix_main_d_oeuvre AS prix, 
                       reparation.id_facture AS facture,
                       type_reparation.libelle_type_reparation AS type_reparation,
                       Velo.libelle_velo AS velo,
                       Individu.nom AS individu
                FROM reparation
                JOIN Velo ON reparation.code_velo = Velo.code_velo
                JOIN Individu ON reparation.id_individu = loc.id_individu
                JOIN type_reparation ON reparation.code_type_reparation = type_reparation.code_type_reparation
                ORDER BY date;   
            '''
    
    mycursor.execute(sql)

    reparations = mycursor.fetchall()
    return render_template('reparation/show_reparation.html', reparations=reparations)

########### Velo ###########




#####################

if __name__ == '__main__':
    app.run()
