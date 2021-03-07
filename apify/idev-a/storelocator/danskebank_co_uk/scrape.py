from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
import json

locator_domain = "https://danskebank.co.uk/"
base_url = "https://danskebank.co.uk/web/search/domapsearch/do?c={38ECF3E2-52C7-4220-8277-2CBF2E228531}&l=en&o=0&m=999&r=500&q=Belfast&cl=54.59728500000001,-5.93012&lt=&f="


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url)
        locations = json.loads(res.text)
        for _ in locations:
            hours_of_operation = ""
            if _["AtmOpen24Hours"]:
                hours_of_operation = "Open 24/7"
            else:
                availability = _["Availability"]
                if availability["HasOpeningHours"]:
                    if availability.get("MondayHours"):
                        hours_of_operation += (
                            f"{availability['Monday']}: {availability['MondayHours']};"
                        )
                    if availability.get("TuesdayHours"):
                        hours_of_operation += f"{availability['Tuesday']}: {availability['TuesdayHours']};"
                    if availability.get("WednesdayHours"):
                        hours_of_operation += f"{availability['Wednesday']}: {availability['WednesdayHours']};"
                    if availability.get("ThursdayHours"):
                        hours_of_operation += f"{availability['Thursday']}: {availability['ThursdayHours']};"
                    if availability.get("FridayHours"):
                        hours_of_operation += (
                            f"{availability['Friday']}: {availability['FridayHours']};"
                        )
                    if availability.get("SaturdayHours"):
                        hours_of_operation += f"{availability['Saturday']}: {availability['SaturdayHours']};"
                    if availability.get("SundayHours"):
                        hours_of_operation += (
                            f"{availability['Sunday']}: {availability['SundayHours']};"
                        )

            addr = parse_address_intl(
                f"{_['PrimaryAddress']['AddressLine']} {_['PrimaryAddress']['City']} {_['PrimaryAddress']['ZipCode']} GB"
            )
            record = SgRecord(
                store_number=_["ServiceID"],
                location_name=_["Name"],
                street_address=addr.street_address_1,
                city=addr.city,
                zip_postal=addr.postcode,
                phone=_["PhoneNumber"],
                country_code="GB",
                latitude=_["Location"]["Coordinate.Latitude"],
                longitude=_["Location"]["Coordinate.Longitude"],
                location_type=_["Type"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
