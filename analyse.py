# coding=utf-8
import os
import sys
import re
import requests
from lxml import etree
from lxml import html
from io import StringIO
from openpyxl import Workbook
from openpyxl import load_workbook

def clean_str(str_line):
    pattern = '\s*(?P<content>.*)'
    m = re.search(pattern, str_line)
    if m:
        return m.group('content')
    return ''


def get_info_from_content(article_content):
    title = ''
    auth = ''
    key_word = ''
    from_src = ''
    article_time = ''
    comments_count = 0
    thumb_up_count = 0

    root = etree.HTML(article_content)
    nodes = root.xpath('//h1[@class="news_title"]')
    if len(nodes):
        title = nodes[0].text
        print title
    else:
        print 'about not found'

    nodes = root.xpath('//div[@class="news_about"]')
    if len(nodes):
        auth = nodes[0].xpath('.//p')[0].text
        info_node = nodes[0].xpath('.//p')[1]
        article_time = clean_str(info_node.text)
        from_src = info_node.xpath('.//span')[0].text
        print auth
        print article_time
        print from_src
    else:
        print 'about not found'

    nodes = root.xpath('//div[@class="news_keyword"]')
    if len(nodes):
        key_word = nodes[0].text
    else:
        print 'keyword not found'

    nodes = root.xpath('//a[@id="zan"]')
    if len(nodes):
        thumb_up_count = clean_str(nodes[0].text)
    else:
        print 'zan not found'

    nodes = root.xpath('//h2[@id="comm_span"]')
    if len(nodes):
        print nodes[0].text
        comments_count = clean_str(nodes[0].xpath('.//span')[0].text)
        print comments_count
    else:
        print 'command not found'

    ret_dict = dict()

    ret_dict['title'] = title
    ret_dict['auth'] = auth
    ret_dict['key_word'] = key_word
    ret_dict['from_src'] = from_src
    ret_dict['article_time'] = article_time
    ret_dict['comments_count'] = comments_count
    ret_dict['thumb_up_count'] = thumb_up_count
    print ret_dict
    return ret_dict

    pass


class SaverXLSX:
    def __init__(self, file_path):
        self.file_path = file_path
        if os.path.exists(file_path):
            self.wb = load_workbook(filename=file_path)
            self.ws = self.wb.active
        else:
            self.wb = Workbook()
            self.ws = self.wb.active
            self.do_init_xlsx()

    def do_init_xlsx(self):
        self.ws.append(['title', 'auth', 'key_word', 'from_src', 'article_time', 'comments_count', 'thumb_up_count'])
        pass

    def quit(self):
        self.wb.save(filename=self.file_path)

    def insert_row(self, row_dict):
        self.ws.append([row_dict['title'],
                       row_dict['auth'],
                       row_dict['key_word'],
                       row_dict['from_src'],
                       row_dict['article_time'],
                       row_dict['comments_count'],
                       row_dict['thumb_up_count']])
        pass


def do_test(file_path):
    with open(file_path, 'r') as fd:
        content = fd.read()
        get_info_from_content(content)
    pass


def do_test_save(file_name):
    saver = SaverXLSX(file_name)
    saver.quit()

    pass


def get_all_file_list(folder_path):
    ret_list = list()
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_path[-len('.html'):] == '.html':
                ret_list.append(file_path)
                pass
    return ret_list


def do_parser_info(folder_path, xlsx_name):
    saver = SaverXLSX(xlsx_name)
    html_list = get_all_file_list(folder_path)
    for html_file in html_list:
        with open(html_file, 'r') as fd:
            content = fd.read()
            row_dict = get_info_from_content(content)
            saver.insert_row(row_dict)
    saver.quit()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        get_all_file_list(sys.argv[1])
        exit(0)
        do_test_save(sys.argv[1])
        exit(0)
        do_test(sys.argv[1])
    elif len(sys.argv) == 3:
        do_parser_info(sys.argv[1], sys.argv[2])











