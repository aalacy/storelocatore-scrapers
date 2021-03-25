import csv
import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("iguanas_co_uk")


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

    base_link = "https://api.bigtablegroup.com/pagedata?brandKey=lasiguanas&path=/spaces/6qprbsfbbvrl/entries?access_token=30ad3e38f991a61b137301a74d5a4346f29fa442979b226cbca1a85acc37fc1c%26select=fields.title,fields.slug,fields.addressLocation,fields.storeId,fields.showOffers,fields.hours,fields.alternativeHours,fields.services,fields.amenities,fields.addressLine1,fields.addressLine2,fields.addressCity,fields.county,fields.postCode,fields.takeawayDeliveryServices,fields.takeawayCollectionService,fields.collectionMessage,fields.bookATableWidgetId,fields.bookingEngineType,fields.bookingProviderUrl%26content_type=location%26include=10%26limit=1000"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    locator_domain = "iguanas.co.uk"

    stores = json.loads(base.text)["items"]

    for store in stores:
        slug = store["fields"]["slug"]
        link = "https://www.iguanas.co.uk/restaurants/" + slug
        logger.info(link)

        api_link = (
            "https://api.bigtablegroup.com/pagedata?brandKey=lasiguanas&path=/spaces/6qprbsfbbvrl/entries?access_token=30ad3e38f991a61b137301a74d5a4346f29fa442979b226cbca1a85acc37fc1c%26select=fields%26content_type=location%26fields.slug="
            + slug
            + "%26include=10"
        )

        req = session.get(api_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        main_store = json.loads(base.text)
        store = json.loads(base.text)["items"][0]["fields"]

        location_name = "Las Iguanas " + store["title"]
        if "coming soon" in location_name.lower():
            continue
        try:
            street_address = (
                store["addressLine1"] + " " + store["addressLine2"]
            ).strip()
        except:
            street_address = store["addressLine1"].strip()
        city = store["addressCity"]
        state = store["county"]
        zip_code = store["postCode"]
        country_code = "GB"
        store_number = store["storeId"]
        location_type = "<MISSING>"
        phone = store["phoneNumber"]
        latitude = store["addressLocation"]["lat"]
        longitude = store["addressLocation"]["lon"]

        hours = ""
        hours_of_operation = ""
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        rows = main_store["includes"]["Entry"]
        for row in rows:
            if "mondayOpen" in str(row):
                hours = row["fields"]
                break
        if hours:
            for day in days:
                hours_of_operation = (
                    hours_of_operation
                    + " "
                    + day
                    + " "
                    + hours[day + "Open"]
                    + "-"
                    + hours[day + "Close"]
                ).strip()
        else:
            hours_of_operation = "Temporarily Closed"

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
