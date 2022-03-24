from pathlib import Path
import fluid_wrapper as fluid # FOR REAPERML
import utils # FOR REAPERML
#from reathon.exceptions import InvalidNodeMethod

class Node:
    def __init__(self, *nodes_to_add, **kwargs):
        if 'node_name' in kwargs:
            self.name = kwargs.get('node_name')
        else:
            self.name = 'UNTITLED'
        if 'meta_props' in kwargs:
            self.meta_props = kwargs.get('meta_props')
        else:
            self.meta_props = None
        self.valid_children = [Node, Track, Item, Source, FXChain, AU, VST]
        self.nodes = []
        self.props = []
        self.parents = []
        self.string = ''
        self.add(*nodes_to_add)
        for prop, value in kwargs.items():
            if prop == 'file':
                value = self.wrap_file(value)
            if prop != 'node_name' and prop != 'meta_props':
                self.props.append([prop.upper(), str(value)])

    def replace_prop(self, prop_key, prop_value):
        replaced = False
        for prop in self.props:
            if prop[0] == prop_key.upper():
                self.props.remove(prop)
                self.props.append([prop_key.upper(), str(prop_value)])
                replaced = True
        if replaced == False:
            self.props.append([prop_key.upper(), str(prop_value)])

    def get_prop(self, prop_key):
        to_return = None

        for prop in self.props:
            if prop[0].upper() == prop_key.upper():
                to_return =  prop[1]

        return to_return

    def __repr__(self):
        return "Node()"

    def __str__(self):
        self.traverse(self)
        return self.string

    def add(self, *nodes_to_add):
        for node in nodes_to_add:
            if any(isinstance(node, x) for x in self.valid_children):
                self.nodes.append(node)
                node.parents.append(self) # add the self to the parents of the node
            else:
                print(f'You cannot add a {node.name} to a {self.name}')
        return self

    def get_children(self, **kwargs):
        children = []
        type_query = kwargs.get('type_query', Node)
        for node in self.nodes:
            if type(node) == type_query:
                children.append(node)
        
        return children

    def traverse(self, origin, this_level = 0):
        indent = ''
        for _ in range(this_level):
            indent += '  '
        
        if origin.meta_props != None:
            self.string += f'{indent}<{origin.name} {origin.meta_props}\n'
        else:
            self.string += f'{indent}<{origin.name}\n'

        for state in origin.props:
            self.string += f'{indent}  {state[0]} {state[1]}\n'
    
        for node in origin.nodes:
            self.traverse(node, this_level = this_level + 1)
        self.string += indent + '>\n'

    @staticmethod
    def wrap_file(path_to_wrap: str) -> str:
        return f"'{path_to_wrap}'"

class Project(Node):
    def __init__(self, *nodes_to_add, **kwargs):
        super().__init__(*nodes_to_add, **kwargs)
        self.name = 'REAPER_PROJECT'
        self.valid_children = [Node, Track]
        self.transport_info = {
            "bpm" : 120,
            "time_sig_top" : 4,
            "time_sig_bottom" : 4,
            "sample_rate" : 44100
        }
        self.replace_prop('TEMPO', '120 4 4')
        self.replace_prop('SAMPLERATE', '44100')
        self.accepted_chunks = {
            # when reading if the chunk is not in this name/class pair, a generic node will be created with name='CHUNK'.
            'PROJECT' : Project,
            'TRACK' : Track,
            'ITEM' : Item,
            'SOURCE' : Source
        } 
        if 'file' in kwargs:
            self.read(kwargs.get('file'))

    def write(self, path):
        self.traverse(self)
        with open(path, "w") as f:
            f.write(self.string)

    def get_tracks(self):
        # Get track in project either by index or track name:
        return super().get_children(type_query = Track)

    def set_transport_info(self, key, val):
        self.transport_info[key] = val
        self.replace_prop('TEMPO', str(self.transport_info["bpm"]) + ' ' + str(self.transport_info["time_sig_top"]) + ' ' + str(self.transport_info["time_sig_bottom"]))
        self.replace_prop('SAMPLERATE', str(self.transport_info["sample_rate"]))

    def read(self, path):
        # Read an rpp file
        self.nodes = [] # Reinit nodes.
        self.props = [] # Reinit props.

        # The first element will always be a project, and it is already created:
        current_parent = self 
        current_hierarchy = [self]
        with open(path, 'r') as f:
            # The first line is the project, so just add it's meta_props if there are any:
            first_line = f.readline()
            line_array = self.line_pre_parse(first_line)
            project_meta_props = self.get_metaprops(line_array)
            self.meta_props = project_meta_props
            
            # Now read through the rest of the file:
            for line in f:
                # Read through the lines in the rpp file:
                line_array = self.line_pre_parse(line)
                if (line_array[0][:1] == '>'):
                    # Closing a chunk:
                    if len(current_hierarchy) != 1: # Skip the last line (the project) as it was never opened!
                        current_hierarchy.pop()
                        current_parent = current_hierarchy[-1]
                else:
                    if(line_array[0][:1] == '<'):
                        # New chunk start
                        this_chunk = line_array[0][1:].replace('\n', '')

                        if(this_chunk in self.accepted_chunks):
                            accepted_chunk = self.accepted_chunks[this_chunk](meta_props = self.get_metaprops(line_array))
                        else:
                            accepted_chunk = Node(node_name = this_chunk, meta_props = self.get_metaprops(line_array))

                        current_parent.add(accepted_chunk)
                        current_parent = accepted_chunk
                        current_hierarchy.append(current_parent)
                    else:
                        # Add a property to the current parent:
                        current_parent.props.append(self.parse_prop(line_array))

                        if isinstance(current_parent, Source) and self.parse_prop(line_array)[0] == 'FILE':
                            current_parent.set_file(self.parse_prop(line_array)[1])  

                        # Update transport info:
                        if isinstance(current_parent, Project) and self.parse_prop(line_array)[0] == 'TEMPO':
                            self.transport_info["bpm"] = line_array[1]
                            self.transport_info["time_sig_top"] = line_array[2]
                            self.transport_info["time_sig_bottom"] = line_array[3]
                            
                        if isinstance(current_parent, Project) and self.parse_prop(line_array)[0] == 'SAMPLERATE':
                            self.transport_info["sample_rate"] = line_array[1]

    def get_metaprops(self, full_line):
        # Parse meta props. 
        # I tried combining this with parse_prop(), however the many sublte differences made it a nightmare.
        if len(full_line) == 1:
            return None
        else:
            prop_string = ''
            for i in range(len(full_line)):
                if i != 0:
                    prop_string += full_line[i].replace('\n', '')
                    if i != len(full_line) -1:
                        prop_string += ' '
            return prop_string

    def parse_prop(self, full_line):
        return_array = []
        prop_string = ''
        for i in range(len(full_line)):
            if i == 0:
                return_array.append(full_line[i])
            else:
                prop_string = prop_string + full_line[i].replace('\n', '')
                if i != len(full_line) -1:
                    prop_string = prop_string + ' '

        return_array.append(prop_string)
        return return_array

    def line_pre_parse(self, full_line):
        # Transform a line from an rpp file into an array without preceeding spaces.
        # For example: ['<REAPER_PROJECT', '0.1', '"6.51/OSX64"', '1646650836\n']
        initial_line_list = full_line.split(' ')
        removed_initial_spaces = []
        final_array = []
        can_push = False

        # Remove preceeding empty entries:
        for element in initial_line_list:
            if(can_push == False and element != ''):
                can_push = True
            if(can_push):
                removed_initial_spaces.append(element)

        # Stick strings back together:
        adding_string = False
        current_string = ''
        for element in removed_initial_spaces:
            if('"' in element): 
                last_char = element.replace('\n', '')[-1]
                if(element[0] == '"' and last_char == '"'):
                    final_array.append(element.replace('\n', '')[1:-1])
                elif(element[0] == '"'):
                    adding_string = True
                    current_string = element[1:]
                elif(adding_string == True and last_char == '"'):
                    current_string = current_string + ' ' + element.replace('\n', '')[-1]
                    final_array.append(current_string)
                    adding_string = False
            elif(adding_string == True):
                current_string = current_string + ' ' + element
            else:
                final_array.append(element)

        return final_array

    def convert_to_collection(self, **kwargs):
        # FOR REAPERML
        the_collection = fluid.Collection()

        tracks = kwargs.get('tracks', [])
        filter_selected = kwargs.get('filter_selected', False)

        if len(tracks) == 0 or len(tracks) == 1 and tracks[0] == -1:
            tracks = utils.make_index_array(len(self.get_tracks()))

        for i in range(len(tracks)):
            this_track = self.get_tracks()[tracks[i]]
            for item in this_track.get_items():
                can_add = True
                if filter_selected:
                    sel_prop = item.get_prop('sel')
                    if sel_prop == '0':
                        can_add = False
                
                if can_add:
                    the_collection.append_slice(item.get_source().get_prop('file'), 
                    start_frame = int(self.time_convert('reaper', 'samps', float(item.get_prop('SOFFS')))), 
                    num_frames = int(self.time_convert('reaper', 'samps', float(item.get_prop('LENGTH')))),
                    custom_params = {"reaper_position" : float(item.get_prop('position')), "reaper_track" : i})

        return the_collection

    def beat_to_midi(self, beat):
        return beat * 960

    def beat_to_reaper(self, beat):
        return beat * 0.5

    def beat_to_ms(self, beat):
        return (beat * (60000.0 / float(self.transport_info["bpm"]))) / (float(self.transport_info["time_sig_bottom"]) * 0.25)

    def ms_to_samps(self, ms):
        return ms * (float(self.transport_info["sample_rate"]) / 1000.0)

    def midi_to_beat(self, midi):
        return midi / 960

    def ms_to_beat(self, ms):
        return (ms * (float(self.transport_info["time_sig_bottom"]) * 0.25)) / (60000.0 / float(self.transport_info["bpm"]))

    def samps_to_ms(self, samps):
        return samps / (float(self.transport_info["sample_rate"]) / 1000.0)

    def reaper_to_beat(self, reaper):
        return reaper * 2

    def time_convert(self, source_type, target_type, value):
        if source_type == 'beat':
            if target_type == 'midi':
                return self.beat_to_midi(value)
            elif target_type == 'reaper':
                return self.beat_to_reaper(value)
            elif target_type == 'ms':
                return self.beat_to_ms(value)
            elif target_type == 'samps':
                return self.ms_to_samps(self.beat_to_ms(value))

        elif source_type == 'midi':
            this_beat = self.midi_to_beat(value)
            if target_type == 'beat':
                return this_beat
            elif target_type == 'reaper':
                return self.beat_to_reaper(this_beat)
            elif target_type == 'ms':
                return self.beat_to_ms(this_beat)
            elif target_type == 'samps':
                return self.ms_to_samps(self.beat_to_ms(this_beat))

        elif source_type == 'reaper':
            this_beat = self.reaper_to_beat(value)
            if target_type == 'beat':
                return this_beat
            elif target_type == 'midi':
                return self.beat_to_midi(this_beat)
            elif target_type == 'ms':
                return self.beat_to_ms(this_beat)
            elif target_type == 'samps':
                return self.ms_to_samps(self.beat_to_ms(this_beat))
        
        elif source_type == 'ms':
            this_beat = self.ms_to_beat(value)
            if target_type == 'beat':
                return this_beat
            elif target_type == 'midi':
                return self.beat_to_midi(this_beat)
            elif target_type == 'reaper':
                return self.beat_to_reaper(this_beat)
            elif target_type == 'samps':
                return self.ms_to_samps(self.beat_to_ms(this_beat))

        elif source_type == 'samps':
            this_ms = self.samps_to_ms(value);
            this_beat = self.ms_to_beat(this_ms);
            if target_type == 'ms':
                return this_ms
            elif target_type == 'beat':
                return this_beat
            elif target_type == 'midi':
                return self.beat_to_midi(this_beat)
            elif target_type == 'reaper':
                return self.beat_to_reaper(this_beat)

class FXChain(Node):
    def __init__(self, *nodes_to_add, **kwargs):
        super().__init__(*nodes_to_add, **kwargs)
        self.name = 'FXCHAIN'

class VST(Node):
    def __init__(self, *nodes_to_add, **kwargs):
        super().__init__(*nodes_to_add, **kwargs)
        self.name = 'VST'

class AU(Node):
    def __init__(self, *nodes_to_add, **kwargs):
        super().__init__(*nodes_to_add, **kwargs)
        self.name = 'AU'
        
class Track(Node):
    def __init__(self, *nodes_to_add, **kwargs):
        super().__init__(*nodes_to_add, **kwargs)
        self.name = 'TRACK'
        self.valid_children = [FXChain, Item, Node]
        
    def get_items(self):
        # Get track in project either by index or track name:
        return super().get_children(type_query = Item)
         
class Item(Node):
    def __init__(self, *nodes_to_add, **kwargs):
        super().__init__(*nodes_to_add, **kwargs)
        self.name = 'ITEM'
        self.valid_children = [Node, Source]

    def get_source(self):
        to_return = None
        for node in self.nodes:
            if type(node) == Source:
                to_return = node
        
        return to_return

class Source(Node):
    def __init__(self, *nodes_to_add, **kwargs):
        super().__init__(*nodes_to_add, **kwargs)
        self.valid_children = [Node, Source]
        self.name = 'SOURCE'
        self.extension_lookup = {
            '.wav' : 'WAVE',
            '.wave' : 'WAVE',
            '.aiff' : 'WAVE',
            '.aif' : 'WAVE',
            '.mp3' : 'MP3',
            '.ogg' : 'VORBIS'
        }
        # Only do the source parsing if it is given:
        if 'file' in kwargs:
            self.file = kwargs.get('file')      
            self.process_extension()

    def set_file(self, path):
        # Allow for setting of the file from elsewhere.
        self.file = path
        self.process_extension()

    def process_extension(self):
        ext = Path(self.file.replace('"', '')).suffix
        try:
            self.meta_props = self.extension_lookup[ext]
        except KeyError:
            self.meta_props = 'SECTION'