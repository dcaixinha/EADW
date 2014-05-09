import imdb
import nltk
import urllib
import difflib
import re
import sqlite3
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import *
from whoosh.index import open_dir
from whoosh import scoring


def init_whoosh():

    #Database
    schema = Schema(id=NUMERIC(stored=True), content=TEXT)
    ix = create_in("indexdir", schema)
    writer = ix.writer()

    f = open('u.item', 'r')
    searcher = imdb.IMDb()
    id = 1

    for line in f:
        new_line = line.replace('\n', '').split('|')
        if len(new_line) > 1:
            movie_id = int(new_line[0])
            movie_name = new_line[1]
            s_result = searcher.search_movie(movie_name)
            the_movie = s_result[0]
            searcher.update(the_movie)
            print id, '- I\'M GETTING THE PLOT OF THE MOVIE:', movie_name
            #print 'ESTE MOVIE TEM AS KEYS', the_movie.keys()
            if 'plot' in the_movie.keys():
                #print 'THE MOVIE[PLOT] IS', the_movie['plot']
                plot = the_movie['plot'][0]
            elif 'plot outline' in the_movie.keys():
                plot_list = the_movie['plot outline']
                if len(plot_list) > 0:
                    #print 'THE MOVIE[PLOT OUTLINE] IS', the_movie['plot outline']
                    plot = the_movie['plot outline'][0]
                else:
                    plot = movie_name.decode('unicode-escape')
            else:
                plot = movie_name.decode('unicode-escape')
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
        id += 1
    writer.commit()


if __name__ == '__main__':

    #init_whoosh()
    print 'lol'

    # db = sqlite3.connect('mydb')
    # cursor = db.cursor()
    #
    # schema = Schema(id=NUMERIC(stored=True), content=TEXT(stored=True))
    # ix = create_in("indexdir", schema)
    # writer = ix.writer()
    # movie_id = 1331
    #
    # synop_test = u'The Last Klezmer: Leopold Kozlowski, His Life and Music'
    # print 'IM INSERTING THE SYNOPSIS:', synop_test
    # writer.add_document(id=movie_id, content=synop_test)
    # cmd = """INSERT INTO synops(item_id, synopsys) VALUES("%d", "%s")""" % (movie_id, synop_test)
    # cursor.execute(cmd)
    # movie_im_URL = 'http://ia.media-imdb.com/images/M/MV5BMTk2NjAwNTM1Ml5BMl5BanBnXkFtZTcwNDEwNDkyMQ@@._V1__SX1305_SY580_.jpg'
    # cmd2 = """INSERT INTO movie_images(item_id, image_URL) VALUES("%d", "%s")""" % (movie_id, movie_im_URL)
    # cursor.execute(cmd2)
    # cmd3 = """INSERT INTO top_actors(item_id, actor_1, actor_2, actor_3) VALUES("%d", "%s", "%s", "%s")""" % (1331, 'Leopold Kozlowski', 'no_actor', 'no_actor')
    # cursor.execute(cmd3)
    #
    # db.commit()
    #
    # cursor.close()
    # db.close()
    #
    # writer.commit()

    # searcher = imdb.IMDb()
    #
    # # Search for a movie (get a list of Movie objects).
    # #s_result = searcher.search_movie('Wolf of Wall Street (2013)')
    # s_result = searcher.search_movie('Last Klezmer: Leopold Kozlowski, His Life and Music, The')
    #
    # print 'O S_RESULT E\'', s_result
    # # Print the long imdb canonical title and movieID of the results.
    # #for item in s_result:
    # #    print item['long imdb canonical title'], item.movieID
    #
    # # Retrieves default information for the first result (a Movie object).
    # the_wolf = s_result[0]
    #
    # searcher.update(the_wolf)
    # print 'THE MOVIE KEYS ARE', the_wolf.keys()
    #
    # akas = the_wolf['akas']
    # print 'THE AKAS IS', akas
    #
    # kind = the_wolf['kind']
    # print 'THE KIND IS', kind
    #
    # cast = the_wolf['cast']
    # print 'THE CAST IS', cast
    #
    # print 'TOP1 CAST IS', cast[0]
    # print 'TOP2 CAST IS', cast[1]
    # print 'TOP3 CAST IS', cast[2]
    #
    # director = the_wolf['director']
    # print 'THE director IS', director
    #
    # genres = the_wolf['genres']
    # print 'THE genres IS', genres
    #
    # img_url = the_wolf['full-size cover url']
    # print 'THE IMG URL IS', img_url
    #
    # urllib.urlretrieve(img_url, "movie_cover.jpg")
    # #img = urllib2.urlopen(img_url).read()





    # # Print some information.
    # print 'Runtime:', the_wolf['runtime'][0], 'min.'
    # print 'Rating:', the_wolf['rating']
    # director = the_wolf['director']  # get a list of Person objects.
    # print 'Director:', director[0]
    #
    # #print 'Plot outline:', the_wolf['plot outline']
    # plot = the_wolf['plot'][0]
    # #print 'Plot:', plot
    #
    # movie_synop = nltk.word_tokenize(plot)
    # #print 'THE MOVIE SYNOP IS', movie_synop
    # movie_synop_tagged = nltk.pos_tag(movie_synop)
    # #print 'THE TAGGED MOVIE SYNOP IS', movie_synop_tagged
    # new_synop = ''
    #
    # for item in movie_synop_tagged:
    #     if item[1] == 'CD' or item[1] == 'FW' or item[1] == 'LS' or item[1] == 'NN' or item[1] == 'NNP' or item[1] == 'NNS' or item[1] == 'NNPS' or item[1] == 'SYM' or item[1] == 'UH':
    #         new_synop += item[0]
    #         new_synop += ' '
    #
    # #print 'THE NEW PLOT IS', new_synop
    # new_synop = 'boy Andy toys doll "Woody" life Woody toy birthday party figure Buzz Lightyear toy killer Sid Phillips.'
    #
    # # s_result = searcher.search_movie('Wall Street')
    # # the_movie = s_result[0]
    # #
    # # searcher.update(the_movie)
    # # # Print some information.
    # # #print 'Runtime:', the_movie['runtime'][0], 'min.'
    # # #print 'Rating:', the_movie['rating']
    # # director1 = the_movie['director']  # get a list of Person objects.
    # # #print 'Director:', director1[0]
    # #
    # # #print 'Plot outline:', the_movie['plot outline']
    # # plot_2 = the_movie['plot'][0]
    # # #print 'Plot:', plot_2
    # #
    # # movie_synop_2 = nltk.word_tokenize(plot_2)
    # # #print 'THE MOVIE SYNOP IS', movie_synop
    # # movie_synop_tagged_2 = nltk.pos_tag(movie_synop_2)
    # # #print 'THE TAGGED MOVIE SYNOP2 IS', movie_synop_tagged_2
    # # new_synop_2 = ''
    # #
    # # for item in movie_synop_tagged_2:
    # #     if item[1] == 'CD' or item[1] == 'FW' or item[1] == 'LS' or item[1] == 'NN' or item[1] == 'NNP' or item[1] == 'NNS' or item[1] == 'NNPS' or item[1] == 'SYM' or item[1] == 'UH':
    # #         new_synop_2 += item[0]
    # #         new_synop_2 += ' '
    # #
    # # print 'THE NEW PLOT2 IS', new_synop_2
    # #
    # # #new_synop_2 = new_synop
    # #
    # # seq = difflib.SequenceMatcher(a=new_synop.lower(), b=new_synop_2.lower())
    # # print 'THE SYNOPSIS SIMILARITY IS', seq.ratio()
    #
    # ix = open_dir("indexdir")
    # queryResults = []
    #
    # with ix.searcher(weighting=scoring.TF_IDF()) as searcher:
    #     print 'ESTOU A FAZER A QUERY COM A SYNOP', new_synop
    #     query = QueryParser("content", ix.schema, group=OrGroup).parse(new_synop)
    #     results = searcher.search(query, limit=100)
    #     print 'O TOTAL RESUTLS E\'', results
    #     for r in results:
    #         queryResults.append(r['id'])
    #         if __name__ == "__main__":
    #             print 'O SCORE ORIGINAL E\'', r.score
    #             new_score = (r.score + 0.0) / (r.score + 20)
    #             print 'PARA O DOCNUM', r['id'], 'O SCORE DO RESULT E\'', new_score
    #     if __name__ == "__main__":
    #         print "Number of results:", results.scored_length()