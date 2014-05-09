#!/usr/bin/python2.7
# -*- coding: latin-1 -*-

import imdb
import nltk
import sqlite3
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import *
from whoosh.index import open_dir
from whoosh import scoring
import time

genre_names = {}  # <genre_number : genre_name>
genres = {}  # <item_id : genres array(genre index) >
movie_names = {}  # <item_id : name>

#Fills the global variable:
#genre_names: <genre_number : genre_name>
def fill_genre_names():
    global genre_names
    f = open('u.genre', 'r')

    for line in f:
        array = line.replace('\n','').split('|')
        if len(array) > 1:
            genre_names[int(array[1])] = array[0]


#Fills the global variables:
# genres <item_id : array(with the indices of the genres) ex:[3,4,6] >
# movie_names <item_id : array(with the indices of the genres) >
def fill_genres():
    global genres
    global movie_names

    f = open('u.item', 'r')

    for line in f:
        array = line.replace('\n', '').split('|')
        if len(array) > 1:
            item_id = array[0]
            name = array[1]
            movie_names[int(item_id)] = name
            genres[int(item_id)] = []
            for i in range(1, 20):
                if array[i+4] == '1':
                    genres[int(item_id)].append(i)



#Uses a global dictionary of genres (which needs to be be previously filled)
#Outputs the genre_similarity between 2 movies (given their ids)
#Returns:
#1 if all genres from item1 are in item2
#common_genres/genres_from_item_1 if they have at least 1 genre in common
#0.01 if they are completely different genre-wise
def get_genre_similarity(item_id_1, item_id_2):
    global genres

    total_common_genres = 0
    total_genres_item_1 = len(genres[item_id_1])

    for genre in genres[item_id_1]:
        if genre in genres[item_id_2]:
            total_common_genres += 1

    if total_genres_item_1 == total_common_genres:
        return 1
    if total_common_genres > 0:
        return (total_common_genres + 0.0) / total_genres_item_1
    return 0

#Uses a dictionary of synopses (which needs to be be previously filled)
#Outputs the synopsis_similarity between 2 movies (given their ids)
#Returns:
#Whoosh score normalized by the formula: score = N / (N + 10)
def get_synop_similarity(item_id_1, item_id_2, movie_synopsys):

    synop_item_1 = movie_synopsys[int(item_id_1)]

    ix = open_dir("indexdir")

    with ix.searcher(weighting=scoring.TF_IDF()) as searcher:
        qry = QueryParser("content", ix.schema, group=OrGroup).parse(synop_item_1)
        results = searcher.search(qry, limit=50)
        for r in results:
            if r['id'] == int(item_id_2):
                new_score = (r.score + 0.0) / (r.score + 10)
                return new_score
        return 0    # Se nao estiver no top50 das similaridades na query, retornamos uma similarity de 0

#Uses a dictionary of top cast (which needs to be be previously filled)
#Outputs the topcast_similarity between 2 movies (given their ids)
#Returns:
#1 if all actors from item1 are in item2
#common_actors/actors_from_item_1 if they have at least 1 actor in common
#0.01 if they are completely different actor-wise
def get_top_cast_similarity(item_id_1, item_id_2, top_cast_dict):

    total_common_actors = 0

    top_cast_item_1 = top_cast_dict[int(item_id_1)]
    top_cast_item_2 = top_cast_dict[int(item_id_2)]

    for actor in top_cast_item_1:
        if actor in top_cast_item_2 and actor != 'no_actor':
            total_common_actors += 1

    return total_common_actors / (3 + 0.0)

#Fills the global variables needed for genre comparisons
def init_genres():

    fill_genre_names()
    fill_genres()

#Fills the Whoosh index and the SQLite database with info about synopses, movie images URLs and top actors of each movie
#Only needs to be run once!
#Outputs: Nothing
#Returns: Nothing
def init_whoosh_and_IMDbPy():

    db = sqlite3.connect('mydb')
    cursor = db.cursor()
    cursor.execute('''DROP TABLE IF EXISTS synops''')

    cursor.execute('''CREATE TABLE synops(item_id INTEGER, synopsys TEXT)''')

    cursor.execute('''DROP TABLE IF EXISTS movie_images''')

    cursor.execute('''CREATE TABLE movie_images(item_id INTEGER, image_URL TEXT)''')

    cursor.execute('''DROP TABLE IF EXISTS top_actors''')

    cursor.execute('''CREATE TABLE top_actors(item_id INTEGER, actor_1 TEXT, actor_2 TEXT, actor_3 TEXT)''')

    schema = Schema(id=NUMERIC(stored=True), content=TEXT(stored=True))
    ix = create_in("indexdir", schema)
    writer = ix.writer()

    f = open('u.item', 'r')
    searcher = imdb.IMDb()
    iter = 1

    for line in f:
        new_line = line.replace('\n', '').split('|')
        if len(new_line) > 1:
            movie_id = int(new_line[0])
            movie_name = new_line[1]
            print iter, '- I\'M GETTING THE MOVIE', movie_name
            s_result = []
            while s_result == []:
                s_result = searcher.search_movie(movie_name)

            the_movie = s_result[0]
            searcher.update(the_movie)
            # Movie with error in IMDbPy (can't find right movie)...
            if movie_id == 1331:
                synop_klezmer = u'The Last Klezmer: Leopold Kozlowski, His Life and Music'
                print 'IM INSERTING THE SYNOPSIS:', synop_klezmer
                writer.add_document(id=movie_id, content=synop_klezmer)
                cmd = """INSERT INTO synops(item_id, synopsys) VALUES("%d", "%s")""" % (movie_id, synop_klezmer)
                cursor.execute(cmd)
                movie_im_URL = 'http://ia.media-imdb.com/images/M/MV5BMTk2NjAwNTM1Ml5BMl5BanBnXkFtZTcwNDEwNDkyMQ@@._V1__SX1305_SY580_.jpg'
                cmd2 = """INSERT INTO movie_images(item_id, image_URL) VALUES("%d", "%s")""" % (movie_id, movie_im_URL)
                cursor.execute(cmd2)
                cmd3 = """INSERT INTO top_actors(item_id, actor_1, actor_2, actor_3) VALUES("%d", "%s", "%s", "%s")""" % (1331, 'Leopold Kozlowski', 'no_actor', 'no_actor')
                cursor.execute(cmd3)
                continue
            #print iter, '- I\'M GETTING THE PLOT OF THE MOVIE:', movie_name
            if 'plot' in the_movie.keys():
                plot = the_movie['plot'][0]
                if len(plot) < 3:
                    plot_list = the_movie['plot outline']
                    if len(plot_list) > 0:
                        plot = the_movie['plot outline'][0]
                    else:
                        plot = movie_name.decode('unicode-escape')
                        plot = plot[:-7]    # remove the year from movie name
            elif 'plot outline' in the_movie.keys():
                plot_list = the_movie['plot outline']
                if len(plot_list) > 0:
                    plot = the_movie['plot outline'][0]
                    if len(plot) < 3:
                        plot = movie_name.decode('unicode-escape')
                        plot = plot[:-7]        # remove the year from movie name
                else:
                    plot = movie_name.decode('unicode-escape')
                    plot = plot[:-7]    # remove the year from movie name
            else:
                plot = movie_name.decode('unicode-escape')
            if 'full-size cover url' in the_movie.keys():
                movie_img_URL = the_movie['full-size cover url']
            elif 'cover url' in the_movie.keys():
                movie_img_URL = the_movie['cover url']
            else:
                movie_img_URL = 'no_image'
            if 'cast' in the_movie.keys():
                cast = the_movie['cast']
                if len(cast) == 1:
                    cast = [cast[0], 'no_actor', 'no_actor']
                elif len(cast) == 2:
                    cast = [cast[0], cast[1], 'no_actor']
            else:
                cast = ['no_actor', 'no_actor', 'no_actor']
            movie_synop = nltk.word_tokenize(plot)
            movie_synop_tagged = nltk.pos_tag(movie_synop)
            new_synop = ''
            for item in movie_synop_tagged:
                if item[1] == 'CD' or item[1] == 'FW' or item[1] == 'LS' or item[1] == 'NN' or item[1] == 'NNP' or item[1] == 'NNS' or item[1] == 'NNPS' or item[1] == 'SYM' or item[1] == 'UH':
                    new_synop += item[0]
                    new_synop += ' '
            if new_synop != '':
                synop_list = re.split('\W+', new_synop.lower(), flags=re.UNICODE)
                final_synop = ' '.join(synop_list)
                print 'IM INSERTING THE SYNOPSIS:', final_synop
                writer.add_document(id=movie_id, content=final_synop)
                cmd = """INSERT INTO synops(item_id, synopsys) VALUES("%d", "%s")""" % (movie_id, final_synop)
                cursor.execute(cmd)
                cmd2 = """INSERT INTO movie_images(item_id, image_URL) VALUES("%d", "%s")""" % (movie_id, movie_img_URL)
                cursor.execute(cmd2)
                cmd3 = """INSERT INTO top_actors(item_id, actor_1, actor_2, actor_3) VALUES("%d", "%s", "%s", "%s")""" % (movie_id, cast[0], cast[1], cast[2])
                cursor.execute(cmd3)
            else:
                print 'THE NEW_SYNOP WAS NULL. DIDN\'T INSERT ANYTHING IN WHOOSH!\n\''
        iter += 1
    writer.commit()
    db.commit()

    cursor.close()
    db.close()