﻿# SpiderMusic
整个QQ音乐的分类信息，都是通过JS动态加载，所以需要分析源码JS返回data

1.通过全部分类歌单，得到所有的歌单的详细页面的链接

2.访问歌单详细页面，得到所有歌曲的链接

3.抓取歌曲的详细信息

4.存储详细信息到csv文件
5.存储到mysql数据库
6.分析下载链接
7.通过下载链接下载

