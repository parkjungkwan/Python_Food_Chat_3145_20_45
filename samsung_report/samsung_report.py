from konlpy.tag import Okt
from nltk.tokenize import word_tokenize
import nltk
import re
import pandas as pd
from nltk import FreqDist
from wordcloud import WordCloud
import matplotlib.pyplot as plt

class SamsungReport:
    def __init__(self):
        self.okt = Okt()

    def read_file(self):
        self.okt.pos("삼성전자 글로벌센터 전자사업부", stem=True)
        filename = './data/kr-Report_2018.txt'
        with open(filename, 'r', encoding='utf-8') as f:
            texts = f.read()
        return texts

    @staticmethod
    def extract_hangeul(texts):
        temp = texts.replace('\n', ' ')
        tokenizer = re.compile(r'[^ ㄱ-힣]+')
        temp = tokenizer.sub('', temp)
        return temp

    @staticmethod
    def change_token(texts):
        tokens = word_tokenize(texts)
        return tokens

    def extract_noun(self):
        noun_tokens = []
        tokens = self.change_token(self.extract_hangeul(self.read_file()))
        for token in tokens:
            token_pos = self.okt.pos(token)
            temp = [txt_tag[0] for txt_tag in token_pos if txt_tag[1] == 'Noun']
            if len(''.join(temp)) > 1:
                noun_tokens.append("".join(temp))
        texts = " ".join(noun_tokens)
        return texts

    @staticmethod
    def download():
        nltk.download()

    @staticmethod
    def read_stopword():
        stopfile = './data/stopwords.txt'
        with open(stopfile, 'r', encoding='utf-8') as f:
            stopwords = f.read()
        stopwords = stopwords.split(' ')
        return stopwords

    def remove_stopword(self):
        texts = self.extract_noun()
        tokens = self.change_token(texts)
        stopwords = self.read_stopword()
        texts = [text for text in tokens
                    if text not in stopwords]
        return texts

    def hook(self):
        texts = self.remove_stopword()
        freqtxt = pd.Series(dict(FreqDist(texts))).sort_values(ascending=False)
        print(freqtxt[:30])
        return freqtxt

    def draw_wordcloud(self):
        texts = self.remove_stopword()
        wcloud = WordCloud('./data/D2Coding.ttf', relative_scaling=0.2,
                           background_color='white').generate(" ".join(texts))
        plt.figure(figsize=(12,12))
        plt.imshow(wcloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()

class Service:
    def __init__(self):
        self.sam = SamsungReport()

    def execute(self, option):
        if option == '1':
            self.sam.read_file()
        elif option == '2':
            self.sam.download()
        elif option == '3':
            self.sam.read_stopword()
        elif option == '4':
            self.sam.hook()
        elif option == '5':
            self.sam.draw_wordcloud()


class Controller:
    def __init__(self):
        self.service = Service()

    def print_menu(self):
        print('0. 종료\n')
        print('1. 파일읽기\n')
        print('2. 자연어 처리키트 다운로드\n')
        print('3. 삭제할 단어 보기\n')
        print('4. 빈출단어 목록보기\n')
        print('5. 워드클라우드 보기\n')
        return input('메뉴 선택\n')

    def run(self):
        while 1:
            menu = self.print_menu()
            if menu == '1':
                self.service.execute('1')
            if menu == '2':
                self.service.execute('2')
            if menu == '3':
                self.service.execute('3')
            if menu == '4':
                self.service.execute('4')
            if menu == '5':
                self.service.execute('5')
            elif menu == '0':
                break

if __name__ == '__main__':

    ctrl = Controller()
    ctrl.run()