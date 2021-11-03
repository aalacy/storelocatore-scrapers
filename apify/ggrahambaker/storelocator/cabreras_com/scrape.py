import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="cabreras.com")


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


def addy_ext(addy):
    address = addy.split(",")
    city = address[0]
    state_zip = address[1].strip().split(" ")
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def fetch_data():
    log.info("Fetching store_locator data")
    base_link = "https://www.cabreras.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    hrefs = base.find(id="SITE_PAGES").find_all(class_="Ued3M _2ws69")
    link_list = []
    for href in hrefs:
        link_list.append(href.a["href"])
    log.info("Found {} store URL ".format(len(link_list)))

    all_store_data = []
    locator_domain = "cabreras.com"

    for link in link_list:
        log.info("Pull content {}".format(link))
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        contents = base.find_all(class_="font_2")[1:14]

        street_address = contents[1].text.strip()
        if "E Live Oak Ave" in street_address:
            href = contents[0].a["href"]
            start_idx = href.find("@")
            coords = href[start_idx + 1 :].split(",")

            lat = coords[0]
            longit = coords[1]
        elif "655 N Lake" in street_address:
            lat = "34.157211"
            longit = "-118.13269"
        elif "1856 Huntington" in street_address:
            lat = "34.139693"
            longit = "-117.964668"
        else:
            lat = "<INACCESSIBLE>"
            longit = "<INACCESSIBLE>"

        city, state, zip_code = addy_ext(contents[2].text)
        location_name = city
        phone_number = contents[4].text
        hours = " ".join(
            [
                x.get_text(strip=True)
                for x in base.find_all(
                    "span", {"style": "font-family:montserrat,sans-serif"}
                )
            ]
        ).replace("&", "-")
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        store_data = [
            locator_domain,
            link,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone_number,
            location_type,
            lat,
            longit,
            hours,
        ]
        log.info("Append {} => {}".format(location_name, street_address))
        all_store_data.append(store_data)

    return all_store_data


def scrape():
    log.info("Start {} Scraper".format("cabreras.com"))
    data = fetch_data()
    log.info("Found {} locations".format(len(data)))
    write_output(data)
    log.info("Finish processed " + str(len(data)))


scrape()
