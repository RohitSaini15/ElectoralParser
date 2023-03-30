import csv
import json
from normalization import get_normalized_name
import argparse
import os
from helper import create_path

ELECTORAL_ID = 0
ELECTORAL_NAME = 1
RELATION_NAME = 2
RELATION_TYPE = 3
HOUSE_NO = 4
AGE = 5
GENDER = 6
ADDRESS = 7
MAIN_TOWN = 8
DISTRICT = 9

def create_person(name,id=None,house_no = None,district = None,gender = None,age = None,address = None,main_town = None):
    person = {
        "card_number": id,
        "name": name,
        "house_no": house_no,
        "district": district,
        "gender": gender,
        "age": age,
        "address": address,
        "village": main_town,
        "koot_falan": get_normalized_name(name)
    }

    return person

# id,electoral_name,father_or_husband_name,relationship,house_no,age,gender,address,main_town,district

def create_family_json(familys,visit,start_id):
    house_no = familys[start_id][HOUSE_NO]
    print(f"processing house no {house_no}")
    name = []
    id = start_id

    if len(house_no.strip()) == 0:
        return []

    while id < len(familys) and familys[id][HOUSE_NO] == house_no:
        visit[id] = True
        normalized_name = get_normalized_name(familys[id][ELECTORAL_NAME])
        if normalized_name:
            name.append(normalized_name)
        id+=1
    
    q = []
    temp_q = []
    id = start_id

    while id < len(familys) and familys[id][HOUSE_NO] == house_no:
        normalized_relation_name = get_normalized_name(familys[id][RELATION_NAME])
        if normalized_relation_name and  normalized_relation_name not in name and normalized_relation_name not in temp_q:
            temp_q.append(get_normalized_name(normalized_relation_name))
            person = create_person(name = familys[id][RELATION_NAME],
                                   district = familys[id][DISTRICT],
                                   main_town = familys[id][MAIN_TOWN],
                                   address = familys[id][ADDRESS])
            q.append(person)
        id+=1
    pos = 0
    no_of_familys = len(q)

    q_visited = {}

    while pos<len(q):
        cur_person = q[pos]
        id = start_id
        while id < len(familys) and familys[id][HOUSE_NO] == house_no:
            
            if get_normalized_name(familys[id][RELATION_NAME]) == get_normalized_name(cur_person["name"]):

                # if q_visited.get(id):
                #     id+=1
                #     continue

                if not get_normalized_name(familys[id][ELECTORAL_NAME]):
                    id+=1
                    continue

                relation_type = familys[id][RELATION_TYPE]
                if relation_type == "husband":
                    # name,id,house_no,district,gender,age,address,main_town
                    spouse = create_person(name = familys[id][ELECTORAL_NAME],
                                           id = familys[id][ELECTORAL_ID],
                                           house_no = familys[id][HOUSE_NO],
                                           district = familys[id][DISTRICT],
                                           gender = familys[id][GENDER],
                                           age = familys[id][AGE],
                                           address = familys[id][ADDRESS],
                                           main_town = familys[id][MAIN_TOWN])
                    cur_person["spouse"] = spouse
                elif relation_type == "father":
                    if not cur_person.get("children"):
                        cur_person["children"] = []
                    child = create_person(name = familys[id][ELECTORAL_NAME],
                                           id = familys[id][ELECTORAL_ID],
                                           house_no = familys[id][HOUSE_NO],
                                           district = familys[id][DISTRICT],
                                           gender = familys[id][GENDER],
                                           age = familys[id][AGE],
                                           address = familys[id][ADDRESS],
                                           main_town = familys[id][MAIN_TOWN])

                    cur_person["children"].append(child)
                    q.append(child)
                
                # q_visited[id] = True
            id+=1
        pos+=1
    
    familys_json = []
    for i in range(no_of_familys):
        familys_json.append(q[i])

    return familys_json

def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputcsv",help = "path of the csv file",required = True)
    args = parser.parse_args()

    csv_file_path = args.inputcsv
    
    familys = []

    with open(csv_file_path,"r",encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            familys.append(row)
    
    visit = [False]*(len(familys))

    familys_json = []

    for id in range(len(visit)):
        if not visit[id]:
            familys_json.extend(create_family_json(familys,visit,id))
    
    json_file_name = os.path.basename(csv_file_path).replace(".csv",".json")
    family_json_folder = "family_json/"

    create_path(family_json_folder)

    with open(os.path.join(family_json_folder,json_file_name),"w",encoding="utf-8") as f:
        data = json.dumps(familys_json)
        f.write(data)

if __name__ == "__main__":
    main()