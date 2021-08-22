from sgselenium.sgselenium import SgChrome
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("steinhafels_com")


def fetch_data():

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    with SgChrome(user_agent=user_agent) as driver:
        driver.get("https://www.steinhafels.com/Location/GetLocationsJson")
        htmlsource = driver.page_source
        convert_json = htmlsource.split('">')[1].replace("</pre></body></html>", "")
        website = "steinhafels.com"
        typ = "<MISSING>"
        country = "US"
        loc = "<MISSING>"
        logger.info("Pulling Stores")
        for item in json.loads(convert_json):
            name = item["StoreName"]
            loc = "https://www.steinhafels.com/location/details/" + item["UrlName"]
            add = item["Address"]
            city = item["City"]
            state = item["State"]
            zc = item["ZipCode"]
            phone = item["PhoneNumber"]
            store = item["StoreCode"]
            lat = item["Latitude"]
            lng = item["Longitude"]
            if "-mattress" in loc:
                name = name + " Mattress Store"
            if item["IsFurnitureStore"] is True:
                name = name + " Furniture Store"
            hours = item["SundayHours"]
            hours = hours + "; " + item["MondayHours"]
            hours = hours + "; " + item["TuesdayHours"]
            hours = hours + "; " + item["WednesdayHours"]
            hours = hours + "; " + item["ThursdayHours"]
            hours = hours + "; " + item["FridayHours"]
            hours = hours + "; " + item["SaturdayHours"]
            yield SgRecord(
                locator_domain=website,
                page_url=loc,
                location_name=name,
                street_address=add,
                city=city,
                state=state,
                zip_postal=zc,
                country_code=country,
                phone=phone,
                location_type=typ,
                store_number=store,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
            )


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


if __name__ == "__main__":
    scrape()
