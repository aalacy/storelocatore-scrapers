import csv
import json

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger(logger_name="lloydsbank.com")


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

    base_link = "https://branches.lloydsbank.com/index.html"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    main_links = []
    final_links = []

    main_items = base.find_all(class_="Directory-listLink")
    for main_item in main_items:
        main_link = "https://branches.lloydsbank.com/" + main_item["href"]
        count = main_item["data-count"].replace("(", "").replace(")", "").strip()
        if count == "1":
            final_links.append(main_link)
        else:
            main_links.append(main_link)

    for main_link in main_links:
        req = session.get(main_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        next_items = base.find_all(class_="Directory-listLink")
        if next_items:
            for next_item in next_items:
                next_link = "https://branches.lloydsbank.com/" + next_item["href"]
                count = (
                    next_item["data-count"].replace("(", "").replace(")", "").strip()
                )

                if count == "1":
                    final_links.append(next_link)
                else:
                    next_req = session.get(next_link, headers=headers)
                    next_base = BeautifulSoup(next_req.text, "lxml")

                    final_items = next_base.find_all(class_="Teaser-titleLink")
                    for final_item in final_items:
                        final_link = (
                            "https://branches.lloydsbank.com/" + final_item["href"]
                        ).replace("../", "")
                        final_links.append(final_link)
        else:
            final_items = base.find_all(class_="Teaser-titleLink")
            for final_item in final_items:
                final_link = (
                    "https://branches.lloydsbank.com/" + final_item["href"]
                ).replace("../", "")
                final_links.append(final_link)

    log.info("Processing %s links .." % (len(final_links)))
    for link in final_links:
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        store = json.loads(base.find(id="js-map-config-dir-map").text)["entities"][0]

        locator_domain = "lloydsbank.com"
        try:
            street_address = (
                store["profile"]["address"]["line1"]
                + " "
                + store["profile"]["address"]["line2"]
                + " "
                + store["profile"]["address"]["line3"]
            ).strip()
        except:
            try:
                street_address = (
                    store["profile"]["address"]["line1"]
                    + " "
                    + store["profile"]["address"]["line2"]
                ).strip()
            except:
                street_address = store["profile"]["address"]["line1"].strip()
        location_name = store["profile"]["c_internalName"]
        city = store["profile"]["address"]["city"]
        state = "<MISSING>"
        zip_code = store["profile"]["address"]["postalCode"]
        country_code = store["profile"]["address"]["countryCode"]
        store_number = store["profile"]["meta"]["id"]
        phone = store["profile"]["mainPhone"]["display"]
        location_type = "<MISSING>"
        hours_of_operation = ""
        raw_hours = store["profile"]["hours"]["normalHours"]
        for raw_hour in raw_hours:
            day = raw_hour["day"]
            if raw_hour["isClosed"]:
                hours = "Closed"
            else:
                hours = (
                    str(raw_hour["intervals"][0]["start"])
                    + "-"
                    + str(raw_hour["intervals"][0]["end"])
                )
            hours_of_operation = (hours_of_operation + " " + day + " " + hours).strip()
        hours_of_operation = (
            hours_of_operation.replace("00-", ":00-")
            .replace("30-", ":30-")
            .replace("30 ", ":30 ")
            .replace("00 ", ":00 ")
        )

        latitude = store["profile"]["yextDisplayCoordinate"]["lat"]
        longitude = store["profile"]["yextDisplayCoordinate"]["long"]

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
