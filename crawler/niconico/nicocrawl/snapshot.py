# -*- coding:utf-8 -*-

import requests
import json

class NicoSnapshot:
    ENDPOINT_URL="http://api.search.nicovideo.jp/api/snapshot/"
    
    def __init__(self):
        '''
  		"query" : 検索キーワード
  		"service" : 検索対象サービスリスト,
  		"search" : 検索対象フィールドリスト,
  		"join" : 取得対象フィールドリスト,
  		"filters" : フィルタ指定リスト(オプション),
  		"sort_by" :  並べ替えフィールド名(オプション),
  		"order" : 並べ替え順序 "desc" もしくは "asc"(オプション、デフォルト: "desc"),
  		"from" : N (数値指定、オプション、デフォルト: 0),
  		"size" : M (数値指定、オプション、デフォルト: 10, 最大: 100),
  		"issuer" : サービス/アプリケーション名 (最大: 40文字)
        '''
        self.query=""
        self.service=["video"]
        self.search=[]
        self.join=[]
        self.filters=None
        self.sortby =None
        self.order  =None
        self._from  =None
        self.size   =None
        self.issuer ="data mining practice"

    def make_request(self):
        payload = {}
        payload["query"] = self.query
        payload["service"] = self.service
        payload["search"] = self.search
        payload["join"] = self.join
        if self.filters:
            payload["filters"] = self.filters
        if self.sortby:
            payload["sort_by"] = self.sortby
        if self.order :
            payload["order"] = self.order
        if self._from :
            payload["from"] = self._from
        if self.size :
            payload["size"] = self.size
        payload["issuer"] = self.issuer
        return payload

    def get_last_modified(self):
        r = requests.get(self.ENDPOINT_URL+"version").json()
        return r["last_modified"]

    def parse(self, text):
        results = {"total":0, "offset":0, "hits":[]}
        status_code = 200
        lines = text.split("\n")
        for line in lines:
            if line == "":
                break
            parsed = json.loads(line)
            if "errid" in parsed :
                return None, "[Erro ID="+ parsed["errid"] + "]:" + parsed["desc"]

            if "endofstream" in parsed:
                continue

            if parsed["type"] == "stats" :
                results["total"] = parsed["values"][0]["total"]
                continue

            if parsed["type"] == "hits" :
                results["hits"].extend(parsed["values"])

        if self._from:
            results["offset"] = self._from
        return results, None
            

    def searchAPI(self):
        r = requests.post(self.ENDPOINT_URL, json=self.make_request())
        if r.status_code != 200 :
            return None, r.status_code
        return self.parse(r.text)

if __name__ == '__main__':
    api = NicoSnapshot()
    api.query = "im@s | The idolm@ster | アイドルマスター | アイマス | ミリオンライブ | シンデレラガールズ | ミリマス | デレマス | サイドM"
    api.search= ["title","tags"]
    api.join  = ["cmsid","title","description","tags","start_time","thumbnail_url"]
    print(api.get_last_modified())
    results, status = api.searchAPI()
    if status:
        print(status)
    else:
        print(results)

    #
    api.search = [] 
    results, status = api.searchAPI()
    if status:
        print(status)
    else:
        print(results)
    
