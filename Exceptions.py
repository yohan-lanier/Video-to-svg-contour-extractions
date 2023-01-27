import os

def check_if_saving_directory_exists(path):
    try :
        test_a_path(path)
        return path
    except SavePathAlreadyExists as spae:
        np = spae.ask_for_new_directory_name()
        np = test_a_path(np)
        return np

def test_a_path(path):
    if os.path.exists(path):
        raise SavePathAlreadyExists(path)
    else:
        return path

def check_if_input_file_exists(file):
    try:
        test_input_file(file)
        return file
    except InputFileNotFound as ifnf:
        nif = ifnf.ask_for_input_file()
        test_input_file(nif)
        return nif

def test_input_file(file):
    if not os.path.exists(file):
        raise InputFileNotFound(file)

def check_input_format(file):
    try:
        test_input_format(file)
        return file
    except WrongInputFormat as wif:
        file = wif.ask_for_input_file()
        test_input_format(file)
        return file


def test_input_format(file):
    ext = file.split('.')[-1]
    if ext not in ['mp4', 'mpeg', 'avi']:
        raise WrongInputFormat(file)

class SavePathAlreadyExists(Exception):
    '''
    Exception in case saving path already exists
    '''
    def __init__(self, sp):
        super().__init__()
        self._value = sp

    def ask_for_new_directory_name(self):
        print('\n-------------------------------------')
        print(f"Saving directory '{self._value}' already exists. Please input another saving directory name")
        print('-------------------------------------\n')
        sp = input()
        return sp

class InputFileNotFound(Exception):
    '''
    Exception in case saving path already exists
    '''
    def __init__(self, file):
        super().__init__()
        self._value = file

    def ask_for_input_file(self):
        print('\n-------------------------------------')
        print(f"Input file '{self._value}' not found. Please input another video")
        print('-------------------------------------\n')
        file = input()
        return file

class WrongInputFormat(Exception):
    def __init__(self, file):
        super().__init__()
        self._value=file
    
    def ask_for_input_file(self):
        print('\n-------------------------------------')
        print(f"Input file '{self._value}' fomat not supported. Please input another video with type .mp4, .avi or .mpeg")
        print('-------------------------------------\n')
        file = input()
        return file