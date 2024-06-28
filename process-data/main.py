import requests
from bs4 import BeautifulSoup
import csv
import re
import pymongo


def collect(url: str) -> BeautifulSoup:
    """Perform GET request and return soup object

    keyword arguments:
    - url: str = the https url
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    content = response.content
    soup: BeautifulSoup = BeautifulSoup(content, "html.parser")
    return soup


def find_computers(soup: BeautifulSoup) -> tuple:
    """Find every elements in the soup object"""
    containers = soup.find_all(class_="pdt-item")

    # Instrouvable sur le html de la page
    # prices = [c.find_all(class_="basket") for c in containers]

    names = [c.find("h3").text for c in containers]
    descriptions = [c.find(class_="desc").text for c in containers]
    stars = [r.find("span")["class"] for r in containers]
    reviews = [c.find(class_="ratingClient").text for c in containers]

    computers = tuple(
        {
            "NAME": n,
            "DESCRIPTION": descriptions[i],
            "STARS": stars[i],
            "NUMBER REVIEWS": reviews[i],
        }
        for i, n in enumerate(names)
    )

    return computers


def unpack_config(computer):
    """Extract informations about computer's configuration and store them in the dict"""

    # NAME part
    name = computer["NAME"]
    # Explanation : Brand | Model
    pattern_n = r"^(\w+) (.+)"
    match_n = re.search(pattern_n, name)
    config = {}
    if match_n:
        config["BRAND"] = match_n.group(1)
        config["MODEL"] = match_n.group(2)

    # DESCRIPTION part
    description = computer["DESCRIPTION"]
    # Explanation : Processor | RAM | Storage | Size screen
    pattern_d = r"(.+) ([0-9]).+o (\w+ [0-9].+o) ([0-9.]+)"
    match_d = re.search(pattern_d, description)
    if match_d:
        config["PROCESSOR"] = match_d.group(1)
        config["RAM"] = match_d.group(2)
        config["STORAGE"] = match_d.group(3)
        config["SIZE SCREEN"] = match_d.group(4)

    return config


def transform_number_review(computer: dict) -> dict:
    dictionnaire = {}

    # REVIEW part
    number_reviews = computer["NUMBER REVIEWS"]
    pattern = "([0-9]+)"
    match_r = re.search(pattern, number_reviews)
    if match_r:
        dictionnaire["NUMBER REVIEWS"] = match_r.group(1)
    elif not match_r:
        dictionnaire["NUMBER REVIEWS"] = "0"

    # STARS part
    stars = computer["STARS"][0]
    match_s = re.search(pattern, stars)
    if match_s:
        dictionnaire["STARS"] = match_s.group(1)
    elif not match_s:
        dictionnaire["STARS"] = "0"
    return dictionnaire


def keep_keys(computer):
    """Keep some keys and return the clean computer dict"""
    keys = [
        "BRAND",
        "MODEL",
        "PROCESSOR",
        "RAM",
        "STORAGE",
        "SIZE SCREEN",
        "NUMBER REVIEWS",
        "STARS",
    ]
    cleaned = {k: v for k, v in computer.items() if k in keys}
    return cleaned


def convert_types(computer):
    """Convert types for the mentioned columns"""
    keys = [
        "RAM",
        "SIZE SCREEN",
        "NUMBER REVIEWS",
        "STARS",
    ]
    converted = {}
    for k in keys:
        if k in computer.keys():
            converted[k] = eval(computer[k])

    return converted


def load_computers(computers):  #: tuple[dict[str, str]]) -> None:
    """Load the output of transformations"""

    # client = pymongo.MongoClient("localhost", 27017, username='sdv', password='sdv')
    client = pymongo.MongoClient("mongodb://sdvroot:sdvroot@localhost:27017")
    db = client.products
    collection = db.computers

    # Save to Mongo
    collection.insert_many(computers)

    return None


# Initialize page number
pages = list(range(1, 16))

for p in pages:
    if p == 1:
        url = "https://www.ldlc.com/informatique/ordinateur-portable/pc-portable/c4265/"
    else:
        url = f"https://www.ldlc.com/informatique/ordinateur-portable/pc-portable/c4265/page{p}/"
    soup = collect(url)
    computers_raw = find_computers(soup)
    computers_config = tuple(dict(c, **unpack_config(c)) for c in computers_raw)
    computers_reviews = tuple(
        dict(c, **transform_number_review(c)) for c in computers_config
    )
    computers_convert = tuple(dict(c, **convert_types(c)) for c in computers_reviews)
    computers_cleaned = tuple(keep_keys(c) for c in computers_convert)
    load_computers(computers=computers_cleaned)

    del soup
    del computers_raw
    del computers_config
    del computers_reviews
    del computers_convert
    del computers_cleaned
