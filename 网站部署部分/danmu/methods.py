import math
import jieba
import psycopg2

def gbk(query, conn, doc_len={}, doc_name={}, top=10, k=1.2, b=0.75):
    words = jieba.lcut(shorten(query))
    query = []
    for word in words:
        if len(word) == 1 or word.isdigit():
            continue
        else:
            query.append(word)
    scores = dict()
    idf = dict()
    N = len(doc_len)
    avg_doclen = sum(doc_len.values()) / N
    for doc in doc_len:
        scores[doc] = 0
    for key in query:
        dic = get_dictionary(conn, key)
        idf[key] = 1.0 + math.log(N / len(dic))
        for item in dic:
            split = item.split('-')
            juji = int(split[0])
            cnt = int(split[1])
            scores[juji] += idf[key] * (k + 1) * cnt / (k * (1 - b + b * (doc_len[juji] / avg_doclen)) + cnt)
    scores_list = []
    for key in scores:
        scores_list.append((doc_name[key], scores[key]))
    scores_list.sort(key=lambda x: x[1], reverse=True)
    result = []
    for res in scores_list[:top]:
        if res[1] != 0:
            result.append(res[0])
    return result


def gbk_file(query, doc_len={}, doc_name={}, top=10, k=1.2, b=0.75):
    words = jieba.lcut(shorten(query))
    query = []
    for word in words:
        if len(word) == 1 or word.isdigit():
            continue
        else:
            query.append(word)
    scores = dict()
    idf = dict()
    N = len(doc_len)
    avg_doclen = sum(doc_len.values()) / N
    for doc in doc_len:
        scores[doc] = 0
    for key in query:
        if key not in dictionary:
            continue
        dic = get_dictionary_file(key)
        idf[key] = 1.0 + math.log(N / len(dic))
        for item in dic:
            split = item.split('-')
            juji = int(split[0])
            cnt = int(split[1])
            scores[juji] += idf[key] * (k + 1) * cnt / (k * (1 - b + b * (doc_len[juji] / avg_doclen)) + cnt)
    scores_list = []
    for key in scores:
        scores_list.append((doc_name[key], scores[key]))
    scores_list.sort(key=lambda x: x[1], reverse=True)
    result = []
    for res in scores_list[:top]:
        if res[1] != 0:
            result.append(res[0])
    return result


def get_connection():
    return psycopg2.connect(user="checker",
                            password="wangxiaohan",
                            host="121.36.22.150",   # localhost，远程较慢，故用文件系统！
                            port="5432",
                            database="postgres")


def get_doc_len(con):
    doc_len = dict()
    doc_name = dict()
    cursor = con.cursor()
    doc_len_query = """select * from postgres.ir.text_len"""
    cursor.execute(doc_len_query)
    rows = cursor.fetchall()
    for row in rows:
        doc_len[row[0]] = row[1]
        doc_name[row[0]] = row[2]
    return doc_len, doc_name


def get_doc_len_file():
    doc_len = dict()
    doc_name = dict()
    f = open("static\\doclen.txt")
    lines = f.readlines()
    doc_len = dict()
    for line in lines:
        split = line.strip().split('-')
        doc_len[int(split[0])] = int(split[1])
    f = open("static\\juji.txt", 'r', encoding='UTF-8')
    lines = f.readlines()
    doc_name = dict()
    for line in lines:
        split = line.strip().split(',')
        doc_name[int(split[0])] = split[1][3:]
    return doc_len, doc_name


def get_dictionary(con, key):
    try:
        cursor = con.cursor()
        reversed_index_query = "select * from postgres.ir.reversed_index where term = '{}'".format(key)
        cursor.execute(reversed_index_query)
        rows = cursor.fetchall()
        return rows[0][2]
    except Exception as e:
        print("执行sql时出错：%s" % (e))
        con.rollback()


def get_dictionary_file(key):
    return dictionary[key]


def get_dictionary_all_file():
    f = open("static\\block.csv")
    lines = f.readlines()
    dictionary = dict()
    for line in lines:
        split = line.strip().split(',')
        for i in split[2:]:
            if split[0] in dictionary:
                dictionary[split[0]].append(i)
            else:
                dictionary[split[0]] = [i]
    return dictionary


def jiebaUtil(conn):
    cursor = conn.cursor()
    query = """select * from postgres.ir.raw_words"""
    cursor.execute(query)
    new_words = cursor.fetchall()
    for key_word in new_words:
        if key_word[1] > 2:
            jieba.add_word(key_word[0], freq=key_word[1] * 10, tag=None)


def jiebaUtil_file():
    new_words = []
    f = open("static\\new_words_all.txt")
    lines = f.readlines()
    for line in lines:
        split = line.strip().split(',')
        new_words.append((split[0], int(split[1])))
    f.close()
    for key_word in new_words:
        if key_word[1] > 2:
            jieba.add_word(key_word[0], freq=key_word[1] * 10, tag=None)


def shorten(s):
    if s is None:
        return ''
    superfluous = ' 啊吧哇呀嘛吗耶？！?!.。诶了阿哈呗啥'
    for i in superfluous:
        s = s.rstrip(i).lower()
    ss = ''.join(reversed(s))
    k = -1
    j = 0
    array = [-1]
    plen = len(ss)
    zeros = 0
    nonze = 0
    while j < plen:
        if k == -1 or ss[j] == ss[k]:
            k += 1
            j += 1
            if k == 0:
                if j != zeros + 1:
                    loop = (int)(nonze / zeros) - 1
                    return cut_string(s, plen) if loop < 1 else cut_string(s, plen - zeros * loop)
                zeros += 1
            else:
                nonze += 1
            array.append(k)
        else:
            k = array[k]
    return cut_string(s, plen) if zeros == plen else (cut_string(s, zeros) if zeros > 1 else cut_string(s, zeros + 1))


def cut_string(s, lens):
    return s[0: lens]


def get_fanju(con):
    fanju_name = dict()
    name_fanju = dict()
    cursor = con.cursor()
    doc_len_query = """select * from postgres.ir.fanju_id"""
    cursor.execute(doc_len_query)
    rows = cursor.fetchall()
    for row in rows:
        fanju_name[row[0]] = row[1]
        name_fanju[row[1]] = row[0]
    return fanju_name, name_fanju


def get_fanju_file():
    name_fanju = dict()
    fanju_name = dict()
    f = open("static\\dic.txt", 'r', encoding='UTF-8')
    lines = f.readlines()
    doc_len = dict()
    for line in lines:
        split = line.strip().split(',')
        fanju_name[int(split[0])] = split[1]
        name_fanju[split[1]] = int(split[0])
    return fanju_name, name_fanju


def distance_ave(conn, clust, target):
    dis = 0
    for i in clust:
        cursor = conn.cursor()
        query = "select avg(distance) from postgres.ir.distance3 where id1 = {} and id2 = {} or id1 = {} and id2 = {}".format(
            i, target, target, i)
        cursor.execute(query)
        rows = cursor.fetchall()
        dis += rows[0][0]
    return dis / len(clust)


def distance_complete(conn, clust, target):
    dis = 0
    for i in clust:
        cursor = conn.cursor()
        query = "select avg(distance) from postgres.ir.distance3 where id1 = {} and id2 = {} or id1 = {} and id2 = {}".format(
            i, target, target, i)
        cursor.execute(query)
        rows = cursor.fetchall()
        dis = max(rows[0][0], dis)
    return dis


def distance_single(conn, clust, target):
    dis = 1
    for i in clust:
        cursor = conn.cursor()
        query = "select avg(distance) from postgres.ir.distance3 where id1 = {} and id2 = {} or id1 = {} and id2 = {}".format(
            i, target, target, i)
        cursor.execute(query)
        rows = cursor.fetchall()
        dis = min(rows[0][0], dis)
    return dis


def distance_ave_file(clust, target):
    dis = 0
    for i in clust:
        dis += (distances[i][target] + distances[target][i]) / 2
    return dis / len(clust)


def distance_complete_file(clust, target):
    dis = 0
    for i in clust:
        dis = max((distances[i][target] + distances[target][i]) / 2, dis)
    return dis


def distance_single_file(clust, target):
    dis = 1
    for i in clust:
        dis = min((distances[i][target] + distances[target][i]) / 2, dis)
    return dis


def suggest(conn, clust, fanju_name):
    if len(clust) == 0:
        return []
    distance = [1, 1, 1, 1, 1, 1]
    indice = [-1, -1, -1, -1, -1, -1]
    for i in fanju_name:
        if i in clust:
            continue
        else:
            dis = distance_single(conn, clust, i)
            if dis < distance[0]:
                distance[0] = dis
                indice[0] = i
            dis = distance_complete(conn, clust, i)
            if dis < distance[0]:
                distance[1] = dis
                indice[1] = i
            dis = distance_ave(conn, clust, i)
            maximumd = 0
            maxindex = 0
            for j in range(4):
                if distance[j + 2] > maximumd:
                    maximumd = distance[j + 2]
                    maxindex = j + 2
            if dis < maximumd:
                distance[maxindex] = dis
                indice[maxindex] = i
    res = []
    for i in range(6):
        if indice[i] == -1:
            continue
        if fanju_name[indice[i]] not in res:
            res.append(fanju_name[indice[i]])
    return res


def suggest_file(clust, fanju_name):
    if len(clust) == 0:
        return []
    distance = [1, 1, 1, 1, 1, 1]
    indice = [-1, -1, -1, -1, -1, -1]
    for i in fanju_name:
        if i in clust:
            continue
        else:
            dis = distance_single_file(clust, i)
            if dis < distance[0]:
                distance[0] = dis
                indice[0] = i
            dis = distance_ave_file(clust, i)
            if dis < distance[0]:
                distance[1] = dis
                indice[1] = i
            dis = distance_complete_file(clust, i)
            maximumd = 0
            maxindex = 0
            for j in range(4):
                if distance[j + 2] > maximumd:
                    maximumd = distance[j + 2]
                    maxindex = j + 2
            if dis < maximumd:
                distance[maxindex] = dis
                indice[maxindex] = i
    res = []
    for i in range(6):
        if indice[i] == -1:
            continue
        if fanju_name[indice[i]] not in res:
            res.append(fanju_name[indice[i]])
    return res


def get_dic():
    matrix = []
    f = open("static\\dis_matrix_file.txt", 'r')
    lines = f.readlines()
    for line in lines:
        split = line.strip().split(' ')
        dis = []
        for l in split:
            dis.append(float(l))
        matrix.append(dis)
    return matrix

jiebaUtil_file()
distances = get_dic()
dictionary = get_dictionary_all_file()