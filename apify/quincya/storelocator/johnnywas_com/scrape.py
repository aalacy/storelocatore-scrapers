import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("johnnywas_com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    session = SgRequests()

    base_link = "https://www.johnnywas.com/store_locator/location/updatemainpage"

    headers = {
        "authority": "www.johnnywas.com",
        "method": "POST",
        "origin": "https://www.johnnywas.com",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br",
        "referer": "https://www.johnnywas.com/store-locator",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    response = session.post(base_link, headers=headers)
    base = BeautifulSoup(response.text, "lxml")

    raw_text = str(base).split("</script>")[1].split("var locations")[0]
    base = BeautifulSoup(raw_text, "lxml")

    items = base.find_all("a", string="Store Page")
    locator_domain = "johnnywas.com"

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers1 = {"User-Agent": user_agent}

    for item in items:
        link = item["href"]

        logger.info(link)
        req = session.get(link, headers=headers1)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h2.text.strip()

        raw_data = list(
            base.find(
                class_="mw-sl__details__item mw-sl__details__item--location"
            ).stripped_strings
        )

        street_address = " ".join(raw_data[0].split(",")[:-1]).strip()
        street_address = (re.sub(" +", " ", street_address)).strip()

        city = raw_data[0].split(",")[-1].strip()
        state = raw_data[1].split(",")[0].strip().replace("Washington", "WA")
        zip_code = raw_data[1].split(",")[1].strip().split()[0]
        if len(zip_code) == 4:
            zip_code = "0" + zip_code
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        try:
            phone = base.find(
                class_="mw-sl__details__item mw-sl__details__item--tel"
            ).text.strip()
        except:
            if "OPENING" in base.find(class_="description").text.upper():
                continue
            phone = "<MISSING>"

        hours_of_operation = (
            base.find(class_="mw-sl__infotable__table").text.replace("\n", " ").strip()
        )
        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

        fin_script = ""
        all_scripts = base.find_all("script")
        for script in all_scripts:
            if "var location" in str(script):
                fin_script = str(script)
                break
        try:
            geo = re.findall(
                r"lat: [0-9]{2}\.[0-9]+, lng:.+[0-9]{2,3}\.[0-9]+", fin_script
            )[0].split(",")
            latitude = geo[0].split(":")[1].strip()
            longitude = geo[1].split(":")[1].strip()
            if "-" not in longitude:
                longitude = "-" + longitude
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        yield [
            locator_domain,
            link,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
