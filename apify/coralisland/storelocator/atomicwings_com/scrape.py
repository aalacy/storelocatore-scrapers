import json
import usaddress

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

base_url = "https://www.atomicwings.com/"


def validate(item):
    if type(item) == list:
        item = " ".join(item)
    return item.strip()


def get_value(item):
    item = validate(item)
    if item == "" or item == "N/A":
        item = "<MISSING>"
    return item


def fetch_data(sgw: SgWriter):
    url = "https://api.responsival.net/atomicwings/locations.php"
    session = SgRequests()
    request = session.get(url)
    store_list = json.loads(request.text)
    for store in store_list:
        if "COMING SOON" in store["name"].upper() or "OPENING" in store["name"].upper():
            continue
        output = []
        output.append(base_url)  # url
        output.append(store["name"])  # location name
        address = usaddress.parse(store["address"])
        street = ""
        city = ""
        state = ""
        zipcode = ""
        for addr in address:
            if addr[1] == "PlaceName":
                city += addr[0].replace(",", "") + " "
            elif addr[1] == "ZipCode":
                zipcode = addr[0]
            elif addr[1] == "StateName":
                state = addr[0]
            else:
                street += addr[0].replace(",", "") + " "
        output.append(get_value(street).replace("Corona Pizza ", ""))  # address
        output.append(get_value(city).split("(")[0].strip())  # city
        output.append(get_value(state))  # state
        output.append(get_value(zipcode))  # zipcode
        output.append("US")  # country code
        output.append("<MISSING>")  # store_number
        output.append(get_value(store["phone"]).replace("WING (9464)", "9464"))  # phone
        output.append("<MISSING>")  # location type
        output.append(store["latitude"])  # latitude
        output.append(store["longitude"])  # longitude
        store_hours = "  "
        days_of_week = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for day in days_of_week:
            store_hours += day.capitalize() + " " + store[day + "-hours"] + ", "
        if "-" not in store_hours:
            store_hours = ""
        output.append(get_value(store_hours[:-2].replace("–", "-")))  # opening hours

        sgw.write_row(
            SgRecord(
                locator_domain=output[0],
                location_name=output[1],
                street_address=output[2],
                city=output[3],
                state=output[4],
                zip_postal=output[5],
                country_code=output[6],
                store_number=output[7],
                phone=output[8],
                location_type=output[9],
                latitude=output[10],
                longitude=output[11],
                hours_of_operation=output[12],
                page_url="https://www.atomicwings.com/locations",
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
