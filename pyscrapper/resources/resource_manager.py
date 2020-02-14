import os


def get_phantom_driver_path():
    return get_current_path() + 'phantomjs'


def get_current_path():
    my_name = __file__
    try:
        lst_index = my_name.rindex(os.path.sep)
        my_name = my_name[:lst_index+1]
    except ValueError | IndexError:
        return None
    return my_name
