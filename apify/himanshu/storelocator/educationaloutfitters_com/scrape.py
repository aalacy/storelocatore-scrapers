import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("educationaloutfitters_com")
session = SgRequests()


def log(*args, **kwargs):
    if show_logs is True:
        logger.info(" ".join(map(str, args)), **kwargs)


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


show_logs = True


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    addressess = []
    base_url = "https://www.educationaloutfitters.com"
    r = session.get("http://www.educationaloutfitters.com/states", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "http://www.educationaloutfitters.com/states"
    for script in soup.find_all("li", {"class": "navList-item"}):
        r1 = session.get(script.find("a")["href"], headers=headers)
        if not r1:
            continue
        soup1 = BeautifulSoup(r1.text, "lxml")
        for lep in soup1.find_all("article", {"class": "modern__card"}):
            location_name = lep.find("a", {"class": "modern__card-title-link"}).text
            r_location = session.get(lep.find("a")["href"], headers=headers)
            if not r_location:
                continue
            soup_location = BeautifulSoup(r_location.text, "lxml")
            page_url = soup_location.find("div", {"class": "store-button"}).find("a")[
                "href"
            ]
            log(page_url)
            hours_of_operation = "<MISSING>"
            if (
                "shop.readsuniforms.net/educationnc" not in page_url
                and "toledo.educationaloutfitters.com" not in page_url
            ):
                r4 = session.get(page_url, timeout=(30, 30), headers=headers)
                if r4:
                    if r4.status_code == 200:
                        soup5 = BeautifulSoup(r4.text, "lxml")
                        try:
                            hours_of_operation = (
                                " ".join(
                                    list(
                                        soup5.find(
                                            "p", {"class": "basic__hours"}
                                        ).stripped_strings
                                    )
                                )
                                .replace("Customer Service Hours:", "")
                                .replace("Store Hours:", "")
                            )
                        except:
                            hours_of_operation = "<MISSING>"

            d = soup_location.find("li", {"class": "store-address"})
            full_detail = list(d.stripped_strings)
            phone = soup_location.find("li", {"class": "store-tel"}).text.strip()
            full_address = full_detail[1:]
            location_name = full_detail[0]
            if len(full_address) == 1:
                street_address = "<MISSING>"
                city = full_address[0].split(",")[0]
                state = full_address[0].split(",")[1]
            elif len(full_address) == 2:
                street_address = " ".join(full_address[:-1])
                city = full_address[-1].split(",")[0]
                state = (
                    full_address[-1]
                    .split(",")[-1]
                    .strip()
                    .split()[0]
                    .replace("78213", "TX")
                )
                zipp = full_address[-1].split(",")[-1].strip().split()[-1]
            store = [
                locator_domain,
                location_name,
                street_address,
                city,
                state.strip(),
                zipp,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation.replace("Store Hours for Curb-side Pick-up:", "")
                .replace("REQUIRED APPOINTMENT to shop in store  ", "")
                .strip(),
                page_url,
            ]
            if str(store[2] + store[-1]) in addressess:
                continue
            addressess.append(str(store[2] + store[-1]))
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
