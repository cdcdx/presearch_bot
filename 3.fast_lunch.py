# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import ui
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService, Service
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor
import threading
from configuration import config
from datetime import datetime
from time import sleep
import random
import os
import pickle
import time
# 全局锁
mutex = threading.Lock()
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

    pwd = os.getcwd()
    user_data_path = pwd + './/google-chrome//{}'.format(email)
    profile_name = "Profile " + str(config["profile_number"])

    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
    options.add_argument('--user-data-dir=' + user_data_path)
    options.add_argument('--profile-directory=' + profile_name)
    # options.add_argument('--proxy-server=http://127.0.0.1:10809')
    options.add_argument('--proxy-server=' + config['https_proxy'])

    # 浏览器不提供可视化界面。Linux下如果系统不支持可视化不加这条会启动失败
    # options.add_argument('--headless')

    # driver = webdriver.Chrome('./chromedriver', options=options)
    # service=Service(r'./chromedriver.exe')
    # driver = webdriver.Chrome(service=service, options=options)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    driver.execute_script('return navigator.userAgent')
    # 最大等待10s
    driver.set_page_load_timeout(10)
    driver.set_script_timeout(10)
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


def deleteLoginCache(email):
    if os.path.exists("ExtraFiles//cookies//"+email+"_cookies.pkl"):
        os.remove("ExtraFiles//cookies//"+email+"_cookies.pkl")
    if os.path.exists("google-chrome//"+email):
        shutil.rmtree("google-chrome//"+email)


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


def check_local_login(email):
    if not os.path.exists("ExtraFiles//cookies//"+email+"_cookies.pkl"):
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
            # Get a word and search for it
            word = word_generator.random_word().strip()
            link = "https://engine.presearch.org/search?q=" + word
            driver.get(link)
            return False

    except ValueError as e:
        print(e)
        print("\n\nSomething went wrong!\nPlease re-run the bot to try again")
        return False


def loop_search(email, driver):
    try:
        word = word_generator.random_word().strip()
        # Get a word and search for it
        # link = "https://engine.presearch.org/search?q=" + random.choice(words).strip()
        link = "https://engine.presearch.org/search?q=" + word
        driver.get(link)

        # Search for words randomly or in order in the file.
        if config["random"]:
            for i in range(0, config["searches_count"]):
                word = word_generator.random_word().strip()
                search_result = search(word, driver)
                i_2 = '%02d' % i
                print(email, "search", str(i_2), "->", word, "=>", str(search_result))
                # if not search_result:
                #     return
                # sleep(random.randint(3, config["delay"]))
                sleep(max(config["delay"], 3))

                if i%5 == 1:
                    # It will do the daily searches only if they are not all done yet.
                    day_task = check_day_searchs(email, driver)
                    if day_task:
                        break
        else:
            for word in words:
                word = word.strip()
                if not search(word, driver):
                    return
                print("search", word)
                # sleep(random.randint(3, config["delay"]))
                sleep(max(config["delay"], 3))
        
        # check_day_searchs(email, driver)

        print("\n\nAll surveys have been completed!\nIf you didn't get the maximum daily reward, run the bot again.")
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
        # sleep(random.randint(3, config["delay"]))
        sleep(max(config["delay"], 3))
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


def start(email, password, driver):
    try:
        checkResult = checkLogin(driver, email)
        # 如果不能用缓存登录，则用cookie试试,记录并直接跳过
        if not checkResult:
            checkResult = login_with_cookies(email, driver)

        if not checkResult:
            print('登录失败,写入刷新文件',email)
            writeNeedLogin(email, password)
            deleteLoginCache(email)
            return

        if checkResult:
            # It will do the daily searches only if they are not all done yet.
            day_task = check_day_searchs(email, driver)
            if not day_task:
                loop_search(email, driver)
            # get_reward_tokens(driver)
        else:
            # if os.path.exists("ExtraFiles//cookies//"+email+"_cookies.pkl"):
            #     os.remove("ExtraFiles//cookies//"+email+"_cookies.pkl")
            # if os.path.exists("google-chrome//"+email):
            #     shutil.rmtree("google-chrome//"+email)
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


def start_thread(email, password):
    print("")
    print("开始处理...", email, password)
    t = time.time()
    # 需要5s
    driver = init_browse(email);
    print(f'加载driver:{time.time() - t:.8f}s',email)
    start(email, password, driver)
    print("")


def job_function():
    mutex.acquire() # 上锁
    pool = ThreadPoolExecutor(max_workers=1)
    root = "ExtraFiles//3-task//"
    for fl in os.listdir(root):
        accounts_data = open(os.path.join(root, fl), "r").readlines()
        for account in accounts_data:
            account_splited = account.split(":", maxsplit=1)
            # Extract Email and Password from accounts.txt
            password = account_splited[1].strip()
            email = account_splited[0].strip()
            if check_local_login(email):
                continue
            if check_local_today_task(email):
                continue
            if email != "" and password != "":
                pool.submit(start_thread, email, password)
    mutex.release() # 释放锁


def main():
    # # 立即启动
    # job_function()
    pool1 = ThreadPoolExecutor(max_workers=1)
    pool1.submit(job_function)
    # # 定时启动
    # BlockingScheduler
    scheduler = BlockingScheduler()
    # Schedule job_function to be called every two hours
    scheduler.add_job(job_function, 'interval', hours=1)
    scheduler.start()

try:
    main()
except ValueError as e:
    print(e)
