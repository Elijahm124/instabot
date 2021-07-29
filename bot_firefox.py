from instapy import InstaPy
from random import randint
from time import sleep


def start_instapy():
    """Starts an instapy firefox session"""
    login = input("Enter a username: ")
    password = input("Enter a password: ")
    session = InstaPy(username=login, password=password, headless_browser=True)
    session.login()

    # allows us to view and work with private accounts
    session.set_skip_users(skip_private=False)
    return session


def get_followers(session):
    """Retrieves all followers of a user
    puts data in someones followers text file"""

    someone = input("Whose following would you like to scrape?: ")

    # noinspection PyTypeChecker
    someones_followers = session.grab_followers(username=someone, amount='full', live_match=True, store_locally=True)
    print(someones_followers)
    for i in someones_followers:
        with open("text_files/someones_followers", "a") as sf:
            sf.write(f"{i}\n")
    return someones_followers


def see_ppl_who_dont_fol_me_back(session):
    """Retrieves people that a user follows that dont follow the user back"""
    sleep(5)
    someone = input("Whose following would you like to scrape?: ")
    lst = session.pick_nonfollowers(username=someone, live_match=True, store_locally=True)
    print(lst)
    for user in lst:
        with open("text_files/unloyals", "a") as u:
            u.write(f"{user}\n")
    sleep(5)
    return lst


def end_session(session):
    """closes session"""
    sleep(randint(5, 10))
    session.end()


