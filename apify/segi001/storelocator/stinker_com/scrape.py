import csv
from sgselenium import SgChrome
import req
import bs4
import time
import random
import json


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    locator_domain = "https://www.stinker.com/"
    missingString = "<MISSING>"

    class stinker:
        __sess = req.Req()

        def __init_soup(self, l):
            return bs4.BeautifulSoup(self.__sess.get(l).text, features="lxml")

        def __get_names(self):
            __all_loc = "https://www.stinker.com/all-locations/"
            __res = []
            s = self.__init_soup(__all_loc)
            for e in s.findAll("div", {"class": "one-sixth"}):
                __res.append(e.text.strip())
            random.shuffle(__res)
            return __res

        def __get_intotal_len(self):
            return len(self.__get_names())

        def __parse_duplicates(self, arr):
            stringified = []
            for e in arr:
                stringified.append(json.dumps(e))
            s = set(stringified)
            res = []
            for el in s:
                res.append(json.loads(el))
            return res

        def execute(self):
            batch = []
            b = []
            with SgChrome(is_headless=True) as driver:
                driver.get("https://www.stinker.com/store-search/")

                total = self.__get_intotal_len()
                names = self.__get_names()
                for name in names:
                    input_box = driver.find_element_by_class_name("location-input")
                    input_box.clear()
                    search = driver.find_element_by_class_name("update-location")
                    input_box.send_keys(name)
                    search.click()
                    time.sleep(3)
                    g = bs4.BeautifulSoup(driver.page_source, features="lxml")

                    for s in g.findAll("tr", {"class": "resultRow"}):
                        n = missingString
                        location = missingString
                        phone = missingString
                        content = missingString
                        if s.find("h2", {"class": "result title"}):
                            n = s.find("h2", {"class": "result title"}).text.strip()
                        if s.find("p", {"class": "result location"}):
                            location = s.find(
                                "p", {"class": "result location"}
                            ).text.strip()
                        if s.find("p", {"class": "phone"}):
                            phone = s.find("p", {"class": "phone"}).text.strip()
                        if s.find("div", {"class": "content"}):
                            content = s.find("div", {"class": "content"}).text.strip()
                        d = {
                            "name": n,
                            "location": location,
                            "phone": phone,
                            "content": content,
                        }
                        batch.append(d)

                    b = self.__parse_duplicates(batch)

                    if len(b) == total:
                        break
            return b

    batch_stores = stinker().execute()

    def parser(l):
        loc_marker = l["location"].split(",")

        name = l["name"]
        store_num = l["name"].split()[0]
        street = loc_marker[0]
        city = loc_marker[1]
        state = loc_marker[-2].strip().split()[0]
        zp = loc_marker[-2].strip().split()[1]
        country = loc_marker[-1]
        phone = l["phone"].replace("p.", "")
        hours = (
            l["content"]
            .split("\n")[0]
            .replace("Temporary Hours", "")
            .replace("Hours:", "")
        )

        if name == "":
            name = missingString
        if store_num == "":
            store_num = missingString
        if street == "":
            street = missingString
        if city == "":
            city = missingString
        if state == "":
            state = missingString
        if zp == "":
            zp = missingString
        if country == "":
            country = missingString
        if phone == "":
            phone = missingString
        if hours == "":
            hours = missingString

        return {
            "locator": locator_domain.strip(),
            "name": name.strip(),
            "store_num": store_num.strip(),
            "street": street.strip(),
            "city": city.strip(),
            "state": state.strip(),
            "zp": zp.strip(),
            "country": country.strip(),
            "phone": phone.strip(),
            "hours": hours.strip(),
        }

    def urlGenerator(n):
        slug = n.strip().replace("#", "").replace(" ", "-").lower()
        return "https://www.stinker.com/locations/{}/".format(slug)

    result = []

    for e in batch_stores:
        l = parser(e)
        result.append(
            [
                l["locator"],
                urlGenerator(l["name"]),
                l["name"],
                l["street"],
                l["city"],
                l["state"],
                l["zp"],
                l["country"],
                l["store_num"],
                l["phone"],
                missingString,
                missingString,
                missingString,
                l["hours"],
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
