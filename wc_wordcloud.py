import configparser
import os,shutil
import time
import re

import jieba
import random
from jieba.analyse import extract_tags
import wordcloud
import numpy as np

# from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from PIL import Image

MAIN_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
os.chdir(MAIN_FILE_PATH)

DATA_DIR = os.path.join(MAIN_FILE_PATH, "data") # 数据存放目录
RES_DIR = os.path.join(MAIN_FILE_PATH, "res") # 资源存放目录

# 读取配置文件
config = configparser.ConfigParser()
config.read("./CONFIG.ini")

if not 'WORDCLOUD' in config: ## 判断配置文件中是否存在WordCloud配置信息
    print('请设置WORDCLOUD参数')
    exit()

# WordCloud配置,如是否需要手动修改txt、
needManual = config['WORDCLOUD']['needManual']  # 有些时候需要手动处理一下数据        
stopwords =  config['WORDCLOUD']['stopwords']     # 停词文件默认采用stopwords.txt
wordsCount =  config['WORDCLOUD']['wordsCount']  # 显示词的数量，默认180
inputImg =  config['WORDCLOUD']['inputImg']  # 模板图片，默认juejin.jpg
fontFamily =  config['WORDCLOUD']['fontFamily']  # 字体，默认simhei.ttf
mode =  config['WORDCLOUD']['MODE']  # 生成模式，单张或全部，默认single，可选all

class MyWordCloud():
    def __init__(self):
        print('开始生成词云……')
        

        self.TEXTPATH = r'%s\wc_moment_list_wordcloud.txt'%(DATA_DIR)
        self.TEXTRESULTPATH = r'%s\result.txt'%(DATA_DIR)
        self.STOPWPRDSPATH = r'%s\%s.txt'%(RES_DIR,stopwords)
        self.INPUTIMGPATH = r'%s\images\%s.jpg'%(RES_DIR,inputImg)
        self.INPUTIMGDIR = r'%s\images'%(RES_DIR)         # MODE为all时，默认将res/images下所有.jpg作为模板
        self.FONTPATH = r'%s\%s'%(RES_DIR,fontFamily)
        self.OUTPUTPATH = r'%s\result-%s.jpg'%(DATA_DIR,int(round(time.time() * 1000)))


        # 如果需要手动修改源数据则将needManual设为有值

        if needManual:
            shutil.copy('./data/wc_moment_list_wordcloud.txt', './data/wc_moment_list_wordcloud_bak.txt')
            print('手动修改模式将重新生成wc_moment_list_wordcloud.txt')
            print('请确保当前已修改完毕')
            self.remove_icondesc()
    
    # 重写wc_moment_list_wordcloud.txt
    def remove_icondesc(self):
        #读取文件
        ms = open(r'%s\wc_moment_list.txt'%(DATA_DIR),'r', encoding='utf-8')
        f = open(self.TEXTPATH,'w', encoding='utf-8')  
        patten = re.compile('\w+(?![\u4e00-\u9fa5]*])')  #匹配除表情文本外的所有文本
        #逐行写入
        print('开始重写……')
        try:
            for line in ms.readlines():  
                if line == '\n':
                    line = line.strip("\n")
                s = re.sub(r'[a-z]*[:.]+\S+', '', line)  # 去除链接
                splitted_sentences = re.findall(patten, s)
                for p in splitted_sentences:
                    f.write(p + '\n')
        finally:
            ms.close()
            print('重写成功！')

    #将存储的文本分词
    def cut_text(self,store_path):
        f=open(store_path,'r',encoding='UTF-8')
        text=f.read() #从文件读取所有字符并将它们作为字符串返回
        cutted_words=jieba.cut(text)#返回的是一个生成器
        return cutted_words

    #剔除停用词
    def store_cut_text(self,textstore_path='',cut_store_path=''):
            cutted_words=self.cut_text(textstore_path or self.TEXTPATH)
            #下面把不在停用词表中的词语添加到这个字符串中，并用空白符分隔开;
            # 必须给个符号分隔开分词结果形成字符串，否则不能生成词云
            f=open(cut_store_path or self.TEXTRESULTPATH,"w",encoding="utf-8")
            for w in cutted_words:
                f.write(w+"\n")
            f.close()

    def del_stopwords(self,stopwords_path='',cut_store_path=''):
        stopwords_list = [line.strip() for line in open(stopwords_path or self.STOPWPRDSPATH, 'r', encoding='utf-8').readlines()]  # 将停用词表转换成列表
        words_str = ''
        f=open(cut_store_path or self.TEXTRESULTPATH,"r",encoding='utf-8')
        w=f.readline()
        words_dir={}
        while w!="":
            if w.strip() not in stopwords_list:
                if w not in words_dir.keys():
                    words_dir[w]=1
                else:
                    words_dir[w]+=1
                words_str+=w
                words_str+=' '
            w=f.readline()
        set_lst=sorted(words_dir.items(),key= lambda item:item[1],reverse=True)    #按字典的值排序，返回一个二元元组的列表，元组第一个元素是关键字，第二个是值
        return words_str

    #生成词云
    def get_wordcloud(self,imagePath,words_str,store_path=''):
        background=plt.imread(imagePath) #设定云图背景图案，参数为图片路径，不设置的话云图默认为方形
        img = Image.open(imagePath)
        width = img.width
        height = img.height
        wc=wordcloud.WordCloud(mask=background,font_path=self.FONTPATH,background_color='white',width=width,height=height,max_font_size=400,min_font_size=5)

        alice_coloring = np.array(img)

        image_colors = wordcloud.ImageColorGenerator(alice_coloring)
        #font_path是中文字体路径，因为wordcloud库本身只支持英文，需要下载中文字体；
        # max_font_size和min_font_size分别设置云图最大词语的大小和最小词语的大
        wc.generate(words_str)#生成词云
        # show
        fig, axes = plt.subplots(1, 3)
        axes[0].imshow(wc, interpolation="bilinear")
        # recolor wordcloud and show
        # we could also give color_func=image_colors directly in the constructor
        axes[1].imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
        axes[2].imshow(alice_coloring, cmap=plt.cm.gray, interpolation="bilinear")
        for ax in axes:
            ax.set_axis_off()
        plt.show()


        wc.to_file(store_path or self.OUTPUTPATH)#将词云存储到指定路径

    #打印关键字
    def keywords_delstop(self,s,n):#提取tf*idf排名前n的n个关键词
        tfidf = extract_tags # 引入TF-IDF关键词抽取接口
        keywords=tfidf(s,n,withWeight=True)

        print("今年关键词是：")
        i=1
        while i<11:
            print(str(i) + "、" + keywords[i-1][0] )
            i+=1
        construct_lst=[]#根据tf*idf值构建新的字符串，使得tf*idf值大的词词频也大，以便生成词云图。因为词云会单纯依据词频来生成
        for keyword in keywords:
            num=round(keyword[1],2)*100  #根据tf-idf值确定词语在新字符串中的个数
            n=0
            while n<num:
                construct_lst.append(keyword[0])
                n+=1
        random.shuffle(construct_lst) #将原列表打乱
        construct_str=""
        for word in construct_lst:
            construct_str+=word
            construct_str+=" "
        return construct_str

    # 多张模式
    def get_wordclouds(self,rootdir,construct_str):      
        for root, dirs, files in os.walk(rootdir,topdown = True):
            for name in files: 
                _, ending = os.path.splitext(name)
                if ending == '.jpg':
                    storePath = r'%s\result-%s.jpg'%(DATA_DIR,int(round(time.time() * 1000)))
                    self.get_wordcloud(os.path.join(root,name),construct_str,storePath)   

if __name__ == '__main__':
    
    wc_wordcloud = MyWordCloud()
    wc_wordcloud.store_cut_text()   #切词并存储切分的词语
    words_str=wc_wordcloud.del_stopwords()  #删除停用词
    construct_str=wc_wordcloud.keywords_delstop(words_str,int(wordsCount))   #使用tf-idf值排名前180的词语构造新字符串
    if mode == 'single':
        wc_wordcloud.get_wordcloud(wc_wordcloud.INPUTIMGPATH,construct_str)  #用新字符串生成词云
    elif mode == 'all':
        wc_wordcloud.get_wordclouds(wc_wordcloud.INPUTIMGDIR,construct_str)  #用新字符串生成词云
    
