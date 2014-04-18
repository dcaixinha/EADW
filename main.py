from item_based_colabfilt import *
from content_based_filter import *
from user_based_colabfilt import *


items = {}
users = {}

def batch_training():
    global items
    global users
    file_name = raw_input("File name: ")
    items, users = get_dictionaries(file_name) #TODO items e users devem ser persistentes! BD!

def batch_testing():
    global items
    global users
    if len(items.keys()) > 0:
        input_name = raw_input("Testing input file name: ")
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
                #Comment this later, MAE
                score = array[2]


                #score_prediction = randint(1, 5)
                score_prediction, count , top_similarities = predict_score_item_based(user_id, item_id, users, items)
            #    score_prediction = predict_score_user_based(user_id, item_id, users)
                #if score_prediction > 5.0:
                #    score_prediction = 5.0
                #print "User with id", user_id, "would give the movie with id", item_id, "a score of", score_prediction
                #f_write.write(user_id + '\t' + item_id + '\t' + repr(score_prediction) + '\n')
                error = abs(int(score) - score_prediction)
                f_write.write(user_id + '\t' + item_id + '\t' + score + '\t' + repr(score_prediction) + '\t' + repr(error) + '\t[' + repr(count) + ']\t')
                top_similarities_list = top_similarities.values()
                top_similarities_list.sort()
                f_write.write(repr('%.2f' % top_similarities_list[0]) + '\t' + repr('%.2f' % top_similarities_list[-1]) + '\n')
                errors.append(error)
            mae = 0
            for err in errors:
                mae += err
            mae /=len(errors)
            print mae
            f_write.close()

        except IOError:
            print "No file with that name!"
    else:
        print "No model present! Run batch training first!"

def online_mode():
    print "lol online"

if __name__ == '__main__':
    print "Modes available: (command - mode)"
    print "\t'training' - Batch training"
    print "\t'testing' - Batch testing"
    print "\t'online' - Online mode"
    print "\t'exit' - Exit the application"

    modes = {
        "training" : batch_training,
        "testing" : batch_testing,
        "online" : online_mode,
    }

    mode = ""
    while mode != "exit":
        mode = raw_input("Choose a mode: ")
        if mode in modes.keys():
            modes[mode]()
        else:
            if mode != "exit":
                print "Command malformed!"
