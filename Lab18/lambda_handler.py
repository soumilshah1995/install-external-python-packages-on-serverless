try:
    import json

    import os
    import shutil
    import uuid


    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver import Chrome

    import base64
    import datetime
    from dateutil.parser import parse
    from datetime import datetime, timedelta
    from dateutil.tz import tzutc
    from time import sleep
    from enum import Enum
    import hashlib

    print("All Modules are ok ...")

except Exception as e:

    print("Error in Imports ")



class WebDriver(object):

    def __init__(self):
        self.options = Options()

        self.options.binary_location = '/opt/headless-chromium'
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--start-maximized')
        self.options.add_argument('--start-fullscreen')
        self.options.add_argument('--single-process')
        self.options.add_argument('--disable-dev-shm-usage')

    def get(self):
        driver = Chrome('/opt/chromedriver', options=self.options)
        return driver



class Hasher(object):
    def __init__(self) -> None:
        pass

    def get_hash(self, data):
        """
        Returns the Hash for any data
        :return string
        """
        return hashlib.md5(repr(data).encode("UTF-8")).hexdigest().__str__()



class PaginationScrollBottom(object):
    """
        {
            "sleep_interval_time_between_pagination":2
        }
    """

    def __init__(
            self, driver, sleep_interval_time_between_pagination, max_iteration=500
    ):
        self.driver = driver
        self.sleep_interval_time_between_pagination = (
            sleep_interval_time_between_pagination
        )
        self.max_iteration = max_iteration
        self.last_height = self.driver.execute_script(
            "return document.body.scrollHeight"
        )

    def paginate(self):

        for i in range(0, self.max_iteration):

            # Scroll down to bottom
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            # Wait to load page
            sleep(self.sleep_interval_time_between_pagination)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height == self.last_height:
                break

            self.last_height = new_height

        html = self.driver.page_source

        return html


class PaginationClickAndScroll(object):

    """
        {
            "commands":[
                     {
                         "selector":"xpath",
                         "path":"/html/body/div[1]/div/form/div[1]/div/input",
                         "command":"type",
                         "search":"software Engineer"
                      },
                      {
                         "command":"sleep",
                         "time":"1"
                      },
                      {
                         "selector":"xpath",
                         "path":"//html/body/div[1]/div/form/button",
                         "command":"click"
                      },
                      {
                         "command":"scroll_bottom",
                          "sleep_interval_time_between_pagination":2
                      }
               ]
        }
    """

    def __init__(self, driver, jsonaction, max_iteration=500):
        self.driver = driver
        self.jsonaction = jsonaction
        self.max_iteration = max_iteration
        self.last_height = self.driver.execute_script(
            "return document.body.scrollHeight"
        )

    def paginate(self):
        try:
            commands = self.jsonaction.get("commands", [])
            _commands = Commands(driver=self.driver, commands=commands)
            response = _commands.execute()
            return True
        except Exception as e:
            return False


class Commands(object):

    """
    {
         "commands":[
             {
                 "selector":"xpath",
                 "path":"/html/body/div[1]/div/form/div[1]/div/input",
                 "command":"type",
                 "search":"software Engineer"
              },
              {
                 "command":"sleep",
                 "time":"1"
              },
              {
                 "selector":"xpath",
                 "path":"//html/body/div[1]/div/form/button",
                 "command":"click"
              },
               {
                "command":"scroll_bottom",
                "sleep_interval_time_between_pagination":2
               }
       ]
   }
    """

    def __init__(self, driver, commands):

        self.driver = driver
        self.commands = commands

    def execute(self):

        if self.commands is not None:

            for command in self.commands:

                try:
                    if command.get("command").lower() == "sleep":
                        sleep(command.get("time", 0))

                    if command.get("command").lower() == "click":

                        if command.get("selector").lower() == "xpath":
                            try:
                                self.driver.find_element_by_xpath(
                                    command.get("path")
                                ).click()
                            except Exception as e:
                                print("Click error ", e)
                                raise Exception ("error")

                        if command.get("selector").lower() == "id":
                            try:
                                self.driver.find_element_by_id(
                                    command.get("path")
                                ).click()
                            except Exception as e:
                                raise Exception ("error")

                    if command.get("command").lower() == "type":

                        if command.get("selector").lower() == "xpath":
                            try:
                                self.driver.find_element_by_xpath(
                                    command.get("path")
                                ).send_keys(command.get("search"))
                            except Exception as e:
                                print("error: {}".format(e))

                        if command.get("selector") == "id":
                            try:
                                self.driver.find_element_by_xpath(
                                    command.get("path")
                                ).send_keys(command.get("search"))
                            except Exception as e:
                                pass

                    if command.get("command").lower() == "scroll_bottom":
                        _helper = PaginationScrollBottom(
                            driver=self.driver,
                            sleep_interval_time_between_pagination=command.get(
                                "sleep_interval_time_between_pagination", 2
                            ),
                        )
                        _helper.paginate()

                except Exception as e:pass


class WindowTracker(Enum):
    MAIN_WINDOW = 0
    TAB_WINDOW = 1


def get_page_data(driver, PARENT, LOOP, xp_name, xp_review, xp_text):

    data = []

    parent_element = driver.find_element_by_xpath(PARENT)         # get the Parent
    loop_element = parent_element.find_elements_by_xpath(LOOP)    # [xx1, xx2, xx3 ........]
    sleep(4)
    hasher = Hasher()

    for item in loop_element:

        _data = {}

        try:
            _data["name"] = item.find_element_by_xpath(xp_name).text.strip()
        except Exception as e:
            pass

        review_data = item.find_element_by_xpath(xp_review).text

        try:
            _data["review_date"] = review_data.split("Degree")[0].split("Reviewed:")[1]
        except Exception as e:
            pass

        try:
            _data["review_major"] = review_data.split("Year:")[0].split("Degree:")[1]
        except Exception as e:
            pass

        try:
            _data["review_major"] = review_data.split("Year:")[1]
        except Exception as e:
            pass

        try:
            _data["review_text"] = item.find_element_by_xpath(xp_text).text
        except Exception as e:
            pass

        hash_key= hasher.get_hash(data=_data)
        _data["review_hash_key"] = hash_key

        data.append(_data)
        print(_data)

    return data


def start_scrape(url, id, name):

    # ============================================================
    PARENT = """html/body/div[@id='under_splash']/main/div[@class='review__page']/div[@class='fixed-width mdc-layout-grid']"""
    LOOP = """.//school-review-list[@id='reviews']/div[@class='reviews']/div[@class='reviews__item']"""
    xp_name = """.//div[@class='reviews__text--name']"""
    xp_review = ".//div[@class='mdc-layout-grid__inner reviews__item--inner']/div[@class]/ul[@class='reviews__details']"
    xp_text = ".//div[@class='reviews__text']"

    # =============================================================

    # path = os.path.join(os.getcwd(), "chromedriver.exe")
    # driver_ = WebDriver(path=path)
    # driver = driver_.get(headless=False)

    instance_ = WebDriver()
    driver = instance_.get()

    driver.get(url)
    sleep(2)

    commands = [{"command": "scroll_bottom", "sleep_interval_time_between_pagination": 2},]
    commands = Commands(commands=commands, driver=driver)
    commands.execute()
    sleep(3)

    global_data = []

    for i in range(1, 100):
        try:
            url_ = "{}/?page={}".format(url, i)
            driver.get(url_)
            sleep(2)

            try:
                parent_nav = driver.find_element_by_xpath(""".//nav[@class='pagination text--centered']""")

                if str(i) in parent_nav.text:
                    print("Valid page : {} ".format(i))
                    sleep(2)
                    data = get_page_data( driver=driver,PARENT=PARENT ,LOOP=LOOP, xp_name=xp_name, xp_review=xp_review, xp_text=xp_text)
                    for x in data:
                        global_data.append(x)

            except Exception as e:

                if i==1:
                    data = get_page_data( driver=driver,PARENT=PARENT ,LOOP=LOOP, xp_name=xp_name, xp_review=xp_review, xp_text=xp_text)
                    for x in data:
                        global_data.append(x)

            break

        except Exception as e:
            print("Complete", e)
            break

    if global_data != []:

        _ = {
            "id":id,
            "name":name,
            "reviews":global_data,
            "total_reviews" : len(global_data),
            "ingestion_date":datetime.now().__str__()

        }

    driver.quit()

    return global_data


def lambda_handler(event, context):
    print("In...")
    url = "https://www.gradreports.com/colleges/stanford-university"
    response = start_scrape(url=url, id="121", name="stanford")
    print(response)
    return True
