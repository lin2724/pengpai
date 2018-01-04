# coding=utf-8
import os
import re
import requests
from lxml import etree
from common_lib import LogHandle

gLogHandle = LogHandle('pengpai.log')


class InfoParser:
    def __init__(self):
        self.log = gLogHandle.log
        pass

    def do_parse(self, content):
        print self.title(content)
        print self.news_about(content)
        print self.time(content)
        print self.source(content)
        print self.news_editor(content)
        print self.news_keyword(content)
        print self.news_text(content)
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

def test():
    new_info_parser = InfoParser()
    with open('test.html', 'rb') as fd:
        content = fd.read()
        new_info_parser.do_parse(content)
    pass


if __name__ == '__main__':
    test()























