# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import ui
from selenium.webdriver.chrome.service import Service as ChromeService, Service
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor
import threading
from configuration import config
from datetime import datetime
from time import sleep
import random
import os
import sys
import pickle
import time
import platform

# 定时任务
from apscheduler.schedulers.blocking import BlockingScheduler
# 随机字符串
from random_words import RandomWords
word_generator = RandomWords()

#  Initialization
words = open("ExtraFiles//words.txt", "r").readlines()


def init_browse(email):
    #  Setting up chrome
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    if global_proxy != "":
        proxy_array = config['https_proxy'][int(global_proxy)]
    else:
        proxy_array = config['https_proxy'][0]
    print("proxy: "+proxy_array)

    user_data_path = os.getcwd()
    if platform.system().lower() == 'windows':
        user_data_path += '\\google-chrome\\{}'.format(email)
    else: 
        user_data_path += '/google-chrome/{}'.format(email)
    profile_name = "Profile " + str(config["profile_number"])

    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
    options.add_argument('--user-data-dir=' + user_data_path)
    options.add_argument('--profile-directory=' + profile_name)
    # options.add_argument('--proxy-server=http://127.0.0.1:10809')
    # options.add_argument('--proxy-server=' + config['https_proxy'])
    options.add_argument('--proxy-server=' + proxy_array)

    # 浏览器不提供可视化界面。Linux下如果系统不支持可视化不加这条会启动失败
    # options.add_argument('--headless')

    # driver = webdriver.Chrome('./chromedriver', options=options)
    # service=Service(r'./chromedriver.exe')
    # driver = webdriver.Chrome(service=service, options=options)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    driver.execute_script('return navigator.userAgent')
    # 最大等待10s
    # driver.set_page_load_timeout(10)
    # driver.maximize_window()
    driver.set_window_size(1024, 768)
    return driver


def page_loaded(driver):
    return driver.find_element(By.TAG_NAME, 'body') != None


def check_is_logged_in(driver):
    #Check if you is logged in
    # print(driver.current_url)
    if driver.current_url == "https://account.presearch.com/":
        return True
    return False


def writeNeedLogin(email, password):
    if check_login_reload(email):
        return
    f = open("ExtraFiles//2-relogin//login_reload.txt", "a+")
    f.write("{}:{}\n".format(email, password))
    f.close()


def check_login_reload(email):
    path = "ExtraFiles//2-relogin//login_reload.txt"
    if not os.path.exists(path):
        return False
    today_finish = open(path, "r").readlines()
    for t in today_finish:
        if t.startswith(email):
            return True
    return False


def write_today_task_finish(email):
    today_date = datetime.today().strftime('%Y-%m-%d')
    f = open("ExtraFiles//task_log//" + today_date + ".txt", "a+")
    f.write("{}\n".format(email))
    f.close()


def check_local_today_task(email):
    today_date = datetime.today().strftime('%Y-%m-%d')
    path = "ExtraFiles//task_log//" + today_date + ".txt"
    if not os.path.exists(path):
        return False
    today_finish = open(path, "r").readlines()
    for t in today_finish:
        if t.startswith(email):
            return True
    return False


def checkLogin(driver, email):
    driver.get("https://account.presearch.com/")
    wait = ui.WebDriverWait(driver, 10)
    wait.until(page_loaded)
    check_is_logged = check_is_logged_in(driver)

    if check_is_logged:
        userNameSpan = driver.find_element(By.XPATH, '//*[@id="main"]/div[1]/p/a').text
        if email == userNameSpan:
            return True
    return False


def NodeExists(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
        return True
    except:
        return False


def check_day_searchs(email, driver):
    try:
        # Page where we have the list of daily searches.
        link = "https://account.presearch.com/tokens/usage-rewards?page=3"
        driver.get(link)
        wait = ui.WebDriverWait(driver, 10)
        wait.until(page_loaded)

        # Get a date from 25 searches, if it is equal to today's date, we have all daily searches completed
        is_search_date = NodeExists(driver, '//*[@id="main"]/table/tbody/tr[5]/td[1]')
        if not is_search_date:
            return False
        search_date = driver.find_element(By.XPATH, '//*[@id="main"]/table/tbody/tr[5]/td[1]').text
        search_date = search_date[0: search_date.index(' ')]
        today_date = datetime.today().strftime('%Y-%m-%d')
        if search_date == today_date:
            current_pre = driver.find_element(By.XPATH,
                                              '/html/body/div[1]/div/header/div[2]/div[2]/div/div[1]/div/div[1]/div/span[1]').text
            print(email + '-当日任务已完成',current_pre)
            write_today_task_finish(email+":"+current_pre)
            return True
        else:
            return False

    except ValueError as e:
        print(e)
        print("\n\nSomething went wrong!\nPlease re-run the bot to try again")
        return False


def loop_search(email, driver):
    try:
        link = "https://account.presearch.com"
        driver.get(link)
        wait = ui.WebDriverWait(driver, 60)
        wait.until(page_loaded)
        sleep(600)
    except ValueError as e:
        print(e)
        print("\n\nSomething went wrong!\nPlease re-run the bot to try again")
        return


def search(word, driver):
    try:
        search_bar = driver.find_element(By.NAME, "q")
        search_bar.clear()
        search_bar.send_keys(word)
        search_bar.submit()
        return True
    except ValueError as e:
        print(e)
        print("\n\nSomething went wrong!\nPlease re-run the bot to try again")
        return False


# def get_reward_tokens(driver):
#     #Position yourself on the main page of Presearch
#     link = "https://account.presearch.com/"
#     driver.get(link)
#     wait = ui.WebDriverWait(driver, 10)
#     wait.until(page_loaded)
#
#     reward_tokens = driver.find_element(By.XPATH, '//*[@id="main"]/div[2]/div/div[2]/div[2]/a[2]/span/span').text
#     print("\nYou have collected " + reward_tokens + " Usage Reward Tokens.\n\n")


def start(email, driver):
    try:
        checkResult = checkLogin(driver, email)
        # 如果不能用缓存登录，则用cookie试试,记录并直接跳过
        if not checkResult:
            checkResult = login_with_cookies(email, driver)

        if not checkResult:
            print('登录失败,写入刷新文件',email)
            password='zxcvbnm123'
            writeNeedLogin(email, password)
            return

        if checkResult:
            # # It will do the daily searches only if they are not all done yet.
            # day_task = check_day_searchs(email, driver)
            # if not day_task:
            loop_search(email, driver)
            # get_reward_tokens(driver)
        else:
            # if os.path.exists("ExtraFiles//cookies//"+email+"_cookies.pkl"):
            # os.remove("ExtraFiles//cookies//"+email+"_cookies.pkl")
            print("\n\nUnable to login to your Presearch account, please re-run the bot to try to login.")
    except Exception as e:
        print(e)
    finally:
        driver.close()


def login_with_cookies(email, driver):
    try:
        if not os.path.exists("ExtraFiles//cookies//" + email + "_cookies.pkl"):
            return False
        # Apply cookies
        cookies = pickle.load(open("ExtraFiles//cookies//" + email + "_cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        # Position yourself on your Presearch profile page
        driver.get("https://account.presearch.com/")
        wait = ui.WebDriverWait(driver, 5)
        wait.until(page_loaded)
        # Return your login state
        return check_is_logged_in(driver)
    except ValueError as e:
        print(e)
        print("\n\nSomething went wrong!\nPlease re-run the bot to try again")
        return False


def main(global_email):
    print("")
    if global_email == "":
        global_email = "cdcdx888@gmail.com"
    print("开始处理...", global_email)
    t = time.time()
    # 需要5s
    driver = init_browse(global_email);
    print(f'加载driver:{time.time() - t:.8f}s',global_email)
    start(global_email, driver)
    print("")


try:
    global global_email
    global_email = ""
    global global_proxy
    global_proxy = ""
    if len(sys.argv) == 2:
        global_email = sys.argv[1]
    if len(sys.argv) == 3:
        global_email = sys.argv[1]
        global_proxy = sys.argv[2]
    main(global_email)
except ValueError as e:
    print(e)
