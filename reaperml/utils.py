import os
import soundfile as sf

def get_files(path, **kwargs):
    types = kwargs.get('types', ['.wav'])
    mode = kwargs.get('mode', 'file')

    if mode == 'file':
        file_list = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and get_file_extension(f) in types]
    elif mode == 'path':
        file_list = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and get_file_extension(f) in types]
    
    return file_list

def get_file_extension(path):
    return os.path.splitext(path)[1]

def get_filename(path):
    return os.path.basename(path)

def get_folder(path):
    return os.path.dirname(path)

def process_meta_data(src):
    return_data = {}
    with sf.SoundFile(src, 'r+') as f:
        return_data['path'] = f.name
        return_data['frames'] = f.frames
        return_data['samplerate'] = f.samplerate
        return_data['channels'] = f.channels
        return_data['ms'] = (f.frames / f.samplerate) * 1000
    f.close()
    return return_data

def make_index_array(num_elements):
    to_return = []
    for count in range(num_elements):
        to_return.append(count)
    return to_return

def sf_to_np(path):
    # Convert the contents of a soundfile to a numpy array.
    try:
        # Retieve the contents of the soundfile and the sample rate.
        t_data, _ = sf.read(path)
        # Not sure hy the data needs to be transposed here...
        return t_data.transpose()
    except:
        print(f'Could not read: {path}')

def dict_equals(dict1, dict2):
    if len(dict1) != len(dict2):
        return False
    else:
        same_items = {k: dict1[k] for k in dict1 if k in dict2 and dict1[k] == dict2[k]}
        if len(same_items) == len(dict1) and len(same_items) == len(dict2):
            return True
        else:
            return False

def create_empty_2d_array(num_entries):
    main_array = []
    for i in range(num_entries):
        main_array.append([])
    return main_array