import logging
import os
import multiprocessing
import string
from functools import partial
from pathlib import Path
from tkinter import *
from tkinter import filedialog

import yaml

from main import generate_mod

with open('base_settings.yaml', 'r') as f:
    base_settings = yaml.safe_load(f)


class WidgetLogger(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.setLevel(logging.INFO)
        self.widget = widget
        self.widget.config(state='disabled')

    def emit(self, record):
        self.widget.config(state='normal')
        # Append message (record) to the widget
        self.widget.insert(END, self.format(record) + '\n')
        self.widget.see(END)  # Scroll to the bottom
        self.widget.config(state='disabled')


def load_settings():
    with open('settings.yaml', 'r') as f:
        settings = yaml.safe_load(f)
    return settings


def save_settings(settings):
    with open('settings.yaml', 'w') as f:
        yaml.safe_dump(settings, f)

def get_default_paths():
    settings_paths = settings.get('file_path', {})
    
    # 1. Dynamically find the EU4 Documents folder across all drives
    eu4_doc_folder = ''
    saved_game_folder = settings_paths.get('game_folder', '')
    
    # Search common locations and available drives for the Paradox folder
    search_bases = [Path.home() / 'Documents']
    for letter in string.ascii_uppercase:
        drive_root = Path(f"{letter}:/")
        if drive_root.exists():
            search_bases.append(drive_root / 'Documents')
            search_bases.append(drive_root / 'Users')

    for base in search_bases:
        if base.exists():
            try:
                matches = list(base.rglob('Paradox Interactive/Europa Universalis IV'))
                if matches:
                    eu4_doc_folder = str(matches[0])
                    break
            except (PermissionError, OSError):
                continue
                
    # Fallback if dynamic search doesn't find it immediately
    if not eu4_doc_folder:
        eu4_doc_folder = 'F:/Documents/Paradox Interactive/Europa Universalis IV'

    # 2. Dynamically find the Steam Game folder across all drives
    game_folder = ''
    if saved_game_folder and os.path.isdir(saved_game_folder):
        game_folder = saved_game_folder
    else:
        for letter in string.ascii_uppercase:
            drive_root = Path(f"{letter}:/")
            if drive_root.exists():
                try:
                    # Look for steamapps common folder efficiently
                    matches = list(drive_root.glob('**/steamapps/common/Europa Universalis IV'))
                    if matches:
                        game_folder = str(matches[0])
                        break
                except (PermissionError, OSError):
                    continue
        if not game_folder:
            game_folder = 'C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis IV'

    # 3. Resolve remaining paths relative to the discovered folders
    if os.path.isdir(settings_paths.get('eu4_mod_folder', '')):
        eu4_mod_folder = settings_paths['eu4_mod_folder']
    else:
        eu4_mod_folder = os.path.join(eu4_doc_folder, 'mod')
        
    if os.path.isdir(settings_paths.get('node_data_folder', '')):
        node_data_folder = settings_paths['node_data_folder']
    else:
        node_data_folder = os.path.join(game_folder, 'common/tradenodes')
        
    mod_name = 'dynamic_trade'
    save_dir = os.path.join(eu4_doc_folder, 'save games')
    
    return game_folder, eu4_mod_folder, save_dir, mod_name, node_data_folder


def browsefunc(path_label, path, is_file=False):
    if not is_file:
        temp = filedialog.askdirectory(initialdir=path)
        if temp != '':
            path_label.config(text=temp)
    else:
        temp = filedialog.askopenfilename(initialdir=path, filetypes=[('eu4 save', '.eu4')])
        if temp != '':
            path_label.config(text=temp)


def compile_settings():
    new_settings = {'file_path': {
        'eu4_mod_folder': path_labels['eu4_mod_folder']['text'],
        'game_folder': game_folder,
        'mod_name': 'dynamic_trade',
        'node_data_folder': path_labels['node_data_folder']['text'],
        'save_file': path_labels['save_dir']['text']
    },
        'flow_rules': {
            'n_end_nodes': n_end_nodes.get(),
            'end_node_restriction': end_node_restriction.get(),
            'equal_threshold': 1,
            'flow_power_rules': [flow_rules[i].get() for i in range(5)]
        },
        'reload_save_data': reload_save_data.get()
    }
    save_settings(new_settings)
    logging.info('new settings saved!')


def call_engine():
    compile_settings()
    generate_mod()
    logging.info('mod generated!')


if __name__ == '__main__':
    multiprocessing.freeze_support()
    settings = load_settings()
    root_window = Tk()
    root_window.title('EU4 Dynamic Trade mod generator')
    input_window = Frame(root_window, highlightbackground="black", highlightthickness=1)
    path_input_window = Frame(input_window)
    path_input_window.grid(row=0, column=0)
    flow_rules_window = Frame(input_window)
    flow_rules_window.grid(row=0, column=1)
    input_window.grid(row=0, column=0)
    output_window = Frame(root_window)
    output_window.grid(row=1, column=0)
    game_folder, eu4_mod_folder, save_dir, mod_name, node_data_folder = get_default_paths()
    browse_list = zip(['node_data_folder', 'eu4_mod_folder', 'save_dir'],
                      ['node_data_folder', 'eu4 mod folder', 'reference save file'],
                      [False, False, True])
    path_labels = {}
    browse_buttons = {}
    for i, (browse_item, label, is_file) in enumerate(browse_list):
        path_labels[browse_item] = Label(path_input_window)
        path_labels[browse_item].grid(row=i, column=0)
        if not is_file:
            path_labels[browse_item].config(text=globals()[browse_item])
        else:
            if os.path.isfile(settings['file_path']['save_file']):
                path_labels[browse_item].config(text=settings['file_path']['save_file'])
            else:
                path_labels[browse_item].config(text=max(list(map(lambda x: os.path.join(globals()[browse_item], x),
                                                                  filter(lambda x: x.endswith('.eu4'),
                                                                         os.listdir(globals()[browse_item])))),
                                                         key=lambda x: os.path.getmtime(x)))
        browse_buttons[browse_item] = Button(path_input_window, text=label,
                                             command=partial(browsefunc,
                                                             path_label=path_labels[browse_item],
                                                             path=globals()[browse_item],
                                                             is_file=is_file))
        browse_buttons[browse_item].grid(row=i, column=1)

    n_end_nodes = IntVar(value=settings['flow_rules']['n_end_nodes'])
    n_end_nodes_box = Spinbox(flow_rules_window, from_=1, to=10, increment=1, textvariable=n_end_nodes)
    n_end_nodes_box.grid(row=0, column=0)
    n_end_nodes_name = Label(flow_rules_window, text='n_end_nodes')
    n_end_nodes_name.grid(row=0, column=1)
    end_node_restriction = StringVar(value=settings['flow_rules']['end_node_restriction'])
    end_node_restriction_box = OptionMenu(flow_rules_window, end_node_restriction, *['restricted', 'unrestricted'])
    end_node_restriction_box.grid(row=1, column=0)
    end_node_restriction_name = Label(flow_rules_window, text='end_node_restriction')
    end_node_restriction_name.grid(row=1, column=1)
    flow_rules = []
    flow_rules_box = []
    flow_rules_id = []
    for i, value in zip(range(1, 6), settings['flow_rules']['flow_power_rules'][:6]):
        flow_rules.append(StringVar(value=value))
        flow_rules_box.append(OptionMenu(flow_rules_window, flow_rules[-1], *sorted(base_settings['flow_power_rules'])))
        flow_rules_box[-1].grid(row=i + 1, column=0)
        flow_rules_id.append(Label(flow_rules_window, text=f'flow rule {i}'))
        flow_rules_id[-1].grid(row=i + 1, column=1)
    reload_save_data = BooleanVar(value=settings['reload_save_data'])
    reload_save_data_box = Checkbutton(output_window, text='reload save data', variable=reload_save_data, onvalue=True,
                                       offvalue=False)
    reload_save_data_box.grid(row=0, column=0)
    save_settings_button = Button(output_window, text="save settings", command=compile_settings)
    save_settings_button.grid(row=1, column=0)
    generate_mod_button = Button(output_window, text="generate mod", command=call_engine)
    generate_mod_button.grid(row=2, column=0)
    text_window = Frame(root_window, height=10)
    text_window.grid(row=2, column=0)
    v = Scrollbar(text_window, orient='vertical')
    v.pack(side=RIGHT, fill='y')
    output_console = Text(text_window, height=10)
    v.config(command=output_console.yview)
    output_console.pack(side=LEFT)
    logger = logging.getLogger()
    logger.addHandler(WidgetLogger(output_console))
    logger.addHandler(logging.FileHandler('logfile.txt', 'w'))
    logger.setLevel(logging.INFO)

    root_window.mainloop()
