# -*- coding: utf-8 -*-
import shutil

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import ui
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService, Service
from webdriver_manager.chrome import ChromeDriverManager
from configuration import config
from datetime import datetime
from time import sleep
import random
import os
import pickle
from shutil import copyfile
from random_words import RandomWords
word_generator = RandomWords()


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
    # driver.maximize_window()
    driver.set_window_size(1024,768)
    return driver


def page_loaded(driver):
	return driver.find_element(By.TAG_NAME, 'body') != None


def reg(email,password,driver):
    try:
        #Fill Email

        email_input = driver.find_element(By.XPATH, '//*[@id="register-form"]/div[1]/form/div[1]/input')
        email_input.send_keys(email)

        #Fill Password
        password_input = driver.find_element(By.XPATH, '//*[@id="register-form"]/div[1]/form/div[2]/input')
        password_input.send_keys(password)

        password_confirmation = driver.find_element(By.XPATH, '//*[@id="password-confirm"]')
        password_confirmation.send_keys(password)

        #Check the "Remember Me" checkbox
        driver.find_element(By.XPATH, '//*[@id="register-form"]/div[1]/form/div[4]/label/input').click()

        #Open the challenge to prove you're not a robot
        driver.find_element(By.XPATH, '//*[@id="register-form"]/div[1]/form/div[5]/div/iframe').click()

        print('Press Enter after proving you are not a robot: ')
        input()
        #Click in Login button
        driver.find_element(By.XPATH, '//*[@id="register-form"]/div[1]/form/div[6]/button').click()
        sleep(5)
        #Position yourself on your Presearch profile page
        driver.get("https://account.presearch.com/")
        wait = ui.WebDriverWait(driver, 10)
        wait.until(page_loaded)

        #Save cookies so you don't have to log in again next time
        pickle.dump(driver.get_cookies() , open("ExtraFiles//cookies//"+email+"_cookies.pkl","wb"))

        #Return your login state
        return check_is_logged_in(driver)

    except ValueError as e:
        print (e)
        print ("\n\nSomething went wrong!\nPlease re-run the bot to try again")
        return False


def NodeExists(driver,xpath):
    try:
        driver.find_element(By.XPATH,xpath)
        return True
    except:
        return False


#开通邀请并生成随机名
def referral(email,driver):
    #开通邀请
    driver.get("https://account.presearch.com/referral-terms")
    if NodeExists(driver,'//*[@id="main"]/div[2]/form/div/label/input'):
        driver.find_element(By.XPATH,'//*[@id="main"]/div[2]/form/div/label/input').click()
        driver.find_element(By.XPATH, '//*[@id="main"]/div[2]/form/button').click()
        sleep(3)
    #获取ID并生成随机名
    driver.get("https://account.presearch.com/referrals")
    sleep(3)
    referral_link = driver.find_element(By.XPATH, '//*[@id="beta-ref"]').text
    start = referral_link.find("=")+1
    parentId = referral_link[start::]

    file = open('ExtraFiles//0-reg-mail//{}={}_{}.txt'.format(email,parentId,word_generator.random_word().strip()), 'w')
    file.close()


def check_is_logged_in(driver):
    #Check if you is logged in
    # print(driver.current_url)
    if driver.current_url == "https://account.presearch.com/":
        return True
    return False


def check_reg_status(email):
    path = "ExtraFiles//3-task//accounts.txt"
    if not os.path.exists(path):
        return False
    today_finish = open(path, "r").readlines()
    for t in today_finish:
        if t.startswith(email):
            return True
    return False


def writeLoginSuccess(parentId,email,password):
    f = open("ExtraFiles//3-task//accounts.txt", "a+")
    f.write("{}:{}\n".format(email, password))
    f.close()
    # lines = open("ExtraFiles//1-reg-presearch//*"+parentId+"*.txt","r").readlines()
    # f_w = open("ExtraFiles//1-reg-presearch//*"+parentId+"*.txt","w")
    # for line in lines:
    #     key = email+":"+password
    #     if key in line:
    #         continue
    #     f_w.write(line)
    # f_w.close()


def register(driver,parentId,email,password):
    link = "https://presearch.com/signup?rid={}".format(parentId)
    driver.get(link)
    wait = ui.WebDriverWait(driver, 10)
    wait.until(page_loaded)
    #Join_Presearch
    driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/div/a').click()
    wait = ui.WebDriverWait(driver, 5)
    wait.until(page_loaded)
    return reg(email,password,driver)


def regByfile(filename):
    start = filename.find("=")
    end = filename.find("_")
    parentId = filename[start + 1:end]

    accounts_data = open(filename, "r").readlines()
    for account in accounts_data:
        account_splited = account.split(":", maxsplit=1)
        # Extract Email and Password from accounts.txt
        email = account_splited[0].strip()
        password = account_splited[1].strip()
        if email != "" and password != "" and check_reg_status(email) == False :
            print("")
            print("开始注册...",email,password)
            driver=init_browse(email)
            isRegister=register(driver,parentId,email,password)
            print("注册状态...",isRegister)
            if isRegister:
                referral(email, driver)
            writeLoginSuccess(parentId,email,password)
            driver.close()
            print("")


root='ExtraFiles//1-reg-presearch/'
for fl in os.listdir(root):
    flpath=os.path.join(root,fl)
    regByfile(flpath)
    #拷文件到task
    shutil.move(flpath,"ExtraFiles//3-task//"+fl)
