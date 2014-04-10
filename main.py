from item_based_colabfilt import *

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

            for line in f:
                array = line.replace('\n', '').split('\t')
                user_id = array[0]
                item_id = array[1]

                user_rated_items = get_user_rated_item_ids(user_id, users)
                score_prediction = compare_item_against_user_rated(user_rated_items, item_id, items, user_id, users)
                #print "User with id", user_id, "would give the movie with id", item_id, "a score of", score_prediction
                f_write.write(user_id + '\t' + item_id + '\t' + repr(score_prediction) + '\n')

            f_write.close()
        except IOError:
            print "No file with that name!"
    else:
        print "No model present! Run batch training first!"

def online_mode():
    print "lol online"

if __name__ == '__main__':
    print "Mpdes available: (command - mode)"
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
