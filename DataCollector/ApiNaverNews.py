import pandas as pd
import threading
import re
import requests

class ApiNaverNews(threading.Thread):
    def __init__(self, url, headers, company_name):
        threading.Thread.__init__(self, name="Naver News Api Thread")
        self.url = url
        self.headers = headers
        self.dataFrame = pd.DataFrame()
        self.company_name = company_name

    def clean_html(self, x):
        x = re.sub("\&\w*\;", "", x)
        x = re.sub("<.*?>", "", x)
        return x

    #Thread가 실행하는 함수
    def run(self):
        # HTTP요청 보내기
        r = requests.get(self.url, headers = self.headers)

        df = pd.DataFrame(r.json()['items'])
        columns = df.columns
        if 'title' in columns:
            df['title'] = df['title'].apply(lambda x: self.clean_html(x))
        if 'description' in columns:
            df['description'] = df['description'].apply(lambda x: self.clean_html(x))

        # company name 열추가하기
        df['company name'] = self.company_name

        # label 열추가하기
        df['label'] = 0


        self.dataFrame = df