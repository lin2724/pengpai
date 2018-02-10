# coding=utf-8
import os
import re
import sys
import requests
from lxml import etree
from lxml import html
from io import StringIO
from common_lib import MyArgParse
from common_lib import LogHandle

gstLogHandle = LogHandle('pengpai.log')

class ScrapLogin:
    def __init__(self):
        self.set_log_url = ''
        self.is_login = False
        self.set_cookie_file_name = 'cookie'
        self.set_domain = 'new'
        self.set_config_path = ''
        pass

    def do_login(self):
        pass

    def _save_cookie(self):
        pass

    def _get_config(self):
        pass


class ScrapContent2Data:
    def __init__(self):
        pass

    def load_urls(self):
        pass

    def run(self):
        pass

    def _save_data(self):
        pass


class ScrapContent2Urls:
    def __init__(self):
        pass

    def load_urls(self):
        pass

    def run(self, url):

        pass

    def _save_data(self):
        pass


class ScrapUrls2Content:
    def __init__(self):
        global gstLogHandle
        self.log = gstLogHandle.log
        self.set_timeout = 60
        pass

    def load_urls(self):
        pass

    def run_parse(self, url=None):
        try:
            r = requests.get(url, timeout=self.set_timeout)
            return r.content
        except requests.ConnectTimeout():
            self.log('Timeout while parse [%s]' % url)
            return ''
            pass
        pass


class ScrapMng:
    def __init__(self):
        pass

    def run(self):
        pass


class ScrapPengpaiNews:

    def __init__(self):
        pass

    def get_top_channels(self):
        pass

    def get_channel_lists(self):
        pass


class PPPageNode:
    def __init__(self):
        self.is_done = False
        self.content = ''
        self.sub_nodes = list()
        self.title = ''
        self.url = ''
        self.parent_node = None
        pass

    def do_parse(self):
        pass

    def get_content(self):
        return self.content

    def get_sub_nodes(self):
        return self.sub_nodes
        pass

    def add_sub_node(self, node):
        node.set_parent_node(self)
        self.sub_nodes.append(node)

    def init_node(self, url, title):
        self.url = url
        self.title = self.filter_title(title)
        pass

    def get_info(self):
        return self.title + self.url

    def get_title(self):
        return self.title

    def set_title(self, title):
        self.title = self.filter_title(title)

    def get_url(self):
        return self.url

    def get_self_id(self):
        pass

    def set_parent_node(self, node):
        self.parent_node = node
        pass

    def get_parent_node(self):
        return self.parent_node
        pass

    def filter_title(self, title):
        valid_title = ''
        for idx, char in enumerate(title):
            if '0' <= char <= '9' or 'A' <= char <= 'Z' or 'a' <= char <= 'z' or 127 < char:
                valid_title += char
        if not len(valid_title):
            valid_title = 'buggytitle'
        return valid_title
        pass


class PPFrontPageNode(PPPageNode):
    def do_parse(self):
        url2content_handle = ScrapUrls2Content()

        start_url = 'http://www.thepaper.cn/'
        start_url = self.url
        self.content = url2content_handle.run_parse(start_url)
        if not self.content:
            return
            pass
        write_content(self.content, 'start.html')

        tr = etree.HTML(self.content)
        channel_unit_tr_nodes = tr.xpath('//div[@class="head_banner"]/div[@class="bn_bt"]')
        for channel_unit_tr_node in channel_unit_tr_nodes:
            a_nodes = channel_unit_tr_node.xpath('a[@class="bn_a"]')
            if len(a_nodes):
                try:
                    channel_unit_node = PPChannelUnitPageNode()
                    url = start_url + a_nodes[0].attrib['href']
                    title = a_nodes[0].text
                    channel_unit_node.init_node(url, title)
                    self.add_sub_node(channel_unit_node)
                except IndexError:
                    print 'Page content not expected at [%s]' % start_url
                    continue
            else:
                continue
            sub_channel_tr_nodes = channel_unit_tr_node.xpath('div/ul[@class="clearfix"]/li/a')
            for sub_channel_tr_node in sub_channel_tr_nodes:
                channel_node = PPChannelPageNode()
                url = start_url + sub_channel_tr_node.attrib['href']
                title = sub_channel_tr_node.text
                channel_node.init_node(url, title)
                channel_unit_node.add_sub_node(channel_node)

    pass


class PPChannelUnitPageNode(PPPageNode):
    def get_self_id(self):
        m = re.match('.*channel_(?P<id>\d+)', self.url)
        if m:
            id = int(m.groupdict()['id'])
            return id
        return None
        pass
    pass


class PPChannelPageNode(PPPageNode):
    def do_parse(self):
        page_id = 0
        while True:
            channel_id = self.get_self_id()
            start_url = 'http://www.thepaper.cn/load_index.jsp?nodeids=%s&pageidx=%d' % (channel_id, page_id)
            print start_url
            url2content_handle = ScrapUrls2Content()
            content = url2content_handle.run_parse(start_url)
            if not len(content):
                print 'All article list get done, total article [%d]' % len(self.get_sub_nodes())
                break
            root = etree.HTML(content)
            nodes = root.xpath('//div[@class="news_li"]/h2/a')
            for node in nodes:
                article_node = PPArticlePageNode()
                url = 'http://www.thepaper.cn/' + node.attrib['href']
                title = node.text
                article_node.init_node(url, title)
                self.add_sub_node(article_node)
            page_id += 1
        pass

    def get_self_id(self):
        m = re.match('.*list_(?P<id>\d+)', self.url)
        if m:
            id = int(m.groupdict()['id'])
            return id
        return None
        pass

    pass


class PPArticlePageNode(PPPageNode):
    def do_parse(self):
        if check_if_exist(self.get_parent_node().get_parent_node(), self.get_parent_node(), self):
            print 'Already exist, skip [%s]' %self.url
            return True
        start_url = self.url
        #start_url = 'http://www.thepaper.cn/newsDetail_forward_1742361'
        print start_url
        url2content_handle = ScrapUrls2Content()
        self.content = url2content_handle.run_parse(start_url)
        if not len(self.content):
            print 'Empty content'
            return False
        root = etree.HTML(self.content)
        title_node = root.xpath('//div[@class="newscontent"]/h1[@class="news_title"]')
        news_about_node = root.xpath('//div[@class="newscontent"]/div[@class="news_about"]')
        news_txt_node = root.xpath('//div[@class="newscontent"]/div[@class="news_txt"]')

        if len(title_node):
            self.title = self.filter_title(title_node[0].text)
        else:
            self.title = 'None'

        self.get_pic_from_content()
        store_new_article(self.get_parent_node().get_parent_node(), self.get_parent_node(), self)
        pass

    def get_self_id(self):
        m = re.match('.*newsDetail_forward_(?P<id>\d+)', self.url)
        if m:
            id = int(m.groupdict()['id'])
            return id
        return None
        pass

    def get_pic_from_content(self):
        root = etree.HTML(self.content)
        news_txt_nodes = root.xpath('//div[@class="newscontent"]/div[@class="news_txt"]')
        try:
            img_nodes = news_txt_nodes[0].xpath('.//img[@src]')
        except IndexError:
            print 'Page content for img not expected'
            return
        for idx, img_node in enumerate(img_nodes):
            img_url = img_node.attrib['src']
            img_name = os.path.basename(img_url)
            url2content_handle = ScrapUrls2Content()
            img_content = url2content_handle.run_parse(img_url)
            if len(img_content):
                store_new_article_file(self.get_parent_node().get_parent_node(), self.get_parent_node(), self, img_name, img_content)
        pass
    pass


def write_content(content, file_name):
    with open(file_name, 'w+') as fd:
        fd.write(content)


def do_test_get_channels():
    ret_list = list()
    url2content_handle = ScrapUrls2Content()

    start_url = 'http://www.thepaper.cn/'
    content = url2content_handle.run_parse(start_url)
    write_content(content, 'start.html')

    tr = etree.HTML(content)
    nodes = tr.xpath('//div[@class="head_banner"]/div/a')
    for node in nodes:
        item = dict()
        item['title'] = node.text
        item['url'] = node.attrib['href']
        ret_list.append(item)
        list_nodes = node.xpath('//ul[@class="clearfix"]/li/a')
        item['subs'] = list()
        for list_node in list_nodes:
            sub_dict = dict()
            sub_dict['url'] = list_node.attrib['href']
            sub_dict['title'] = list_node.text
            item['subs'].append(sub_dict)
            print list_node.text, list_node.attrib['href']

    write_content(str(ret_list), 'items.txt')
    return ret_list


gLocalStoreFolder = 'PengPaiArticle'


def get_list(folder_path):
    items = os.listdir(folder_path)
    ret_list = list()
    for item in items:
        new_dict = dict()
        id = item.split('-')[0]
        new_dict['id'] = id
        new_dict['full_name'] = item
        ret_list.append(new_dict)
    return ret_list


def check_if_exist(channel_unit_node, channel_node, article_node):
    global gLocalStoreFolder
    if not os.path.exists(gLocalStoreFolder):
        os.mkdir(gLocalStoreFolder)
        return False
    items = get_list(gLocalStoreFolder)
    is_found = False
    channel_file_node = None
    for item in items:
        if item['id'] == str(channel_unit_node.get_self_id()):
            is_found = True
            channel_file_node = item
            break
    if not is_found:
        return False

    folder_path = os.path.join(gLocalStoreFolder, channel_file_node['full_name'])
    items = get_list(folder_path)
    list_file_node = None
    for item in items:
        if item['id'] == str(channel_node.get_self_id()):
            list_file_node = item
            break
    if not list_file_node:
        return False
    folder_path = os.path.join(folder_path, list_file_node['full_name'])
    items = get_list(folder_path)
    for item in items:
        if item['id'] == str(article_node.get_self_id()):
            return True
    return False
    pass


def store_new_article(channel_unit_node, channel_node, article_node):
    global gLocalStoreFolder
    try:
        if not os.path.exists(gLocalStoreFolder):
            os.mkdir(gLocalStoreFolder)

        folder_path = os.path.join(gLocalStoreFolder,  '%d-%s' % (channel_unit_node.get_self_id(), channel_unit_node.get_title()))
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        folder_path = os.path.join(folder_path, '%s-%s' % (channel_node.get_self_id(), channel_node.get_title()))
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        article_name = '%d-%s' % (article_node.get_self_id(), article_node.get_title())
        folder_path = os.path.join(folder_path, article_name)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        file_name = os.path.join(folder_path, article_name + '.html')

        with open(file_name, 'w+') as fd:
            fd.write(article_node.get_content())
    except:
        print 'ERROR: Failed to store new article [%s]' % str(sys.exc_info())


def store_new_article_file(channel_unit_node, channel_node, article_node, file_name, content):
    global gLocalStoreFolder
    try:
        if not os.path.exists(gLocalStoreFolder):
            os.mkdir(gLocalStoreFolder)

        folder_path = os.path.join(gLocalStoreFolder,  '%d-%s' % (channel_unit_node.get_self_id(), channel_unit_node.get_title()))
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        folder_path = os.path.join(folder_path, '%s-%s' % (channel_node.get_self_id(), channel_node.get_title()))
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        article_name = '%d-%s' % (article_node.get_self_id(), article_node.get_title())
        folder_path = os.path.join(folder_path, article_name)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        full_file_path = os.path.join(folder_path, file_name)
        #print 'Create file [%s]' % full_file_path
        with open(full_file_path, 'wb+') as fd:
            fd.write(content)
    except :
        print 'ERROR: Failed to store new article file'


# front-page  channel-unit  channel  article-list-in-channel


def choose_node(node, input_idx=None):
    sub_nodes = node.get_sub_nodes()
    for idx, sub_node in enumerate(sub_nodes):
        print(str(idx) + ':' + sub_node.get_title())
    if not len(sub_nodes):
        gstLogHandle.log('ERROR: no channel found...')
        return None
    while True:
        if input_idx:
            num = input_idx
        else:
            num = raw_input('choose channel unit-->')
        try:
            num = int(num)
            if num > len(sub_nodes):
                if not input_idx:
                    gstLogHandle.log('Wrong choice for id [%d]' % num)
                    return None
                gstLogHandle.log('wrong choice! try again.')
                continue
            print('choose [%d]:[%s]' % (num, sub_nodes[num].get_title()))
            break
        except ValueError:
            gstLogHandle.log('Please input number..')
    return sub_nodes[num]
    pass

def init_arg_parser(argv):
    arg_parse = MyArgParse()
    arg_parse.add_option('-parse', [2], 'parse channel, you must to input channle and sub-channel')
    arg_parse.add_option('-parse_all', [0], 'parse all channel & all articles')
    arg_parse.add_option('-d', 1, 'where to store those articles')
    arg_parse.add_option('-h', 0, 'print help')
    arg_parse.parse(argv)
    return arg_parse
    pass


def main():
    arg_parser = init_arg_parser(sys.argv)
    if arg_parser.check_option('-h'):
        print (arg_parser)
        exit(0)
    front_page_node = PPFrontPageNode()
    front_page_node.init_node('http://www.thepaper.cn/', u'澎湃')
    front_page_node.do_parse()

    if arg_parser.check_option('-d'):
        gLocalStoreFolder = arg_parser.get_option_args('-d')[0]
        gstLogHandle.log('Set Store path to [%s]' % gLocalStoreFolder)
        pass

    if arg_parser.check_option('-parse'):
        channle_id = int(arg_parser.get_option_args('-parse')[0])
        sub_channel_id = int(arg_parser.get_option_args('-parse')[1])
        channel_unit_node = choose_node(front_page_node, channle_id)
        if not channel_unit_node:
            exit(1)
        channel_node = choose_node(channel_unit_node, sub_channel_id)
        if not channel_node:
            exit(1)
        channel_node.do_parse()
        article_nodes = channel_node.get_sub_nodes()
        print 'len [%d]' % len(article_nodes)
        for article_node in article_nodes:
            article_node.do_parse()
        exit(0)
        pass

    if arg_parser.check_option('-parse_all'):
        channel_unit_nodes = front_page_node.get_sub_nodes()
        for idx, channel_unit_node in enumerate(channel_unit_nodes):
            print('Start to get ' + str(idx) + ':' + channel_unit_node.get_title())
            if 0 == idx:
                print 'Skip video channel..'
                continue
            for sub_idx, channel_node in enumerate(channel_unit_node.get_sub_nodes()):
                channel_node.do_parse()
                article_nodes = channel_node.get_sub_nodes()
                print('Start to get ' + str(idx) + ':' + channel_node.get_title())
                print('Total Article cnt [%d]' % len(article_nodes))
                for article_node in article_nodes:
                    article_node.do_parse()
        exit(0)
        pass



    channel_unit_node = choose_node(front_page_node)
    channel_node = choose_node(channel_unit_node)
    channel_node.do_parse()
    article_nodes = channel_node.get_sub_nodes()
    print len(article_nodes)
    for article_node in article_nodes:
        article_node.do_parse()


if __name__ == '__main__':
    main()
    exit(0)
    pass







