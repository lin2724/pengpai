# coding=utf-8
import os
import re
import requests
from lxml import etree
from common_lib import LogHandle

gLogHandle = LogHandle('pengpai.log')


class ArticleInfo:
    def __init__(self):
        self.article_id = 0
        self.title = ''
        self.about = ''
        self.time = ''
        self.source = ''
        self.editor = ''
        self.keyword = ''
        pass

    def init_all(self, article_id, title, about, time, source, editor, keyword):
        self.article_id = article_id
        self.title = title[:]
        self.about = about[:]
        self.time = time[:]
        self.source = source[:]
        self.editor = editor[:]
        self.keyword = keyword[:]
        pass


class InfoParser:
    def __init__(self):
        self.log = gLogHandle.log
        pass

    def do_parse(self, article_id, content):
        article_info = ArticleInfo()
        article_info.init_all(article_id,
                              self.title(content),
                              self.news_about(content),
                              self.time(content),
                              self.source(content),
                              self.news_editor(content),
                              self.news_keyword(content))
        return article_info
        print self.title(content)
        print self.news_about(content)
        print self.time(content)
        print self.source(content)
        print self.news_editor(content)
        print self.news_keyword(content)
        pass

    def title(self, content):
        tr = etree.HTML(content)
        nodes = tr.xpath('//h1[@class="news_title"]')
        if not len(nodes):
            self.log('Failed to get title')
        else:
            return nodes[0].text.strip()
        return 'No title'
        pass

    def news_about(self, content):
        tr = etree.HTML(content)
        nodes = tr.xpath('//div[@class="news_about"]/p')
        if not len(nodes):
            self.log('Failed to get about')
        else:
            return nodes[0].text.strip()
        return 'No about'
        pass

    def time(self, content):
        tr = etree.HTML(content)
        nodes = tr.xpath('//div[@class="news_about"]/p')
        if len(nodes) < 2:
            self.log('Failed to get time')
        else:
            return nodes[1].text.strip()
        return 'No time'
        pass

    def source(self, content):
        tr = etree.HTML(content)
        nodes = tr.xpath('//div[@class="news_about"]/p')
        if len(nodes) < 2:
            self.log('Failed to get source')
        else:
            subnodes = nodes[1].xpath('span')
            if not len(subnodes):
                self.log('Faield to find source')
            else:
                return subnodes[0].text.strip().strip(u'来源：')
        return 'No time'
        pass


    def news_editor(self, content):
        tr = etree.HTML(content)
        nodes = tr.xpath('//div[@class="news_editor"]')
        if not len(nodes):
            self.log('Failed to get editor')
        else:
            return nodes[0].text.strip().strip(u'责任编辑：')
        return 'No editor'
        pass

    def news_keyword(self, content):
        tr = etree.HTML(content)
        nodes = tr.xpath('//div[@class="news_keyword"]')
        if not len(nodes):
            self.log('Failed to get keyword')
        else:
            return nodes[0].text.strip().strip(u'关键词 >>')
        return 'No keyword'
        pass

    def get_node_text_recurise(self, nodes):
        text = ''
        if not len(nodes):
            return ''
        if len(nodes) == 1:
            return nodes[0].text
        for node in nodes:
            text += self.get_node_text_recurise(node)
        return text
        pass

    def news_text(self, content):
        tr = etree.HTML(content)
        nodes = tr.xpath('//div[@class="news_txt"]')
        if not len(nodes):
            self.log('Failed to get content')
        else:
            return self.get_node_text_recurise(nodes)
        return 'No content'
        pass


def collect_all_files(folder):
    id_pattern = '(?P<id>\d+).*'
    ret_dict_list = list()
    article_id = 0
    for root, dirs, files in os.walk(folder):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_path.endswith('html'):
                m = re.search(id_pattern, file_name)
                if m:
                    article_id = m.group('id')
                dict_item = dict()
                dict_item['id'] = int(article_id)
                dict_item['file_path'] = file_path
                ret_dict_list.append(dict_item)
        pass
    return ret_dict_list
    pass


def collect_all_info(dict_list):
    for dict_item in dict_list:
        file_path = dict_item['file_path']
        article_id = dict_item['id']

    pass

def store_info(dict_item):
    store_file_name = 'info.txt'
    if not os.path.exists(store_file_name):
        with open(store_file_name, 'w+') as fd:
            fd.write('#######\n')
    with open(store_file_name, 'a') as fd:
        fd.write()

def test():
    new_info_parser = InfoParser()
    with open('test.html', 'rb') as fd:
        content = fd.read()
        new_info_parser.do_parse(0, content)
    pass

if __name__ == '__main__':
    collect_all_info('.')
    # test()























