#!/usr/bin/python2.7
# -*- coding: latin-1 -*-

from content_based_info import *
from online_mode import *
import sqlite3
import time


items = {}
users = {}


def batch_training(mode_input):

    if mode_input != 'ask':
        file_name = mode_input
    else:
        file_name = raw_input("File name: ")

    items_bd, users_bd = get_dictionaries(file_name)

    db = sqlite3.connect('mydb')
    cursor = db.cursor()
    cursor.execute('''DROP TABLE IF EXISTS items''')

    cursor.execute('''CREATE TABLE items(item_id INTEGER, user_id INTEGER, rating INTEGER)''')

    for item in items_bd:
        for user in items_bd[item]:
            cmd = """INSERT INTO items(item_id, user_id, rating) VALUES("%d", "%d", "%d")""" % (item, user, items_bd[item][user])
            cursor.execute(cmd)

    db.commit()

    cursor.close()
    db.close()


#Opens file 'file_name' (u1.base for ex.) and fills 2 dictionaries: one indexed by user_id
#and the other by item_id (these are redundant with each other, they just facilitate search);
#Returns items_dict: <item_id : < user_id : rating >> and users <user_id : <item_id : rating>>
def get_dictionaries(file_name):
    try:
        f = open(file_name, 'r')

        items_dict = {}  #dictionary of dictionaries
        users_dict = {}  #especially useful for the score avg by user

        for line in f:

            array = line.split('\t')

            user_id = array[0]
            item_id = array[1]
            rating = array[2]
            #if the user didnt exist, we need to create the items dictionary for that user
            if int(user_id) not in users.keys():
                users_dict[int(user_id)] = {}
            #adds the rating for an item for that user
            users_dict[int(user_id)][int(item_id)] = int(rating)

            #if the item didnt exist, we need to create the users dictionary for that item
            if int(item_id) not in items_dict.keys():
                items_dict[int(item_id)] = {}
            #saves the rating the user gave to this item
            items_dict[int(item_id)][int(user_id)] = int(rating)

        return items_dict, users_dict
    except IOError:
        print "No file with that name!"
        return None, None


def fill_dicts_from_DB():

    global items
    global users

    items = {}
    users = {}

    db = sqlite3.connect('mydb')
    cursor = db.cursor()

    cmd = "SELECT * FROM items"
    cursor.execute(cmd)
    results = cursor.fetchall()
    for item in results:
        if int(item[0]) not in items.keys():
            items[int(item[0])] = {}
        items[int(item[0])][int(item[1])] = int(item[2])
        if int(item[1]) not in users.keys():
            users[int(item[1])] = {}
        users[int(item[1])][int(item[0])] = int(item[2])

    db.commit()

    cursor.close()
    db.close()

    return items, users


def get_synops_dict():

    db = sqlite3.connect('mydb')
    cursor = db.cursor()

    movie_synops = {}

    cmd = "SELECT * FROM synops"
    cursor.execute(cmd)
    results = cursor.fetchall()
    for movie_id in results:
        movie_synops[movie_id[0]] = movie_id[1]

    db.commit()

    cursor.close()
    db.close()

    return movie_synops


def get_top_cast_dict():

    db = sqlite3.connect('mydb')
    cursor = db.cursor()

    top_cast_dict = {}

    cmd = "SELECT * FROM top_actors"
    cursor.execute(cmd)
    results = cursor.fetchall()
    for movie_id in results:
        top_cast_dict[movie_id[0]] = [movie_id[1], movie_id[2], movie_id[3]]

    db.commit()

    cursor.close()
    db.close()

    return top_cast_dict


def get_movie_names_dict():

    movie_names_dict = {}

    f = open('u.item', 'r')

    for line in f:
        new_line = line.replace('\n', '').split('|')
        if len(new_line) > 1:
            item_id = new_line[0]
            name = new_line[1]
            movie_names_dict[int(item_id)] = name

    return movie_names_dict


def get_URLs_dict():

    db = sqlite3.connect('mydb')
    cursor = db.cursor()

    URLs_dict = {}

    cmd = "SELECT * FROM movie_images"
    cursor.execute(cmd)
    results = cursor.fetchall()
    for movie_id in results:
        URLs_dict[movie_id[0]] = movie_id[1]

    db.commit()

    cursor.close()
    db.close()

    return URLs_dict


def batch_testing(mode_input):

    global items
    global users

    # Get the model created by batch training (from the DB)
    fill_dicts_from_DB()

    movie_synopsys = get_synops_dict()
    top_cast_dict = get_top_cast_dict()

    if mode_input != 'ask':
        input_name = mode_input
    else:
        input_name = raw_input("Testing input file name: ")

    if len(items.keys()) > 0:
        try:
            f = open(input_name, 'r')

            #process input file name to establish the output file name
            #ex: testing.input => testing.output
            array = input_name.split('.')
            output_name = array[0] + '.output'
            f_write = open(output_name, 'w')

            errors = []
            init_genres()

            for line in f:
                array = line.replace('\n', '').split('\t')
                user_id = array[0]
                item_id = array[1]
                user_id = int(user_id)
                item_id = int(item_id)
                #Comment this later, MAE
                score = array[2]

                score_prediction = predict_score_item_based(user_id, item_id, users, items, movie_synopsys, top_cast_dict)

                #score_prediction = predict_score_user_based(user_id, item_id, users)
                #print "User with id", user_id, "would give the movie with id", item_id, "a score of", score_prediction
                #f_write.write(user_id + '\t' + item_id + '\t' + repr(score_prediction) + '\n')

                f_write.write(str(user_id) + '\t' + str(item_id) + '\t' + repr(score_prediction) + '\n')
                error = abs(int(score) - score_prediction)
                errors.append(error)
            f_write.close()
            if len(errors) != 0:
                mae = 0
                for err in errors:
                    mae += err
                mae /= len(errors)
                print mae
                return mae
            else:
                print 'Errors\' vector is empty!'

        except IOError:
            print "No file with that name!"
    else:
        print "No model present! Run batch training first!"


def batch_testing_500():

    batch_training('u1.base')
    mae1 = batch_testing('u1.test500')

    batch_training('u2.base')
    mae2 = batch_testing('u2.test500')

    batch_training('u3.base')
    mae3 = batch_testing('u3.test500')

    batch_training('u4.base')
    mae4 = batch_testing('u4.test500')

    batch_training('u5.base')
    mae5 = batch_testing('u5.test500')

    mean_mae = (mae1 + mae2 + mae3 + mae4 + mae5) / (5 + 0.0)
    print 'The average MAE is', mean_mae


def batch_testing_2000():

    batch_training('u1.base')
    mae1 = batch_testing('u1.test2000')

    batch_training('u2.base')
    mae2 = batch_testing('u2.test2000')

    batch_training('u3.base')
    mae3 = batch_testing('u3.test2000')

    batch_training('u4.base')
    mae4 = batch_testing('u4.test2000')

    batch_training('u5.base')
    mae5 = batch_testing('u5.test2000')

    mean_mae = (mae1 + mae2 + mae3 + mae4 + mae5) / (5 + 0.0)
    print 'The average MAE is', mean_mae


def batch_testing_all():

    batch_training('u1.base')
    mae1 = batch_testing('u1.test')

    batch_training('u2.base')
    mae2 = batch_testing('u2.test')

    batch_training('u3.base')
    mae3 = batch_testing('u3.test')

    batch_training('u4.base')
    mae4 = batch_testing('u4.test')

    batch_training('u5.base')
    mae5 = batch_testing('u5.test')

    mean_mae = (mae1 + mae2 + mae3 + mae4 + mae5) / (5 + 0.0)
    print 'The average MAE is', mean_mae


def online_mode():

    init_genres()

    mvie_names_dict = get_movie_names_dict()

    URLs_dict = get_URLs_dict()

    synopsys_dict = get_synops_dict()

    topcast_dict = get_top_cast_dict()

    init_online_mode(mvie_names_dict, URLs_dict, synopsys_dict, topcast_dict)


if __name__ == '__main__':

    print "Modes available:"
    print "\t1 - Batch training"
    print "\t2 - Batch testing (single)"
    print "\t3 - Batch testing (all tests 500)"
    print "\t4 - Batch testing (all tests 2000)"
    print "\t5 - Batch testing (all tests full)"
    print "\t6 - Init Whoosh and IMDbPy"
    print "\t7 - Online mode"
    print "\t8 - Exit the application"

    mode = 0
    while True:
        mode = raw_input("Choose a mode: ")
        try:
            mode = int(mode)
        except ValueError:
            print "Command malformed!"
            continue
        start_time = time.time()
        if mode == 1:
            batch_training('ask')
        elif mode == 2:
            batch_testing('ask')
        elif mode == 3:
            batch_testing_500()
        elif mode == 4:
            batch_testing_2000()
        elif mode == 5:
            batch_testing_all()
        elif mode == 6:
            init_whoosh_and_IMDbPy()
        elif mode == 7:
            online_mode()
        elif mode == 8:
            exit()
        else:
            print "Command malformed!"

        print "It ran for", (time.time() - start_time) / 60, "minutes..."