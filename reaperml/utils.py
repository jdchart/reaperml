import os
import soundfile as sf
import subprocess
import wave

def get_files(path, **kwargs):
    types = kwargs.get('types', ['.wav'])
    mode = kwargs.get('mode', 'file')
    recursive = kwargs.get('recursive', False)
    file_list = []

    if recursive:
        for pat, subdirs, files in os.walk(path):
            for name in files:
                if get_file_extension(name) in types:
                    if mode == 'file':
                        file_list.append(name)
                    elif mode == 'path':
                        file_list.append(os.path.join(pat, name))
    else:
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

    f = wave.open(src, mode = 'rb')
    return_data['path'] = src ## TO CHECK - was this just filename?
    return_data['frames'] = f.getnframes()
    return_data['samplerate'] = f.getframerate()
    return_data['channels'] = f.getnchannels()
    return_data['ms'] = (f.getnframes() / f.getframerate()) * 1000

    '''
    with sf.SoundFile(src, 'r+') as f:
        return_data['path'] = f.name
        return_data['frames'] = f.frames
        return_data['samplerate'] = f.samplerate
        return_data['channels'] = f.channels
        return_data['ms'] = (f.frames / f.samplerate) * 1000
    f.close()
    '''
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

def convert_to_wav(in_path, out_path):
    command_array = ['ffmpeg', '-i', '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '44100']
    command_array.insert(2, in_path)
    command_array.append(out_path)

    subprocess.call(command_array)

def replace_extension(to_replace, new_extension):
    pre, ext = os.path.splitext(to_replace)
    return pre + new_extension

def create_direc(to_create):
    isExist = os.path.exists(to_create)

    if not isExist:
        os.makedirs(to_create)

def append_list(original_list, to_append):
    return_list = original_list
    for item in to_append:
        return_list.append(item)
    return return_list

def flatten_lists(list_list):
    ret_list = []
    for list in list_list:
        ret_list = append_list(ret_list, list)
    return ret_list