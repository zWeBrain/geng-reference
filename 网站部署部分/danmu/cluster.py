import random
import psycopg2


def get_lables(con):
    labels = dict()
    cursor = con.cursor()
    doc_len_query = """select * from postgres.ir.cluster2"""
    cursor.execute(doc_len_query)
    rows = cursor.fetchall()
    cluster = dict()
    for row in rows:
        labels[row[1]] = row[0]
        cluster[row[0]] = []
        for j in row[2]:
            cluster[row[0]].append(j)
    return labels, cluster

#cluster = [cluster1.split(','), cluster2.split(','), cluster3.split(','), cluster4.split(','),
#           cluster5.split(','), cluster6.split(','), cluster7.split(','), cluster8.split(','),
#           cluster9.split(','), cluster10.split(','), cluster11.split(','), cluster12.split(','),
#           cluster13.split(','), cluster14.split(','), cluster15.split(','), cluster16.split(','),
#           cluster17.split(',')]

# 密码不会泄露吧...
conn = psycopg2.connect(user="checker",
                        password="wangxiaohan",
                        host="121.36.22.150", 
                        port="5432",
                        database="postgres")

labels, cluster = get_lables(conn)


def rand(key):
    return random.sample(cluster[key], 5)
