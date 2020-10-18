from re import search as re_search
from time import time
import sys
import gzip
from datetime import datetime

def init_list(list1, list2, def_value=0):
    for x in list2:
        list1.append(def_value)

def concat_re_str(string_list):
    if string_list is None:
        return -1
    cat_str = r''
    i = 0
    for string in string_list:
        cat_str += r'(?P<m{}>'.format(str(i)) + string + r')|'
        i += 1
    cat_str = cat_str[:-1]
    return cat_str

def get_index_from_key(string):
    string = string[1:]
    return int(string)


class log_store:
    def __init__(self, index=None, match_log_file=None, count=0, pattern=None,
                 time_string_regex=r"(?P<time>(\d{4})\-(\d{2})\-(\d{2})T(\d{2})\:(?P<minute>\d{2})\:(\d{2})\.(\d{6}))",
                 time_string_format="%Y-%m-%dT%H:%M:%S.%f", interval=5):
        if match_log_file is not None:
            self.fh = open(match_log_file, 'a')
            self.file_open = True
        else:
            self.fh = None
            self.file_open = False
        self.index = index
        self.total_count = count
        self.pattern = pattern
        self.log_list = []
        self.time_string_regex = time_string_regex
        self.time_string_format = time_string_format
        self.minute_interval = interval
        self.interval_table = None

    def get_base_time(self, line):
        match = re_search(self.time_string_regex, line)
        assert match is not None, "time could not parsed in log line : \n    {}".format(line)
        temp_dict = match.groupdict()
        line_minute = int(temp_dict['minute'])
        base_minute = (line_minute // self.minute_interval) * self.minute_interval
        line_time = datetime.strptime(temp_dict['time'], self.time_string_format)
        return datetime(line_time.year, line_time.month, line_time.day,
                             line_time.hour, base_minute)

    def add_log(self, log_line, print_to_file=True, copy_to_list=False):
        if self.file_open is True and print_to_file is True:
            self.fh.write(log_line)
        self.total_count += 1
        base_time = self.get_base_time(log_line)
        if self.interval_table is None:
            self.interval_table = {}
        if base_time not in self.interval_table:
            self.interval_table[base_time] = {}
            self.interval_table[base_time]['log_count'] = 1
            self.interval_table[base_time]['log_list'] = []
            self.interval_table[base_time]['log_list'].append(log_line)
            self.interval_table[base_time]['interval_start_time'] = base_time
        else:
            self.interval_table[base_time]['log_count'] += 1
            self.interval_table[base_time]['log_list'].append(log_line)
 
        """
        if copy_to_list is True:
            self.log_list.append(log_line)
        """

    def close_file(self):
        if self.file_open is True:
            close(self.fh)
        self.file_open = False

    def get_log_stats(self, print_to_screen=False, print_to_file=False):
        if self.pattern is not None and print_to_screen is True:
            print("")
            print("logs found for pattern {} : {}".format(self.pattern, self.total_count))
            if self.interval_table is None:
                return
            for key in self.interval_table.keys():
                print("In interval starting at "
                      "{} : {}".format(self.interval_table[key]['interval_start_time'],
                                       self.interval_table[key]['log_count']))
                for line in self.interval_table[key]['log_list']:
                    print("    " + line.rstrip("\n"))
        if print_to_file is True:
            if self.interval_table is None:
                return
            self.fh.write("\n")
            for key in self.interval_table.keys():
                self.fh.write("log_checker.py update : Logs found in interval starting at {} : {}"
                              "".format(self.interval_table[key]['interval_start_time'],
                                        self.interval_table[key]['log_count']))
                self.fh.write("\n")
        

def init_log_stores(log_regex_list, print_to_file=True, file_name_prefix=None):
    log_store_list = []
    i = 0
    for regex in log_regex_list:
        if print_to_file is True:
            if file_name_prefix is None:
                match_log_file="matched_logs{}.txt".format(i)
            else:
                match_log_file="{}{}.txt".format(file_name_prefix, i)
        else:
            match_log_file=None
        log_store_list.append(log_store(
            index=i, pattern=regex,
            match_log_file=match_log_file))
        i += 1
    return log_store_list

def close_log_store_files(objects_list):
    if objects_list is None:
        return
    for store in objects_list:
        store.close_file()

def get_matched_logs(log_file_list, log_regex_source=None, return_list=True,
                     print_to_file=True, file_name_prefix=None, print_to_screen=True):
    """
    """
    if isinstance(log_regex_source, str):
        # given string is a file's name
        f = open(log_regex_source, 'r')
        string_list = f.readlines()
        log_regex_list = []
        for string in string_list:
            log_regex_list.append(string.rstrip('\n'))
    elif log_regex_source is None or not isinstance(log_regex_source, list):
        return "log_regex_list argument must be either a file name or a list of strings"

    log_store_list = init_log_stores(log_regex_list, print_to_file=print_to_file,
                                     file_name_prefix=file_name_prefix)
    regex_string = concat_re_str(log_regex_list)
    print("Summed up regex string : {}".format(regex_string))

    # a = time()
    logs_parsed = 0
    index = 0

    for log_file_name in log_file_list:
        if "gz" in log_file_name:
            f = gzip.open(log_file_name, 'rt')
        else:
            f = open(log_file_name, 'r')

        for line in f:
            match = re_search(regex_string, line)
            if match is None:
                continue
            temp_dict = match.groupdict()
            for key in temp_dict:
                if temp_dict[key] is None:
                    continue
                index = get_index_from_key(key)
                log_store_list[index].add_log(line)
            logs_parsed += 1
        f.close

    # b = time()
    # print("execution time for parsing : {}".format(b-a))

    for store in log_store_list:
        store.get_log_stats(print_to_screen=True, print_to_file=True)
    if return_list is False:
        return
    matched_log_lists = []
    for store in log_store_list:
        matched_log_lists.append(store.log_list)
    return matched_log_lists


if __name__ == "__main__":
    log_regex_list = sys.argv[1] 
    i = 2
    log_file_list = []
    while (i < len(sys.argv)):
        log_file_list.append(sys.argv[i])
        i += 1

    # avoid named groups in log_regex_list and ensure all are raw string literals
    """
    log_regex_list = [
        r'DMA\szone\:\s\d+\spages',
        r'ipercpu\:\sEmbedded\s\d+\spages/cpu',
        r'\d+.*memmap'
        ]
    log_regex_list = "regex_file.txt"
    """

    print("starting log check")
    print("")
    a = time()
    get_matched_logs(log_file_list, log_regex_source=log_regex_list)
    b = time()
    print("")
    print("done")
    print("execution time for whole program : {}".format(b-a))
