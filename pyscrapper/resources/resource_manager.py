import os

def get_phantom_driver_path():
    filename = 'phantomjs'
    my_name =__file__
    try:
        lstIndex = my_name.rindex(os.path.sep)
        my_name = my_name[:lstIndex+1] + filename
    except:
        return None
    return my_name