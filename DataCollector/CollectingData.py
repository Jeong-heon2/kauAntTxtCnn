import pandas as pd
from ApiNaverNews import ApiNaverNews
import xlwt
import openpyxl
import xml.etree.ElementTree as elemTree
import threading

pd.set_option('display.expand_frame_repr', True)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

client_id = "9mphub_9Yx6zLlRlkkIT"  # 1.에서 취득한 아이디 넣기
client_secret = "730Dw7dKqM"  # 1. 에서 취득한 키 넣기

class CommentedTreeBuilder(elemTree.TreeBuilder):
    def __init__(self, *args, **kwargs):
        super(CommentedTreeBuilder, self).__init__(*args, **kwargs)
    def comment(self, data):
        self.start(elemTree.Comment, {})
        self.data(data)
        self.end(elemTree.Comment)

xml_path = 'DataCollection/DataSets/company.xml'
xml = open(xml_path, 'rt', encoding='UTF8')
tree = elemTree.parse(xml, parser=elemTree.XMLParser(target= CommentedTreeBuilder()))

search_words = []
for type in tree.findall('./*'):
    for company in type.findall('company'):
        search_words.append(company.text)


encode_type = 'json'  # 출력 방식 json 또는 xml
max_display = 100  # 출력 뉴스 수
sort = 'date'  # 결과값의 정렬기준 시간순 date, 관련도 순 sim

def naverNewsRequest():
    thread_list = []
    count = 0
    for keyword in search_words:
        # 일단 20개만 테스트
        if count > 20:
            break
        count += 1
        start = 1  # 출력 위치
        for repeat in range(10):
            url = f"https://openapi.naver.com/v1/search/news.{encode_type}?query={keyword}&display={str(int(max_display))}&start={str(int(start))}&sort={sort}"

            # 헤더에 아이디와 키 정보 넣기
            headers = {'X-Naver-Client-Id': client_id,
                       'X-Naver-Client-Secret': client_secret
                       }

            tr = ApiNaverNews(url, headers, keyword)
            thread_list.append(tr)
            tr.start()
            start += 100
            tr.join()




    # 각 스레드의 dataframe을 main_df로 하나로 합친다
    main_df = pd.DataFrame()
    for thread in thread_list:
        main_df = pd.concat([main_df, thread.dataFrame], ignore_index=True)

    # 엑셀 파일로 내보내기
    main_df.to_excel('news_data_set.xlsx')

def naverNewsRequest2(fr,to, path):
    thread_list = []
    for i in range(fr, to+1):

        start = 1  # 출력 위치
        for repeat in range(10):
            url = f"https://openapi.naver.com/v1/search/news.{encode_type}?query={search_words[i]}&display={str(int(max_display))}&start={str(int(start))}&sort={sort}"

            # 헤더에 아이디와 키 정보 넣기
            headers = {'X-Naver-Client-Id': client_id,
                       'X-Naver-Client-Secret': client_secret
                       }

            tr = ApiNaverNews(url, headers, search_words[i])
            thread_list.append(tr)
            tr.start()
            start += 100
            tr.join()


    # 각 스레드의 dataframe을 main_df로 하나로 합친다
    main_df = pd.DataFrame()
    for thread in thread_list:
        main_df = pd.concat([main_df, thread.dataFrame], ignore_index=True)

    # 엑셀 파일로 내보내기
    main_df.to_excel(path+'.xlsx')


if __name__ == '__main__':
    naverNewsRequest2(0, 69, 'news_data_set1')
    print("20% 완료")
    naverNewsRequest2(69, 138, 'news_data_set2')
    print("40% 완료")
    naverNewsRequest2(138, 207, 'news_data_set3')
    print("60% 완료")
    naverNewsRequest2(207, 276, 'news_data_set4')
    print("80% 완료")
    naverNewsRequest2(276, len(search_words)-1, 'news_data_set5')
    print("100% 완료")
