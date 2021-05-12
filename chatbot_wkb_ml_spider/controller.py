import cgi
import codecs
from bs4 import BeautifulSoup
import urllib.request
from konlpy.tag import Twitter
import os, re, json, random
dict_file = "chatbot-data.json"
dic = {}
twitter = Twitter()
from chatbot_wkb_ml_spider.botengine import make_reply
form = cgi.FieldStorage()

# 딕셔너리에 단어 등록하기 --- (※1)
class ChatbotModel:
    def __init__(self):
        pass

    def register_dic(self, words):
        global dic
        if len(words) == 0: return
        tmp = ["@"]
        for i in words:
            word = i[0]
            if word == "" or word == "\r\n" or word == "\n": continue
            tmp.append(word)
            if len(tmp) < 3: continue
            if len(tmp) > 3: tmp = tmp[1:]
            self.set_word3(dic, tmp)
            if word == "." or word == "?":
                tmp = ["@"]
                continue
        # 딕셔너리가 변경될 때마다 저장하기
        json.dump(dic, open(dict_file, "w", encoding="utf-8"))

    # 딕셔너리에 글 등록하기
    def set_word3(dic, s3):
        w1, w2, w3 = s3
        if not w1 in dic: dic[w1] = {}
        if not w2 in dic[w1]: dic[w1][w2] = {}
        if not w3 in dic[w1][w2]: dic[w1][w2][w3] = 0
        dic[w1][w2][w3] += 1

    # 문장 만들기 --- (※2)
    def make_sentence(self, head):
        if not head in dic: return ""
        ret = []
        if head != "@": ret.append(head)
        top = dic[head]
        w1 = self.word_choice(top)
        w2 = self.word_choice(top[w1])
        ret.append(w1)
        ret.append(w2)
        while True:
            if w1 in dic and w2 in dic[w1]:
                w3 = self.word_choice(dic[w1][w2])
            else:
                w3 = ""
            ret.append(w3)
            if w3 == "." or w3 == "？ " or w3 == "": break
            w1, w2 = w2, w3
        ret = "".join(ret)
        # 띄어쓰기
        params = urllib.parse.urlencode({
            "_callback": "",
            "q": ret
        })
        # 네이버 맞춤법 검사기를 사용합니다.
        data = urllib.request.urlopen("https://m.search.naver.com/p/csearch/dcontent/spellchecker.nhn?" + params)
        data = data.read().decode("utf-8")[1:-2]
        data = json.loads(data)
        data = data["message"]["result"]["html"]
        data = soup = BeautifulSoup(data, "html.parser").getText()
        # 리턴
        return data

    def word_choice(sel):
        keys = sel.keys()
        return random.choice(list(keys))

    # 챗봇 응답 만들기 --- (※3)
    def make_reply(self, text):
        # 단어 학습시키기
        if not text[-1] in [".", "?"]: text += "."
        words = twitter.pos(text)
        self.register_dic(words)
        # 사전에 단어가 있다면 그것을 기반으로 문장 만들기
        for word in words:
            face = word[0]
            if face in dic: return self.make_sentence(face)
        return self.make_sentence("@")

    # 딕셔너리가 있다면 읽어 들이기
    if os.path.exists(dict_file):
        dic = json.load(open(dict_file, "r"))



class ChatbotController:
    def __init__(self):
        pass

    def main(self):
        m = form.getvalue("m", default="")
        if m == "":
            self.show_form()
        elif m == "say":
            self.api_say()

    # 사용자의 입력에 응답하기 --- (※3)
    def api_say(self):
        print("Content-Type: text/plain; charset=utf-8")
        print("")
        txt = form.getvalue("txt", default="")
        if txt == "": return
        res = make_reply(txt)
        print(res)

    # 입력 양식 출력하기 --- (※4)
    def show_form(self):
        print("Content-Type: text/html; charset=utf-8")
        print("")
        print("""
        <html><meta charset="utf-8"><body>
        <script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
        <style>
            h1   { background-color: #ffe0e0; }
            div  { padding:10px; }
            span { border-radius: 10px; background-color: #ffe0e0; padding:8px; }
            .bot { text-align: left; }
            .usr { text-align: right; }
        </style>
        <h1>대화하기</h1>
        <div id="chat"></div>
        <div class='usr'><input id="txt" size="40">
        <button onclick="say()">전송</button></div>
        <script>
        var url = "./chatbot.py";
        function say() {
          var txt = $('#txt').val();
          $.get(url, {"m":"say","txt":txt},
            function(res) {
              var html = "<div class='usr'><span>" + esc(txt) +
                "</span>: 나</div><div class='bot'> 봇:<span>" + 
                esc(res) + "</span></div>";
              $('#chat').html($('#chat').html()+html);
              $('#txt').val('').focus();
            });
        }
        function esc(s) {
            return s.replace('&', '&amp;').replace('<','&lt;')
                    .replace('>', '&gt;');
        }
        </script></body></html>
        """)