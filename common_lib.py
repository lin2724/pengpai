import ConfigParser
import os
import time
import threading
import datetime
import sys


class CfgParse(ConfigParser.ConfigParser):
    def __init__(self, cfg_file_path):
        ConfigParser.ConfigParser.__init__(self)
        self.cfg_file_path = cfg_file_path
        if not os.path.exists(cfg_file_path):
            print 'cfg file not exist'
            self.create_default_cfg()
        self.readfp(open(cfg_file_path))
        pass

    def create_default_cfg(self):
        print 'create default configure file'
        with open(self.cfg_file_path, 'w+') as fd:
            pass
        pass

    def fill_default_cfg(self, default_cfg):
        print 'fill cfg with default set'
        with open(self.cfg_file_path, 'w+') as fd:
            fd.write(default_cfg)
        self.readfp(open(self.cfg_file_path))

    def check_cfg_empty(self):
        with open(self.cfg_file_path, 'r') as fd:
            content = fd.read(1)
        if not len(content):
            return True
        return False
        pass
    pass


class ConColor:
    def __init__(self):
        pass
    Black = '\33[30m'
    Red = '\33[31m'
    Green = '\33[32m'
    Yellow = '\33[33m'
    Blue = '\33[34m'
    Magenta = '\33[35m'
    Cyan = '\33[36m'
    LightGray = '\33[37m'
    DarkGray = '\33[90m'
    LightRed = '\33[91m'
    LightGreen = '\33[92m'
    LightYellow = '\33[93m'
    LightBlue = '\33[94m'
    LightMagenta = '\33[95m'
    LightCyan = '\33[96m'
    White = '\33[97m'

    Underline = '\33[4m'
    Blink = '\33[5m'
    Reverse = '\33[7m'
    Hidden = '\33[8m'
    Reset = '\33[0m'
    ResetUnderline = '\33[24m'
    ResetBlink = '\33[25m'
    ResetReverse = '\33[27m'
    ResetHidden = '\33[28m'

    if os.name == 'nt' and False:
        Black = ''
        Red = ''
        Green = ''
        Yellow = ''
        Blue = ''
        Magenta = ''
        Cyan = ''
        LightGray = ''
        DarkGray = ''
        LightRed = ''
        LightGreen = ''
        LightYellow = ''
        LightBlue = ''
        LightMagenta = ''
        LightCyan = ''
        White = ''

        Underline = ''
        Blink = ''
        Reverse = ''
        Hidden = ''
        Reset = ''
        ResetUnderline = ''
        ResetBlink = ''
        ResetReverse = ''
        ResetHidden = ''


class ConColorShow(ConColor):

    def warning_show(self, str_info):
        print self.Red + str_info + self.Reset
        pass

    def highlight_show(self, str_info):
        print self.LightYellow + str_info + self.Reset
        pass

    def blink_show(self, str_info):
        print self.Blink + str_info + self.Reset
        pass

    def error_show(self, str_info):
        print self.LightRed + str_info + self.Reset
        pass

    def color_show(self, str_info, color):
        print color + str_info + self.Reset
        pass

    def common_show(self, str_info):
        print str_info


class MyArgParse:
    def __init__(self):
        self.OptionList = list()
        pass

    def __str__(self):
        info_list = str()
        for option_info in self.OptionList:
            info_list += '%15s    %s' % (option_info['option_str'], option_info['help_info'])
            info_list += '\n\r'
        return info_list
        pass

    def add_option(self, option_str, arg_num, help_info):
        option_info_dict = dict()
        option_info_dict['option_str'] = option_str
        if type(arg_num) != list:
            tmp_arg_num = arg_num
            arg_num = list()
            arg_num.append(tmp_arg_num)
        option_info_dict['arg_num_list'] = arg_num
        option_info_dict['help_info'] = help_info
        option_info_dict['arg_list'] = list()
        option_info_dict['set'] = False

        self.OptionList.append(option_info_dict)

        pass

    def check_arg_num_valid(self, arg_list, arg_num_list):
        arg_count = len(arg_list)
        valid_arg_count = 0
        for i in range(arg_count):
            if arg_list[i][:1] == '-':
                break
            valid_arg_count += 1
        for arg_num in arg_num_list:
            if valid_arg_count >= arg_num:
                return True
        return False
        pass

    def parse(self, arg_list):
        arg_i = 0
        valid_option_count = 0
        for arg in arg_list:
            for option_info in self.OptionList:
                if arg == option_info['option_str']:
                    if not self.check_arg_num_valid(arg_list[arg_i+1:], option_info['arg_num_list']):
                        ConColorShow().error_show('ERROR:option %s need %s args' % (option_info['option_str'], str(option_info['arg_num_list']) ))
                        print option_info['help_info']
                        return False
                    else:
                        arg_num = self.get_real_arg_num(arg_list[arg_i+1:], option_info['arg_num_list'])
                        option_info['arg_list'] = arg_list[arg_i+1:][:arg_num + 1]
                        option_info['set'] = True
                        valid_option_count += 1
            arg_i += 1
        return valid_option_count
        pass

    def get_real_arg_num(self, arg_list, arg_num_list):
        arg_count = len(arg_list)
        valid_arg_count = 0
        for i in range(arg_count):
            if arg_list[i][:1] == '-':
                break
            valid_arg_count += 1
        max_num_arg = 0
        for arg_num in arg_num_list:
            if valid_arg_count >= arg_num > max_num_arg:
                max_num_arg = arg_num

        return max_num_arg
        pass

    def check_option(self, option_str):
        for option_info in self.OptionList:
            if option_info['option_str'] == option_str:
                return option_info['set']

    def get_option_args(self, option_str):
        for option_info in self.OptionList:
            if option_info['option_str'] == option_str:
                if not option_info['set']:
                    ConColorShow().error_show('ERROR:option %s not set!' % option_str)
                return option_info['arg_list']
        ConColorShow().error_show('ERROR:option %s not found!' % option_str)
        return ''
        pass

    def init_example(self):
        arg_parse = MyArgParse()
        arg_parse.add_option('-cp', 0, 'do copy from scan list')
        arg_parse.add_option('-d', [0,1], 'specific dir to scan')
        arg_parse.add_option('-t', 1, 'min time specific')
        arg_parse.add_option('-desc', 1, 'specific destination folder to copy')
        arg_parse.add_option('-p', 0, 'print default scan folder and des folder')
        return arg_parse
        pass


def get_dir_depth(dir_path):
    depth = 0
    if 'nt' == os.name:
        depth = dir_path.count('\\')
    else:
        depth = dir_path.count('/')
    if os.path.isabs(dir_path):
        depth -= 1
    return depth
    pass


def convert_list(list_or_item):
    if type(list_or_item):
        return list_or_item
    ret_list = list()
    ret_list.append(list_or_item)
    return ret_list


class ScanHandle:
    def __init__(self):
        pass

    # add tail such as '.so' to skip scan those file
    # tail_str can be list or item
    def add_filter_tail(self, tail_str):
        pass

    def add_scan_tail(self, tail_str):
        pass


def scan_new_files_v2(scan_folder, time_gap, scan_depth=1000):
    """
    time_gap:>0 scan file changed within time_gap(sec) from now
             =0 will scan and return all files in scan_folder
    """
    try:
        time_min = int(time_gap)
    except ValueError:
        print 'ERROR:only number! %s' % time_gap
        return None
    limit_sec = time_min*60
    now_sec = time.time()
    new_file_full_path_list = list()
    scan_folder_list = list()
    start_time = time.time()
    if type(scan_folder) == list:
        scan_folder_list = scan_folder
    else:
        scan_folder_list.append(scan_folder)
    for scan_folder in scan_folder_list:
        if not os.path.exists(scan_folder):
            print 'folder [%s] not exist!' % scan_folder
            return None
        for (dirpath, dirnames, filenames) in os.walk(scan_folder):
            #stat = os.stat(dirpath)
            #if stat.st_mtime + limit_sec < now_sec:
            #    continue
            dir_depth = get_dir_depth(dirpath) - get_dir_depth(scan_folder)
            if dir_depth >= scan_depth:
                #print ('skip dub dir of [%s]' % dirpath)
                count = len(dirnames)
                for i in range(count):
                    dirnames.pop()

            for filename in filenames:
                stat = os.stat(os.path.join(dirpath, filename))
                if stat.st_mtime + limit_sec >= now_sec or limit_sec == 0:
                    new_file_full_path = os.path.join(dirpath, filename)
                    ConColorShow().color_show('%24s  %12s' % (filename, time.ctime(stat.st_mtime)), ConColorShow.Green)
                    new_file_full_path_list.append(new_file_full_path)
            pass
        print '### Dir %s changed count [%d]###' % (scan_folder, len(new_file_full_path_list))
    print 'time use %f' % (time.time() - start_time)
    return new_file_full_path_list
    pass


class LogHandle:
    def __init__(self, log_file_path):
        self.set_max_log_size = 5*1024*1024
        self.set_log_file_path = log_file_path[:]
        self.set_log_file_path_bk = self.set_log_file_path + '-bk'
        self.mutex = threading.Lock()

        log_file_folder = os.path.dirname(log_file_path)
        try:
            if log_file_folder and not os.path.exists(log_file_folder):
                os.mkdir(log_file_folder)
            self.log_fd = open(log_file_path, 'a+', os.O_APPEND)
        except IOError:
            print 'Failed to open logfile [%s]' % log_file_path
            pass
        pass

    def switch_log_file(self):
        self.mutex.acquire()
        if os.path.exists(self.set_log_file_path_bk):
            os.remove(self.set_log_file_path_bk)
        self.log_fd.close()
        os.rename(self.set_log_file_path, self.set_log_file_path_bk)
        self.log_fd = open(self.set_log_file_path, 'a+', os.O_APPEND)
        self.mutex.release()
        pass

    def log(self, log_str):
        self.mutex.acquire()
        try:
            cur_time = datetime.datetime.today()
            # cur_date= get_cur_date()
            time_str = str(cur_time) + '  '
            self.log_fd.write(time_str)
            self.log_fd.write(log_str)
            print log_str
            self.log_fd.write('\n')
        except:
            e = sys.exc_clear()[0]
            print 'Failed to log [%s]' % e
        self.mutex.release()
        if self.log_fd.tell() > self.set_max_log_size:
            self.switch_log_file()

    def write_only(self, log_str):
        self.log_fd.write(log_str)
        self.log_fd.write('\n')
        pass

    def write(self, log_str):
        pass
