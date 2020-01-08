# LogInspector

![LogInspector](https://user-images.githubusercontent.com/32869950/71964860-e1c0e680-3241-11ea-892d-082d3ad24593.png)

**LogInspector**は**Apach**のログを解析するためのライブラリ、
また、それを用いて制作された対話型のログ解析プログラムです。
**Python3**で書かれており、動作環境は**Linux**を想定しています。


 **依存ライブラリのインストール**

     pip3 install apache_log_parser
     pip3 install pandas
     pip3 install subprocess
     pip3 install pprint


**起動**

    python3 LogInspector.py

## LI
LI.pyは本体である解析をするためのライブラリです。
***
**log_list**

      def __init__(self):
        self.log_list = []
LIライブラリでは、**log_list**というインスタンス関数にログファイルのデータを入れて取り扱います。
***
**LogReceiver(str, str)**

      def LogReceiver(self, file_locate, log_format):
        parser = apache_log_parser.make_parser(log_format)
        P = []
        E = []
        with open(file_locate) as f:
          for line in f:
            try:
              parsed_line = parser(line)
              P.append(parsed_line)
            except ValueError:
              E.append(line)
        print("Parsed    : {0}".format(len(P)))
        print("ValueError: {0}".format(len(E)))
        self.log_list[len(self.log_list):len(self.log_list)] = P

**LogReceiver**はログファイルのパス（**file_locate**）とフォーマット（**log_format**）を引数とします。
**apache_log_parser**を使ってログファイルからリモートホスト、タイムスタンプなどの要素を抽出し、辞書型として**リストP**に追加します。もしログファイルが部分的に破損していた場合には、それらは**リストE**に追加され、エラー件数のを報告します。
**リストP**は最終的にクラス内のインスタンス変数（**log_list**）に**結合**されます。
つまり、**LogReceiver**に異なるログファイルを渡すとインスタンス変数（**log_list**）は要素が追加される形でアップデートされます。
***
**LogListParser(datetime, datetime)**

      def LogListParser(self, time_from, time_to):
        D = []
        print("[FROM]", time_from)
        print("[TO  ]", time_to)
        for page in self.log_list:
          target = page["time_received_datetimeobj"]
          if time_from <= target <= time_to:
            D.append(page)
        self.log_list = D

**LogListParser**は始端時刻（**time_from**）と終端時刻（**time_to**）を引数とします。
各引数の型を**datetime**として受け取っている部分に注意が必要です。
ログのタイムスタンプを参照して、受け取った始端時刻と終端時刻の間のアクセスを抽出します。
なお、この関数ではクラス内のインスタンス変数（**log_list**）は**上書き**されます。
***
**LogInitializer()**

      def LogInitializer(self):
        self.log_list = []

**LogInitializer**は引数を必要としません。
この関数の役割はクラス内のインスタンス変数である**log_list**の初期化です。
***
**LogListPrinter()**

      def LogListPrinter(self):
        for page in self.log_list:
          print(page["time_received"],page["remote_host"],page["remote_logname"],page["remote_user"],page["request_first_line"],page["status"],page["request_header_user_agent"])

**LogListPrinter**は引数を必要としません。
この関数の役割はクラス内のインスタンス変数である**log_list**の**標準出力**です。
主に取り扱っているログの確認などに使うことを想定しています。
***
**AC_AtHost()**

      def AC_AtHost(self):
        counter = {}
        for page in self.log_list:
          target = page["remote_host"]
          try:
            counter[target] += 1
          except KeyError:
            counter[target] = 1
        return sorted(counter.items(), key=lambda x:x[1],reverse=True)

**AC_AtHost**は引数を必要としません。
クラス内のインスタンス変数（**log_list**）を参照し、リモートホスト毎のアクセス数をカウントします。
カウントの結果は辞書型としてcounterにまとめられ、アクセス件数をキーとしてソートしたものを返します。
***
**AC_AtTime()**

      def AC_AtTime(self):
        counter = {}
        for page in self.log_list:
          timeobj = page["time_received_datetimeobj"]
          target = str(timeobj.year) + "-" + str(timeobj.month) + "-" + str(timeobj.day) + "-" + str(timeobj.hour)
          try:
            counter[target] += 1
          except KeyError:
            counter[target] = 1
        return sorted(counter.items(), key=lambda x:x[0])


**AC_AtTime**は引数を必要としません。
クラス内のインスタンス変数（**log_list**）を参照し、毎時ごとのアクセス数をカウントします。
カウントの結果は辞書型としてcounterにまとめられ、日時をキーとしてソートしたものを返します。
***
**OutputCSV(str)**

      def OutputCSV(self,filename):
        df = pd.DataFrame(self.log_list)
        df.to_csv(filename)

**OutputCSV**は出力するファイル名（**filename**）を引数とします。
この関数の役割はクラス内のインスタンス変数である**log_list**の**ファイル出力**です。
受け取ったログファイルを**apache_log_parser**を用いてパースしたものを**csv**として出力します。
**LogListParser**で時刻抽出したものを最終的に出力することもできます。
***
**OutputCSV2(str, str)**

      def OutputCSV2(self,data,filename):
        df = pd.DataFrame(data)
        df.to_csv(filename)

**OutputCSV2**は出力するデータ（**data**）と、出力するファイル名（**filename**）を引数とします。
与えられたデータを**pandas**で整形した後、csvファイルとして出力します。
pandasで受け取れるものは大体出力することができますが、主に想定しているデータは
**AC_AtHost**または**AC_AtTime**の結果です。
***
**StreamLogReceiver(str, str, datetime, datetime)**

      def Stream_LogReceiver(self, file_locate, log_format, time_from, time_to):
        parser = apache_log_parser.make_parser(log_format)
        with open(file_locate) as f:
          line = f.readline()
          counter_t = {}
          counter_h = {}
          ac = 0
          while line:
            parsed_line = parser(line)
            :
          ｛略｝
            :
             subprocess.call("clear")
            print("[*]Current number of log:",ac)
            ac += 1
            line = f.readline()
        return sorted(counter_h.items(), key=lambda x:x[1],reverse=True) , sorted(counter_t.items(), key=lambda x:x[0])

**StreamLogReceiver**はログファイルのパス（**file_locate**）、ログのフォーマット（**log_format**）、始端時刻（**time_from**）、終端時刻（**time_to**）を引数とします。
**StreamLogReceiver**はメモリに乗らないような大容量のログファイルを扱う場合に使用します。この関数ではブロック処理ではなく、ストリーム処理（**f.readline**を用いるような）でファイルを取り扱うため、理論的には扱うログファイルがどんなに大容量でも対応できるはずです。また、この関数ではアクセスログを一行づつ取り扱う関係上、**AC_AtTime**、**AC_AtHost**、**LogListParser**の機能を内蔵しています。そのため返り値は、**AC_AtTime**と**AC_AtHost**で得られる辞書型リスト2つに設定されています。
**LogListParser**を使う必要のない場合には、始端時刻を1年1月1日0時0分0秒、終端時刻を9999年1月1日0時0分0秒などに設定することで対応できます。

ただし、一行づつをメモリに載せて破棄するこの処理方法ではメモリを大きく節約できるものの、**LogReceiver**で行うようなファイル全体をメモリに乗せる処理方法に比べ大きく処理時間で大きく劣ります。
改善案としては、一行づつメモリに乗せるのではなく、複数行をメモリに載せて処理した後破棄する実装方法が挙げられます。その場合、どれだけの行を読み込む設定にするかの判断はプログラムを動かすハードのメモリに依拠します。

## LogInspector

起動

    python3 LogInspector.py

![LogInspector](https://user-images.githubusercontent.com/32869950/71964860-e1c0e680-3241-11ea-892d-082d3ad24593.png)

ログFileのパスはデフォルトで

    FILE = "/var/log/httpd/access_log"

ログフォーマットはデフォルトで

    format = '%h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\"'

として設定されています。

 - AddFile	
 -**LogReceiver**
 - ShowLog
 -**LogListPrinter**
 - FlashLog
 -**LogInitializer**
 - CountAccess
 -**AC_AtTime**
 -**AC_AtHost**
 - ParseLog
 -**LogListParser**
 - OutputOption
 -ファイル出力を有効/無効にする
 -出力するファイルの名前を設定する
 - StreamMode
 -**StreamLogReceiver**
 
 というように、各コマンドでそれぞれの機能を確認・使用することができます。
 OutputOptionで設定後は、ShowLog、CountAccessの出力結果がファイルで出力されます。
 ![Screenshot2](https://user-images.githubusercontent.com/32869950/71966158-6a408680-3244-11ea-86df-06252892f73a.png)

## 参考

[# ApacheのアクセスログをPythonのモジュールで読み込む](https://qiita.com/shotakaha/items/05287cd625176945322a)
[# apache-loggen を使って Apache アクセスログのダミーログを生成する](https://inokara.hateblo.jp/entry/2015/06/21/225143)
[# Pythonのdatetimeで日付の範囲を比較演算子で指定する](https://qiita.com/Alice1017/items/4ce5be3f46aa34f9f900)
[# Python メモリに乗らない巨大なデータを扱う](https://roy29fuku.com/tips/python-load-large-xml/)
