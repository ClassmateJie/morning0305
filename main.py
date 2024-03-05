import pytz
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import random
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import yaml
from zhdate import ZhDate

def get_yaml_data():
    # 从YAML文件中读取数据
    with open('config.yml', 'r', encoding='utf-8') as yaml_file:
        loaded_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
    return loaded_data


def get_weather(city_code):
    url = "http://t.weather.itboy.net/api/weather/city/" + city_code
    res = requests.get(url).json()
    city = res['cityInfo']['city']
    weather = res['data']['forecast'][0]
    return city, weather['type'], weather['low'], weather['high'], weather['notice']


def get_count(start_date):
    delta = datetime.now(pytz.timezone(timezone1)) - datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=pytz.timezone(timezone1))
    return delta.days


def get_birthday(birthday):
    today1 = datetime.now(pytz.timezone(timezone1)).date()
    next = datetime.strptime(str(today1.year) + "-" + birthday, "%Y-%m-%d").replace(tzinfo=pytz.timezone(timezone1))
    if next < datetime.now(pytz.timezone(timezone1)):
        next = next.replace(year=next.year + 1)
    return (next - datetime.now(pytz.timezone(timezone1))).days


def get_words():
    url = "https://api.shadiao.pro/"
    param = ["du", "chp", "pyq"]
    url += str(param[random.randint(0, 2)])
    words = requests.get(url)
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


if __name__ == '__main__':
    SHA_TZ = timezone(
        timedelta(hours=8),
        name='Asia/Shanghai',
    )
    timezone1 = "Asia/Shanghai"
    # 协调世界时
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    # 北京时间
    beijing_now = utc_now.astimezone(SHA_TZ)

    today = beijing_now.now()
    time = str(beijing_now.date()) + " " + beijing_now.date().strftime("%A")

    # today = datetime.now()
    # time = str(date.today())+" "+date.today().strftime("%A")
    config_data = get_yaml_data()

    app_id = config_data.get('app').get('id')
    app_secret = config_data.get('app').get('secret')

    template = config_data.get('msg')[0].get('template')
    template_id = template.get('id')

    user_id_list = template.get('user_id')

    other_list = template.get('other')
    city_code = other_list[0]
    day_count = get_count(other_list[1])
    birthday_count = get_birthday(other_list[2])
    city, wea, low, high, notice = get_weather(city_code)

    # 创建一个公历日期对象
    lunar_date = ZhDate.today()

    # 获取农历的月份和日期
    lunar_month = lunar_date.lunar_month
    lunar_day = lunar_date.lunar_day
    lunar_chinese = lunar_date.chinese().split(" ")[0]
    lunar_chinese_md = lunar_chinese.split("年")[1]


    data = {"time": {"value": time, "color": get_random_color()},"timezh": {"value": lunar_chinese_md, "color": get_random_color()}, "city": {"value": city, "color": get_random_color()},
            "weather": {"value": wea, "color": get_random_color()}, "low": {"value": low, "color": get_random_color()},
            "high": {"value": high, "color": get_random_color()},
            "days": {"value": day_count, "color": get_random_color()},
            "birthday": {"value": birthday_count, "color": get_random_color()},
            "words": {"value": notice, "color": get_random_color()}}

    client = WeChatClient(app_id, app_secret)
    wm = WeChatMessage(client)

    for user_id in user_id_list:
        wm.send_template(user_id, template_id, data)
