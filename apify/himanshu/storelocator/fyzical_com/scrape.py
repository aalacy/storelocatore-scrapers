from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("fyzical_com")

session = SgRequests()


def fetch_data(sgw: SgWriter):

    data = session.get(
        "https://www.fyzical.com/contact.php?v=4&action=ajax_get_locations&ne=65.47336744902078,-12.629251250000006&sw=8.312726964373702,-167.66831375"
    ).json()

    found = []

    for data in data["locations"]:
        Suite = ""
        Suit = ""
        if "Suite" in data:

            Suite = str(data["Suite"])
            if Suite:
                if "suite" in str(Suite).lower():
                    Suit = Suite
                else:
                    Suit = " Suite " + Suite

        street_address = (data["Street"] + " " + Suit).replace("  ", " ")
        location_name = data["Name"]
        if "ming soon" in location_name.lower():
            continue
        city = data["City"]
        zipp = data["Zip"]
        state = data["State"]
        phone = data["Phone"]
        longitude = data["Longitude"]
        latitude = data["Latitude"]
        page_url = data["Long_description_url"]

        hours = ""
        for hour in data["Workhours"]:
            if data["Workhours"][hour]["Always_closed"] == "yes":
                hours = hours + " " + data["Workhours"][hour]["Weekday"] + " Closed "
            else:
                hours = (
                    hours
                    + " "
                    + data["Workhours"][hour]["Weekday"]
                    + " "
                    + data["Workhours"][hour]["Opening_time"]
                    + " "
                    + data["Workhours"][hour]["Closing_time"]
                )
        hours = hours.replace("  ", " ")
        store_number = data["ID_Location"]

        if street_address in found:
            continue
        found.append(street_address)

        sgw.write_row(
            SgRecord(
                locator_domain="https://www.fyzical.com",
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code="US",
                store_number=store_number,
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
