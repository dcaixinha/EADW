import math
from item_based_colabfilt import get_dictionaries

#user is the user_id
#target is the target item_id
#usrs is the dictionary <user_id : <item_id : rating>>
#Returns a list of user_ids who rated all of the items that I rated
def get_users_who_rated_same_as_me(user, target, usrs):
    users = []
    my_items = usrs[user].keys()
    user_items_count = len(my_items)
    for usr in usrs.keys():
        counted = 0
        for item in my_items:
            if item in usrs[usr].keys():
                counted += 1
        #if this user rated all of my items
        if counted > user_items_count/2:
            #and if also rated the target
            if target in usrs[usr].keys():
                users.append(usr)
    return users

#Calculates the cosine similarity between 2 users
def user_adjusted_cosine_similarity(user_id_a, user_id_b, usrs):

    avgs = {}

    set_p = []

    #get set of items rated by both users a and b -> set_p
    for item_id in usrs[user_id_a].keys():
        if item_id in usrs[user_id_b].keys():
            set_p.append(item_id)

    #for user a and b calculate the global average of their ratings -> avgs
    avgs[user_id_a] = 0
    for rating in usrs[user_id_a].values():
        avgs[user_id_a] += rating
    avgs[user_id_a] = (avgs[user_id_a]+0.0)/len(usrs[user_id_a].values())

    avgs[user_id_b] = 0
    for rating in usrs[user_id_b].values():
        avgs[user_id_b] += rating
    avgs[user_id_b] = (avgs[user_id_b]+0.0)/len(usrs[user_id_b].values())

    #calculate the numerator and the denominator
    sum_numerator = 0
    sum_denominator_a = 0
    sum_denominator_b = 0
    for item_id in set_p:
        r_ap = int(usrs[user_id_a][item_id])
        r_bp = int(usrs[user_id_b][item_id])
        sum_numerator += (r_ap - avgs[user_id_a]) * (r_bp - avgs[user_id_b])
        sum_denominator_a += (r_ap - avgs[user_id_a]) ** 2
        sum_denominator_b += (r_bp - avgs[user_id_b]) ** 2
    sum_denominator_a = math.sqrt( sum_denominator_a )
    sum_denominator_b = math.sqrt( sum_denominator_b )

    if sum_numerator == 0:  #rare case
        return 0            #avoid division by zero...

    return (sum_numerator+0.0)/(sum_denominator_a*sum_denominator_b)

#Given a user and an item, get the users who gave score to the same items of the user,
#then calculate the similarity between the user and all those other users
#finally weigh the score each user gave to the item in question (item_id) by the square
#of the similarity between that user and the initial user.
def predict_score_user_based(user_id, item_id, usrs):
    users_who_rated = get_users_who_rated_same_as_me(user_id, item_id, usrs)

    results = {}
    similarities = 0

    #calculate the similarity between each user who has rated the same as me, and me
    for usr_id in users_who_rated:
        similarity = user_adjusted_cosine_similarity(user_id, usr_id, usrs)
        if similarity > 0: #filtering only the positive similarities
            if __name__ == '__main__':
                print user_id,":",usr_id,"=>",similarity,",",usrs[usr_id][item_id],"(",(similarity**2)*usrs[usr_id][item_id],")"
            #use the square of the similarity(to give more weight to the higher similarities' scores)
            similarities += similarity**2
            #multiply by the rate the user gave that items
            results[usr_id] = (similarity**2)*usrs[usr_id][item_id]

    result = 0
    for val in results.values():
        result += val
    if similarities > 0:
        result /= (0.0+similarities) #average weighted by the square of the similarities
    else:
        result = 3 #if there are no similar users we say the default value is 3
    return result
