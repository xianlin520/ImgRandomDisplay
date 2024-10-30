# 设置配置数值
class InitVar:
    """
    全大写变量为静态常量
    小写变量为动态变量
    """
    # 设置配置文件名称
    CONFIG_FILE = 'config.ini'
    LIKE_CONFIG_FILE = 'favorites.ini'

    # 设置程序窗体大小
    WINDOW_SIZE = (1300, 750)
    # 设置程序标题
    WINDOW_TITLE = '千寻图片查看器'

    # 设置下拉框动态配置值
    options = "随机展示"  # 默认值/选择值
    # OPTIONS_LIST = ["随机展示", "按时间↓",  "按时间↑", "按大小↓", "按大小↑"] # 下拉框选项
    OPTIONS_LIST = ["随机展示", "新 -> 旧", "旧 -> 新", "小 -> 大", "大 -> 小"]  # 下拉框选项

    # 设置图片路径
    image_dir = ''
    default_read_dir = ''  # 默认读取目录
    default_save_dir = ''  # 默认保存目录
    # image_dir = r'D:\123pan\1818068532\123同步文件夹\P站图片'
    # default_read_dir = r'D:\123pan\1818068532\123同步文件夹\P站图片'
    # default_read_dir = r'D:\P站图片'

    # 最爱图片列表
    favorites = []
