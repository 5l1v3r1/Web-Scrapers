#!/usr/bin/env python

from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from xlsxwriter import Workbook
import os
import requests
import shutil

import math
from tqdm import tqdm
"""
This Instagram Webscraper was designed to run on windows, however, With a little refactoring, It will also run on linux
And Mac OS.
I added tqdm to make the downloading of Images on the command line look nicer with more information about the files.
If you have a slower internet connection, it is useful, otherwise you won't notice much of a difference. : )
"""

# Since my UserName has a space in it, I created a seperate variable to hold the path to
# my Pictures folder, Same goes for the chrome driver executable file because I didn't feel like
# adding the chrome driver to my environment variables path on Windows.

path_to_pictures = os.path.normpath(
    'C:/Users/Phil Miller/Pictures/InstaScraper')

path_to_chrome_driver = os.path.normpath(
    'C:/Users/Phil Miller/Downloads/chromedriver')

# Add your USERNAME and Password in the __init__ function,
# Target profile is the profile that you would like to scrape / download images from


class App:
    def __init__(
            self,
            username='USERNAME-GOES-HERE',
            password='YOUR-PASSWORD-GOES-HERE',
            target_username='USERNAME-TO-SCRAPE/DOWNLOAD-IMAGES-GOES-HERE',
            path=path_to_pictures):
        self.username = username
        self.password = password
        self.target_username = target_username
        self.path = path
        self.driver = webdriver.Chrome(path_to_chrome_driver)
        self.main_url = 'https://www.instagram.com'
        self.driver.get(self.main_url)
        self.error = False
        sleep(1)
        # Write login function
        self.log_in()
        if self.error is False:
            self.close_pop_up()
            self.open_target_profile()
        if self.error is False:
            self.scroll_down()
        if self.error is False:
            if not os.path.exists(path):
                os.mkdir(path)
            self.downloading_images()
        sleep(100)
        self.driver.close()

# This function will write all scraped captions to an excel file for their corresponding image

    def write_captions_to_excel_file(self, images, caption_path):
        print('writing to excel')
        workbook = Workbook(os.path.join(caption_path, 'captions.xlsx'))
        worksheet = workbook.add_worksheet()
        row = 0
        worksheet.write(row, 0,
                        'Image name')  # 3 --> row number, column number, value
        worksheet.write(row, 1, 'Caption')
        row += 1
        for index, image in enumerate(images):
            filename = 'image_' + str(index) + '.jpg'
            try:
                caption = image['alt']
            except KeyError:
                caption = 'No caption exists'
            worksheet.write(row, 0, filename)
            worksheet.write(row, 1, caption)
            row += 1
        workbook.close()

# This function will create a folder and download captions that will be used in an xlsx excel file

    def download_captions(self, images):
        captions_folder_path = os.path.join(self.path, 'captions')
        if not os.path.exists(captions_folder_path):
            os.mkdir(captions_folder_path)
        self.write_captions_to_excel_file(images, captions_folder_path)
        '''for index, image in enumerate(images):
            try:
                caption = image['alt']
            except KeyError:
                caption = 'No caption exists for this image'
            file_name = 'caption_' + str(index) + '.txt'
            file_path = os.path.join(captions_folder_path, file_name)
            link = image['src']
            with open(file_path, 'wb') as file:
                file.write(str('link:' + str(link) + '\n' + 'caption:' + caption).encode())'''

# This function will download 33 images from the target profile, starting with the oldest posts
# The Instagram developers lowered the amount of data that can be scraped from the site I believe, otherwise,
# Theoretically, this function should download all images from the target profile

    def downloading_images(self):
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        all_images = soup.find_all('img')
        self.download_captions(all_images)
        print('Length of all images', len(all_images))

        for index, image in enumerate(all_images):
            filename = 'image_' + str(index) + '.jpg'
            image_path = os.path.join(self.path, filename)
            link = image['src']
            print('[+] Downloading image', index)
            response = requests.get(link, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            wrote = 0
            try:
                with open(image_path, 'wb') as fd:
                    for data in tqdm(
                            response.iter_content(block_size),
                            total=math.ceil(total_size // block_size),
                            unit='B',
                            unit_scale=True):
                        wrote = wrote + len(data)
                        fd.write(data)
                if total_size != 0 and wrote != total_size:
                    print("ERROR, something went wrong")
            except Exception as e:
                print(e)
                print('Could not download image number ', index)
                print('Image link [+] ', link)

# This function will go into the search bar and look up which ever user that you specified in target profile variable

    def open_target_profile(self):
        try:
            search_bar = self.driver.find_element_by_xpath(
                '//input[@class="XTCLo x3qfX "]')
            search_bar.send_keys(self.target_username)
            target_profile_url = self.main_url + '/' + self.target_username + '/'
            self.driver.get(target_profile_url)
            sleep(3)
        except Exception:
            self.error = True
            print('Could not find search bar')

# Must scroll down to find the number of posts...

    def scroll_down(self):
        try:
            no_of_posts = self.driver.find_element_by_xpath(
                '//span[text()=" posts"]').text
            no_of_posts = no_of_posts.replace(' posts', '')
            no_of_posts = str(no_of_posts).replace(',', '')  # Number of posts
            self.no_of_posts = int(no_of_posts)
            if self.no_of_posts > 12:
                no_of_scrolls = int(self.no_of_posts / 12) + 3
                try:
                    for _ in range(no_of_scrolls):
                        self.driver.execute_script(
                            'window.scrollTo(0, document.body.scrollHeight);')
                        sleep(1)
                except Exception as e:

                    self.error = True
                    print(e)
                    print('Some error occurred while trying to scroll down')
            sleep(2)
        except Exception:
            print('Could not find number of posts while trying to scroll down')
            self.error = True

# This function closes the annoying pop up when you sign in with chrome

    def close_pop_up(self):
        try:
            sleep(3)
            not_now = self.driver.find_element_by_xpath(
                "//div[@class='mt3GC']//button[@class='aOOlW   HoLwm ']")
            sleep(3)
            not_now.click()
            sleep(1)
        except Exception:
            print("Something went wrong :( ")
            self.error = True


# This function will login in to your user account

    def log_in(self):
        try:
            login_button = self.driver.find_element_by_xpath(
                "//span[@id='react-root']//p[@class='izU2O']/a")

            login_button.click()
            sleep(2)
        except Exception:
            self.error = True
            print('Could not find the login button')
        else:
            try:
                user_name_input = self.driver.find_element_by_xpath(
                    "//span[@id='react-root']//input[@name='username']")
                password_input = self.driver.find_element_by_xpath(
                    "//span[@id='react-root']//input[@name='password']")
                user_name_input.send_keys(self.username)
                password_input.send_keys(self.password)
                submit_button = self.driver.find_element_by_xpath(
                    "//span[@id='react-root']//button[@class='_0mzm- sqdOP  L3NKy       ']"
                )
                submit_button.submit()
            except Exception:
                print("Couldn't login :( ")
                self.error = True

if __name__ == '__main__':
    app = App()