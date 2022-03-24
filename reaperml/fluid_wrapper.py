'''
A set of functions for interfacing with the FluCoMa CLI Tools in Python.
Credit to James Bradbury who did most of the leg work on this stuff.
I've essentially built his work again in a way that makes sense to me, with a few additions.
However, the core of this - notably the subprocess stuff, was made by him.
'''

'''
TO DO:
- Derivs for label parsing (currently only works with no derivs)
- Channels for label parsing (currently defaults to mono)
- Possibilities for slice end/start (done now i think)
- More than 2 chans breaks shit
- parse labels and parse to keep array same method
- make it always check for and create TEMPORARY DATA if needed.
'''

# Requirements
import tempfile
import os
import shutil
import subprocess
import json
from matplotlib.pyplot import axis
import numpy as np
import math
import utils

module_direc = os.path.dirname(os.path.realpath(__file__))
np.set_printoptions(precision = 3, suppress = True)

class Collection:
    def __init__(self, **kwargs):
        self.slices = []
        self.name = kwargs.get('name', 'Untitled Collection')
        if 'folder' in kwargs:
            self.folder = kwargs.get('folder')
            self.temp_folder = False
        else:
            self.folder = tempfile.mkdtemp(prefix = os.path.join(module_direc, 'Temporary Data/'))
            self.temp_folder = True
        if 'file' in kwargs:
            self.read(kwargs.get('file'))

    def __del__(self):
        if self.temp_folder:
            shutil.rmtree(self.folder)

    def __repr__(self):
        return "Collection()"

    def __str__(self):
        return 'Collection: ' + self.name + '. ' + str(len(self.slices)) + ' slices.'

    def append_slice(self, src, **kwargs):
        new_slice = Slice(src, **kwargs)
        new_slice.write(os.path.join(self.folder, new_slice.name + '.json'))
        self.slices.append(os.path.join(self.folder, new_slice.name + '.json'))

    def append_slices(self, src_list):
        for file_path in src_list:
            new_slice = Slice(file_path)
            new_slice.write(os.path.join(self.folder, new_slice.name + '.json'))
            self.slices.append(os.path.join(self.folder, new_slice.name + '.json'))

    def read(self, in_path):
        if self.temp_folder:
            shutil.rmtree(self.folder)
            
        with open(in_path) as json_file:
            load_data = json.load(json_file)
            
            self.slices = load_data["slices"]
            self.name = load_data["name"]
            self.folder = load_data["folder"]
            self.temp_folder = load_data["temp_folder"]

    def write(self, destination_path, **kwargs):
        if self.temp_folder:
            dest_folder = utils.get_folder(destination_path)
            new_slice_list = []
            for slice in self.slices:
                this_slice = Slice(slice)
                this_slice.write(os.path.join(dest_folder, this_slice.name + '.json'))
                new_slice_list.append(os.path.join(dest_folder, this_slice.name + '.json'))
            self.slices = new_slice_list
            shutil.rmtree(self.folder)
            self.folder = dest_folder
            self.temp_folder = False
        
        output_data = {
            "name" : self.name,
            "slices" : self.slices,
            "folder" : self.folder,
            "temp_folder" : self.temp_folder
        }

        with open(destination_path, 'w') as outfile:
            json.dump(output_data, outfile, indent = kwargs.get('indent', 0))
        
    def get_description(self, slice, process_name, **kwargs):
        to_return = None

        for description in slice.descriptions:
            # Check, if is same as given, return
            if description.process_name == process_name:
                # now check params and stuff:
                descriptor_params = kwargs.get('descriptor_params', {})
                statistic_params = kwargs.get('statistic_params', {})
                if utils.dict_equals(descriptor_params, description.descriptor_params) and utils.dict_equals(statistic_params, description.statistic_params):
                    descriptors_to_keep = self.parse_to_keep_array(kwargs.get('descriptors_to_keep', []), process_name, descriptor_params)
                    statistics_to_keep = self.parse_to_keep_array(kwargs.get('statistics_to_keep', []), 'stats', descriptor_params)
                    if descriptors_to_keep.sort() == description.descriptors_to_keep.sort() and statistics_to_keep.sort() == description.statistics_to_keep.sort():
                        to_return = description

        return to_return

    def parse_to_keep_array(self, original_array, process_name, d_params):
        to_return = original_array
        # !!! This has been duplicated in parse labels
        if len(original_array) == 0 or len(original_array) == 1 and original_array[0] == -1 and process_name == 'stats':
            to_return =  utils.make_index_array(7)
        else:
            if len(original_array) == 0 or len(original_array) == 1 and original_array[0] == -1:
                if process_name == 'pitch':
                    to_return = utils.make_index_array(2)
                elif process_name == 'loudness':
                    to_return = utils.make_index_array(2)
                elif process_name == 'spectralshape':
                    to_return = utils.make_index_array(7)
                elif process_name == 'melbands':
                    if 'numbands' in d_params:
                        to_return = utils.make_index_array(d_params['numbands'])
                    else:
                        to_return = utils.make_index_array(40)
                elif process_name == 'mfcc':
                    if 'numcoeffs' in d_params:
                        to_return = utils.make_index_array(d_params['numcoeffs'])
                    else:
                        to_return = utils.make_index_array(40)

        return to_return

    def describe(self, process_name, **kwargs):
        for slice in self.slices:
            this_slice = Slice(slice)
            
            description_check = self.get_description(this_slice, process_name, **kwargs)
            
            if description_check == None:
                this_slice.describe(process_name, **kwargs)
            else:
                print('The description ' + process_name + ' already exists with these params for slice ' + this_slice.name + '!')
                print('This was the description:')
                print(description_check)

            this_slice.write(slice)

    def descriptors_to_np(self, process_array):
        # Will need some way of identifying slices still (index as first column maybe)
        return_np_array = np.array([])
        
        for i in range(len(self.slices)):
            this_slice = Slice(self.slices[i])
            slice_np_array = np.array([i])
            for query in process_array:
                this_process_name = query["process_name"]
                
                this_descriptor_params = {}
                if "descriptor_params" in query:
                    this_descriptor_params = query["descriptor_params"]
                
                this_statistic_params = {}
                if "statistic_params" in query:
                    this_statistic_params = query["statistic_params"]
                
                this_descriptors_to_keep = {}
                if "descriptors_to_keep" in query:
                    this_descriptors_to_keep = query["descriptors_to_keep"]
                
                this_statistics_to_keep = {}
                if "statistics_to_keep" in query:
                    this_statistics_to_keep = query["statistics_to_keep"]

                retrieved_description = self.get_description(this_slice, 
                                                                this_process_name, 
                                                                descriptor_params = this_descriptor_params,
                                                                statistic_params = this_statistic_params,
                                                                descriptors_to_keep = this_descriptors_to_keep,
                                                                statistics_to_keep = this_statistics_to_keep)
                
                slice_np_array = np.append(slice_np_array, retrieved_description.data)
            
            #print(this_slice.name)
            #print(slice_np_array)
            if np.size(return_np_array, axis = 0) == 0:
                return_np_array = np.append(return_np_array, slice_np_array)
            else:
                return_np_array = np.vstack((return_np_array, slice_np_array))
        
        return return_np_array

class Slice:
    def __init__(self, src, **kwargs):
        self.accepted_audio_types = ['.wav']
        self.path = ''
        self.name_suffix = kwargs.get('name_suffix', '')
        self.name = kwargs.get('name_suffix', '')
        self.frames = 0
        self.samplerate = 0
        self.ms = 0
        self.channels = 0
        self.descriptions = []
        self.start_frame = kwargs.get('start_frame', 0)
        self.end_frame = kwargs.get('end_frame', -1)
        self.num_frames = kwargs.get('num_frames', -1)
        self.custom_params = kwargs.get('custom_params', {})

        if utils.get_file_extension(src) == '.json':
            self.read(src)
        elif utils.get_file_extension(src) in self.accepted_audio_types:
            self.set_meta_data(src)
            self.num_frames = self.get_num_frames()
            
    def __repr__(self):
        return "Slice()"

    def __str__(self):
        return 'Slice: ' + self.name + ' for file ' + self.path + '.\n' + str(len(self.descriptions)) + ' descriptions.'

    def get_num_frames(self):
        if self.num_frames == -1:
            if self.end_frame == -1 and self.start_frame == 0:
                return self.frames
            elif self.end_frame == -1:
                return self.frames - self.start_frame
            else:
                return self.end_frame - self.start_frame
        else:
            return self.num_frames

    def set_meta_data(self, path):
        meta_data = utils.process_meta_data(path)
        self.path = meta_data['path']
        if self.name_suffix != '':
            self.name = utils.get_filename(meta_data['path']) + self.name_suffix + '_' + str(self.start_frame) + '_' + str(self.end_frame)
        else:
            self.name = utils.get_filename(meta_data['path']) + '_' + str(self.start_frame) + '_' + str(self.end_frame)
        self.frames = meta_data['frames']
        self.samplerate = meta_data['samplerate']
        self.ms = meta_data['ms']
        self.channels = meta_data['channels']

    def write(self, out_path, **kwargs):
        output_dict = {
            "accepted_audio_types" : self.accepted_audio_types,
            "path" : self.path,
            "name" : self.name,
            "frames" : self.frames,
            "samplerate" : self.samplerate,
            "ms" : self.ms,
            "channels" : self.channels,
            "start_frame" : self.start_frame,
            "end_frame" : self.end_frame,
            "num_frames" : self.num_frames,
            "name_suffix" : self.name_suffix,
            "descriptions" : [],
            "custom_params" : self.custom_params
        }

        for description in self.descriptions:
            output_dict['descriptions'].append(description.to_json())
            
        with open(out_path, 'w') as outfile:
            json.dump(output_dict, outfile, indent = kwargs.get('indent', 0))
    
    def read(self, in_path):
        with open(in_path) as json_file:
            load_data = json.load(json_file)
            
            self.accepted_audio_types = load_data["accepted_audio_types"]
            self.path = load_data["path"]
            self.name = load_data["name"]
            self.frames = load_data["frames"]
            self.samplerate = load_data["samplerate"]
            self.ms = load_data["ms"]
            self.channels = load_data["channels"]
            self.start_frame = load_data["start_frame"]
            self.end_frame = load_data["end_frame"]
            self.num_frames = load_data["num_frames"]
            self.name_suffix = load_data["name_suffix"]
            self.custom_params = load_data["custom_params"]
            
            for description in load_data["descriptions"]:
                this_description = Description(description["process_name"], self)
                this_description.from_json(description)
                self.descriptions.append(this_description)

    def describe(self, process_name, **kwargs):
        this_description = Description(process_name, self, **kwargs)
        this_description.process()
        self.descriptions.append(this_description)

class Description:
    def __init__(self, process_name, slice, **kwargs):
        self.slice = slice
        self.process_name = process_name
        self.descriptor_params = kwargs.get('descriptor_params', {})
        self.statistic_params = kwargs.get('statistic_params', {})
        self.descriptors_to_keep = kwargs.get('descriptors_to_keep', [])
        self.statistics_to_keep = kwargs.get('statistics_to_keep', [])
        self.channels_to_keep = kwargs.get('channels_to_keep', [])
        self.label_prefix = kwargs.get('label_prefix', '')
        
        self.labels = np.array([])
        self.data = np.array([])

    def __repr__(self):
        return "Description()"

    def __str__(self):
        return 'Description: ' + self.process_name + ' for slice ' + self.slice.name + '.'

    def to_json(self):
        return {
            "process_name" : self.process_name,
            "descriptor_params" : self.descriptor_params,
            "statistic_params" : self.statistic_params,
            "descriptors_to_keep" : self.descriptors_to_keep,
            "statistics_to_keep" : self.statistics_to_keep,
            "channels_to_keep" : self.channels_to_keep,
            "label_prefix" : self.label_prefix,
            "labels" : self.labels.tolist(),
            "data" : self.data.tolist()
        }

    def from_json(self, input_data):
        self.process_name = input_data["process_name"]
        self.descriptor_params = input_data["descriptor_params"]
        self.statistic_params = input_data["statistic_params"]
        self.descriptors_to_keep = input_data["descriptors_to_keep"]
        self.statistics_to_keep = input_data["statistics_to_keep"]
        self.channels_to_keep = input_data["channels_to_keep"]
        self.label_prefix = input_data["label_prefix"]
        
        self.labels = np.array(input_data["labels"])
        self.data = np.array(input_data["data"])

    def process(self):
        tmpdir = tempfile.mkdtemp(prefix = os.path.join(module_direc, 'Temporary Data/'))
        
        desc_result = self.process_descriptor(tmpdir)
        stat_result = self.process_stats(desc_result, tmpdir)
        parsed_stats = self.parse_stats(stat_result)
        self.data = self.average_stats(parsed_stats)
        self.labels = self.parse_labels()

        self.data = self.data.flatten()
        self.labels = self.labels.flatten()

        shutil.rmtree(tmpdir)

    def process_descriptor(self, process_direc):
        subprocess_array = self.get_process_array(self.slice.path, self.process_name, self.descriptor_params)

        results = os.path.join(process_direc, 'features.wav')
        subprocess_array.append('-features')
        subprocess_array.append(results)
        subprocess_array.append('-startframe')
        subprocess_array.append(str(self.slice.start_frame))
        subprocess_array.append('-numframes')
        subprocess_array.append(str(self.slice.num_frames))

        subprocess.call(subprocess_array)

        return results

    def process_stats(self, src, process_direc):
        stats = os.path.join(process_direc, 'stats.wav')

        subprocess_array = self.get_process_array(src, 'stats', self.statistic_params)
        subprocess_array.append('-stats')
        subprocess_array.append(stats)

        subprocess.call(subprocess_array)

        return utils.sf_to_np(stats)

    def parse_stats(self, full_stats):
        # Remove unwanted stats:
        delete_array_stats = self.get_delete_array_stats(np.size(full_stats, 1))
        parsed_stats = np.delete(full_stats, delete_array_stats, 1)

        # Remove unwanted channels:
        delete_array_chans = self.get_delete_array_chans(np.size(parsed_stats, 0))
        parsed_stats_final = np.delete(parsed_stats, delete_array_chans, 0)

        return parsed_stats_final

    def parse_labels(self):
        # this first bit is duplicated in parse_to_keep_array
        if len(self.descriptors_to_keep) == 0 or len(self.descriptors_to_keep) == 1 and self.descriptors_to_keep[0] == -1:
            if self.process_name == 'pitch':
                self.descriptors_to_keep = utils.make_index_array(2)
            elif self.process_name == 'loudness':
                self.descriptors_to_keep = utils.make_index_array(2)
            elif self.process_name == 'spectralshape':
                self.descriptors_to_keep = utils.make_index_array(7)
            elif self.process_name == 'melbands':
                if 'numbands' in self.descriptor_params:
                    self.descriptors_to_keep = utils.make_index_array(self.descriptor_params['numbands'])
                else:
                    self.descriptors_to_keep = utils.make_index_array(40)
            elif self.process_name == 'mfcc':
                if 'numcoeffs' in self.descriptor_params:
                    self.descriptors_to_keep = utils.make_index_array(self.descriptor_params['numcoeffs'])
                else:
                    self.descriptors_to_keep = utils.make_index_array(40)
        if len(self.statistics_to_keep) == 0 or len(self.statistics_to_keep) == 1 and self.statistics_to_keep[0] == -1:
            self.statistics_to_keep = utils.make_index_array(7)

        label_array = np.array([])
        settings_string = self.get_settings_string()

        for descriptor_index in self.descriptors_to_keep:
            this_descriptor_name = self.parse_label_index(descriptor_index, self.process_name)
            descriptor_array = np.array([])
            for stat_index in self.statistics_to_keep:
                this_stat_name = self.parse_label_index(stat_index, 'stats')
                #this_label = self.label_prefix + ';,' + self.process_name + ';,' + settings_string + ';,' + this_descriptor_name + ';,' + this_stat_name
                if self.label_prefix != '':
                    this_label = self.label_prefix + ';,' + this_descriptor_name + ';,' + this_stat_name
                else:
                    this_label = this_descriptor_name + ';,' + this_stat_name
                descriptor_array = np.append(descriptor_array, this_label)
            
            if np.size(label_array) == 0:
                label_array = np.append(label_array, descriptor_array)
            else:
                label_array = np.vstack((label_array, descriptor_array))
        
        return label_array

    def get_settings_string(self):
        output_string = ''
        for item in self.descriptor_params:
            output_string = output_string + item + '=' + str(self.descriptor_params[item]) + ','
        return output_string[:-1]

    def parse_label_index(self, idx, main_name):
        if main_name == 'loudness':
            if idx == 0:
                return 'loudness_true_peak'
            elif idx == 1:
                return 'loudness_percieved'
        elif main_name == 'pitch':
            if idx == 0:
                return 'frequency'
            elif idx == 1:
                return 'confidence'
        elif main_name == 'melbands':
            return 'band_' + str(idx)
        elif main_name == 'mfcc':
            return 'coeff_' + str(idx)
        elif main_name == 'spectralshape':
            if idx == 0:
                return 'centroid'
            elif idx == 1:
                return 'spread'
            elif idx == 2:
                return 'skewness'
            elif idx == 3:
                return 'kurtosis'
            elif idx == 4:
                return 'rolloff'
            elif idx == 5:
                return 'flatness'
            elif idx == 6:
                return 'crest'
        elif main_name == 'stats':
            if idx == 0:
                return 'mean'
            elif idx == 1:
                return 'standard_deviation'
            elif idx == 2:
                return 'skewness'
            elif idx == 3:
                return 'kurtosis'
            elif idx == 4:
                return 'minimum'
            elif idx == 5:
                return 'median'
            elif idx == 6:
                return 'maximum'
        
    def average_stats(self, full_stats):
        num_rows = math.floor(np.size(full_stats, 0) / self.slice.channels)

        if num_rows == np.size(full_stats, 0):
            return full_stats
        else:
            to_return = np.array([])

            for i in range(num_rows):
                collection = np.array([])
                for j in range(self.slice.channels):
                    to_add = full_stats[i + (j * num_rows)]
                    if j == 0:
                        collection = np.append(collection, to_add)
                    else:
                        collection = np.vstack((collection, to_add))

                averaged = np.mean(collection, axis=0)

                if i == 0:
                    to_return = np.append(to_return, averaged)
                else:
                    to_return = np.vstack((to_return, averaged))
            
            return to_return

    def get_delete_array_chans(self, total_chans):
        return_array = []
        chans_per_chan = math.floor(total_chans / self.slice.channels)

        chan_count = 0

        if len(self.descriptors_to_keep) == 0 or len(self.descriptors_to_keep) == 1 and self.descriptors_to_keep[0] == -1:
            if len(self.channels_to_keep) == 0 or len(self.channels_to_keep) == 1 and self.channels_to_keep[0] == -1:
                return_array = []
            else:
                # Keep all descriptors
                for i in range(total_chans):
                    current_desc = i % chans_per_chan
                    if(current_desc == 0):
                        chan_count += 1
                    current_can = chan_count - 1

                    if current_can not in self.channels_to_keep:
                        return_array.append(i)
        elif len(self.channels_to_keep) == 0 or len(self.channels_to_keep) == 1 and self.channels_to_keep[0] == -1:
            # Keep all channels
            for i in range(total_chans):
                current_desc = i % chans_per_chan
                if(current_desc == 0):
                    chan_count += 1
                current_can = chan_count - 1

                if current_desc not in self.descriptors_to_keep:
                    return_array.append(i)
        else:
            for i in range(total_chans):
                current_desc = i % chans_per_chan
                if(current_desc == 0):
                    chan_count += 1
                current_can = chan_count - 1

                if current_desc not in self.descriptors_to_keep or current_can not in self.channels_to_keep:
                    return_array.append(i)

        return return_array

    def get_delete_array_stats(self, num_stats):
        return_array = []
        if len(self.statistics_to_keep) == 0 or len(self.statistics_to_keep) == 1 and self.statistics_to_keep[0] == -1:
            return_array = []
        else:
            for i in range(math.floor(num_stats / 7)):
                for j in range(7):
                    if j not in self.statistics_to_keep:
                        return_array.append(j + (i * 7))

        return return_array
            
    def get_process_array(self, src, process_name, user_params):
        process_array = []
        process_array.append('fluid-' + process_name)
        process_array.append('-source')
        process_array.append(src)

        for item in user_params:
            if item in ['startchan', 'numchans']:
                process_array = self.append_param(item, process_array, user_params[item])
            if process_name == 'loudness':
                if item in ['hopsize', 'kweighting', 'truepeak', 'windowsize']:
                    process_array = self.append_param(item, process_array, user_params[item])
            elif process_name == 'melbands':
                if item in ['fftsettings', 'maxfreq', 'minfreq', 'normalize', 'numbands', 'padding', 'scale']:
                    process_array = self.append_param(item, process_array, user_params[item])
            elif process_name == 'mfcc':
                if item in ['fftsettings', 'maxfreq', 'minfreq', 'numbands', 'numcoeffs', 'padding', 'startcoeff']:
                    process_array = self.append_param(item, process_array, user_params[item])
            elif process_name == 'pitch':
                if item in ['fftsettings', 'algorithm', 'maxfreq', 'minfreq', 'padding', 'unit']:
                    process_array = self.append_param(item, process_array, user_params[item])
            elif process_name == 'spectralshape':
                if item in ['fftsettings', 'maxfreq', 'minfreq', 'padding', 'power', 'rolloffpercent', 'unit']:
                    process_array = self.append_param(item, process_array, user_params[item])
            elif process_name == 'stats':
                if item in ['high', 'low', 'middle', 'numderivs', 'outlierscutoff', 'weights']:
                    process_array = self.append_param(item, process_array, user_params[item])

        return process_array

    def append_param(self, param_name, target_array, value):
        temp_array = target_array
        temp_array.append('-' + param_name)

        if isinstance(value, list):
            for element in value:
                temp_array.append(str(element))
        else:
            temp_array.append(str(value))

        return temp_array