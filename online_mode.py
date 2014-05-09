#!/usr/bin/python2.7
# -*- coding: latin-1 -*-

import sys
import random
import urllib
import time
from main import get_dictionaries
from item_based_colabfilt import predict_score_item_based
from PyQt4 import QtCore, QtGui


class EADW_Proj_Window(QtGui.QWidget):


    #Function that inits all the UI component (buttons, textboxes, images etc.) and defines handlers for the buttons.
    def __init__(self, names_dict, URLs_dict, synopsys_dict, topcast_dict):

        super(EADW_Proj_Window, self).__init__()

        self.movie_name_dict = names_dict
        self.URLs_dict = URLs_dict
        self.synops_dict = synopsys_dict
        self.tcast_dict = topcast_dict

        self.ids_generated = []
        self.batch_training_dict = {}

        self.developers = QtGui.QLabel('        Developed by:\n\nDaniel Caixinha - 71049\nJoão Granchinho - 54766', self)
        self.developers.move(732, 25)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.developers.setFont(self.font)

        self.pic1 = QtGui.QPixmap('icons/ist_logo.jpg')
        self.ist_img = QtGui.QLabel(self)
        self.ist_img.setPixmap(self.pic1)
        self.ist_img.move(375, 5)
        self.ist_img.resize(200, 90)
        self.ist_img.setScaledContents(True)

        self.pic2 = QtGui.QPixmap('icons/movie_logo.png')
        self.icon_img = QtGui.QLabel(self)
        self.icon_img.setPixmap(self.pic2)
        self.icon_img.move(40, 5)
        self.icon_img.resize(150, 90)
        self.icon_img.setScaledContents(True)

        self.rate_msg = QtGui.QLabel('Please rate the movie: ', self)
        self.rate_msg.move(50, 478)
        self.rate_msg.setScaledContents(True)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.rate_msg.setFont(self.font)

        self.rates_left = QtGui.QLabel('(Rate 15 movies with the same User ID to get recommendations)', self)
        self.rates_left.move(50, 549)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.rates_left.setFont(self.font)

        self.uid = QtGui.QLabel('User ID:', self)
        self.uid.move(50, 524)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.uid.setFont(self.font)

        self.uid_textbox = QtGui.QLineEdit(self)
        self.uid_textbox.move(110, 516)
        self.uid_textbox.setText('')
        self.uid_textbox.setMaxLength(3)
        self.uid_textbox.resize(40, 29)

        self.rates_left = QtGui.QLabel('Rating:', self)
        self.rates_left.move(160, 524)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.rates_left.setFont(self.font)

        self.rate_textbox = QtGui.QLineEdit(self)
        self.rate_textbox.move(215, 516)
        self.rate_textbox.setText('')
        self.rate_textbox.setMaxLength(1)
        self.rate_textbox.resize(40, 29)

        self.rate_button = QtGui.QPushButton('Rate!', self)
        self.rate_button.clicked.connect(self.handle_rate_button)
        self.rate_button.move(265, 518)
        self.rate_button.setStyleSheet('QPushButton {background-color: grey; color: white}')

        self.movie_name = QtGui.QLineEdit('', self)
        self.movie_name.move(47, 493)
        self.movie_name.resize(350, 21)
        self.movie_name.setReadOnly(True)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.movie_name.setFont(self.font)

        self.error_box = QtGui.QLabel('                                                                         ', self)
        self.error_box.move(50, 579)
        self.font_red = QtGui.QFont()
        self.font_red.setBold(True)
        self.error_box.setFont(self.font)
        self.palette = QtGui.QPalette()
        self.palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
        self.error_box.setPalette(self.palette)

        self.error_box2 = QtGui.QLabel('                                                                        ', self)
        self.error_box2.move(550, 579)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.error_box2.setFont(self.font)
        self.palette2 = QtGui.QPalette()
        self.palette2.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
        self.error_box2.setPalette(self.palette2)

        self.uid2 = QtGui.QLabel('User ID:', self)
        self.uid2.move(550, 488)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.uid2.setFont(self.font)

        self.uid_textbox2 = QtGui.QLineEdit(self)
        self.uid_textbox2.move(610, 480)
        self.uid_textbox2.setText('')
        self.uid_textbox2.setMaxLength(4)
        self.uid_textbox2.resize(40, 29)

        self.recommend_button = QtGui.QPushButton('Get random movie classification!', self)
        self.recommend_button.clicked.connect(self.handle_recommend_button)
        self.recommend_button.move(660, 482)
        self.recommend_button.setStyleSheet('QPushButton {background-color: grey; color: white}')

        self.for_movie_name = QtGui.QLabel('For the movie:', self)
        self.for_movie_name.move(550, 514)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.for_movie_name.setFont(self.font)
        self.for_movie_name.hide()

        self.recommend_movie_name = QtGui.QLineEdit('', self)
        self.recommend_movie_name.move(547, 530)
        self.recommend_movie_name.resize(350, 21)
        self.recommend_movie_name.setReadOnly(True)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.recommend_movie_name.setFont(self.font)
        self.recommend_movie_name.hide()

        self.recommend_rate_text = QtGui.QLabel('The system predicts a rating of:', self)
        self.recommend_rate_text.move(550, 560)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.recommend_rate_text.setFont(self.font)
        self.recommend_rate_text.hide()

        self.recommend_rate_value = QtGui.QLineEdit('', self)
        self.recommend_rate_value.move(770, 556)
        self.recommend_rate_value.resize(45, 21)
        self.recommend_rate_value.setReadOnly(True)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.recommend_rate_value.setFont(self.font)
        self.recommend_rate_value.hide()

        self.movie_img = QtGui.QLabel(self)
        self.movie_img.move(50, 95)

        self.movie_img2 = QtGui.QLabel(self)
        self.movie_img2.move(550, 95)

        self.setGeometry(700, 700, 960, 600)
        self.setStyleSheet("background-color: white;")
        self.setWindowTitle('Movie Recommendation System - EADW Project')

        # Init the window's logic now (after everything is set)
        self.current_mov_id = random.randint(1, 1682)

        self.ids_generated.append(self.current_mov_id)

        current_movie_name = self.movie_name_dict[self.current_mov_id]
        movie_img_URL = self.URLs_dict[self.current_mov_id]

        if movie_img_URL == 'no_image':
            self.updateImg("no_cover.png")
        else:
            urllib.urlretrieve(movie_img_URL, "movie_rate.jpg")
            self.updateImg("movie_rate.jpg")

        self.movie_name.setText(current_movie_name)

        self.center()
        self.show()

    #Tries to center the window on the screen
    def center(self):

        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    #Override of the closeEvent, to ask the user before he closes the program
    def closeEvent(self, event):
        
        reply = QtGui.QMessageBox.question(self, 'Message', 'Are you sure you want to quit?', QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    #Function that sets the image on the left (rated movie) to the parameter 'img'
    def updateImg(self, img):

        pixmp = QtGui.QPixmap(img)
        self.movie_img.setPixmap(pixmp)
        self.movie_img.resize(345, 380)
        self.movie_img.setScaledContents(True)
        self.movie_img.show()

    #Function that sets the image on the right (recommended movie) to the parameter 'img'
    def updateImg2(self, img):

        pixmp = QtGui.QPixmap(img)
        self.movie_img2.setPixmap(pixmp)
        self.movie_img2.resize(345, 380)
        self.movie_img2.setScaledContents(True)
        self.movie_img2.show()

    #Function that gets the rate and User ID from the textboxes, updates the training dict and gives a random movie
    #for the user to rate
    def handle_rate_button(self):

        uid = self.uid_textbox.text()
        rating = self.rate_textbox.text()

        try:
            uid = int(uid)
        except ValueError:
            self.error_box.setText('Please insert a User ID between 1 and 943!')
            return

        if uid not in range(1, 944):
            self.error_box.setText('Please insert a User ID between 1 and 943!')
            return

        try:
            rating = int(rating)
        except ValueError:
            self.error_box.setText('Please insert a rating between 1 and 5!')
            return

        if rating not in range(1, 6):
            self.error_box.setText('Please insert a rating between 1 and 5!')
        else:
            self.error_box.setText('')
            if uid not in self.batch_training_dict.keys():
                self.batch_training_dict[uid] = [(self.current_mov_id, rating)]
            else:
                self.batch_training_dict[uid].append((self.current_mov_id, rating))

            new_movie_id = random.randint(1, 1682)
            while new_movie_id in self.ids_generated:
                new_movie_id = random.randint(1, 1682)

            self.current_mov_id = new_movie_id
            self.ids_generated.append(new_movie_id)

            current_movie_name = self.movie_name_dict[self.current_mov_id]
            self.movie_name.setText(current_movie_name)

            movie_img_URL = self.URLs_dict[self.current_mov_id]

            if movie_img_URL == 'no_image':
                self.updateImg("no_cover.png")
            else:
                urllib.urlretrieve(movie_img_URL, "movie_rate.jpg")
                self.updateImg("movie_rate.jpg")

    #Function that sets the system model according to what's in training_dict and gives a score prediction for a
    #random generated movie ID
    def handle_recommend_button(self):

        uid_2 = self.uid_textbox2.text()

        try:
            uid_2 = int(uid_2)
        except ValueError:
            self.error_box2.setText('Please insert a User ID between 1 and 943!')
            return

        if uid_2 not in range(1, 944):
            self.error_box2.setText('Please insert a User ID between 1 and 943!')
            return

        if uid_2 not in self.batch_training_dict.keys():
            self.error_box2.setText('This User ID hasn\'t rated any item yet!')
            return

        if len(self.batch_training_dict[uid_2]) < 15:
            self.error_box2.setText('This User ID hasn\'t rated 15 items yet!')
            return

        self.error_box2.setText('')

        f = open('online_mode.base', 'w')

        f_init = open('online_mode_init.base', 'r')
        all_lines = f_init.read()
        f_init.close()

        f.write(all_lines)

        for user_id in self.batch_training_dict:
            for movie_tuple in self.batch_training_dict[user_id]:
                f.write(str(user_id) + '\t' + str(movie_tuple[0]) + '\t' + str(movie_tuple[1]) + '\n')

        f.close()

        items_dict, users_dict = get_dictionaries('online_mode.base')

        recommend_mov_id = random.randint(1, 1682)
        while recommend_mov_id in self.ids_generated:
            recommend_mov_id = random.randint(1, 1682)

        self.ids_generated.append(recommend_mov_id)

        # print 'THE UID2 IS', uid_2, 'THE RECOMMENDEDMOVID IS', recommend_mov_id
        #
        # print 'O SYNOPS DICT E', self.synops_dict
        # print 'O TOPCAST DICT E', self.tcast_dict

        score_prediction = predict_score_item_based(uid_2, recommend_mov_id, users_dict, items_dict, self.synops_dict, self.tcast_dict)

        self.for_movie_name.show()

        recommend_movie_name = self.movie_name_dict[recommend_mov_id]
        self.recommend_movie_name.show()
        self.recommend_movie_name.setText(recommend_movie_name)

        self.recommend_rate_text.show()
        self.recommend_rate_value.setText(str(round(score_prediction, 2)))
        self.recommend_rate_value.show()

        movie_img1_URL = self.URLs_dict[recommend_mov_id]

        if movie_img1_URL == 'no_image':
            self.updateImg2("no_cover.png")
        else:
            urllib.urlretrieve(movie_img1_URL, "movie_recommend.jpg")
            self.updateImg2("movie_recommend.jpg")

#Method that inits the Window's Class (called from main.py)
def init_online_mode(mvie_names_dict, URLs_dict, synps_dict, tcast_dict):
    
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('EADW Project')
    app.setWindowIcon(QtGui.QIcon('icons/ist_logo_1.png'))
    window = EADW_Proj_Window(mvie_names_dict, URLs_dict, synps_dict, tcast_dict)
    window.show()
    sys.exit(app.exec_())