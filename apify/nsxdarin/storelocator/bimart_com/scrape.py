import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "cookie": "sb-sf-at-prod-s=at=9AQlj%2FOkUGeF9XjLQn9yvSwm%2B5XSxNv1hCHLydL%2Fsad%2FtOjShidKzIVb3VaUkzyfk%2Fudau7q12v9QsxViMp9vI8RCI9XBnUswxWloT%2BEgU44FnFyaXyAB%2FZxxlLPk%2FbodnTygFdkArtGqgmnxViJFDEAb5oFFTW9rRynIQ8qAv9VuuemTwC9A6rZ2m1KPYjfh9%2BhY6f6MAYF9jCmIrQFfBCOzsjOwd1PTkIlS8v83qbG%2F6ykt6JuoQwf%2BZPw8P2d43E%2FEvDdTa1joFiT9VLYmJ5APyec6Q6okJkRJGEmZKgAC%2B3MMxLZlHf%2B24BtWsR%2FIcRpE5HSYXVqWdt0Mf4abA%3D%3D&dt=2021-06-08T19%3A36%3A45.6385734Z; sb-sf-at-prod=at=9AQlj%2FOkUGeF9XjLQn9yvSwm%2B5XSxNv1hCHLydL%2Fsad%2FtOjShidKzIVb3VaUkzyfk%2Fudau7q12v9QsxViMp9vI8RCI9XBnUswxWloT%2BEgU44FnFyaXyAB%2FZxxlLPk%2FbodnTygFdkArtGqgmnxViJFDEAb5oFFTW9rRynIQ8qAv9VuuemTwC9A6rZ2m1KPYjfh9%2BhY6f6MAYF9jCmIrQFfBCOzsjOwd1PTkIlS8v83qbG%2F6ykt6JuoQwf%2BZPw8P2d43E%2FEvDdTa1joFiT9VLYmJ5APyec6Q6okJkRJGEmZKgAC%2B3MMxLZlHf%2B24BtWsR%2FIcRpE5HSYXVqWdt0Mf4abA%3D%3D; _mzvr=JHXXrtHSmkqBMHY97UgPSg; _mzvs=nn; _ga=GA1.2.2106834004.1623181007; _gid=GA1.2.1651838716.1623181007; mt.sc=%7B%22i%22%3A1623181006791%2C%22d%22%3A%5B%5D%7D; mt.v=2.203603775.1623181006793; mozucartcount=%7B%22fd6bab79a1804249b328a3922563d725%22%3A0%7D",
}

logger = SgLogSetup().get_logger("bimart_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    url = "https://www.bimart.com/api/commerce/storefront/locationUsageTypes/SP/locations/?filter=tenant~siteId%20eq%2049677%20and%20locationType.Code+eq+MS%20and%20geo+near(45.6401259685065,-122.6413462660265,16000934)"
    r = session.get(url, headers=headers)
    website = "bimart.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["items"]:
        store = item["code"]
        lurl = "<MISSING>"
        name = item["name"]
        state = item["address"]["stateOrProvince"]
        zc = item["address"]["postalOrZipCode"]
        add = item["address"]["address1"]
        city = item["address"]["cityOrTown"]
        lat = item["geo"]["lat"]
        lng = item["geo"]["lng"]
        phone = item["phone"]
        hours = "Monday-Friday 9AM-8PM; Saturday 9AM-6PM; Sunday 9AM-6PM"
        if "Pharmacy" in phone:
            phone = phone.split("Pharmacy")[0]
        phone = phone.replace("Store", "")
        phone = phone.strip()
        yield [
            website,
            lurl,
            name,
            add,
            city,
            state,
            zc,
            country,
            store,
            phone,
            typ,
            lat,
            lng,
            hours,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
