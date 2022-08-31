import base64
import json
import os

from flask import Flask, jsonify, redirect, render_template, request
from flask_bootstrap import Bootstrap
from graphviz import Digraph, Graph
from neo4j import GraphDatabase

id = os.getenv('NEO4J_SECRET_KEY')
pwd = os.getenv('NEO4J_PW')

driver = GraphDatabase.driver(
    uri="neo4j+s://99ba1c1a.databases.neo4j.io", auth=(id, pwd)
)
session = driver.session()

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    def get_cat_breeds(tx):
        catquery = """
        MATCH (p:Pet) WHERE p.petSpecies = "Cat"
        WITH DISTINCT p.petBreed as breeds
        RETURN breeds ORDER BY breeds
        """
        results = tx.run(catquery)
        cat_list = [record[0] for record in results]
        return cat_list

    def get_dog_breeds(tx):
        dogquery = """
        MATCH (p:Pet) WHERE p.petSpecies = "Dog"
        WITH DISTINCT p.petBreed as breeds
        RETURN breeds ORDER BY breeds
        """
        results = tx.run(dogquery)
        dog_list = [record[0] for record in results]
        return dog_list

    def get_sitter_by_town(tx):
        query = """
        MATCH (p:Person)
        WITH DISTINCT p.personTown as towns
        RETURN towns ORDER BY towns SKIP 1
        """
        results = tx.run(query)
        town_list = [record[0] for record in results]
        return town_list

    def getpetsitters(tx):
        query = """
    MATCH (p:PetSitter)
    RETURN p.personName as personName, p.personAge as personAge, p.personJob as personJob, p.personTown as personTown, p.personLabels as personLabels
    ORDER BY personName
    """
        results = tx.run(query)
        graphs = []
        for result in results:
            dc = {}
            personName = result["personName"]
            personAge = result["personAge"]
            personTown = result["personTown"]
            personLabels = result["personLabels"]
            dc.update(
                {"personName": personName, "personAge": personAge, "personTown": personTown, "personLabels":personLabels}
            )
            graphs.append(dc)
        return graphs


    with driver.session() as session:
        allpets = session.read_transaction(getpetsitters)
        cat_list = session.read_transaction(get_cat_breeds)
        dog_list = session.read_transaction(get_dog_breeds)
        town_list = session.read_transaction(get_sitter_by_town)


    return render_template("home.html", cat_list=cat_list, dog_list=dog_list, allpets=allpets, town_list=town_list)
    session.close()

@app.route('/pets', methods = ['POST', 'GET'])
def breed_result():
    def get_cat_breeds(tx):
        catquery = """
        MATCH (p:Pet) WHERE p.petSpecies = "Cat"
        WITH DISTINCT p.petBreed as breeds
        RETURN breeds ORDER BY breeds
        """
        results = tx.run(catquery)
        cat_list = [record[0] for record in results]
        return cat_list

    def get_dog_breeds(tx):
        dogquery = """
        MATCH (p:Pet) WHERE p.petSpecies = "Dog"
        WITH DISTINCT p.petBreed as breeds
        RETURN breeds ORDER BY breeds
        """
        results = tx.run(dogquery)
        dog_list = [record[0] for record in results]
        return dog_list

    def get_all_pets(tx):
        query = """
        MATCH(a:Pet)
        return a.petName as petName, a.petAge as petAge, a.petSpecies as petSpecies, a.petBreed as petBreed, a.petImage as petImage
        """
        results = tx.run(query)
        all_pets = []
        for result in results:
            dc = {}
            name = result["petName"]
            age = result["petAge"]
            breed = result["petBreed"]
            species = result["petSpecies"]
            image = result["petImage"]
            dc.update(
                {"petName": name, "petSpecies": species, "petBreed": breed, "petAge": age, "petImage": image}
            )
            all_pets.append(dc)
        return all_pets

    def get_breed_result(tx):
       if request.method == 'POST':
          breed = request.form["breeds"]
          query = """
          MATCH(a:Pet{petBreed:$breed})
          return a.petName as petName, a.petAge as petAge, a.petSpecies as petSpecies, a.petBreed as petBreed, a.petImage as petImage
          """
          parameter = {"breed": breed}
          results = tx.run(query, parameter)
          filtered_pets = []
          for result in results:
              dc = {}
              name = result["petName"]
              age = result["petAge"]
              breed = result["petBreed"]
              species = result["petSpecies"]
              image = result["petImage"]
              dc.update(
                  {"petName": name, "petSpecies": species, "petBreed": breed, "petAge": age,  "petImage": image}
              )
              filtered_pets.append(dc)
          return filtered_pets

    def get_breed():
       if request.method == 'POST':
           breed = request.form["breeds"]
           return breed

    with driver.session() as session:
        cat_list = session.read_transaction(get_cat_breeds)
        dog_list = session.read_transaction(get_dog_breeds)
        all_pets = session.read_transaction(get_all_pets)
        filtered_pets = session.read_transaction(get_breed_result)
        breed = get_breed()
    return render_template("breed_result.html", cat_list=cat_list, dog_list=dog_list, breed=breed, all_pets=all_pets, filtered_pets=filtered_pets)
    session.close()



@app.route('/petsitters', methods = ['POST', 'GET'])
def town_result():
    def get_all_petsitters(tx):
        query = """
    MATCH (p:PetSitter)
    RETURN p.personName as personName, p.personAge as personAge, p.personJob as personJob, p.personTown as personTown, p.personLabels as personLabels
    ORDER BY personName
    """
        results = tx.run(query)
        graphs = []
        for result in results:
            dc = {}
            personName = result["personName"]
            personAge = result["personAge"]
            personTown = result["personTown"]
            personLabels = result["personLabels"]
            dc.update(
                {"personName": personName, "personAge": personAge, "personTown": personTown, "personLabels":personLabels}
            )
            graphs.append(dc)
        return graphs

    def get_sitter_by_town(tx):
        query = """
        MATCH (p:Person)
        WITH DISTINCT p.personTown as towns
        RETURN towns ORDER BY towns SKIP 1
        """
        results = tx.run(query)
        town_list = [record[0] for record in results]
        return town_list

    def get_town_results(tx):
       if request.method == 'POST':
          town = request.form["towns"]
          query = """
          MATCH(p:PetSitter{personTown:$town})
          RETURN p.personName as personName, p.personAge as personAge, p.personJob as personJob, p.personTown as personTown, p.personLabels as personLabels
          ORDER BY personName
          """
          parameter = {"town": town}
          results = tx.run(query, parameter)
          petsitters = []
          for result in results:
              dc = {}
              name = result["personName"]
              age = result["personAge"]
              job = result["personJob"]
              town = result["personTown"]
              labels = result["personLabels"]
              dc.update(
                  {"personName": name, "personAge": age, "personJob": job, "personTown": town, "personLabels": labels}
              )
              petsitters.append(dc)
          return petsitters

    def get_town(tx):
       if request.method == 'POST':
           town = request.form["towns"]
           return town

    with driver.session() as session:
        all_petsitters = session.read_transaction(get_all_petsitters)
        town_list = session.read_transaction(get_sitter_by_town)
        filtered_list = session.read_transaction(get_town_results)
        town = session.read_transaction(get_town)
    return render_template("town_result.html", all_petsitters=all_petsitters, town_list=town_list, filtered_list=filtered_list, town=town)
    session.close()


@app.route('/networks', methods = ['POST', 'GET'])
def paths():
    def get_pet_owners(tx):
        query = """
        MATCH (p:Person) where p.personLabels contains "PetOwner"
        WITH DISTINCT p.personName as petOwners
        RETURN petOwners ORDER BY petOwners
        """
        results = tx.run(query)
        pet_owner_list = [record[0] for record in results]
        return pet_owner_list

    def get_pet_sitters(tx):
        query = """
        MATCH (p:Person) where p.personLabels = "PetSitter"
        WITH DISTINCT p.personName as petSitters
        RETURN petSitters ORDER BY petSitters
        """
        results = tx.run(query)
        pet_sitter_list = [record[0] for record in results]
        return pet_sitter_list

    def get_path(tx):
       if request.method == 'POST':
          ownerName = request.form["pet_owners"]
          sitterName = request.form["pet_sitters"]
          query = """
            MATCH (p1:Person),(p2:Person),
            p = shortestPath((p1)-[*..15]-(p2))
            WHERE p1.personName = $p1 AND p2.personName = $p2
            UNWIND p AS x
            WITH DISTINCT x
            RETURN collect(x) AS setOfVals
          """
          parameters = {"p1": ownerName, "p2":sitterName}
          results = tx.run(query, parameters)
          data = results.data()[0]['setOfVals'][0]
          clean_data = [value for value in data if value != "knows"]
          chart_data = Digraph('path', node_attr={'shape': 'parallelogram'}, edge_attr={'arrowhead': 'vee'})
          l = []
          for count, item in enumerate(clean_data):
              name = item['personName']
              l.append(name)
              chart_data.node(name, name)
          for first, second in zip(l, l[1:]):
              chart_data.edge(first, second, label='knows')

          chart_output = chart_data.pipe(format='png')
          chart_output = base64.b64encode(chart_output).decode('utf-8')
          return chart_output


    with driver.session() as session:
        pet_owners = session.read_transaction(get_pet_owners)
        pet_sitters = session.read_transaction(get_pet_sitters)
        get_path = session.read_transaction(get_path)
    return render_template("path_result.html", pet_owners=pet_owners, pet_sitters=pet_sitters, get_path=get_path)
    session.close()


if __name__ == "__main__":
    app.run(port=5000, debug=True)
