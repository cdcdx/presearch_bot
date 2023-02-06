# -*- coding: utf-8 -*-
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
import time
import shutil

def init_browse(email):
    #  Setting up chrome
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    user_data_path = './google-chrome/{}'.format(email)
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


def login(email,password,driver):
    try:
        #Position yourself on the main page of Presearch
        driver.get("https://account.presearch.com/")
        wait = ui.WebDriverWait(driver, 10)
        wait.until(page_loaded)

        #Fill Email
        email_input = driver.find_element(By.XPATH, '//input[@name="email"]')
        email_input.send_keys(email)

        #Fill Password
        password_input = driver.find_element(By.XPATH, '//input[@name="password"]')
        password_input.send_keys(password)

        #Check the "Remember Me" checkbox
        driver.find_element(By.XPATH, '//input[@name="remember"]').click()

        #Open the challenge to prove you're not a robot
        driver.find_element(By.XPATH, '//*[@id="login-form"]/form/div[3]/div[2]/div/iframe').click()

        print('Press Enter after proving you are not a robot: ')
        input()
        #Click in Login button
        driver.find_element(By.XPATH, '//*[@id="login-form"]/form/div[3]/div[3]/button').click()

        #Position yourself on your Presearch profile page
        driver.get("https://account.presearch.com/")
        wait = ui.WebDriverWait(driver, 10)
        wait.until(page_loaded)

        # print("driver.get_cookies()",driver.get_cookies())
        #Save cookies so you don't have to log in again next time
        pickle.dump(driver.get_cookies() , open("ExtraFiles//cookies//"+email+"_cookies.pkl","wb"))

        deleteLoginSuccess(email,password)

        #Return your login state
        return check_is_logged_in(driver)

    except ValueError as e:
        print (e)
        print ("\n\nSomething went wrong!\nPlease re-run the bot to try again")
        return


def check_is_logged_in(driver):
    #Check if you is logged in
    # print(driver.current_url)
    if driver.current_url == "https://account.presearch.com/":
        return True
    return False

def ignore_extended_attributes(func, filename, exc_info):
    is_meta_file = os.path.basename(filename).startswith("._")
    if not (func is os.unlink and is_meta_file):
        raise

def deleteLoginCache(email):
    if os.path.exists("ExtraFiles//cookies//"+email+"_cookies.pkl"):
        os.remove("ExtraFiles//cookies//"+email+"_cookies.pkl")
    if os.path.exists("google-chrome//"+email):
        shutil.rmtree("google-chrome//"+email, onerror=ignore_extended_attributes)


def deleteLoginSuccess(email,password):
    lines = open("ExtraFiles//2-relogin//login_reload.txt","r").readlines()
    f_w = open("ExtraFiles//2-relogin//login_reload.txt","w")
    for line in lines:
        key = email+":"+password
        if key in line:
            continue
        f_w.write(line)
    f_w.close()


accounts_data = open("ExtraFiles//2-relogin//login_reload.txt", "r").readlines()
accounts = {}
for account in accounts_data:
    account_splited = account.split(":", maxsplit=1)
    # Extract Email and Password from accounts.txt
    email = account_splited[0].strip()
    password = account_splited[1].strip()
    if email != "" and password !="":
        print("")
        deleteLoginCache(email)
        print("重新登录...",email,password)
        driver=init_browse(email);
        login(email,password,driver)
        driver.close()
        print("")
