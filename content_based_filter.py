genre_names = {} # <genre_number : genre_name>
genres = {} #<item_id : array de generos(indice do genero) >
movie_names = {} # <item_id : name>

def fill_genre_names():
    global genre_names
    f = open('u.genre', 'r')

    for line in f:
        array = line.replace('\n','').split('|')
        if len(array) > 1:
            genre_names[int(array[1])] = array[0]

#percorrer o ficheiro e preencher o dicionario de generos
# genres <item_id : array de generos(indice do genero) >
# movie_names <item_id : array de generos(indice do genero) >
def fill_genres():
    global genres
    global movie_names

    f = open('u.item', 'r')

    for line in f:
        array = line.replace('\n','').split('|')
        if len(array) > 1:
            item_id = array[0]
            name = array[1]
            movie_names[item_id] = name
            genres[item_id] = []
            for i in range(1, 20):
                if array[i+4] == '1':
                    genres[item_id].append(i)
            #print name, genre[item_id]


#devolve uma lista de filmes com pelo menos 1 genero em comum
#dicio <item_id : array de generos(indice do genero) >
def get_movies_of_genre(target_id, dicio):
    subset_movies = []
    set_movies = []
    for i in dicio[target_id]:
        for element in dicio.items():
            if i in element[1]:
                subset_movies.append(element[0])
        set_movies = list(set(subset_movies + set_movies)) #merge sem repeticao de elementos

    return set_movies

#devolve a lista de filmes dos mesmos generos exactamente, ex: [0111000..0] == [01110..0]
#dicio <item_id : array de generos(indice do genero) >
def get_movies_with_same_genres(target_id):
    global genres

    genre_list = genres[target_id]
    results = []
    for element in dicio.items():
        if genre_list == element[1]:
            results.append(element[0])
    return results

#devolve os filmes que tem os mesmos generos
def get_similar_movies(target_id):
    global movie_names

    #set_movies = get_movies_of_genre(target_id, genres)
    set_movies = get_movies_with_same_genres(target_id)
    return set_movies

#devolve um score:
#0.1 se forem completamente diferentes
#0.5 se tiverem pelo menos 1 genero em comum
#1.1 se tiverem todos os generos em comum
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
        return 0.1
    return 0.1

def init_genres():
    fill_genre_names()
    fill_genres()

if __name__ == '__main__':
    init_genres()
    set_movies = get_similar_movies('22')
    for movie in set_movies:
        print movie_names[movie]