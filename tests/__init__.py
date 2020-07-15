# coding=utf-8
def __analysis__(routes):
    """
    根据给的一个结果，构造为简单的文字表达形式
    @param routes:
    @return: 简单的文字表达形式
    """
    head = routes['head']
    tail = routes['tail']
    if head is not None:  # 如果存在头的话，说明要按照偶数项去取才能拿到实体,但是由于从0开始，得拿奇数
        # 首先确定顺序
        index = routes["index"][1::2]
        # 对与每一条路径来说
        final_routes = []
        for each_route in routes['bindings']:
            tmp_route = head
            # 按照顺序依次加入特定路径下的每一个节点
            for each_index in index:
                tmp_route += ("->" + each_route[each_index]['value'].replace(
                    "file:///F:/d2r-server-0.7/holder8.nt#holder_copy/", ""))
            # 添加尾节点
            if tail:
                tmp_route += ("->" + tail)
            final_routes.append(tmp_route)
    else:  # 说明头实体是空的，在结果里边要拿偶数项才能拿到实体
        index = routes["index"][::2]
        final_routes = []
        for each_route in routes['bindings']:
            tmp_route = head
            # 按照顺序依次加入特定路径下的每一个节点
            for each_index in index:
                tmp_route += (each_route[each_index]['value'].replace(
                    "file:///F:/d2r-server-0.7/holder8.nt#holder_copy/", "")
                              + "->")
            # 添加尾节点
            tmp_route += ("->" + tail)
            final_routes.append(tmp_route)
    return final_routes


test = {
    "head": "招商局轮船股份有限公司",
    "tail": "招商银行股份有限公司",
    "index": ["p", "o", "q"],
    "bindings": [{"p": {"type": "uri", "value": "http://localhost:2020/vocab/resource/holder_copy_holder_name"},
                  "q": {"type": "uri", "value": "http://localhost:2020/vocab/resource/holder_copy_holder_name"},
                  "o": {"type": "uri", "value": "file:///F:/d2r-server-0.7/holder8.nt#holder_copy/深圳市招融投资控股有限公司"}},
                 {"p": {"type": "uri", "value": "http://localhost:2020/vocab/resource/holder_copy_holder_name"},
                  "q": {"type": "uri", "value": "http://localhost:2020/vocab/resource/holder_copy_holder_name"},
                  "o": {"type": "uri", "value": "file:///F:/d2r-server-0.7/holder8.nt#holder_copy/深圳市晏清投资发展有限公司"}}]
}

routes = __analysis__(test)
print(routes)
