import csv

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("gqtmovies_com")


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

    base_link = "https://www.gqtmovies.com/michigan/ada-lowell-5"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    pages = base.find(class_="select-0").find_all("option")[1:]

    data = []
    for page in pages:
        locator_domain = "gqtmovies.com"

        link = "https://www.gqtmovies.com" + page["value"] + "/theater-info"

        if "coming-soon" in link:
            continue
        logger.info(link)
        req = session.get(link, headers=headers)
        item = BeautifulSoup(req.text, "lxml")

        location_name = page.text.strip()
        raw_address = (
            item.find(class_="cinAdress")
            .text.split("|")[1]
            .strip()
            .replace("\n", "")
            .split(",")
        )
        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        state = raw_address[2].strip().split()[0].strip()
        zip_code = raw_address[2].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        try:
            phone = (
                item.find(class_="cinTel").text.replace("Office Phone: ", "").strip()
            )
        except:
            phone = "<MISSING>"
        map_link = item.find("a", string="GET DIRECTIONS")["href"]
        latitude = map_link[map_link.rfind("=") + 1 : map_link.rfind(",")].strip()
        longitude = map_link[map_link.rfind(",") + 1 :].strip()
        hours_of_operation = "<MISSING>"

        data.append(
            [
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
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
