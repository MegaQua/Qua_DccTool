import os
import requests
import feedparser
from datetime import datetime
import pyautogui
import pyperclip
import time
import subprocess
import pytz
from bs4 import BeautifulSoup
from PIL import Image
import shutil

RSS_PREFIX = "http://localhost:32768"
# RSS源URL
GV_RSS = {
    "RSS_urls": {
        "GunvoltOfficial": f"{RSS_PREFIX}/twitter/user/GunvoltOfficial",
        #"ROCKMAN_UNITY": f"{RSS_PREFIX}/twitter/media/ROCKMAN_UNITY",
        "赤紅烈焰": f"{RSS_PREFIX}/bilibili/user/dynamic/1970436",
        "牌人": f"{RSS_PREFIX}/bilibili/user/dynamic/11497341",
        #"cougar1404": f"{RSS_PREFIX}/twitter/media/cougar1404",
        #"t_aizu": f"{RSS_PREFIX}/twitter/media/t_aizu",
        #"gunvolt_pixiv": f"{RSS_PREFIX}/pixiv/search/gunvolt/empty/safe",
        #"arknights": f"{RSS_PREFIX}/twitter/user/ArknightsStaff",
        "chingis_khanzo": f"{RSS_PREFIX}/twitter/media/chingis_khanzo",
        "meka_moru_4se": f"{RSS_PREFIX}/twitter/media/meka_moru_4se",
        "sakuragawa_megu": f"{RSS_PREFIX}/twitter/media/sakuragawa_megu",
        "iiKOAO": f"{RSS_PREFIX}/twitter/media/iiKOAO",
        },
    "QQimages": ["C:/Users/QHome.S/PycharmProjects/nonebot/autogui/皇神群2.png",
                 "C:/Users/QHome.S/PycharmProjects/nonebot/autogui/皇神群3.png", ]
}
POKEKA_RSS = {
    "RSS_urls": {"pokecamatomeru": f"{RSS_PREFIX}/twitter/media/pokecamatomeru",
                 "pokekameshi":f"{RSS_PREFIX}/twitter/media/pokekameshi",
                 "宝可梦集换式卡牌游戏": f"{RSS_PREFIX}/bilibili/user/dynamic/3461571573450904",
                 "Jaltoom_PTCGL": f"{RSS_PREFIX}/twitter/media/Jaltoom_PTCGL",
                 "Pokemon_cojp":f"{RSS_PREFIX}/twitter/media/Pokemon_cojp"},
    "QQimages": ["C:/Users/QHome.S/PycharmProjects/nonebot/autogui/ptcg1.png",
                 "C:/Users/QHome.S/PycharmProjects/nonebot/autogui/ptcg2.png"]
}

def sanitize_filename(name):
    """通过移除非字母数字字符来清理文件名，同时保留文件扩展名。"""
    name, ext = os.path.splitext(name)
    sanitized_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c in ' _-']).rstrip()
    return sanitized_name + ext

def download_images(image_urls, folder_path, max_size=2000):
    """下载所有图片并保存到指定文件夹，如果图片像素大于400万，则等比例把长边压缩到1000像素。"""
    for i, image_url in enumerate(image_urls, start=1):
        response = requests.get(image_url)
        ext = os.path.splitext(image_url)[1].lower()  # 获取文件扩展名
        if not ext:  # 如果扩展名为空，则默认为.jpg
            ext = '.jpg'
        file_name = f"image{i}{ext}"  # 使用原始扩展名
        file_path = os.path.join(folder_path, file_name)

        # 保存图片文件
        with open(file_path, 'wb') as file:
            file.write(response.content)

        # 如果不是GIF，尝试调整尺寸
        if ext != '.gif':
            with Image.open(file_path) as img:
                width, height = img.size
                if width * height > max_size * max_size:
                    if width > height:
                        new_width = max_size
                        new_height = int(height * max_size / width)
                    else:
                        new_height = max_size
                        new_width = int(width * max_size / height)

                    # 使用ImageResampling.LANCZOS进行调整
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                    # 如果图片模式是RGBA，则将其转换为RGB
                    if resized_img.mode == 'RGBA':
                        resized_img = resized_img.convert('RGB')

                    resized_img.save(file_path)

def download_videos(url_lists, folder_path):
    """下载URL列表中的视频并保存到指定文件夹，文件名为 video{index}.{extension}"""
    for index, video_url in enumerate(url_lists):
        try:
            response = requests.get(video_url, stream=True)

            # 提取文件扩展名
            file_extension = os.path.splitext(video_url.split("?")[0])[1]

            # 构建新的文件名
            file_name = f"video{index}{file_extension}"
            file_path = os.path.join(folder_path, file_name)

            if response.status_code == 200:
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
        except:
            pass

def create_folder_name(entry_title, entry_date):
    """基于条目标题和日期创建一个清理后的文件夹名称，同时删除所有空格。"""
    date_str = entry_date.strftime("%Y%m%d%H%M%S")
    # 先删除标题中的所有空格，然后进行其他清理工作
    title_no_spaces = entry_title.replace(' ', '')
    title_preview = sanitize_filename(title_no_spaces[:20])
    folder_name = f"{date_str}_{title_preview}"
    return folder_name

def convert_utc_to_cst(utc_datetime):
    """
    将UTC时间转换为中国标准时间（CST）。

    :param utc_datetime: UTC时间的datetime对象
    :return: 转换为CST的datetime对象
    """
    utc_tz = pytz.timezone('UTC')
    cst_tz = pytz.timezone('Asia/Shanghai')

    utc_datetime = utc_tz.localize(utc_datetime)
    cst_datetime = utc_datetime.astimezone(cst_tz)

    return cst_datetime

def try_open_QQ():
    pyautogui.rightClick(1640, 1060)
    time.sleep(1)
    pyautogui.leftClick(1736, 998)

def post_to_qq(folder_path):
    # 检查文件夹中是否有除.txt以外的文件
    non_txt_files_exist = any(file for file in os.listdir(folder_path) if not file.endswith('.txt'))

    if not non_txt_files_exist:
        return  # 如果没有除.txt以外的文件，直接返回不执行后续操作
    # 从content.txt中读取内容并复制到剪贴板
    content_file_path = os.path.join(folder_path, "content.txt")
    with open(content_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    pyperclip.copy(content)

    # 移动到指定坐标并点击
    x, y = 560, 936
    pyautogui.click(x, y)

    # 等待一小段时间确保点击生效
    time.sleep(0.5)

    # 模拟按下粘贴热键（Ctrl+V）
    pyautogui.keyDown('ctrl')
    pyautogui.press('v')
    pyautogui.keyUp('ctrl')

    # 等待一小段时间确保第一次粘贴完成
    time.sleep(1)

    # 遍历文件夹中的所有文件
    for file_name in os.listdir(folder_path):

        # 检查文件是否不是.txt文件
        if not file_name.endswith('.txt'):
            file_path = os.path.join(folder_path, file_name)

            # 使用Powershell命令将文件复制到剪贴板
            command = f"powershell -command \"Add-Type -AssemblyName System.Windows.Forms;[System.Windows.Forms.Clipboard]::SetFileDropList([System.Collections.Specialized.StringCollection](@(\\\"{file_path}\\\")))\""
            subprocess.run(command, shell=True)

            # 模拟按键粘贴
            pyautogui.keyDown('ctrl')
            pyautogui.press('v')
            pyautogui.keyUp('ctrl')

    # 模拟按下Ctrl+Enter
    pyautogui.keyDown('ctrl')
    pyautogui.press('enter')
    pyautogui.keyUp('ctrl')

def click_on_image(image_path, click_type='left', max_attempts=2):
    """
    在屏幕上找到指定的图片并执行点击操作。

    :param image_path: 图片路径
    :param click_type: 点击类型 ('left', 'right', 'double')
    :param max_attempts: 尝试查找并点击图片的最大次数
    """
    time.sleep(1)
    attempts = 0
    while attempts < max_attempts:
        try:
            # 在屏幕上寻找图片
            location = pyautogui.locateOnScreen(image_path)

            # 如果找到了图片，根据点击类型执行点击
            if location:
                # 获取图片的中心坐标
                center = pyautogui.center(location)
                if click_type == 'double':
                    pyautogui.doubleClick(center)
                elif click_type == 'right':
                    pyautogui.rightClick(center)
                else:  # 默认为左键单击
                    pyautogui.click(center)
                return True  # 成功找到图片并点击后退出函数
        except:
            print("图片未找到，重试中...")
            attempts += 1
            time.sleep(1)  # 每次尝试间暂停1秒

    print(f"尝试了{max_attempts}次后未能找到图片{image_path}。")

def delete_old_folders(parent_folder, oldest_time_str):
    oldest_time = datetime.strptime(oldest_time_str, "%Y%m%d%H%M%S")
    for folder_name in os.listdir(parent_folder):
        folder_path = os.path.join(parent_folder, folder_name)
        if os.path.isdir(folder_path):
            try:
                folder_time = datetime.strptime(folder_name.split("_")[0], "%Y%m%d%H%M%S")
                if folder_time < oldest_time:
                    shutil.rmtree(folder_path)
                    print(f"已删除旧文件夹: {folder_path}")
            except ValueError:
                pass  # 跳过名称格式不正确的文件夹

def print_rss_feed(RSS_Data):
    # 解析RSS源
    try_open_QQ()
    urls = RSS_Data["RSS_urls"]
    QQimages = RSS_Data["QQimages"]
    success = False
    for QQimage in QQimages:
        success = click_on_image(QQimage)

    if not success:
        return

    oldest_time_str = datetime.now().strftime("%Y%m%d%H%M%S")
    parent_folders = []

    for ID, url in urls.items():
        feed = feedparser.parse(url)
        QQimages = RSS_Data["QQimages"]
        parent_folder = os.path.join(os.getcwd(), f"X_{ID}")
        parent_folders.append(parent_folder)

        for entry in feed.entries:
            print(entry)
            soup = BeautifulSoup(entry.summary, 'html.parser')
            title_content = soup.get_text()
            published_datetime = datetime(*entry.published_parsed[:6])
            published_datetime_cst = convert_utc_to_cst(published_datetime)
            folder_name = create_folder_name(title_content, published_datetime_cst)

            if published_datetime_cst.strftime("%Y%m%d%H%M%S") < oldest_time_str:
                oldest_time_str = published_datetime_cst.strftime("%Y%m%d%H%M%S")

            final_folder_path = os.path.join(parent_folder, folder_name)

            if not os.path.exists(final_folder_path):
                os.makedirs(final_folder_path, exist_ok=True)
                media_urls = []
                if "summary" in entry:
                    images = soup.find_all('img')
                    for img in images:
                        url = img['src']
                        media_urls.append(url)

                    video_urls = []
                    videos = soup.find_all('video')
                    for video in videos:
                        video_url = video.get('src')
                        if video_url:
                            video_urls.append(video_url)
                else:
                    media_urls = []
                    video_urls = []

                try:
                    if media_urls:
                        download_images(media_urls, final_folder_path)
                    if video_urls:
                        download_videos(video_urls, final_folder_path)
                except:
                    print(f"download {media_urls} {video_urls} failed")

                formatted_published_time = published_datetime.strftime('%Y年%m月%d日%H时%M分%S秒')
                content_file_path = os.path.join(final_folder_path, "content.txt")
                with open(content_file_path, 'w', encoding='utf-8') as file:
                    file.write(f"原推: {entry.link}\n")
                    file.write(f"正文: {title_content}\n")
                    file.write(f"发布日期: {formatted_published_time}\n")

                print(f"内容已保存到: {final_folder_path}")
                if media_urls:
                    pass
                    #post_to_qq(final_folder_path)

    for parent_folder in parent_folders:
        delete_old_folders(parent_folder, oldest_time_str)

# 执行函数
while True:
    japan_timezone = pytz.timezone('Asia/Tokyo')
    current_time_japan = datetime.now(japan_timezone)
    print(current_time_japan.strftime('%Y-%m-%d %H:%M:%S'))
    print_rss_feed(GV_RSS)
    print_rss_feed(POKEKA_RSS)
    print("周期执行完成")
    time.sleep(3600)
