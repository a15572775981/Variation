import requests
from lxml import etree
import os
import re
import time


DATA = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'all.17k.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
}

headers = {
    'Host': 'www.17k.com',
    'Referer': 'http://all.17k.com/lib/book/2_0_0_0_0_0_0_1_1.html?',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'
}
session = requests.session()

def get_html(url):
    """请求主网页"""
    response = session.get(url=url, headers=DATA)
    return response.text

def mkdir_file(mkdir_name):
    """创建小说文件夹"""
    path = os.path.join(r'D:\PyCharm 2018.3.1\爬虫自学\Crawler\crawler_text', mkdir_name)
    if not os.path.exists(path):
        os.mkdir(path)
        os.chdir(path)

def parse_title(html):
    """解析主网页"""
    data_dict = {}
    result = etree.HTML(html)
    div_data = result.xpath('//div[@class="alltextlist"]')
    for data in div_data:
        data_dict['href_data'] = data.xpath('./div[1]/a/@href')  # 超链接网址
        data_dict['src_data'] = data.xpath('./div/a/img/@src')  # 图片地址
        data_dict['title'] = data.xpath('./div/a/img/@alt')  # 小说名字
        data_dict['author'] = data.xpath('./div[3]/dl/dd/ul/li/span[1]/a/text()')  # 作者名
        data_dict['category'] = data.xpath('./div[3]/dl/dd/ul/li/span[2]/a/text()')  # 小说类别
        data_dict['number'] = data.xpath('./div[3]/dl/dd/ul/li/span[3]/code/text()')  # 小说字数
        yield data_dict

def get_volume(url, name1):
    """得到小说具体章节网址以及创建文件夹"""
    href_url = 'http://www.17k.com'
    response = session.get(url, headers=headers)
    response = response.content.decode("utf-8")
    html = etree.HTML(response)
    target_data = html.xpath('//div[@class="Main List"]/dl[3]/dd|//div[@class="Main List"]/dl[2]/dd')
    for data in target_data:
        mkdir_file(name1)
        href_data = data.xpath('./a/@href')
        for u in href_data:
            div_url = href_url + u
            resp = get_volume_list(div_url)
            last, file_name = parse_last_url(resp)
            write_file(l=name1, name=file_name, result=last)

def get_volume_list(div_url):
    """挨着请求具体章节数"""
    result = session.get(div_url, headers=headers)
    result = result.content.decode("utf-8")
    return result

def parse_last_url(html):
    """解析出具体章节网页内容"""
    result = etree.HTML(html)
    file = result.xpath('//div[@class="readAreaBox content"]/h1/text()')
    file_name = re.search(r'\s+(.*?)\s+', file[0]).group(1)
    rep_data = result.xpath('//div[@class="p"]/text()|//div[@class="content"]/text()')
    data = str(rep_data).replace(r'\n', '').replace(r'\u3000', '').replace("'", '').replace(',', '').replace('[', '').replace(']', '').strip()
    return data, file_name

def write_file(l, name, result):
    """写入内容"""
    print('小说名字：', l)
    print('具体章节保存开始:', name)
    time.sleep(0.5)
    path = os.path.join(r'D:\PyCharm 2018.3.1\爬虫自学\Crawler\crawler_text', l)
    file_name = os.path.join(path, name+'.txt')
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(result)
    time.sleep(0.5)

def main(num):
    """主函数"""
    url = 'http://all.17k.com/lib/book/2_0_0_0_0_0_0_1_{}.html'.format(num)
    html = get_html(url)
    parse_data = parse_title(html)
    ellipsis_url = 'http://www.17k.com/list/'
    for d in parse_data:
        href = d['href_data'][0].split('/')[4]
        join_url = ellipsis_url + href  # 拼接小说整个大章节网页
        title_name = d['title'][0]
        get_volume(join_url, title_name)
        session.cookies.clear()   # 每循环一次，清空一次cookies

if __name__ == '__main__':
    for i in range(1, 9330):
        main(i)


