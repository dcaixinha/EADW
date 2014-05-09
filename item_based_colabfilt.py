#!/usr/bin/python2.7
# -*- coding: latin-1 -*-

import math
from content_based_info import *


#Compares 2 items a and b (which are vectors containing pairs user - score), the vectors are compared
#based on the common set of users who rated both items.
#a and b dicionaries <user_id : score>
#userDict <user_id : <item_id : rating>>
#Returns a value between -1 and 1
def adjusted_cosine_similarity(a, b, userDict):

    avgs = {}

    set_u = []
    #get set of users who have rated both items a and b -> set_u
    for user_id in a.keys():
        if user_id in b.keys():
            set_u.append(user_id)

    #for each user in this set calculate the global avg of their scores -> avgs list
    #this avg is made over all items scored by that user
    for user_id in set_u:
        avgs[user_id] = 0
        for val in userDict[user_id].values():
            avgs[user_id] += val
        avgs[user_id] = (avgs[user_id]+0.0)/len(userDict[user_id].values())

    #calculate the numerator and denominator
    sum_numerator = 0
    sum_denominator_a = 0
    sum_denominator_b = 0
    for user_id in set_u:
        r_ua = int(a[user_id])  #this user's score for item a
        r_ub = int(b[user_id])
        sum_numerator += (r_ua - avgs[user_id]) * (r_ub - avgs[user_id])
        sum_denominator_a += (r_ua - avgs[user_id]) ** 2
        sum_denominator_b += (r_ub - avgs[user_id]) ** 2
    sum_denominator_a = math.sqrt( sum_denominator_a )
    sum_denominator_b = math.sqrt( sum_denominator_b )

    if sum_numerator == 0:  #rare case (if a user has an average equal to a score)
        return 0            #to avoid division by zero

    return (sum_numerator+0.0)/(sum_denominator_a*sum_denominator_b)


#user_id is the user for which we will predict the score,
#target is a string with item_id,
#usrs is the dictionary of users,
#items is the dictionary of items.
#Returns a float from 0 to 5 indicating the score predicted
def predict_score_item_based(user_id, target, usrs, items, movie_synopsys, top_cast_dict):

    results = {}
    top_similarities = {}   #will contain the 41 most similar items -> magic number from trial and error
    sum_similarities = 0

    #get items that this user rated
    user_rated_items = get_user_rated_item_ids(user_id, usrs)

    #calculate the similarity between each item the user rated and the target item
    for item_id in user_rated_items:
        if target in items:
            print 'ENTREI NO IF, VOU FAZER O COS SIMIL!!!'
            similarity = adjusted_cosine_similarity(items[item_id], items[target], usrs)
            if similarity > -0.83 and similarity < 0.98: #magical parameters from trial and error
                #it will only insert in the list if its bigger than one of the values already present
                insert_top_sim(similarity, item_id, top_similarities)

    #in the end take the top similarities
    for item_id, similarity in top_similarities.iteritems():

        genre_similarity = get_genre_similarity(target, item_id)
        synop_similarity = get_synop_similarity(target, item_id, movie_synopsys)
        cast_similarity = get_top_cast_similarity(target, item_id, top_cast_dict)

        print 'THE GENRE SIMILARITY IS', genre_similarity
        print 'THE SYNOP SIMILARITY IS', synop_similarity
        print 'THE CAST SIMILARITY IS', cast_similarity
        print 'THE SIMILARITY ITSELF IS', similarity

        similarity = ((1*similarity) + (2*genre_similarity) + (1*synop_similarity) + (4*cast_similarity)) / (8 + 0.0)

        print 'AFTER AVERAGE IS', similarity

        #use the square of the similarity(to give more weight to the higher similarities' scores)
        sum_similarities += similarity**2
        #multiply by the rate the user gave that items
        results[item_id] = (similarity**2)*usrs[user_id][item_id]

    result = 0
    for val in results.values():
        result += val
    print 'THE RESULT AFTER FOR IS', result
    print 'THE SUM_SIMILARITIES AFTER FOR IS', sum_similarities
    if sum_similarities != 0:
        result /= (0.0+sum_similarities)  #average weighted by the square of the similarities
        print 'AND THE FINAL RESULT IS', result
    else:
        print 'AND THE FINAL RESULT IS THE DEFAULT'
        result = 3  #if there are no similar movies the default score is 3 (this is very rare)
    return result


#Inserts the item_id and the similarity onto top-similarities only if this similarity
#is bigger than some other similarity already present. If so, it will remove the
#lowest similarity and keep the new one in its stead
#Returns the number of top similarities already gathered
def insert_top_sim(similarity, item_id, top_similarities):
    max_similarity_count = 50   #magic parameter found through trial and error

    if len(top_similarities.keys()) < max_similarity_count:
        top_similarities[item_id] = similarity
    else:
        #find the lowest value present on the top list
        min = 10
        min_item_id = -1
        for item_id_stored, similarity_stored in top_similarities.iteritems():
            if similarity_stored < min:
                min = similarity_stored
                min_item_id = item_id_stored
        #only insert new value if the lowest value present is lower than the new value we want to insert
        if min < similarity:
            del top_similarities[min_item_id]
            top_similarities[item_id] = similarity

#Returns the items (list of item_ids) that the user user_id rated
def get_user_rated_item_ids(user_id, users):
    result = []

    for item_id in users[int(user_id)].keys():
        result.append(int(item_id))
    return result