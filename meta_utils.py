def get_meta_value(meta):
    """
    处理 ebooklib 元数据条目，获得字符串
    支持 dict, tuple, str 三种类型
    """
    if isinstance(meta, dict):
        return meta.get('value', '')
    if isinstance(meta, tuple):
        return meta[0]
    return meta