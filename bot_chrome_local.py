import logging
from time import sleep
from pytz import timezone

from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from random import randint

import follow_data as fd


def configure_chrome_driver():
    """""This creates and saves the Chrome Engine and Driver so it can be reused,
    chromedriver file permissions might have to be reupdated"""
    options = webdriver.ChromeOptions()

    # initiates device and sets server
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/92.0.4515.43 Safari/537.36")

    # options.add_argument("--headless")
    options.add_argument("window-size=1300, 750")

    the_driver = webdriver.Chrome(executable_path="chromedrivers/chromedriver-mac",
                                  options=options)

    # page loading time and wait time for page reload
    try:
        the_driver.set_page_load_timeout(100)
    except TimeoutException:
        print("Timed out, gonna refresh")
        the_driver.refresh()
    the_driver.implicitly_wait(200)
    print("ChromeDriver successfully configured")
    return the_driver


logger = logging.getLogger()


class InstagramBot:
    """This bot uses selenium to like posts, watch stories,
    filter out people based on mutuals, and follower count, and follow and
    unfollow people. It does so in a consistency undetectable by instagram"""

    def __init__(self, driver=configure_chrome_driver()):

        # attribute of driver is from configured driver method (WebDriver Object)
        self.driver = driver
        self.valid = True

    def log_in(self):
        username = input("Enter a username: ")
        password = input("Enter a password: ")

        self.driver.get("https://www.instagram.com/")

        sleep(5)

        # waits until login part shows
        try:
            WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.NAME, 'username')))

            # send login info from config file
            try:
                self.driver.find_element_by_name('username').send_keys(username)
                sleep(1)
                self.driver.find_element_by_name('password').send_keys(password)
                sleep(1)
                self.driver.find_element_by_xpath("//button[@type='submit']").click()

            except (NoSuchElementException, ElementClickInterceptedException) as e:
                logger.warning(f"Could not find element. Error: {e}")
                return

        # logged in already, skipped login page
        except TimeoutException:
            print("Logged in already")
            pass

        sleep(randint(5, 8))

        # post-login stuff, may or may not appear
        try:
            # remember this browser prompt
            # dont remember prompt = yWX7d
            self.driver.find_element_by_class_name(
                'sqdOP L3NKy    y3zKF     ').click()

        except NoSuchElementException:
            pass

        try:
            # turn off notifications
            self.driver.find_element_by_class_name("aOOlW   HoLwm ").click()
            logger.debug("Skipping turn on notifications")
        except NoSuchElementException:
            pass

        sleep(6)
        # home page
        try:
            self.driver.find_element_by_xpath(f'//a[@href="/"]').click()
        except NoSuchElementException:
            print("cant get home button, problem logging in")
            exit()
        sleep(randint(5, 8))

        print("Successfully logged in")

    def search_user(self, user):

        # type in user's name
        try:
            search_bar = WebDriverWait(self.driver, 20).until(
                ec.visibility_of_element_located(
                    (By.XPATH, "//input[@placeholder='Search']")
                )
            )
        except TimeoutException:
            print("cant find search bar")
            search_bar = self.driver.find_element_by_class_name("XTCLo x3qfX")
            sleep(5)
            search_bar.send_keys(f"@{user}")
        else:
            search_bar.send_keys(f"@{user}")
        sleep(5)

        # clicks first name that pops up in search
        # usually first name is exact match to name typed
        try:
            search_button = self.driver.find_element_by_xpath(f'//a[@href="/{user}/"]')
        except NoSuchElementException:
            try:
                search_button = self.driver.find_element_by_class_name("-qQT3")

            # user changed name, so OG name doesnt exist, backspace name and get new user
            except NoSuchElementException:
                sleep(randint(3, 5))
                search_bar.send_keys(Keys.COMMAND, "a")
                search_bar.send_keys(Keys.BACKSPACE)
                sleep(randint(3, 5))
                self.valid = False
            else:
                try:
                    search_button.click()
                except ElementClickInterceptedException:
                    self.driver.execute_script('arguments[0].click();', search_button)
        else:
            try:
                search_button.click()
            except ElementClickInterceptedException:
                self.driver.execute_script('arguments[0].click();', search_button)

        sleep(randint(8, 12))

    def filter_followers(self, amount=25):
        """returns users who satisfy certain conditions"""
        # if using this to scrape, randomize actions in beginning and end

        # ppl will be added to this list if they satisfy requirements
        lst_to_follow = []

        lst_to_filter = fd.get_list_to_filter(amount)

        # index is for remembering spot in list
        # loop thru gathered followers
        for index, value in enumerate(lst_to_filter):

            self.search_user(value)
            if self.valid:

                # check user follower count
                try:
                    followers = self.driver.find_element_by_xpath(
                        '// * [ @ id="react-root"] / section / main / div / header / section / ul '
                        '/ li[2] / span / span')

                except NoSuchElementException:
                    try:
                        followers = self.driver.find_element_by_xpath(
                            '// *[ @ id = "react-root"] / section / main / div / header / section / ul / li[2] / a / '
                            'span')

                    except NoSuchElementException:
                        try:
                            numbers_list = self.driver.find_elements_by_class_name("g47SY ")
                            followers = ""
                            for i in numbers_list:  # 3 elements have class above, followers is only class with title
                                if bool(i.get_attribute("title")):
                                    followers = i
                                    break
                        except NoSuchElementException:
                            print("Cant get amount of followers")
                            continue
                        else:
                            followers = int(followers.get_attribute("title").replace(",", ""))
                    else:
                        followers = int(followers.get_attribute("title").replace(",", ""))
                else:
                    followers = int(followers.get_attribute("title").replace(",", ""))

                sleep(randint(5, 8))
                if followers >= 400:
                    sleep(randint(4, 8))

                    # check how many mutual followers me and the user have
                    try:
                        mutual_line = self.driver.find_element_by_class_name("tc8A9").text

                    except NoSuchElementException:
                        sleep(randint(3, 5))
                        print(f"No mutuals for {value}")
                        continue

                    else:
                        if mutual_line and "+" in mutual_line:
                            mutual_line = mutual_line.split("+")
                            mutuals = int(mutual_line[1].replace(" more", ""))
                        else:
                            print(f"not enough mutuals for {value}")
                            continue

                    sleep(randint(5, 8))
                    if mutuals >= 10:
                        # check if says anything but follow (already following or follow back)

                        try:
                            follow_button = self.driver.find_elements_by_tag_name("button")

                        except NoSuchElementException:
                            print("No follow button")
                        else:
                            for j in follow_button:
                                if j.text == "Follow":
                                    lst_to_follow.append(value)
                                    with open("text_files/to_follow",
                                              "a") as f:
                                        f.write(f"{value}\n")
                                    print(value)
                                    sleep(3)
                                    break
                                else:
                                    continue
                    else:
                        sleep(randint(3, 5))
                        print(f"not enough mutuals for {value}")
                        continue
                else:
                    sleep(randint(3, 5))
                    print(f"not enough followers for {value}")
                    continue
                sleep(randint(10, 20))
            else:
                print("Not a valid user")
                continue

        print(lst_to_follow)
        sleep(randint(2, 4))

        return lst_to_follow

    def like_posts(self):
        sleep(5)

        try:
            self.driver.find_element_by_xpath(f'//a[@href="/"]').click()
        except NoSuchElementException:
            print("cant get home button")

        sleep(3)

        # how many posts to like
        number = randint(1, 7)
        able_to_like = True

        for i in range(1, number + 1):

            try:
                button = self.driver.find_element_by_xpath(
                    f'//*[@id="react-root"]/section/main/section/div/div[2]/div/article[{i}]/div[3]/section[1]/span['
                    f'1]/button')
                sleep(randint(3, 6))
            except NoSuchElementException:
                print(f"cant locate post {i}, trying again")
                sleep(1)
                try:
                    button = self.driver.find_element_by_xpath(
                        f'// *[ @ id = "react-root"] / section / main / section / div[1] / div[2] / div / article[{i}] '
                        f'/div[3] / section[1] / span[1] / button')
                except NoSuchElementException:
                    self.driver.find_element_by_xpath(f'//a[@href="/"]').click()
                    sleep(5)
                    print(f"Unable to locate post {i} again")
                    able_to_like = False
                    break
                else:
                    button.click()
                    sleep(5)
            else:
                button.click()
                sleep(5)
        if not able_to_like:
            # alternative way to like, likes up to four pics
            pics = self.driver.find_elements_by_css_selector('[aria-label="Like"][height="24"]')
            print(len(pics))
            for i in pics[:randint(1, len(pics) + 1)]:
                i.click()

    def watch_stories(self):
        sleep(5)
        try:
            self.driver.find_element_by_xpath(f'//a[@href="/"]').click()
        except NoSuchElementException:
            print("cant get home button")

        sleep(5)

        self.driver.find_element_by_tag_name('body').send_keys(Keys.HOME)
        sleep(5)
        try:
            story = self.driver.find_element_by_css_selector(".OE3OK ")
        except NoSuchElementException:
            print("cant find stories, trying again")
            try:
                story = self.driver.find_element_by_class_name("OE3OK ")
            except NoSuchElementException:
                print("cant find stories at all")
            else:
                sleep(5)
                story.click()
        else:
            sleep(5)
            story.click()

        # random time "viewing stories"
        sleep(randint(20, 125))

        # exits full-screen stories
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

    def suggested(self):
        # only do this locally because its a one time action
        # suggested list doesnt get updated
        """gets entire suggested page as a list and filters then adds to 'to_follow' file.
        manually go thru suggested wack heads (fit pages, finstas, etc.) put in ppl_to_avoid"""

        lst_of_suggested = []
        sleep(5)
        try:
            side_button = WebDriverWait(self.driver, 15).until(
                ec.visibility_of_element_located(
                    (By.XPATH, '//a[@href="/explore/people/"]')))
        except NoSuchElementException:
            print("Unable to get suggested page")

        else:
            sleep(3)
            side_button.click()
            sleep(10)

        # scrolls to very bottom of page, allows entire screen to be scraped
        for i in range(3):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(3)
        sleep(4)

        try:
            lst_of_heads = self.driver.find_elements_by_css_selector("a.FPmhX.notranslate.MBL3Z")
            sleep(5)

        except NoSuchElementException:
            print("Unable to get list of suggested")
        else:
            for i in lst_of_heads:
                lst_of_suggested.append(f'{i.get_attribute("title")}\n')

        sleep(5)

        # compares newly suggested people to registered people
        set_of_suggested = set(lst_of_suggested)
        set_to_compare = set(fd.get_list_of_everyone())
        same_in_both = set_of_suggested.intersection(set_to_compare)
        for i in same_in_both:
            lst_of_suggested.remove(i)
        for j in lst_of_suggested:
            with open("to_follow", "a") as f:
                f.write(j)

        print(f'Suggested list: {lst_of_suggested}')
        sleep(3)
        return lst_of_suggested

    def follow_ppl(self):
        lst = fd.get_list_to_follow()
        for user in lst:
            self.search_user(user)
            if self.valid:
                sleep(7)
                try:
                    follow_button = self.driver.find_element_by_xpath("//button[text()='Follow' and @type='button']")
                except NoSuchElementException:
                    print("cant locate follow button")
                    sleep(5)
                    try:
                        buttons = self.driver.find_elements_by_tag_name("button")

                    except NoSuchElementException:
                        print("No follow button")
                    else:
                        for button in buttons:
                            if button.text == "Follow":
                                sleep(randint(3, 5))
                                # noinspection PyTypeChecker
                                self.driver.execute_script("arguments[0].click();", button)
                                print(f"Followed {user}")
                                sleep(randint(3, 5))
                                break
                            else:
                                continue
                else:
                    sleep(randint(3, 5))
                    # noinspection PyTypeChecker
                    self.driver.execute_script("arguments[0].click();", follow_button)
                    print(f"Followed {user}")
                    sleep(randint(3, 5))
            else:
                sleep(randint(2, 5))
                print(f"Cant locate {user}")
                continue
        fd.convert_follow_to_avoid(lst)

    def unfollow_ppl(self):
        lst = fd.get_list_to_unfollow()
        for user in lst:
            self.search_user(user)
            if self.valid:
                sleep(7)
                try:
                    following = self.driver.find_element_by_css_selector("[aria-label=Following]")
                except NoSuchElementException:
                    try:
                        following = self.driver.find_element_by_class_name("glyphsSpriteFriend_Follow u-__7")
                    except NoSuchElementException:
                        try:
                            following = self.driver.find_element_by_class_name("5f5mN -fzfL _6VtSN yZn4P ")
                        except NoSuchElementException:
                            try:
                                following = self.driver.find_element_by_xpath(
                                    '//*[@id="react-root"]/section/main/div/header/section'
                                    '/div[1]/div[1]/div/div[2]/div/span/span[1]/button')
                            except NoSuchElementException:
                                print(f"Cant find unfollow button for {user}")
                            else:
                                following.click()
                                print(f"Unfollowing {user}")
                        else:
                            following.click()
                            print(f"Unfollowing {user}")
                    else:
                        following.click()
                        print(f"Unfollowing {user}")
                else:
                    following.click()
                    print(f"Unfollowing {user}")
                sleep(3)
                try:
                    confirm_unfollow = self.driver.find_element_by_xpath('//button[text()="Unfollow"]')
                except NoSuchElementException:
                    try:
                        confirm_unfollow = self.driver.find_element_by_class_name("OOlW -Cab_ ")
                    except NoSuchElementException:
                        print(f"Unable to confirm unfollow for {user}")
                    else:
                        confirm_unfollow.click()
                        print(f"Unfollowed {user}")
                else:
                    confirm_unfollow.click()
                    print(f"Unfollowed {user}")
            else:
                sleep(randint(2, 5))
                print(f"Cant locate {user}")
                continue
        fd.remove_unloyals(lst)

    def close_session(self):
        sleep(randint(5, 10))
        self.driver.quit()


def randomize_actions(session, number=randint(1, 5)):
    if number == 1:
        print("No liking or watching")
        pass
    if number == 2:
        print("Just liking")
        session.like_posts()

    if number == 3:
        print("Just watching")
        session.watch_stories()

    if number == 4:
        print("Liking and watching")
        session.like_posts()
        session.watch_stories()

    if number == 5:
        print("Liking and watching")
        session.watch_stories()
        session.like_posts()


eastern = timezone('US/Eastern')

ib = InstagramBot()
ib.log_in()
randomize_actions(ib)
ib.close_session()
