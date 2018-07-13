# coding=utf-8
# brief:通用库
# LastModifyTime:2018-3-20
# author:zhangzhilin/z03467
import ConfigParser
import os
import time
import threading
import datetime
import sys
import signal
import thread
import subprocess
from subprocess import PIPE


class LogHandle:
    def __init__(self, log_file_path):
        self.m_set_max_log_size = 5*1024*1024
        self.m_set_flush_tic = 0
        self.m_set_flush_time_rec = 0
        self.m_set_flush_max_line = 5
        self.m_set_flush_max_time = 5

        self.m_set_max_bk_log = 0
        if os.path.isabs(log_file_path):
            self.set_log_file_path = log_file_path
        else:
            self.set_log_file_path = os.path.join(os.getcwd(), log_file_path)
        self.mutex = threading.RLock()

        log_file_folder = os.path.dirname(log_file_path)
        try:
            if log_file_folder and not os.path.exists(log_file_folder):
                os.mkdir(log_file_folder)
            self.log_fd = open(log_file_path, 'a+', os.O_APPEND)
        except IOError:
            print 'Failed to open logfile [%s]' % log_file_path
            pass
        pass

    def get_log_name(self, idx):
        if 0 == idx:
            return self.set_log_file_path
        if idx > self.m_set_max_bk_log:
            return None
        return self.set_log_file_path + ('%02d' %idx)
        pass

    def move_log_to_next(self, cur_idx):
        cur_log_name = self.get_log_name(cur_idx)
        next_log_name = self.get_log_name(cur_idx + 1)
        if None == next_log_name:
            # print 'Log remove [%s]' % cur_log_name
            os.remove(cur_log_name)
            return
        if os.path.exists(next_log_name):
            self.move_log_to_next(cur_idx + 1)
        # print 'Log rename [%s] [%s]' % (cur_log_name, next_log_name)
        os.rename(cur_log_name, next_log_name)
        return
        pass

    def switch_log_file(self):
        self.log_fd.close()
        self.move_log_to_next(0)
        self.log_fd = open(self.set_log_file_path, 'a+', os.O_APPEND)
        self.m_set_flush_tic = 0
        self.m_set_flush_time_rec = time.time()
        pass

    def set_bk_log_cnt(self, cnt):
        self.m_set_max_bk_log = cnt

    def log(self, log_str, silent=False):
        # silent=True 则不输出log到屏幕
        self.mutex.acquire()
        try:
            cur_time = datetime.datetime.today()
            # cur_date= get_cur_date()
            time_str = str(cur_time) + '  '
            self.log_fd.write(time_str)
            self.log_fd.write(log_str)
            if not silent:
                try:
                    print log_str
                except UnicodeEncodeError:
                    pass
                except:
                    print 'Failed to print log to console'
            self.log_fd.write('\n')
        except:
            e = sys.exc_clear()
            print 'Failed to log [%s]' % str(e)

        if self.log_fd.tell() > self.m_set_max_log_size:
            self.switch_log_file()
        self.m_set_flush_tic += 1
        if self.m_set_flush_tic >= self.m_set_flush_max_line:
            self.m_set_flush_tic = 0
            self.log_fd.flush()
        if time.time() - self.m_set_flush_time_rec >= self.m_set_flush_max_time:
            self.m_set_flush_time_rec = time.time()
            self.m_set_flush_tic = 0
            self.log_fd.flush()
        self.mutex.release()

    def write_only(self, log_str):
        self.log_fd.write(log_str)
        self.log_fd.write('\n')
        pass

    def write(self, log_str):
        pass

gstLoghandler = LogHandle('common_lib.log')


class CfgParse(ConfigParser.ConfigParser):
    def __init__(self, cfg_file_path):
        ConfigParser.ConfigParser.__init__(self)
        self.cfg_file_path = cfg_file_path
        if not os.path.exists(cfg_file_path):
            gstLoghandler.log('cfg file not exist')
            self.create_default_cfg()
        self.readfp(open(cfg_file_path))
        self.log = gstLoghandler.log
        pass

    def create_default_cfg(self):
        gstLoghandler.log('create default configure file')
        with open(self.cfg_file_path, 'w+') as fd:
            pass
        pass

    def fill_default_cfg(self, default_cfg):
        self.log('fill cfg with default set')
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


class ThreadHandler(object):
    def __init__(self):
        self.lock = threading.RLock()
        self.m_quit_flag = False
        self.m_set_work_thread_cnt = 1
        # 保持线程个数 如果有work线程挂掉 重新增加新的work线程
        self.m_set_keep_thread_alive = False
        self.m_running_thread_cnt = 0
        self.m_running_work_thread_cnt = 0
        self.m_self_terminated_work_thread_cnt = 0
        # 三次ctrl+c强制退出
        self.m_set_force_quit_cnt = 3
        self.m_ctrl_c_cnt = 0

        self.m_load_task_done = False
        self.m_task_list = list()

        self.log = gstLoghandler.log

        try:
            signal.signal(signal.SIGINT, self.ctrl_c_signal_handler)
        except ValueError:
            self.log('Failed to sign SIGINT, maybe in sub-thread, ignore it')
        pass

    def ctrl_c_signal_handler(self, signal, frame):
        self.stop()

    def work_thread(self):
        while True:
            time.sleep(5)
            self.log('Thread run...')
            if self.m_quit_flag:
                break
        pass

    def _work_thread(self, func=None):
        self.m_running_thread_cnt += 1
        if func is None:
            # 单独为work线程计数
            self.m_running_work_thread_cnt += 1
        try:
            if func is not None:
                func()
            else:
                ret = self.work_thread()
                if 0 == ret:
                    # return 0 to tell manage, work thread quit at his will
                    self.m_self_terminated_work_thread_cnt += 1
        except:
            self.log('Thread Failed on Exception')
            self.log(str(sys.exc_info()))
        if func is None:
            self.m_running_work_thread_cnt -= 1
        self.m_running_thread_cnt -= 1
        pass

    def _manage_thread(self):
        self.m_running_thread_cnt += 1
        time.sleep(5)
        while True:
            if self.m_quit_flag:
                break
            if self.m_set_keep_thread_alive:
                if self.m_running_work_thread_cnt < self.m_set_work_thread_cnt:
                    cnt = self.m_set_work_thread_cnt - self.m_running_work_thread_cnt - self.m_self_terminated_work_thread_cnt
                    for i in range(cnt):
                        pro = threading.Thread(target=self._work_thread)
                        pro.setDaemon(True)
                        pro.start()
                    self.log('Keep Thread Alive Flag is set, so start new work thread cnt [%d]' % cnt)
            time.sleep(3)
        self.m_running_thread_cnt -= 1
        pass

    def set_work_thread_cnt(self, cnt):
        self.m_set_work_thread_cnt = cnt
        pass

    def start_one_thread(self, func):
        pro = threading.Thread(target=self._work_thread, args=(func,))
        pro.setDaemon(True)
        pro.start()
        pass

    def get_one_task(self):
        self.lock.acquire()
        if not len(self.m_task_list):
            self.lock.release()
            return None
        task = self.m_task_list.pop()
        self.lock.release()
        return task

    def add_tasks(self, tasks):
        self.lock.acquire()
        if type(tasks) == list:
            for task in tasks:
                self.m_task_list.append(task)
                self.log('Add task [%s]' % task.get_column_value('url'))
        else:
            self.m_task_list.append(tasks)
        self.lock.release()
        pass

    def do_start(self):
        pass

    def do_stop(self):
        pass

    def start(self):
        self.log('Start thread')
        for i in range(self.m_set_work_thread_cnt):
            pro = threading.Thread(target=self._work_thread)
            pro.setDaemon(True)
            pro.start()
        # 启动一个内部的manage管理线程
        pro = threading.Thread(target=self._manage_thread)
        pro.setDaemon(True)
        pro.start()
        self.do_start()
        pass

    def stop(self):
        self.m_quit_flag = True
        self.m_ctrl_c_cnt += 1
        self.log('Stop Thread')
        while True:
            if self.m_running_thread_cnt == 0:
                self.log('All thread Quit')
                break
            else:
                self.log('Wait, Running Thread Cnt [%d]' % self.m_running_thread_cnt)
            time.sleep(3)
        self.do_stop()
        if self.m_ctrl_c_cnt > self.m_set_force_quit_cnt:
            self.log('Force quit!!')
            exit(0)
        self.log('Stoped')
        pass


class ThreadItem:
    def __init__(self):
        self.m_thread_id = thread.get_ident()
        self.m_last_alive_tic = time.time()
        self.m_data = ''
        pass

    def __str__(self):
        return 'id [%d], thread [%d] data[%s]' % (id(self), self.m_thread_id, str(self.m_data))

    def set_data(self, data):
        self.m_data = data

    def get_data(self):
        return self.m_data


class ThreadIsolateItem:
    # 这个主要用于多线程对同一个实例的使用
    # 为了节省内存 通常多线程公用一个实例 但同时每个线程又都希望更改该实例的某些变量，
    # 于是该class对变量提供set和get 每个线程set和get变量只在该线程内生效，其他线程不影响
    def __init__(self):
        self.lock = threading.RLock()
        self.data_dict = dict()
        self.log = gstLoghandler.log
        pass

    def set_thread_item(self, name, data):
        # for muti thread
        thread_id = thread.get_ident()
        thread_item_finded = None
        self.lock.acquire()
        if self.data_dict.has_key(name):
            for thread_item in self.data_dict[name]:
                if thread_item.m_thread_id == thread_id:
                    thread_item_finded = thread_item
                    thread_item.m_last_alive_tic = time.time()
                    break
            pass
        else:
            self.data_dict[name] = list()
        # check timeout alive
        for idx, thread_item in enumerate(self.data_dict[name]):
            time_val = time.time() - thread_item.m_last_alive_tic
            if time_val >= 60:
                self.data_dict[name].pop(idx)
                break
        if thread_item_finded is None:
            thread_item_finded = ThreadItem()
            self.data_dict[name].append(thread_item_finded)
        thread_item_finded.m_data = data
        self.lock.release()
        pass

    def get_thread_item(self, name):
        thread_id = thread.get_ident()
        ret_data = 'not found'
        find_flag = False
        if self.data_dict.has_key(name):
            self.lock.acquire()
            for thread_item in self.data_dict[name]:
                if thread_item.m_thread_id == thread_id:
                    ret_data = thread_item.m_data
                    thread_item.m_last_alive_tic = time.time()
                    find_flag = True
            self.lock.release()
        if not find_flag:
            self.log('Failed to find item [%s]' % name)
            pass
        return ret_data
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


class ShellCmd:
    def __init__(self):
        self.m_ret = 0
        self.m_set_poll_gap = 0.5
        self.m_set_timeout_sec = 10
        self.m_set_discard_buf = False
        self.log = gstLoghandler.log
        pass

    def set_timeout(self, timeout=10):
        self.m_set_timeout_sec = timeout
        pass

    def get_last_ret(self):
        return self.m_ret

    def run_cmd(self, args=list()):
        pipe = subprocess.Popen(args=args, stderr=PIPE, stdin=PIPE, stdout=PIPE)
        out = ''
        start_time_rec = time.time()
        while True:
            if pipe.poll() is not None:
                break
            line_str = pipe.stdout.read()
            if not self.m_set_discard_buf and not line_str:
                out += line_str
            time.sleep(self.m_set_poll_gap)
            if time.time() - start_time_rec > self.m_set_timeout_sec > 0:
                self.log('Runt command timeout [%s]' % str(args))
                self.m_ret = -1
                pipe.terminate()
                return out
        self.m_ret = pipe.returncode
        if not self.m_set_discard_buf:
            out += pipe.stdout.read()
        return out
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


def thread_2():
    for i in range(5):
        print 'Hi'
        time.sleep(2)
    pass

def test_thread():
    thread_handler = ThreadHandler()
    thread_handler.start()
    thread_handler.start_one_thread(thread_2)
    time.sleep(20)
    pass

if __name__ == '__main__':
    test_thread()
