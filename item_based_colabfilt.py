import math
from content_based_filter import *

#items a and b are dictionaries <user_id : rating> and may not have the values for all users
def adjusted_cosine_similarity(a, b, userDict):

    avgs = {}

    set_u = []
    #get set of users who have rated both items a and b, set_u
    for user_id in a.keys():
        if user_id in b.keys():
            set_u.append(user_id)

    #para cada user no set_u, calcular a media global dos seus ratings
    for user_id in set_u:
        avgs[user_id] = 0
        for val in userDict[user_id].values():
            avgs[user_id] += val
        avgs[user_id] = (avgs[user_id]+0.0)/len(userDict[user_id].values())
    #esta avg eh sobre todos os items avaliados pelo user
    #print avgs[set_u[0]]

    #calcular o numerador e o denominador do quociente
    sum_numerator = 0
    sum_denominator_a = 0
    sum_denominator_b = 0
    for user_id in set_u:
        r_ua = int(a[user_id])
        r_ub = int(b[user_id])
        sum_numerator += (r_ua - avgs[user_id]) * (r_ub - avgs[user_id])
        sum_denominator_a += (r_ua - avgs[user_id]) ** 2
        sum_denominator_b += (r_ub - avgs[user_id]) ** 2
    sum_denominator_a = math.sqrt( sum_denominator_a )
    sum_denominator_b = math.sqrt( sum_denominator_b )

    if sum_numerator == 0:  #caso raro (com apenas 1 user que deu a mesma cotacao a todas as avaliacoes)
        return 0            #senao dava divisao por zero...

    return (sum_numerator+0.0)/(sum_denominator_a*sum_denominator_b)


#retorna items_dict fica: <item_id : < user_id : rating >> e users <user_ids : <item_id : rating>>
def get_dictionaries(file_name):
    try:
        f = open(file_name, 'r')

        items_dict = {} #este vai ser um dicionario de dicionarios
        users = {} #vai contero dicionario <user_ids : lista de ratings> para a media por user

        for line in f:
            array = line.split('\t')

            user_id = array[0]
            item_id = array[1]
            rating = array[2]
            #se o user ainda n existia, eh preciso criar o dicionario de items para esse user
            if user_id not in users.keys():
                users[user_id] = {}
            #acrescenta ah lista de ratings desse user
            users[user_id][item_id] = int(rating)

            #cria o dicionario de users, dentro do dicionario de items, para cada item, se este ainda n existir
            if item_id not in items_dict.keys():
                items_dict[item_id] = {}
            #saves the rating the user gave to this item
            items_dict[item_id][user_id] = int(rating)

        return items_dict, users
    except IOError:
        print "No file with that name!"
        return None, None

#user_rated list<string> with item ids, target string with item_id, items dictionary of items
def compare_item_against_user_rated(user_rated, target, items, user, usrs):
    results = {}
    similarities = 0

    #calculate the similarity between each item the user rated and the target item
    for item_id in user_rated:
        similarity = adjusted_cosine_similarity(items[item_id], items[target], usrs)
        genre_similarity = get_genre_similarity(target, item_id)
        if similarity > 0: #so nos interessam os mais semelhantes
            similarity *= genre_similarity
            if __name__ == '__main__':
                print item_id,":",target,"=>",similarity,",",items[item_id][user],"(",(similarity**2)*items[item_id][user],")"
            #use the square of the similarity(to give more weight to the higher similarities' scores)
            similarities += similarity**2
            #multiply by the rate the user gave that items
            results[item_id] = (similarity**2)*items[item_id][user]

    result = 0
    for val in results.values():
        result += val
    if similarities > 0:
        result /= (0.0+similarities) #media ponderada pelo quadrado das similarities
    else:
        result = 0
    return result


def get_user_rated_item_ids(user_id, users):
    result = []
    for item_id in users[user_id].keys():
        result.append(item_id)
    return result


if __name__ == '__main__':

    user = "40"
    target = "1000"

    items, usrs = get_dictionaries('u.data')
    user_rated_items = get_user_rated_item_ids(user, usrs)

    #depois de obter os item_ids que o user ja rate'ou, ir ver qual a classificacao
    #que o user deu nestes ids, e pesar essa classificacao com as similiridades entre
    #cada uma dessas e o item target
    score_prediction = compare_item_against_user_rated(user_rated_items, target, items, user, usrs)
    print "User with id",user,"would give the movie with id", target, "a score of", score_prediction