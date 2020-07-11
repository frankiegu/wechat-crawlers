import configparser
import os
import time
import re

import uiautomator2 as u2

# 读取配置文件
config = configparser.ConfigParser()
config.read("./CONFIG.ini")

if not 'APPINFO' in config: ## 判断配置文件中是否存在APP配置信息
    print('请设置APP参数')
    exit()
if not 'WECHAT' in config: ## 判断配置文件中是否存在Wechat配置信息
    print('请设置WECHAT参数')
    exit()

# APP配置，如平台、设备名、包名、包入口
platformName = config['APPINFO']['platformName']
deviceName = config['APPINFO']['deviceName']
appPackage = config['APPINFO']['appPackage']
appActivity = config['APPINFO']['appActivity']

# WeChat配置,如账号、密码、爬取目标用户账号
wechatUser = config['WECHAT']['wechatUser']          
wechatPWd = config['WECHAT']['wechatPWd']      
wechatWho = config['WECHAT']['wechatWho'] 

# 创建data目录
MAIN_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
print(MAIN_FILE_PATH)

os.chdir(MAIN_FILE_PATH)

DATA_DIR = os.path.join(MAIN_FILE_PATH, "data")
try:
    print(DATA_DIR)
    os.makedirs(DATA_DIR)
except OSError:
    pass

# 构建Wechat_Moment类
class Wechat_Moment():
    def __init__(self):
        print('启动中……')

        # 使用WIFI连接
        # d = u2.connect('192.168.0.100')

        # 使用USB连接
        self.d = u2.connect(deviceName) # connect to device
        print('设备连接成功！')

        self.d.app_stop(appPackage)
        # 启动微信
        print('微信启动中……')
        self.d.app_start(appPackage, appActivity)

        # 定义浏览朋友圈的滑动参数
        self.start_x = 300
        self.start_y = 0
        self.end_x = 300
        self.end_y = 0
        self.ListHight = 0
        self.ImgInitHight = 0
        self.ImgSwipeHight = 0

        # 设置等待
        time.sleep(30)
        print('微信启动成功！')


    def login(self):
        print('登录准备...')
        # 处理授权询问
        if self.d(resourceId="com.android.packageinstaller:id/permission_allow_button").exists(timeout=2):
            self.d(resourceId="com.android.packageinstaller:id/permission_allow_button").click()
        if self.d(resourceId="com.android.packageinstaller:id/permission_allow_button").exists(timeout=2):
            self.d(resourceId="com.android.packageinstaller:id/permission_allow_button").click()

        # 如果已登录则跳过
        if not self.d(resourceId="com.tencent.mm:id/emh").exists(timeout=5):
            print('已登录..')
            return True
        # 获取到登录按钮后点击
        self.d(resourceId="com.tencent.mm:id/emh").click()
        # 获取使用微信号登录按钮
        self.d(resourceId="com.tencent.mm:id/d0p").click()
        # 获取输入账号元素并输入
        self.d(resourceId="com.tencent.mm:id/m6", text="请填写微信号/QQ号/邮箱").click()
        self.d.send_keys(wechatUser, clear=True)

        # 获取密码元素并输入
        self.d(resourceId="com.tencent.mm:id/m6", text="请填写密码").click()
        self.d.send_keys(wechatPWd, clear=True)
        # 登录
        self.d(resourceId="com.tencent.mm:id/d0q").click()
        print('登录中...')
        # 点击去掉通讯录提示框(因登录需要时间，延迟3分钟)
        self.d(resourceId="com.tencent.mm:id/b46").click(timeout=180)
        print('登录成功!')


    def find_me(self):
        # 等搜索建立索引（预计5分钟）再点击搜索按钮
        print('数据加载中……')
        time.sleep(300)
        self.d(resourceId="com.tencent.mm:id/r9").click()
        # 获取搜索框并输入
        self.d.send_keys(wechatWho, clear=True)
        print('搜索 %s...'%(wechatWho))
        time.sleep(5)
        # 点击头像进入
        self.d.xpath('//*[@resource-id="com.tencent.mm:id/c4u"]/android.widget.RelativeLayout[2]').click()
        # 点击右上角...进入
        self.d(resourceId="com.tencent.mm:id/ln").click(timeout=2)
        # 再点击头像
        self.d.xpath('//*[@resource-id="com.tencent.mm:id/dkv"]/android.widget.RelativeLayout[1]/android.widget.ImageView[1]').click(timeout=2)

        # 点击朋友圈
        self.d(resourceId="com.tencent.mm:id/dkn").click(timeout=5) 
        print('进入朋友圈...')

    def get_data(self):
        while True:
            # 获取 ListView
            items = self.d(resourceId="com.tencent.mm:id/kq")
            print(items)
            # 滑动
            # if self.d(resourceId="com.tencent.mm:id/eyx").exists(timeout=2):
            #     self.ListHight = self.d(resourceId="com.tencent.mm:id/eyx").info['visibleBounds']['bottom']
            if self.d(resourceId="com.tencent.mm:id/eyx").exists(timeout=2):
                self.ListHight = self.d(resourceId="com.tencent.mm:id/eyx").info['visibleBounds']['bottom']
            if self.d(resourceId="com.tencent.mm:id/ezq").exists(timeout=2):
                self.ImgInitHight = self.d(resourceId="com.tencent.mm:id/ezq").info['visibleBounds']['bottom']
            if self.d(resourceId="com.tencent.mm:id/f1t").exists(timeout=2):
                self.ImgSwipeHight = self.d(resourceId="com.tencent.mm:id/f1t").info['visibleBounds']['bottom']
            self.start_y = self.ListHight  -  self.ImgInitHight + self.ImgSwipeHight
            self.d.swipe(self.start_x, self.start_y, self.end_x, self.end_y,5)
            #遍历获取每个List数据
            for item in items:
                print('details:',item.__dict__)
                if item.child(resourceId="com.tencent.mm:id/ph").exists():
                    print(item.child(resourceId="com.tencent.mm:id/ph").get_text())
                    print('-----图片文字----')
                if item.child(resourceId="com.tencent.mm:id/mj").exists():
                    print(item.child(resourceId="com.tencent.mm:id/mj").get_text())
                    print('-----纯文字-----')
                # moment_text = item.find_element_by_iself.d('com.tencent.mm:id/kt').text
                # day_text = item.find_element_by_iself.d('com.tencent.mm:id/eke').text
                # month_text = item.find_element_by_iself.d('com.tencent.mm:id/ekf').text
                # print('抓取到小帅b朋友圈数据： %s' % moment_text)
                # print('抓取到小帅b发布时间： %s月%s' % (month_text, day_text))
    
    #上拉方法
    def swipe_up(self,time, distance= 0): # time为滑动时间 distance为滑动距离
        # width和height根据不同手机而定
        if self.d(resourceId="com.tencent.mm:id/eyx").exists(timeout=2):
                self.ListHight = self.d(resourceId="com.tencent.mm:id/eyx").info['visibleBounds']['bottom']
        if self.d(resourceId="com.tencent.mm:id/ezq").exists(timeout=2):
            self.ImgInitHight = self.d(resourceId="com.tencent.mm:id/ezq").info['visibleBounds']['bottom']
        if self.d(resourceId="com.tencent.mm:id/f1t").exists(timeout=2):
            self.ImgSwipeHight = self.d(resourceId="com.tencent.mm:id/f1t").info['visibleBounds']['bottom']
        self.start_y = self.ListHight  -  self.ImgInitHight + self.ImgSwipeHight
        self.d.swipe(self.start_x, distance or self.start_y, self.end_x, self.end_y,time)


    def get_onepage_elementlist(self):
        pict_list=[]
        link_list=[]
        # 获取 ListView
        items = self.d(resourceId="com.tencent.mm:id/kq")
        for item in items:
                # print('details:',item.__dict__)
                if item.child(resourceId="com.tencent.mm:id/ph").exists():
                    # print('-----图片文字----')
                    # print(item.child(resourceId="com.tencent.mm:id/ph").get_text())
                    
                    pict_list.append(item.child(resourceId="com.tencent.mm:id/ph").get_text())
                if item.child(resourceId="com.tencent.mm:id/mj").exists():
                    # print('-----纯文字-----')
                    # print(item.child(resourceId="com.tencent.mm:id/mj").get_text())
                    
                    link_list.append(item.child(resourceId="com.tencent.mm:id/mj").get_text())
        elementlist = pict_list + link_list
        return elementlist


    def get_onepage(self):
        eleLst = self.get_onepage_elementlist()
        pagetext = []
        for e in eleLst:
            print(e)
            if not e in pagetext:
                pagetext.append(e)
        return pagetext

    #获取往前倒推year_count年到现在的所有朋友圈
    def get_pages(self,year_count):
        pagestext = []
        current_year = self.d(resourceId="com.tencent.mm:id/f4u").get_text() #获得当前年份
        print('current_year', current_year)
        while True:
            try:
                end_year = str(int(current_year[0:4]) - year_count) + "年"
                y = self.d(resourceId="com.tencent.mm:id/f4u").get_text()  #在页面中寻找显示年份的元素，没找到就会报错，继续上拉
                print('end_year',end_year,'y',y)
                print('endFlag', self.d(resourceId="com.tencent.mm:id/f0y").exists())
                if y == end_year or self.d(resourceId="com.tencent.mm:id/f0y").exists():   #到达结束年份
                    break
                else:  #未到达结束年份，继续上拉
                    pagetext=self.get_onepage()
                    for t in pagetext:
                        if t not in pagestext:
                            pagestext.append(t)
                    swipe_up(5)

            except:
                print('except')
                pagetext = self.get_onepage()
                for t in pagetext:
                    if t not in pagestext:
                        pagestext.append(t)
                self.swipe_up(5)

        pagetext = self.get_onepage()
        for t in pagetext:
            if t not in pagestext:
                pagestext.append(t)
        while True:
            try:
                self.d(resourceId="com.tencent.mm:id/f4u")
                print(self.d(resourceId="com.tencent.mm:id/f4u").get_text())
                self.swipe_up(5)  #继续缓慢上拉保证最后一页都是多余年份的朋友圈
            except:
                break
        #删除最后一页多获取的朋友圈文本
        lastPage=self.get_onepage()
        for t in lastPage:
            if t in pagestext:
                pagestext.remove(t)

        pagestext = list(dict.fromkeys(pagestext))
        return pagestext


    def store_PYQText(self,wc_moment_list,store_path):  #将朋友圈文本存储到指定路径
        f = open(store_path, 'w', encoding='utf-8')
        for text in wc_moment_list:
            f.write(text + '\n\n')
        f.close()
    
    def remove_icondesc(self,list, storepath):
        f = open(storepath, 'w', encoding='utf-8')
        patten = re.compile('\w+(?![\u4e00-\u9fa5]*])')  #匹配除表情文本外的所有文本

        for s in list:
            s  = re.sub(r'[a-z]*[:.]+\S+', '', s)  # 去除链接
            splitted_sentences = re.findall(patten, s)
            for p in splitted_sentences:
                f.write(p + '\n')
        f.close()


if __name__ == '__main__':
    wc_moment = Wechat_Moment()
    wc_moment.login()
    wc_moment.find_me()
    wc_moment_list = wc_moment.get_pages(1)
    wc_moment.store_PYQText(wc_moment_list,r'%s\wc_moment_list.txt'%(DATA_DIR))  #存储原始朋友圈
    wc_moment.remove_icondesc(wc_moment_list, r'%s\wc_moment_list_wordcloud.txt'%(DATA_DIR))  #存储删除表情文本和符号之后的朋友圈，为生成词云做准备

    wc_moment.d.app_stop(appPackage)


