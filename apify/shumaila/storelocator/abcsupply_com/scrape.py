from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import re

from sgselenium import SgSelenium

driver = SgSelenium().chrome()


def fetch_data():

    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.abcsupply.com/wp-admin/admin-ajax.php?action=fetch_all_locations&_ajax_nonce=1bd2076898"
    driver.get(url)
    divlist = json.loads(re.sub(cleanr, "", driver.page_source))
    for div in divlist:
        loclist = div["locations"]
        for loc in loclist:

            store = loc["branchNumber"]
            street = loc["address1"] + str(loc["address2"])
            street = street.replace("None", "")
            city = loc["city"]
            state = loc["state"]
            pcode = loc["postalCode"]
            lat = loc["latitude"]
            longt = loc["longitude"]
            try:
                phone = loc["phoneNumber"].strip()
            except:
                phone = "<MISSING>"

            try:
                hourslist = loc["seasonalHours"][0]["hourDetails"][0]
                hours = (
                    hourslist["hoursText"]
                    + " "
                    + hourslist["openTime"]
                    + " - "
                    + hourslist["closeTime"]
                )
            except:
                hours = "<MISSING>"
            link = "https://www.abcsupply.com/locations/location/?id=" + str(store)
            title = "ABC Supply - " + city + ", " + state
            yield SgRecord(
                locator_domain="https://www.abcsupply.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=str(store),
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
