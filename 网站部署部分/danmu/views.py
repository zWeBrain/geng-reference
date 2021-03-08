from django.shortcuts import render  # 导入render模块
import danmu.methods as dm
import danmu.cluster as dc

# conn = dm.get_connection()
# dm.jiebaUtil(conn)
# fanju_name, name_fanju = dm.get_fanju(conn)
# doc_len, doc_name = dm.get_doc_len(conn)

query = ''
res = []
se6 = '选择你喜欢的类别'
suggest = []
se_set = ['选择你喜欢的动漫', '选择你喜欢的动漫', '选择你喜欢的动漫', '选择你喜欢的动漫', '选择你喜欢的动漫']
num = 0
if num < 1:
    dm.jiebaUtil_file()
    fanju_name, name_fanju = dm.get_fanju_file()
    doc_len, doc_name = dm.get_doc_len_file()


def index(request):
    global num
    num += 1
    query = request.POST.get('query', '')
    se6 = request.POST.get('se6', '选择你喜欢的类别')
    res = dm.gbk_file(query, doc_len, doc_name)
    # res = dm.gbk(query, conn, doc_len, doc_name)
    se_set = [request.POST.get('se1', '选择你喜欢的动漫'), request.POST.get('se2', '选择你喜欢的动漫'),
              request.POST.get('se3', '选择你喜欢的动漫'),
              request.POST.get('se4', '选择你喜欢的动漫'), request.POST.get('se5', '选择你喜欢的动漫')]
    clust = []
    for i in set(se_set):
        if i in name_fanju:
            clust.append(name_fanju[i])
    # suggest = dm.suggest(conn, clust, fanju_name)
    suggest = dm.suggest_file(clust, fanju_name)
    if se6 in dc.labels:
        cluster = dc.rand(dc.labels[se6])
    else:
        cluster = []
    return render(request, 'index.html', {'form': name_fanju, 'result': res, 'query': query, 'suggests': suggest,
                                          'se1': se_set[0], 'se2': se_set[1], 'se3': se_set[2], 'se4': se_set[3],
                                          'se5': se_set[4], 'se6': se6, 'form3': dc.labels, 'cluster': cluster})
