from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

import json

logger = SgLogSetup().get_logger("fhb_com")


def write_output(data):
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for row in data:
            writer.write_row(row)


session = SgRequests()


def fetch_data():
    res = session.get("https://locations.fhb.com/")
    soup = BeautifulSoup(res.text, "html.parser")
    scripts = soup.find_all("script")

    for script in scripts:
        script = str(script)
        if "window.__SLS_REDUX_STATE__" in script:
            script = script.replace(
                "<script>window.__SLS_REDUX_STATE__ = ", ""
            ).replace(";</script>", "")
            jso = json.loads(script)
            locations = jso["dataLocations"]["collection"]["features"]

    for location in locations:

        url_id = location["properties"]["id"]
        name = location["properties"]["name"]
        if "#N/A" in name:
            name = "<MISSING>"
        type = ", ".join(location["properties"]["metaCategories"])
        if "ATM" not in type:
            continue
        id = location["properties"]["branch"]
        long = location["geometry"]["coordinates"][0]
        lat = location["geometry"]["coordinates"][1]
        url = "https://locations.fhb.com/" + location["properties"]["slug"]

        res = session.get(
            "https://sls-api-service.sweetiq-sls-production-east.sweetiq.com/bf9MYWSKMtNIoYjgeuAJduB9VdVVTP/locations-details?locale=en_US&ids="
            + str(url_id)
            + "&clientId=57a20eb57422662f6b9445d8&cname=locations.fhb.com"
        )
        jso = res.json()["features"][0]["properties"]
        street = jso["addressLine1"]
        if jso["addressLine2"]:
            street += ", " + jso["addressLine2"]
        city = jso["city"]
        state = jso["province"]
        zip = jso["postalCode"]
        country = jso["country"]
        phone = jso["phoneNumber"]
        tim = ""
        days = jso["hoursOfOperation"]
        for day in days:

            if days[day]:
                tim += day + ": " + " - ".join(days[day][0]) + ", "
            else:
                tim += day + ": " + "Closed, "

        tim = tim.strip(", ")

        yield SgRecord(
            locator_domain="https://www.fhb.com/",
            page_url=url,
            location_name=name,
            street_address=street,
            city=city,
            state=state,
            zip_postal=zip,
            country_code=country,
            store_number=id,
            phone=phone,
            location_type=type,
            latitude=lat,
            longitude=long,
            hours_of_operation=tim.strip(),
        )


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
