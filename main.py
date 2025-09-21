import numpy as np
from tkinter import filedialog
import tkinter as tk
from tkinter import *
from tkinter import messagebox


def find_quarter_g03(x_value, y_value, x_m_value, y_m_value):  # quarter def only for ccw
    if x_value > x_m_value and y_value >= y_m_value:
        q = 1
    elif x_value <= x_m_value and y_value > y_m_value:
        q = 2
    elif x_value < x_m_value and y_value <= y_m_value:
        q = 3
    else:
        q = 4
    return q


def find_quarter_g02(x_value, y_value, x_m_value, y_m_value):  # quarter def only for cw
    if x_value >= x_m_value and y_value > y_m_value:
        q = 1
    elif x_value < x_m_value and y_value >= y_m_value:
        q = 2
    elif x_value <= x_m_value and y_value < y_m_value:
        q = 3
    else:
        q = 4
    return q


def set_pos(letter, w_list, n_list):  # write the new set positions
    i = 0
    while i < len(w_list):
        if w_list[i][0] == letter:
            return n_list[i]
        i += 1


def check_vec(val_set, val_pos, vec_old):
    if val_set > val_pos:
        vec_set = 1
    elif val_set < val_pos:
        vec_set = -1
    else:
        vec_set = vec_old
    return vec_set


def find_letter(letter, lst):  # check if letter is in list
    return any(letter in word for word in lst)


def write_compensation(_dir, _vec_set, _vec, _lash, _pos, file):
    if _vec_set != _vec and _vec_set != 0:
        _comp = _lash * _vec_set
        file.write('(comp_start-------------)\nG91\nG00 ' + _dir + str(_comp) + '\nG90\n')  # G91 increment G90 absolut
        file.write('G92 ' + _dir + str(_pos) + '\n')  # G92 set position
        file.write('G0 ' + _dir + str(_pos) + '\n(comp_end--------------)\n')  # G92 set position


def write_g02(x, y, i_set, j_set, f_out):
    f_out.write('G02' + ' X' + str(x) + ' ' + 'Y' + str(y) + ' ' + 'i' + str(i_set) + ' ' + 'j' + str(
        j_set) + ' ' + '\n')


def write_g03(x, y, i_set, j_set, f_out):
    f_out.write('G03' + ' X' + str(x) + ' ' + 'Y' + str(y) + ' ' + 'i' + str(i_set) + ' ' + 'j' + str(
        j_set) + ' ' + '\n')


def askopenfile():
    global f1
    f1 = filedialog.askopenfile(mode='r')
    label_open_file.config(text=f1.name, font='Arial 10')


def choose_file_write():
    global f_out1
    f_out1 = filedialog.asksaveasfile(mode='w')
    label_write_file.config(text=f_out1.name, font='Arial 10')


def main():
    # open the nc-code file create output file:
    try:
        with open(f1.name, 'r') as f, open(f_out1.name, 'w') as f_out:
            x_vec = y_vec = -1  # start vector is negative -- user needed - only needed for first line
            x_pos = y_pos = 0  # start position of machine is always at origin - only needed for first line
            x_lash = float(entryX.get())  # depends on the mechanical backlash of the machine
            y_lash = float(entryY.get())
            for line in f:
                if line:  # if the line is not empty do smth
                    line = "".join(line.split())  # remove all white spaces
                    line = line.lower()  # Make everything lower case
                    print(line)
                    # remove comments ############################################
                    if line.find('(') > -1:
                        start = line.find('(')
                        end = line.find(')') + 1
                        f_out.write(line[start:end])
                        line = line[:start] + line[end:]
                    if line.find(';') >= 1 and line.find('(') == -1:
                        start = line.find(';')
                        f_out.write(line[start:] + '\n')
                        line = line[:start]
                    ##############################################################
                    word_list = []  # make list with the letters
                    i = 0
                    while i < len(line):
                        if line[i].isalpha() == 1:
                            word_list.append((line[i], i))
                        i += 1
                    print('word_list: ', word_list)
                    ############################################################
                    # reading the values beneath the letters and making num_list
                    ############################################################
                    num_list = []
                    i = 0
                    while i <= len(word_list) - 1:  # len(word list) == how many letters are there
                        start = word_list[i][1] + 1
                        if i == len(word_list) - 1:
                            end = len(line)  # no -1 slicing ends at -1 from value already
                        else:
                            end = word_list[i + 1][1]  # no -1 slicing ends at -1 from value already
                        if start == end:  # slicing not possible if only one number
                            num = line[start]
                        else:
                            num = line[start:end]
                        num = float(num)
                        num_list.append(num)
                        i += 1
                    print('num_list: ', num_list)
                    ###########################################################
                    # find new set values
                    ###########################################################
                    if find_letter('g', word_list):
                        g_set = set_pos('g', word_list, num_list)
                    if find_letter('i', word_list):
                        i_set = set_pos('i', word_list, num_list)
                    else:
                        i_set = 0
                    if find_letter('j', word_list):
                        j_set = set_pos('j', word_list, num_list)
                    else:
                        j_set = 0
                    if find_letter('x', word_list):
                        x_set = set_pos('x', word_list, num_list)
                    if find_letter('y', word_list):
                        y_set = set_pos('y', word_list, num_list)
                    if find_letter('z', word_list, ):
                        z_set = set_pos('z', word_list, num_list)
                    ############################
                    # Linear motion compensation
                    ############################
                    if line.find('g') != -1:
                        if g_set == 0.0 or g_set == 1.0:  # if it's a linear motion 0 or 1
                            if line.find('x') != -1:  # if there is a new x-value
                                x_vec_set = check_vec(x_set, x_pos, x_vec)  # calculate vector with the set position
                                #  print('x_vec_set: ', x_vec_set)
                                #  print('x_set: ', x_set)
                                #  print('x_pos: ', x_pos)
                                write_compensation('X', x_vec_set, x_vec, x_lash, x_pos, f_out)
                                x_vec = x_vec_set
                                x_pos = x_set
                            if line.find('y') != -1:
                                y_vec_set = check_vec(y_set, y_pos, y_vec)
                                print('y_vec_set: ', y_vec_set)
                                print('y_set: ', y_set)
                                print('y_pos: ', y_pos)
                                write_compensation('Y', y_vec_set, y_vec, y_lash, y_pos, f_out)
                                y_vec = y_vec_set
                                y_pos = y_set
                            f_out.write(line + '\n')
                        #############################################################################################
                        # Arc motion compensation G2
                        #############################################################################################
                        elif g_set == 2.0:  # G2 circular motion clockwise
                            x_m = x_pos + i_set
                            y_m = y_pos + j_set
                            print('x_m', x_m, 'y_m', y_m)
                            # In which quarter is the current position
                            q_pos = find_quarter_g02(x_pos, y_pos, x_m, y_m)
                            # In which quarter is the set position
                            q_pos_set = find_quarter_g02(x_set, y_set, x_m, y_m)

                            # set start vector with comparison
                            if q_pos == 1:
                                x_vec_set = 1
                                y_vec_set = -1
                            elif q_pos == 2:
                                x_vec_set = 1
                                y_vec_set = 1
                            elif q_pos == 3:
                                x_vec_set = -1
                                y_vec_set = 1
                            else:
                                x_vec_set = -1
                                y_vec_set = -1

                            print('y_vec: ', y_vec, 'y_vec_set: ', y_vec_set)

                            # write compensation for the circle start
                            write_compensation('Y', y_vec_set, y_vec, y_lash, y_pos, f_out)
                            write_compensation('X', x_vec_set, x_vec, x_lash, x_pos, f_out)

                            r = pow(pow(x_pos - x_m, 2) + pow(y_pos - y_m, 2), 0.5)
                            print('r', r)

                            if q_pos_set == 1:
                                x_vec = 1
                                y_vec = -1
                            elif q_pos_set == 2:
                                x_vec = 1
                                y_vec = 1
                            elif q_pos_set == 3:
                                x_vec = -1
                                y_vec = 1
                            else:
                                x_vec = -1
                                y_vec = -1

                            print('q_pos', q_pos)
                            print('q_pos_set', q_pos_set)

                            # START IN Q1
                            if q_pos == 1 and q_pos_set == 1 and x_set > x_pos:
                                write_g02(x_set, y_set, i_set, j_set, f_out)
                            elif q_pos == 1 and q_pos_set == 4:
                                x = x_m + r
                                y = y_m
                                write_g02(x, y, i_set, j_set, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                if y_set < y_m:
                                    write_g02(x_set, y_set, -r, 0, f_out)
                            elif q_pos == 1 and q_pos_set == 3:
                                x = x_m + r
                                y = y_m
                                write_g02(x, y, i_set, j_set, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                x = x_m
                                y = y_m - r
                                write_g02(x, y, -r, 0, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                if x_set < x_m:

                                    write_g02(x_set, y_set, 0, r, f_out)
                            elif q_pos == 1 and q_pos_set == 2:
                                x = x_m + r
                                y = y_m
                                write_g02(x, y, i_set, j_set, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                x = x_m
                                y = y_m - r
                                write_g02(x, y, -r, 0, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                x = x_m - r
                                y = y_m
                                write_g02(x, y, 0, r, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                if y_set > y_m:

                                    write_g02(x_set, y_set, r, 0, f_out)
                            elif q_pos == 1 and q_pos_set == 1 and x_set <= x_pos:
                                x = x_m + r
                                y = y_m
                                write_g02(x, y, i_set, j_set, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                x = x_m
                                y = y_m - r
                                write_g02(x, y, -r, 0, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                x = x_m - r
                                y = y_m
                                write_g02(x, y, 0, r, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                x = x_m
                                y = y_m + r
                                write_g02(x, y, r, 0, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                if x_set > x_m:

                                    write_g02(x_set, y_set, 0, -r, f_out)

                            # START IN Q2
                            elif q_pos == 2 and q_pos_set == 2 and x_set > x_pos:
                                write_g02(x_set, y_set, i_set, j_set, f_out)
                            elif q_pos == 2 and q_pos_set == 1:
                                x = x_m
                                y = y_m + r
                                write_g02(x, y, i_set, j_set, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                if x_set > x_m:

                                    write_g02(x_set, y_set, 0, -r, f_out)
                            elif q_pos == 2 and q_pos_set == 4:
                                x = x_m
                                y = y_m + r
                                write_g02(x, y, i_set, j_set, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                x = x_m + r
                                y = y_m
                                write_g02(x, y, 0, -r, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                if y_set < y_m:

                                    write_g02(x_set, y_set, -r, 0, f_out)
                            elif q_pos == 2 and q_pos_set == 3:
                                x = x_m
                                y = y_m + r
                                write_g02(x, y, i_set, j_set, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                x = x_m + r
                                y = y_m
                                write_g02(x, y, 0, -r, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                x = x_m
                                y = y_m - r
                                write_g02(x, y, -r, 0, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                if x_set < x_m:

                                    write_g02(x_set, y_set, 0, -r, f_out)
                            elif q_pos == 2 and q_pos_set == 2 and x_set <= x_pos:
                                x = x_m
                                y = y_m + r
                                write_g02(x, y, i_set, j_set, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                x = x_m + r
                                y = y_m
                                write_g02(x, y, 0, -r, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                x = x_m
                                y = y_m - r
                                write_g02(x, y, -r, 0, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                x = x_m - r
                                y = y_m
                                write_g02(x, y, 0, r, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                if y_set > y_m:

                                    write_g02(x_set, y_set, r, 0, f_out)

                            # START IN Q4
                            elif q_pos == 4 and q_pos_set == 4 and x_set < x_pos:
                                write_g02(x_set, y_set, i_set, j_set, f_out)
                            elif q_pos == 4 and q_pos_set == 3:
                                x = x_m
                                y = y_m - r
                                write_g02(x, y, i_set, j_set, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                if x_set < x_m:
                                    write_g02(x_set, y_set, 0, r, f_out)
                            elif q_pos == 4 and q_pos_set == 2:
                                x = x_m
                                y = y_m - r
                                write_g02(x, y, i_set, j_set, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                x = x_m - r
                                y = y_m
                                write_g02(x, y, 0, r, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                if y_set > y_m:

                                    write_g02(x_set, y_set, r, 0, f_out)
                            elif q_pos == 4 and q_pos_set == 1:
                                x = x_m
                                y = y_m - r
                                write_g02(x, y, i_set, j_set, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                x = x_m - r
                                y = y_m
                                write_g02(x, y, 0, r, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                x = x_m
                                y = y_m + r
                                write_g02(x, y, r, 0, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                if x_set > x_m:

                                    write_g02(x_set, y_set, 0, -r, f_out)
                            elif q_pos == 4 and q_pos_set == 4 and x_set >= x_pos:
                                x = x_m
                                y = y_m - r
                                write_g02(x, y, i_set, j_set, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                x = x_m - r
                                y = y_m
                                write_g02(x, y, 0, r, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                x = x_m
                                y = y_m + r
                                write_g02(x, y, r, 0, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                x = x_m + r
                                y = y_m
                                write_g02(x, y, 0, -r, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                if y_set < y_m:
                                    write_g02(x_set, y_set, -r, 0, f_out)

                            # START IN Q3
                            elif q_pos == 3 and q_pos_set == 3 and x_set < x_pos:
                                write_g02(x_set, y_set, i_set, j_set, f_out)
                            elif q_pos == 3 and q_pos_set == 2:
                                x = x_m - r
                                y = y_m
                                write_g02(x, y, i_set, j_set, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                if y_set > y_m:

                                    write_g02(x_set, y_set, r, 0, f_out)
                            elif q_pos == 3 and q_pos_set == 1:
                                x = x_m - r
                                y = y_m
                                write_g02(x, y, i_set, j_set, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                x = x_m
                                y = y_m + r
                                write_g02(x, y, r, 0, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                if x_set > x_m:

                                    write_g02(x_set, y_set, 0, -r, f_out)
                            elif q_pos == 3 and q_pos_set == 4:
                                x = x_m - r
                                y = y_m
                                write_g02(x, y, i_set, j_set, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                x = x_m
                                y = y_m + r
                                write_g02(x, y, r, 0, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                x = x_m + r
                                y = y_m
                                write_g02(x, y, 0, -r, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                if y_set < y_m:

                                    write_g02(x_set, y_set, -r, 0, f_out)
                            elif q_pos == 3 and q_pos_set == 3 and x_set >= x_pos:
                                x = x_m - r
                                y = y_m
                                write_g02(x, y, i_set, j_set, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                x = x_m
                                y = y_m + r
                                write_g02(x, y, r, 0, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                x = x_m + r
                                y = y_m
                                write_g02(x, y, 0, -r, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                x = x_m
                                y = y_m - r
                                write_g02(x, y, -r, 0, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                if y_set > y_m:

                                    write_g02(x_set, y_set, 0, r, f_out)

                            x_pos = x_set
                            y_pos = y_set

                        ################################################################################################
                        # Arc motion compensation G3
                        ################################################################################################
                        elif g_set == 3.0:  # G2 circular motion counterclockwise
                            x_m = x_pos + i_set
                            y_m = y_pos + j_set
                            print('x_m', x_m, 'y_m', y_m)
                            # In which quarter is the current position
                            q_pos = find_quarter_g03(x_pos, y_pos, x_m, y_m)
                            # In which quarter is the set position
                            q_pos_set = find_quarter_g03(x_set, y_set, x_m, y_m)

                            # set start vector with comparison
                            if q_pos == 1:
                                x_vec_set = -1
                                y_vec_set = 1
                            elif q_pos == 2:
                                x_vec_set = -1
                                y_vec_set = -1
                            elif q_pos == 3:
                                x_vec_set = 1
                                y_vec_set = -1
                            else:
                                x_vec_set = 1
                                y_vec_set = 1

                            print('y_vec: ', y_vec, 'y_vec_set: ', y_vec_set)

                            # write compensation for the circle start
                            write_compensation('Y', y_vec_set, y_vec, y_lash, y_pos, f_out)
                            write_compensation('X', x_vec_set, x_vec, x_lash, x_pos, f_out)

                            r = pow(pow(x_pos - x_m, 2) + pow(y_pos - y_m, 2), 0.5)
                            print('r', r)

                            if q_pos_set == 1:  # For next cycle
                                x_vec = -1
                                y_vec = 1
                            elif q_pos_set == 2:
                                x_vec = -1
                                y_vec = -1
                            elif q_pos_set == 3:
                                x_vec = 1
                                y_vec = -1
                            else:
                                x_vec = 1
                                y_vec = 1

                            # START IN Q1
                            if q_pos == 1 and q_pos_set == 1 and x_set < x_pos:
                                write_g03(x_set, y_set, i_set, j_set, f_out)
                            elif q_pos == 1 and q_pos_set == 2:
                                x = x_m
                                y = y_m + r
                                write_g03(x, y, i_set, j_set, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                if x_set < x_m:

                                    write_g03(x_set, y_set, 0, -r, f_out)
                            elif q_pos == 1 and q_pos_set == 3:
                                x = x_m
                                y = y_m + r
                                write_g03(x, y, i_set, j_set, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                x = x_m - r
                                y = y_m
                                write_g03(x, y, 0, -r, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                if y_set < y_m:

                                    write_g03(x_set, y_set, r, 0, f_out)
                            elif q_pos == 1 and q_pos_set == 4:
                                x = x_m
                                y = y_m + r
                                write_g03(x, y, i_set, j_set, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                x = x_m - r
                                y = y_m
                                write_g03(x, y, 0, -r, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                x = x_m
                                y = y_m - r
                                write_g03(x, y, r, 0, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                if x_set > x_m:

                                    write_g03(x_set, y_set, r, 0, f_out)
                            elif q_pos == 1 and q_pos_set == 1 and x_set >= x_pos:
                                x = x_m
                                y = y_m + r
                                write_g03(x, y, i_set, j_set, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                x = x_m - r
                                y = y_m
                                write_g03(x, y, 0, -r, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                x = x_m
                                y = y_m - r
                                write_g03(x, y, r, 0, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                x = x_m + r
                                y = y_m
                                write_g03(x, y, 0, r, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                if y_set > y_m:

                                    write_g03(x_set, y_set, -r, 0, f_out)

                            # START IN Q2
                            elif q_pos == 2 and q_pos_set == 2 and x_set < x_pos:
                                write_g03(x_set, y_set, i_set, j_set, f_out)
                            elif q_pos == 2 and q_pos_set == 3:
                                x = x_m - r
                                y = y_m
                                write_g03(x, y, i_set, j_set, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                if y_set < y_m:
                                    write_g03(x_set, y_set, r, 0, f_out)
                            elif q_pos == 2 and q_pos_set == 4:
                                x = x_m - r
                                y = y_m
                                write_g03(x, y, i_set, j_set, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                x = x_m
                                y = y_m - r
                                write_g03(x, y, r, 0, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                if x_set > x_m:

                                    write_g03(x_set, y_set, 0, r, f_out)
                            elif q_pos == 2 and q_pos_set == 1:
                                x = x_m - r
                                y = y_m
                                write_g03(x, y, i_set, j_set, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                x = x_m
                                y = y_m - r
                                write_g03(x, y, r, 0, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                x = x_m + r
                                y = y_m
                                write_g03(x, y, 0, r, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                if y_set > y_m:

                                    write_g03(x_set, y_set, -r, 0, f_out)
                            elif q_pos == 2 and q_pos_set == 2 and x_set >= x_pos:
                                x = x_m - r
                                y = y_m
                                write_g03(x, y, i_set, j_set, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                x = x_m
                                y = y_m - r
                                write_g03(x, y, r, 0, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                x = x_m + r
                                y = y_m
                                write_g03(x, y, 0, r, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                x = x_m
                                y = y_m + r
                                write_g03(x, y, -r, 0, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                if x_set < x_m:

                                    write_g03(x_set, y_set, 0, -r, f_out)

                            # START IN Q3
                            elif q_pos == 3 and q_pos_set == 3 and x_set > x_pos:
                                write_g03(x_set, y_set, i_set, j_set, f_out)
                            elif q_pos == 3 and q_pos_set == 4:
                                x = x_m
                                y = y_m - r
                                write_g03(x, y, i_set, j_set, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                if x_set > x_m:

                                    write_g03(x_set, y_set, 0, r, f_out)
                            elif q_pos == 3 and q_pos_set == 1:
                                x = x_m
                                y = y_m - r
                                write_g03(x, y, i_set, j_set, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                x = x_m + r
                                y = y_m
                                write_g03(x, y, 0, r, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                if y_set > y_m:

                                    write_g03(x_set, y_set, -r, 0, f_out)
                            elif q_pos == 3 and q_pos_set == 2:
                                x = x_m
                                y = y_m - r
                                write_g03(x, y, i_set, j_set, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                x = x_m + r
                                y = y_m
                                write_g03(x, y, 0, r, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                x = x_m
                                y = y_m + r
                                write_g03(x, y, -r, 0, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                if x_set < x_m:

                                    write_g03(x_set, y_set, 0, -r, f_out)
                            elif q_pos == 3 and q_pos_set == 3 and x_set <= x_pos:
                                x = x_m
                                y = y_m - r
                                write_g03(x, y, i_set, j_set, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                x = x_m + r
                                y = y_m
                                write_g03(x, y, 0, r, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                x = x_m
                                y = y_m + r
                                write_g03(x, y, -r, 0, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                x = x_m - r
                                y = y_m
                                write_g03(x, y, 0, -r, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                if y_set < y_m:

                                    write_g03(x_set, y_set, r, 0, f_out)

                            # START IN Q4
                            elif q_pos == 4 and q_pos_set == 4 and x_set > x_pos:
                                write_g03(x_set, y_set, i_set, j_set, f_out)
                            elif q_pos == 4 and q_pos_set == 1:
                                x = x_m + r
                                y = y_m
                                write_g03(x, y, i_set, j_set, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                if y_set > y_m:

                                    write_g03(x_set, y_set, -r, 0, f_out)
                            elif q_pos == 4 and q_pos_set == 2:
                                x = x_m + r
                                y = y_m
                                write_g03(x, y, i_set, j_set, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                x = x_m
                                y = y_m + r
                                write_g03(x, y, -r, 0, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                if x_set < x_m:

                                    write_g03(x_set, y_set, 0, -r, f_out)
                            elif q_pos == 4 and q_pos_set == 3:
                                x = x_m + r
                                y = y_m
                                write_g03(x, y, i_set, j_set, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                x = x_m
                                y = y_m + r
                                write_g03(x, y, -r, 0, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                x = x_m - r
                                y = y_m
                                write_g03(x, y, 0, -r, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                if y_set < y_m:

                                    write_g03(x_set, y_set, r, 0, f_out)
                            elif q_pos == 4 and q_pos_set == 4 and x_set <= x_pos:
                                x = x_m + r
                                y = y_m
                                write_g03(x, y, i_set, j_set, f_out)
                                write_compensation('X', -1, 1, x_lash, x, f_out)
                                x = x_m
                                y = y_m + r
                                write_g03(x, y, -r, 0, f_out)
                                write_compensation('Y', -1, 1, y_lash, y, f_out)
                                x = x_m - r
                                y = y_m
                                write_g03(x, y, 0, -r, f_out)
                                write_compensation('X', 1, -1, x_lash, x, f_out)
                                x = x_m
                                y = y_m - r
                                write_g03(x, y, r, 0, f_out)
                                write_compensation('Y', 1, -1, y_lash, y, f_out)
                                if x_set > x_m:

                                    write_g03(x_set, y_set, 0, r, f_out)

                            x_pos = x_set
                            y_pos = y_set


                            print('x_m: ', x_m, ' ,y_m: ', y_m, ' ,x_set: ', x_set, ' ,y_set: ', y_set)
                            print('q_pos: ', q_pos)
                            print('q_pos_set: ', q_pos_set)

                    else:
                        f_out.write(line + '\n')
                else:
                    f_out.write(line + '\n')

                print('_________')

        messagebox.showinfo(title=None, message='Successfully compensated')

    except:
        messagebox.showerror('Python Error', 'Compensation Failed!')

# if __name__ == '__main__':
#     main()

root = Tk()
root.title("Backlash Compensation")
root.geometry("1000x350")
input_file = tk.StringVar(root)
#tk.Button(root, text="Choose G-Code File", command=choose_file())

#tk.Button(root, text="Choose G-Code File", command=choose_file()).grid()
button_open_file = tk.Button(root, text="Choose G-Code File", command=askopenfile, font='Arial 10')
button_write = tk.Button(root, text="Choose File to create", command=choose_file_write, font='Arial 10')
button_start = tk.Button(root, text="Start Compensation", command=main, font='Arial 10')

#Create an Empty Label to Read the content of the File
label_open_file = Label(root, text="", font='Arial 10')
label_write_file = Label(root, text="", font='Arial 10')
label_X_Backlash = Label(root, text="X-Backlash", font='Arial 10')
label_Y_Backlash = Label(root, text="Y-Backlash", font='Arial 10')
entryX = tk.Entry(root)
entryY = tk.Entry(root)

#label = tk.Label(root, fg="dark green")
#label.pack()
#counter_label(label)
#button = tk.Button(root, text='Stop', width=25, command=root.destroy)
button_open_file.pack()
label_open_file.pack()
button_write.pack()
label_write_file.pack()
label_X_Backlash.pack()
entryX.pack()
label_Y_Backlash.pack()
entryY.pack()
button_start.pack()
root.mainloop()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
