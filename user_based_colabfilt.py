import math
from item_based_colabfilt import get_dictionaries

def get_users_who_rated_same_as_me(user, target, usrs):
    users = []
    my_items = usrs[user].keys()
    user_items_count = len(my_items)
    for usr in usrs.keys():
        counted = 0
        for item in my_items:
            if item in usrs[usr].keys():
                counted += 1
        #se este user tambem deu rate a todos os meus
        if counted > user_items_count/2:
            #se alem disso tambem deu rate ao target
            if target in usrs[usr].keys():
                users.append(usr)
    return users

def user_adjusted_cosine_similarity(user_id_a, user_id_b, usrs):

    avgs = {}

    set_p = []

    #get set of items rated by both users a and b, set_p
    for item_id in usrs[user_id_a].keys():
        if item_id in usrs[user_id_b].keys():
            set_p.append(item_id)

    #para cada user (a e b) calcular a media global dos seus ratings
    avgs[user_id_a] = 0
    for rating in usrs[user_id_a].values():
        avgs[user_id_a] += rating
    avgs[user_id_a] = (avgs[user_id_a]+0.0)/len(usrs[user_id_a].values())

    avgs[user_id_b] = 0
    for rating in usrs[user_id_b].values():
        avgs[user_id_b] += rating
    avgs[user_id_b] = (avgs[user_id_b]+0.0)/len(usrs[user_id_b].values())

    #calcular o numerador e o denominador do quociente
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

    if sum_numerator == 0:  #caso raro (com apenas 1 user que deu a mesma cotacao a todas as avaliacoes)
        return 0            #senao dava divisao por zero...

    return (sum_numerator+0.0)/(sum_denominator_a*sum_denominator_b)

#dado um user e um item, vou ver quais os users que avaliaram os mesmos items que este user,
#depois calculo a similaridade com cada um destes users
#depois peso o score que eles deram pelo qdrado da similaridade que eu tiver com eles
def predict_score_user_based(user_id, item_id, usrs):
    users_who_rated = get_users_who_rated_same_as_me(user_id, item_id, usrs)

    results = {}
    similarities = 0

    #calculate the similarity between each user who has rated the same as me, and me
    for usr_id in users_who_rated:
        similarity = user_adjusted_cosine_similarity(user_id, usr_id, usrs)
        if similarity > 0: #so nos interessam os mais semelhantes
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
        result /= (0.0+similarities) #media ponderada pelo quadrado das similarities
    else:
        result = 3 #se nao houver outros users semelhantes dizemos q o score eh default: 3
    return result

if __name__ == '__main__':

    user = "40"
    target = "700"

    #retorna items_dict fica: <item_id : < user_id : rating >> e users <user_ids : <item_id : rating>>
    items, usrs = get_dictionaries('u.data')

    score_prediction = predict_score_user_based(user, target, usrs)
    print "User with id",user,"would give the movie with id", target, "a score of", score_prediction
