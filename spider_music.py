# -*- coding:utf-8 -*-
'''
QQ音乐
1.通过全部分类歌单，得到所有的歌单的详细页面的链接
2.访问歌单详细页面，得到所有歌曲的链接
3.抓取歌曲的详细信息

最好使用代理，防止被黑IP
'''
import requests
import json
import pandas as pd
import csv
import urllib.request
import re
# 增加信息存储到数据库
import pymysql
import os
headers = {'accept': '*/*',
           'accept-encoding': 'gzip, deflate, br',
           'accept-language': 'zh-CN,zh;q=0.9',
           'cookie': 'RK=8DGDBTVuPW; pgv_pvid=8185349399; ptcz=db8bc37ccd61b6d2928e055a2e244ef522f47dc69199e3c554e55d2f187a1f38; pt2gguin=o0530629993; pgv_pvi=6911873024; pgv_si=s391464960; yq_playdata=s; yq_playschange=0; yq_index=0; qqmusic_fromtag=66; player_exist=1; yplayer_open=0; ts_last=y.qq.com/portal/playlist.html; ts_uid=4150155516; yqq_stat=0',
           'referer': 'https://y.qq.com/portal/playlist.html',
           'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
           }
proxies = {'http': 'http://122.193.14.102:80'}

conn = pymysql.connect(host='127.0.0.1', user='root', password='root', db='mysql',use_unicode=True,charset='utf8')
cur = conn.cursor()


# 1.通过全部分类歌单，得到所有的歌单的详细页面的链接
def getFullSongsList(url=''):
    # 歌单为动态加载，通过json动态获取所有歌单链接，需要从链接中获取dissid：886027471
    # 获取第一页的链接请求
    if not url:
        url = 'https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg?picmid=1&rnd=0.8128593803432778&g_tk=5381&jsonpCallback=getPlaylist&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&categoryId=10000000&sortId=5&sin=0&ein=29'
    # 需要加请求头headers

    html = requests.get(url, headers=headers, proxies=proxies).text
    # print(html)
    # 使用json解析html,解析成字典类型
    getPlaylist = json.loads(html.strip('getPlaylist(').strip(')'))
    # print(getPlaylist)
    songList = []
    for songInfo in getPlaylist['data']['list']:
        # print('dissid:',songInfo['dissid'])

        DetailUrl = 'https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?type=1&json=1&utf8=1&onlysong=0&disstid={0}&format=jsonp&g_tk=5381&jsonpCallback=playlistinfoCallback&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'.format(
            songInfo['dissid'])
        print(DetailUrl)
        headers2 = {'accept': '*/*',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'zh-CN,zh;q=0.9',
                    'referer': 'https://y.qq.com/n/yqq/playlist/' + songInfo['dissid'] + '.html',
                    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
                    }
        html2 = requests.get(DetailUrl, headers=headers, proxies=proxies).text
        # print(html2)
        songList.append(html2)
        # 获取详细页面的链接，

    # print(getPlaylist['data']['sin'])
    # print(getPlaylist['data']['ein'])
    # 获得下一页歌单信息
    if getPlaylist['data']['ein'] < getPlaylist['data']['sum']:
        next_url = 'https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg?picmid=1&rnd=0.8128593803432778&g_tk=5381&jsonpCallback=getPlaylist&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&categoryId=10000000&sortId=5&sin={0}&ein={1}'.format(
            getPlaylist['data']['sin'] + 30, getPlaylist['data']['ein'] + 30)
    else:
        next_url = ''
    # next_html = requests.get(next_url, headers=headers, proxies=proxies).text
    # print(next_html)
    return next_url, songList


# 2.访问歌单详细页面，得到所有歌曲的链接
def getSongsAddress(songLists):
    singleSongList = []
    for html in songLists:
        playlistinfoCallback = json.loads(html.strip('playlistinfoCallback(').strip(')'))
        print(playlistinfoCallback)
        for song in playlistinfoCallback['cdlist'][0]['songlist']:
            if 'songmid' in song.keys() and 'albummid' in song.keys():
                print('songmid:', song['songmid'])
                print('albummid:', song['albummid'])
                albumm_url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg?albummid={0}&g_tk=5381&jsonpCallback=getAlbumInfoCallback&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'.format(
                    song['albummid'])
                onesong_url = 'https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid={0}&tpl=yqq_song_detail&format=jsonp&callback=getOneSongInfoCallback&g_tk=5381&jsonpCallback=getOneSongInfoCallback&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'.format(
                    song['songmid'])
                refer = 'https://y.qq.com/n/yqq/song/' + song['songmid'] + '.html'
                singleSongList.append({'albummUrl': albumm_url, 'refer': refer, 'onesongUrl': onesong_url})
                print('onesong_url:', onesong_url)
                # print(singleSongList)

    return singleSongList


# 3.抓取歌曲的详细信息
def getDetailInfo(singleSongList):
    with open("songs.csv", "a+", encoding='utf-8') as csvfile:
        fieldnames = ['media_mid', 'name', 'singerName', 'time_public', 'genre', 'lan', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        csvfile.close()

    for singleSong in singleSongList:
        songs = []
        headers['referer'] = singleSong['refer']
        albumm_html = requests.get(singleSong['albummUrl'], headers=headers, proxies=proxies).text
        # print(html)
        getAlbumInfoCallback = json.loads(albumm_html.strip(' getAlbumInfoCallback(').strip(')'))
        # print(getAlbumInfoCallback)

        onesong_html = requests.get(singleSong['onesongUrl'], headers=headers, proxies=proxies).text
        print(onesong_html)
        getOneSongInfoCallback = json.loads(onesong_html.strip('getOneSongInfoCallback(').strip(')'))
        print(getOneSongInfoCallback)
        onesong_dict = {}
        onesong_dict['media_mid'] = getOneSongInfoCallback['data'][0]['file']['media_mid']
        print(onesong_dict['media_mid'])

        onesong_dict['name'] = getOneSongInfoCallback['data'][0]['name']
        # print(onesong_dict['name'])
        onesong_dict['singerName'] = getOneSongInfoCallback['data'][0]['singer'][0]['name']
        # print(onesong_dict['singerName'])
        onesong_dict['time_public'] = getOneSongInfoCallback['data'][0]['album']['time_public']
        dict01 = getOneSongInfoCallback['url']
        print(type(getOneSongInfoCallback['url']))
        for item in dict01:
            onesong_dict['url'] = dict01[item]
        print(onesong_dict['url'])

        print(re.findall(r"/(.+?)\?", onesong_dict['url']))

        # print(onesong_dict['time_public'])
        if 'data' in getAlbumInfoCallback.keys():
            onesong_dict['genre'] = getAlbumInfoCallback['data']['genre']
            onesong_dict['lan'] = getAlbumInfoCallback['data']['lan']
        # print(onesong_dict)
        songs.append(onesong_dict)
        insertMusicTable(onesong_dict)


        with open("songs.csv", "a+", encoding='utf-8') as csvfile:
            fieldnames = ['media_mid', 'name', 'singerName', 'time_public', 'genre', 'lan', 'url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(onesong_dict)
            csvfile.close()
        download_music(onesong_dict)


def download_music(onesong_dict):
    filename = re.findall(r"/(.+?)\?", onesong_dict['url'])[0]
    url = 'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?&jsonpCallback=MusicJsonCallback&cid=205361747&songmid=' + \
          onesong_dict['media_mid'] + '&filename=' + filename + '&guid=6612300644'
    print('url:', url)
    res2 = requests.get(url)
    jm2 = json.loads(res2.text)
    print(jm2)
    print(res2.text)
    vkey = jm2['data']['items'][0]['vkey']
    print(vkey)
    url2 = 'http://dl.stream.qqmusic.qq.com/' + filename + '?vkey=' + vkey + '&guid=6612300644&uin=0&fromtag=66'
    print(url2)
    try:
        #如果music文件夹不存在，创建文件夹
        if not os.path.exists('muisc'):
            os.mkdir('music')

        urllib.request.urlretrieve(url2, 'music/' + onesong_dict['name'] + ' - ' + onesong_dict['singerName'] + '.mp3')

    except:
        print('Download wrong~')


# 连接接数据库，创建music表
def createTable():

    '''
    'media_mid','name','singerName','time_public','genre','lan','url'
    '''
    sql = """
       create table if not EXISTS music
       (
       id int(11) not null auto_increment PRIMARY key,
       media_mid VARCHAR(255),
       name VARCHAR(255),
       singerName VARCHAR(255),
       time_public VARCHAR(255),
       genre VARCHAR(255),
       lan VARCHAR(255),
       url VARCHAR(255));
       """

    try :
        cur.execute(sql)
        conn.commit()
        #print('成功')
    except:
        print('出错')

#把数据插入到数据库中
def insertMusicTable(onesong_dict):
    # data = pd.DataFrame(songs)
    sql = """
            insert into music(media_mid, name, singerName, time_public, genre, lan, url)
            VALUES(%s,%s,%s,%s,%s,%s,%s)
           """

    try:
        cur.execute(sql,(
        onesong_dict['media_mid'], onesong_dict['name'], onesong_dict['singerName'], onesong_dict['time_public'],
        onesong_dict['genre'], onesong_dict['lan'], onesong_dict['url']))
        conn.commit()
        print('插入成功')

    except :
        print('插入失败')


if __name__ == '__main__':
    createTable()
    # 得到所有的歌单列表
    songLists = []
    next_url, songLists = getFullSongsList()
    count = 1
    print('count=:', count)
    # while next_url :
    #     count+=1
    #     print('count=:',count)
    #     next_url, songList = getFullSongsList(next_url)
    #     songLists.extend(songList)
    # 得到所有的歌曲链接
    # singleSongList = getSongsAddress(songLists)
    singleSongList = getSongsAddress(songLists[:1])

    # 获取歌曲信信息列表
    getDetailInfo(singleSongList)
    #关闭数据库
    cur.close()
    conn.close()
