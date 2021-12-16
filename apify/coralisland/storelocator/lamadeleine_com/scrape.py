import json

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

base_url = "https://lamadeleine.com"


def validate(item):
    if type(item) == list:
        item = " ".join(item)
    return item.strip().replace("\n", "")


def get_value(item):
    item = validate(item)
    if item == "":
        item = "<MISSING>"
    return item


def fetch_data(sgw: SgWriter):
    url = "https://cms.lamadeleine.com/wp-json/wp/v2/restaurant-locations?per_page=150"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://lamadeleine.com/locations",
        "Sec-Fetch-Mode": "cors",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    requests = SgRequests()
    response = requests.get(url, headers=headers)
    store_list = json.loads(response.text)
    for store in store_list:
        hours = store["acf"]["locationHero"]["hoursOfOperation"]
        store_hours = ""
        for x in hours:
            if x["openingTime"] == "Closed":
                store_hours += x["day"] + ": Closed "
            else:
                store_hours += (
                    x["day"] + ":" + x["openingTime"] + "-" + x["closingTime"] + " "
                )
        output = []
        output.append(base_url)  # url
        output.append("https://lamadeleine.com/locations/" + store["slug"])  # page_url
        output.append(
            validate(store["acf"]["locationHero"]["storeName"])
        )  # location name
        output.append(
            validate(
                store["acf"]["locationHero"]["addressLine1"]
                + " "
                + store["acf"]["locationHero"]["addressLine2"]
            )
        )  # address
        output.append(validate(store["acf"]["locationHero"]["city"]))  # city
        output.append(validate(store["acf"]["locationHero"]["state"]))  # state
        output.append(validate(store["acf"]["locationHero"]["zip"]))  # zipcode
        output.append("US")  # country code
        output.append(store["id"])  # store_number
        output.append(validate(store["acf"]["locationHero"]["phone"]))  # phone
        output.append("")  # location type
        output.append(validate(store["acf"]["locationHero"]["lat"]))  # latitude
        output.append(validate(store["acf"]["locationHero"]["lng"]))  # longitude
        output.append(get_value(store_hours))  # opening hours

        sgw.write_row(
            SgRecord(
                locator_domain=output[0],
                page_url=output[1],
                location_name=output[2],
                street_address=output[3],
                city=output[4],
                state=output[5],
                zip_postal=output[6],
                country_code=output[7],
                store_number=output[8],
                phone=output[9],
                location_type=output[10],
                latitude=output[11],
                longitude=output[12],
                hours_of_operation=output[13],
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
