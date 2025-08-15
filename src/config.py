import os
from dotenv import load_dotenv

load_dotenv()

# TuShare 配置
TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN')

# OpenAI 配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')

# 分析配置
DEFAULT_START_DATE = '20180101'
DEFAULT_END_DATE = '20241231'

# 评分权重
SCORE_WEIGHTS = {
    'quality': 0.25,
    'growth': 0.25,
    'valuation': 0.20,
    'momentum': 0.15,
    'risk': 0.15
}

# 行业分类
INDUSTRY_MAPPING = {
    '银行': '金融',
    '保险': '金融',
    '证券': '金融',
    '房地产': '房地产',
    '建筑': '建筑',
    '建材': '建材',
    '钢铁': '钢铁',
    '有色金属': '有色金属',
    '化工': '化工',
    '石油': '石油',
    '电力': '公用事业',
    '燃气': '公用事业',
    '水务': '公用事业',
    '交通运输': '交通运输',
    '汽车': '汽车',
    '家用电器': '家用电器',
    '食品饮料': '食品饮料',
    '纺织服装': '纺织服装',
    '轻工制造': '轻工制造',
    '医药生物': '医药生物',
    '计算机': '计算机',
    '通信': '通信',
    '电子': '电子',
    '机械设备': '机械设备',
    '电气设备': '电气设备',
    '国防军工': '国防军工',
    '农林牧渔': '农林牧渔',
    '商业贸易': '商业贸易',
    '休闲服务': '休闲服务',
    '传媒': '传媒',
    '综合': '综合'
}
