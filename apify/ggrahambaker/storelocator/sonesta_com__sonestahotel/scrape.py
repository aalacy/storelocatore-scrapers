import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgselenium import SgChrome


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "https://www.sonesta.com/"
    ext = "destinations"

    driver = SgChrome().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector("main#main-content")
    us_locs = main.find_element_by_css_selector("div.location-listing__column--left")
    hrefs = us_locs.find_elements_by_css_selector("a")

    ca_locs = main.find_element_by_css_selector(
        "div.location-listing__column--right"
    ).find_element_by_css_selector("div.location-listing__list")
    hrefs = hrefs + ca_locs.find_elements_by_css_selector("a")

    link_list = []
    for href in hrefs:
        link_list.append(href.get_attribute("href"))

    all_store_data = []
    for link in link_list:
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        try:
            if "Temporarily Unavailable" in base.h3.text:
                continue
        except:
            pass

        location_name = base.find(class_="footer-primary__name").text.strip()
        phone_number = base.find(class_="footer-primary__number").text.strip()
        street_address = base.find(class_="thoroughfare").text.strip()
        city = base.find(class_="locality").text.strip()
        state = base.find(class_="state").text.strip()
        zip_code = base.find(class_="postal-code").text.strip()
        country_code = base.find(class_="country footer-address__block").text.strip()
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        map_div = base.find(class_="property-teaser-map--static")
        if map_div:
            lat = map_div["data-lat"]
            longit = map_div["data-lng"]
        else:
            lat = "<MISSING>"
            longit = "<MISSING>"

        hours = "<MISSING>"

        store_data = [
            locator_domain,
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
            link,
        ]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
