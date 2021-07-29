import random

"""One time functions
Done whenever client feels, not included in bot code"""


def remove_common_people():
    """Do this after getting someones_followers
    This checks if someone is following me or in ppl to avoid"""

    # using this list as a comparison
    with open("text_files/someones_followers", "r") as sfr:
        someones_followers = sfr.readlines()

    # my followers and ppl_to_avoid are used to compare
    try:
        with open("text_files/my_followers") as f:
            for line in f:
                if line in someones_followers:
                    someones_followers.remove(line)
    except FileNotFoundError:
        print("File does not exist")
    with open("text_files/ppl_to_avoid") as g:
        for line in g:
            if line in someones_followers:
                someones_followers.remove(line)

    # writes remaining of someones followers to file
    with open("text_files/someones_followers", "w") as sf:
        sf.write("")
    with open("text_files/someones_followers", "a") as sfa:
        for person in someones_followers:
            sfa.write(person)

    print(someones_followers)
    return someones_followers


"""Sub functions
Functions that are used for functions with similar actions"""


def get_list_from_file(file, num):
    """retrieves specific amount of lines in a file and
    converts it to list"""
    with open(file, "r") as f:
        lst = f.readlines()[:num]

        lst = [i.strip() for i in lst]
        return lst


"""Functions called in Bot"""


def get_list_to_filter(number):
    """takes out specific number of lines, and readds the rest
    back to someones followers"""
    lst1 = []
    lst2 = []
    with open("text_files/someones_followers") as f:
        lst = f.readlines()
        for index, value in enumerate(lst):
            if index < number:
                lst1.append(value.replace("\n", ""))
            else:
                lst2.append(value)
    with open("text_files/someones_followers", "w") as file:
        file.write("")
    for i in lst2:
        with open("text_files/someones_followers", "a") as file1:
            file1.write(i)

    return lst1


def get_list_of_everyone():
    """gets list of ppl to avoid, to follow, and my followers"""
    lst1 = []
    try:
        with open("text_files/my_followers") as f1:
            lst1 = f1.readlines()
    except FileNotFoundError:
        print("File Not Found")

    with open("ppl_to_avoid") as f2, open("to_follow") as f3:
        lst2 = f2.readlines()
        lst3 = f3.readlines()
    if not lst1:
        lst = lst2 + lst3
    else:
        lst = lst1 + lst2 + lst3
    return lst


def get_list_to_follow():
    """gets list of people from to_follow"""
    lst = get_list_from_file("text_files/to_follow", random.randint(8,10))
    if not lst:
        print("no more people")
        quit()
    else:
        print(lst)
        return lst


def get_list_to_unfollow():
    """gets list of people from to_unfollow"""
    lst = get_list_from_file("text_files/unloyals", random.randint(8, 10))
    if not lst:
        print("no more people")
        quit()
    else:
        with open('text_files/ppl_to_avoid', "r") as f, open("text_files/unloyals", "r") \
                as f1:
            avoid_lst = f.readlines()
            unloyals = f1.readlines()
            for i in lst:
                user = f"{i}\n"
                if user not in avoid_lst:
                    with open('text_files/ppl_to_avoid', "a") as f2:
                        f2.write(f"{i}\n")
                if user in unloyals:
                    unloyals.remove(user)

        with open("text_files/unloyals", "w") as un:
            un.write("")
        for j in unloyals:
            with open("text_files/unloyals", "a") as file:
                file.write(j)
        print(lst)
        return lst


def remove_unloyals(lst):
    """removes people in unloyals file"""
    lst_for_unloyals = []
    with open("text_files/unloyals", "r") as f, \
            open("text_files/ppl_to_avoid", "r") as g:
        for line in f:
            if line.strip() in lst:
                pass
            else:
                lst_for_unloyals.append(line)
        lst_for_avoid = g.readlines()
        for i in lst:
            if f"{i}\n" in lst_for_avoid:
                pass
            else:
                lst_for_avoid.append(f"{i}\n")
    with open("text_files/unloyals", "w") as h, \
            open("text_files/ppl_to_avoid", "w") as i:
        h.write("")
        i.write("")
    with open("text_files/unloyals", "a") as j, \
            open("text_files/ppl_to_avoid", "a") as k:
        for i in lst_for_avoid:
            k.write(i)
        for z in lst_for_unloyals:
            j.write(z)


def convert_follow_to_avoid(lst):
    """converts everyone after following to to_avoid file"""
    lt = []
    with open("text_files/to_follow") as f, \
            open('text_files/ppl_to_avoid', "a") as g:
        for line in f:
            if line.strip() in lst:
                g.write(line)
            else:
                lt.append(line)

    with open("text_files/to_follow", "w") as swag:
        swag.write("")
    for i in lt:
        with open("text_files/to_follow", "a") as file:
            file.write(i)
