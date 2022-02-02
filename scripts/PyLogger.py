#! /usr/bin/env python3
# Author: Kristopher Kieft
# 2022

# Python Command Line Logger


import os
import sys
import sqlite3
import subprocess
import time
from datetime import datetime, date

global SHOW
SHOW = 50 # how many log results to show
global bold,italic,end
bold,italic,end = '\033[1m', '\x1B[3m', '\033[0m'

class Main:
    def __init__(self, history, func):
        self.history = history
        self.func = func
        
        if self.func == 'h' or self.func == 'help':
            Helpers.main_help()

        if self.func[:6] == 'offset':
            self.offset_args()
        else:
            entry = {
                'main': self.main_args,
                'note': self.main_args,
                'add': self.add_args,
                'find': self.find_args,
                'view': self.view_args,
                'backup': self.backup_args,
                'clear': self.clear_args,
                'remove': self.remove_args
            }

            try:
                entry[func]()
            except KeyError:
                sys.stdout.write(f"PyLog Error\nInvalid entry '{func}'\n")
                Helpers.main_help()
    
    def offset_args(self):
        command = int(self.func.split('_')[1])
        self.func = 'offset'
        Logger(self.func, command, history=self.history)
    
    def main_args(self):
        try:
            command = ' '.join(sys.argv[3:]).strip()
        except IndexError:
            command = ''
        Logger(self.func, command, history=self.history)
    
    def note_args(self):
        Logger(self.func, None, history=self.history)

    def add_args(self):
        try:
            command = ' '.join(sys.argv[3:]).strip()
            Logger(self.func, command)
        except IndexError:
            Helpers.add_help()
    
    def find_args(self):
        try:
            command = ' '.join(sys.argv[3:]).strip()
            Logger(self.func, command)
        except IndexError:
            Helpers.find_help()

    def view_args(self):
        try:
            command = ' '.join(sys.argv[3:]).strip()
        except IndexError:
            command = ''
        Logger(self.func, command)
    
    def backup_args(self):
        Logger(self.func, '')
    
    def clear_args(self):
        Logger(self.func, '')
    
    def remove_args(self):
        Logger(self.func, '')


class Logger:
    def __init__(self, func, command, history=''):
        self.command = command
        self.history = history
        self.func = func
        self.note = ''

        needHelp ={
            'offset': Helpers.main_help,
            'main': Helpers.main_help,
            'note': Helpers.note_help,
            'add': Helpers.add_help,
            'find': Helpers.find_help,
            'view': Helpers.view_help,
            'backup': Helpers.backup_help,
            'clear': Helpers.clear_help,
            'remove': Helpers.remove_help
        }
        if not isinstance(self.command, int) and (self.command.strip('-') == 'h' or self.command.strip('-') == 'help'):
            needHelp[self.func]()

        self.entry = {
            'offset': self.offset_logger,
            'main': self.main_logger,
            'note': self.note_logger,
            'add': self.add_logger,
            'find': self.find_logger,
            'view': self.view_logger,
            'backup': self.backup_logger,
            'clear': self.clear_logger,
            'remove': self.remove_logger
        }
        self.info()
        self.connection()
    
    def creation(self):
        if not os.path.exists(self.logfile):
            try:
                conn_create = sqlite3.connect(self.logfile)
                c_create = conn_create.cursor()
                c_create.execute('''
                CREATE TABLE IF NOT EXISTS PyLogger
                ([index] INTEGER PRIMARY KEY AUTOINCREMENT, [date] TEXT, [time] TEXT, [conda] TEXT, [directory] TEXT, [note] TEXT, [command] TEXT, [stamp] INTEGER)
                ''')
                conn_create.commit()
                conn_create.close()
            except sqlite3.Error:
                sys.stderr.write('sqlite3 error 1\n')
                conn_create.close()
                exit()
    
    def connection(self):
        self.creation()
        try:
            global conn
            conn = sqlite3.connect(self.logfile)
            global c
            c = conn.cursor()
            self.parameters = ('''
            INSERT INTO PyLogger (date, time, conda, directory, note, command, stamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
            ''')

            self.entry[self.func]()

            if os.path.exists(self.logfile):
                find_match = (f'SELECT * FROM PyLogger')
                c.execute(find_match)
                result = c.fetchall()

                for i,r in enumerate(result):
                    edit_index = (f'''
                    UPDATE PyLogger
                    SET "index" = {i+1} WHERE
                    ROWID = "{r[0]}"
                    and stamp = "{r[7]}"
                    and command = "{r[6]}"
                    ''')
                    c.execute(edit_index)

                conn.commit()
            conn.close()
        except sqlite3.Error as e:
            sys.stderr.write('sqlite3 error 2\n')
            print(str(e))
            conn.close()
            exit()
    
    def info(self):
        self.day = date.today().strftime("%m/%d/%y")
        self.now = datetime.now().strftime("%H:%M:%S")
        self.wd = os.getcwd()
        self.stamp = time.time()
        try:
            self.conda = f"{os.environ['CONDA_DEFAULT_ENV']}"
        except KeyError:
            self.conda = 'None'
        try:
            self.logfile = f"{os.environ['PYLOG']}"
        except KeyError:
            sys.stdout.write('\nError: Set $PYLOG as the log file name using export. Exiting.\n')
            exit()
    
    def exe_cmd(self, data):
        c.execute(self.parameters, data)
        conn.commit()
        sys.stdout.write(f'Log success.\n')
    
    def local_logger(self):
        with open('README_PyLogger.log', 'a') as local:
            local.write(f'date: {self.data[0]}  ')
            local.write(f'time: {self.data[1]}  ')
            local.write(f'conda: {self.data[2]}\n')
            local.write(f'directory: {self.data[3]}\n')
            local.write(f'note: {self.data[4]}\n')
            local.write(f'command: {self.data[5]}\n')
            local.write('________________________________________\n')

    def offset_logger(self):
        self.data = (self.day, self.now, self.conda, self.wd, self.note, self.history[-2-self.command], self.stamp)
        self.local_logger()
        self.exe_cmd(self.data)

    def main_logger(self):
        self.data = (self.day, self.now, self.conda, self.wd, self.note, self.history[-2], self.stamp)
        self.local_logger()
        self.exe_cmd(self.data)

    def note_logger(self):
        if self.command == '':
            self.note = input(f'Input notes: ').strip()
        else:
            self.note = self.command

        self.data = (self.day, self.now, self.conda, self.wd, self.note, self.history[-2], self.stamp)
        self.local_logger()
        self.exe_cmd(self.data)
    
    def add_logger(self):
        if not self.command:
            self.command = input(f'Input command: ').strip()
            if not self.command:
                sys.stdout.write(f'No command given.\n')
                return
        self.note = input(f'Input notes: ').strip()
        
        self.data = (self.day, self.now, self.conda, self.wd, self.note, self.command, self.stamp)
        self.local_logger()
        self.exe_cmd(self.data)
    
    def find_logger(self):
        if not self.command:
            self.command = input(f'Input search term: ').strip()
            if not self.command:
                sys.stdout.write(f'No search term given.\n')
                return
        Viewer(self.func, self.command)
    
    def view_all(self):
        if self.length > SHOW:
            n = int(self.length-SHOW)
        else:
            n = 0

        find_match = (f'SELECT * FROM PyLogger WHERE "index" > "{n}"')

        c.execute(find_match)
        result = c.fetchall()
        
        sys.stdout.write('________________________________________________\n')
        for row in result:
            sys.stdout.write(f'{bold}index{end}: {row[0]}  ')
            sys.stdout.write(f'{bold}date{end}: {row[1]}  ')
            sys.stdout.write(f'{bold}time{end}: {row[2]}  ')
            sys.stdout.write(f'{bold}conda{end}: {row[3]}\n')
            sys.stdout.write(f'{bold}directory{end}: {row[4]}\n')
            sys.stdout.write(f'{bold}note{end}: {row[5]}\n')
            sys.stdout.write(f'{bold}command{end}: {row[6]}\n')
            sys.stdout.write('________________________________________________\n')

    def view_logger(self):
        size = 'SELECT COUNT(1) FROM PyLogger'
        c.execute(size)
        self.length = c.fetchone()[0]
        
        if self.command.isdigit():
            global SHOW
            SHOW = int(self.command)

        self.view_all()

        try:
            while True:
                usr = input(f': ').strip()
                try:
                    self.usr_cmd = usr.split(' ')[0]
                    if self.usr_cmd == 'q' or self.usr_cmd == 'quit' or self.usr_cmd == 'exit':
                        break
                    self.usr_term = ' '.join(usr.split(' ')[1:])
                    if self.usr_cmd == 'edit':
                        Viewer(self.usr_cmd, self.usr_term)
                        self.view_all()
                    elif self.usr_cmd == 'remove':
                        view_obj = Viewer(self.usr_cmd, self.usr_term)
                        self.view_all()
                        sys.stdout.write(f'Remove success: {view_obj.rm}\n')
                    elif self.usr_cmd == 'find':
                        Viewer(self.usr_cmd, self.usr_term)
                    elif self.usr_cmd == 'view':
                        self.view_all()
                    else:
                        sys.stdout.write(f'invalid command (find, remove, edit, view, q/quit/exit)\n')
                    

                except Exception as e:
                    sys.stdout.write(f'{e}\n\n')

        except KeyboardInterrupt:
            sys.stdout.write('\n')

    def backup_logger(self):
        s = self.logfile.rsplit('.',1)
        d = self.day.replace('/','-')
        t = self.now.replace(':','')
        new = f"{s[0]}.{d}.{t}.{s[1]}"
        subprocess.run(f'cp {self.logfile} {new}', shell=True)
        sys.stdout.write(f'Backup success -> {new}\n')
    
    def clear_logger(self):
        result = input('Clear Pylog? (y/n):  ').strip()
        if result == 'y' or result == 'yes':
            sys.stdout.write('Clearing Pylog file.\n')
            subprocess.run(f'rm {self.logfile}', shell=True)
        else:
            sys.stdout.write('Keeping Pylog file.\n')

    def remove_logger(self):
        find_last = (f'SELECT * FROM PyLogger ORDER BY "index" DESC LIMIT 1')
        c.execute(find_last)
        row = c.fetchone()
        sys.stdout.write(f'\n{bold}index{end}: {row[0]}  ')
        sys.stdout.write(f'{bold}date{end}: {row[1]}  ')
        sys.stdout.write(f'{bold}time{end}: {row[2]}  ')
        sys.stdout.write(f'{bold}conda{end}: {row[3]}  <- {italic}remove{end}\n')
        sys.stdout.write(f'{bold}directory{end}: {row[4]}\n')
        sys.stdout.write(f'{bold}note{end}: {row[5]}\n')
        sys.stdout.write(f'{bold}command{end}: {row[6]}\n')
        sys.stdout.write('________________________________________________\n')
        result = input('Remove last index? (y/n):  ').strip()
        if result == 'y' or result == 'yes':
            remove_match = (f'DELETE FROM PyLogger WHERE "index" = ?')
            c.execute(remove_match, (row[0],))
            sys.stdout.write('Remove success.\n')
        else:
            sys.stdout.write('Keeping index.\n')


class Viewer:
    def __init__(self, usr_cmd, usr_term):
        self.usr_cmd = usr_cmd
        self.usr_term = usr_term

        view_entry = {
            'remove': self.view_remove,
            'find': self.view_find,
            'edit': self.view_edit}

        view_entry[self.usr_cmd]()

    def view_remove(self):
        self.rm = self.usr_term.replace(', ',',').replace(' ',',').split(',')
        for r in self.rm:
            remove_match = (f'DELETE FROM PyLogger WHERE "index" = ?')
            c.execute(remove_match, (r,))
        if len(self.rm) == 1:
            self.rm = int(self.rm[0])
        else:
            self.rm = tuple([int(i) for i in self.rm])

    def view_find(self):
        if not self.usr_term:
            self.usr_term = input(f'Enter search term: ').strip()
            if not self.usr_term:
                sys.stdout.write(f'No search term given.\n')
                return
        find_match = (f'''SELECT * FROM PyLogger WHERE 
        date LIKE "%{self.usr_term}%" 
        or time LIKE "%{self.usr_term}%"
        or conda LIKE "%{self.usr_term}%"
        or directory LIKE "%{self.usr_term}%"
        or note LIKE "%{self.usr_term}%"
        or command LIKE "%{self.usr_term}%"
        ''')

        c.execute(find_match)
        result = c.fetchall()
        
        sys.stdout.write('\n')
        for row in result:
            sys.stdout.write(f'{bold}index{end}: {row[0]}  ')
            sys.stdout.write(f'{bold}date{end}: {row[1]}  ')
            sys.stdout.write(f'{bold}time{end}: {row[2]}  ')
            sys.stdout.write(f'{bold}conda{end}: {row[3]}  <- {italic}{self.usr_term}{end}\n')
            sys.stdout.write(f'{bold}directory{end}: {row[4]}\n')
            sys.stdout.write(f'{bold}note{end}: {row[5]}\n')
            sys.stdout.write(f'{bold}command{end}: {row[6]}\n')
            sys.stdout.write('________________________________________________\n')
        sys.stdout.write(f'Results for "{self.usr_term}": {len(result)}\n\n')


    def view_edit(self):
        ind = input(f'Index(s) to edit: ').strip()
        if not ind: 
            sys.stdout.write(f'No index provided. Skipping edit.\n')
            return
        ind = ind.replace(', ',',').replace(' ',',').split(',')
        for i in ind:
            cols = input(f'(date, time, conda, directory, note, command)\nColumn(s) to edit at index {i}: ').strip()
            if not cols: 
                sys.stdout.write(f'No column provided. Skipping index {i}.\n')
                continue
            cols = cols.replace(', ',',').replace(' ',',').split(',')

            for col in cols:
                e = input(f'New {col}: ').strip()
                if not cols:
                    sys.stdout.write(f'No edit provided. Skipping {col}.\n')
                    continue
                edit_match = (f'''UPDATE PyLogger
                SET {col} = ?
                WHERE ROWID = {i}
                ''')
                c.execute(edit_match, (e,))

class Helpers:
    def main_help():
        h = f'''
        {italic}Ensure these are in your .bash_profile/.bashrc.{end}
            > export PYLOG='{italic}path_to_log_file_location{end}/pylog_file.db'
            > alias pylog='var=$(history | cut -c 8- | tail -n 10); {italic}path_to_script_location{end}/PyLogger.py "$var"'

        {bold}Description:{end}
        Logging tool for command line inputs.
        version 1.0

        {bold}Usage:{end}
        Input commands as normal.
        To log a command, input 'pylog' (alias) as the next command.

        For help pages:
            > pylog h/help
            > pylog [option] h/help

        {bold}Examples:{end}
        $ blastp -in file -out file
        $ pylog

        $ blastp -in file -out file
        $ pylog note test run of blastp
        
        $ pylog view
        $ pylog view 100
        $ pylog remove
        $ pylog add blastp -in file -out file

        {bold}How NOT to use:{end}
        $ blastp; pylog

        {bold}Interaction Options:{end}
        {italic}pylog h/help{end}: print this help page
        {italic}pylog <int>{end}: log the <int> previous command
            > 0: previous command, default of pylog
            > 1: one command before the previous command
            > n ...
        {italic}pylog note{end}: log previous command with notes
            > type notes after 'note' or enter at prompt
        {italic}pylog add{end}: manually add a command
            > follow prompts to input command or provide after 'add'
            > follow prompts to input notes
        {italic}pylog find{end}: search the log for a term
            > follow prompt to input search term or provide after 'find'
        {italic}pylog remove{end}: remove the last command logged
            > prompt to verify removal
            > use 'view' to remove one or multiple entries by index
                > enter 'remove' within the view prompt
        {italic}pylog view{end}: view, search, edit or remove indexes in the log file
            > enter options at prompt:
                > {italic}find{end}: search the log for a term
                > {italic}remove{end}: remove item from log file by index
                > {italic}edit{end}: edit item from log file by index
            > by default 'view' shows the last 25 entries
                > to change the default, input an integer after view
            > to exit type 'q', 'quit', 'exit' or Ctr-C
        {italic}pylog clear{end}: clear/delete the log file
            > prompt to verify clear
            > does not clear the local log file
            > the local log file can be removed/edited/viewed manually
        {italic}pylog backup{end}: copy the log file to create a backup
            > backup = logfile.DMY.time.db
        '''
        sys.stdout.write(f'{h}\n')
        exit()
    
    def note_help():
        h = f'''
        {italic}pylog note{end}: log previous command with notes
            > follow prompt to input any notes or leave blank (hit enter)
            > add 'h' or 'help' as the note, input 'pylog note' and follow the prompt
        
        $ blastp -in file -out file
        $ pylog note

        $ blastp -in file -out file
        $ pylog note test run of blastp
        '''
        sys.stdout.write(f'{h}\n')
        exit()

    def add_help():
        h = f'''
        {italic}pylog add{end}: manually add a command
            > follow prompt to input command if not given at input (hit enter)
            > follow prompt to input any notes or leave blank (hit enter)
        
        $ pylog add
        $ pylog add blastp -in file -out file
        '''
        sys.stdout.write(f'{h}\n')
        exit()
    
    def find_help():
        h = f'''
        {italic}pylog find{end}: search the log for a term
            > follow prompt to input search term if not given at input (hit enter)
            > searches all categories (date, time, conda env, directory, notes, command)
            > find option is also available within 'view'
            > to search for 'h' or 'help', input 'pylog find' and follow the prompt
        
        $ pylog find
        $ pylog find blastp
        '''
        sys.stdout.write(f'{h}\n')
        exit()
    
    def view_help():
        h = f'''
        {italic}pylog view{end}: view, search, edit or remove indexes in the log file
            > enter options at prompt:
                > {italic}find{end}: search the log for a term
                    > searches all categories (date, time, conda env, directory, notes, command)
                > {italic}remove{end}: remove item from log file by index
                    > enter one index or multiple indexes at prompt (space or comma separated)
                > {italic}edit{end}: edit item from log file by index
                    > enter one index or multiple indexes at prompt (space or comma separated)
            > by default 'view' shows the last 25 entries
                > to change the default, input an integer after view
            > to exit type 'q', 'quit', 'exit' or Ctr-C
        
        $ pylog view
        $ pylog view 100
        '''
        sys.stdout.write(f'{h}\n')
        exit()
    
    def clear_help(self):
        h = f'''
        {italic}pylog clear{end}: clear/delete the log file
            > prompt to verify clear
            > does not clear the local log file
            > the local log file can be removed/edited/viewed manually
        
        $ pylog clear
        '''
        sys.stdout.write(f'{h}\n')
        exit()
    
    def backup_help(self):
        h = f'''
        {italic}pylog backup{end}: copy the log file to create a backup
            > name of new backup file: <logfile>.DMY.time.db
        
        $ pylog backup
        '''
        sys.stdout.write(f'{h}\n')
        exit()
    
    def remove_help(self):
        h = f'''
        {italic}pylog remove{end}: remove the last command logged
            > prompt to verify removal
            > use 'view' to remove one or multiple entries by index
                > enter 'remove' within the view prompt
        
        $ pylog remove
        '''
        sys.stdout.write(f'{h}\n')
        exit()


if __name__ == '__main__':
    try:
        func = sys.argv[2].strip('-')
        if func.isdigit():
            func = f'offset_{func}'
    except IndexError:
        func = 'main'
    try:
        history = sys.argv[1].split('\n')
    except IndexError:
        sys.stdout.write('\nError: history not found or PyLogger improperly set up.\n\n')
        exit()

    Main(history, func)



#
#
#