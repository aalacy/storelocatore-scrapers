from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgscrape import sgpostal as parser

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("thebodyshop_com")


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "thebodyshop.com"

    locs = []
    locs_link = "https://api.thebodyshop.com/rest/v2/thebodyshop-us/cms/pages?pageType=ContentPage&pageLabelOrId=%2Fstore-finder&lang=en_US&curr=USD"
    locs_results = session.get(locs_link, headers=headers).json()["contentSlots"][
        "contentSlot"
    ]
    for i in locs_results:
        if i["slotId"] == "FooterLeftSlot":
            markets = i["components"]["component"][-1]["markets"].split("url'")
    for m in markets:
        row = m.replace("https://www.thebodyshop.com", "").split(",")[0]
        if "-" in row and len(row) < 15:
            locs.append(row[2:-1].replace("gb", "uk"))

    for loc in locs:
        for num in range(0, 100):
            base_link = (
                "https://api.thebodyshop.com/rest/v2/thebodyshop-"
                + loc.split("-")[1][:2]
                + "/stores?fields=FULL&latitude=&longitude=&query=&lang=&curr=&currentPage="
                + str(num)
            )
            logger.info(base_link)
            stores = session.get(base_link, headers=headers).json()["stores"]
            if len(stores) == 0:
                break
            for store in stores:
                if store["permanentlyClosed"]:
                    continue
                location_name = store["displayName"]
                try:
                    raw_address = store["address"]["line1"].replace("  ", " ")
                    if raw_address[-1:] == ",":
                        raw_address = raw_address[:-1]
                except:
                    raw_address = ""
                if "Company Driver" in location_name:
                    continue
                addr = parser.parse_address_intl(raw_address)
                try:
                    street_address = addr.street_address_1 + " " + addr.street_address_2
                except:
                    street_address = addr.street_address_1
                try:
                    city = (
                        store["address"]["town"]
                        .replace("   ", " ")
                        .replace("  ", " ")
                        .split(", STAFFORD")[0]
                        .strip()
                    )
                    if city[-1:] == ",":
                        city = city[:-1]
                except:
                    city = ""
                try:
                    state = store["address"]["region"]["name"]
                except:
                    state = ""
                try:
                    phone = store["address"]["phone"]
                except:
                    phone = ""
                try:
                    zip_code = store["address"]["postalCode"]
                    if str(zip_code) == "0":
                        zip_code = ""
                except:
                    zip_code = ""
                store_number = store["name"]
                location_type = ""
                country_code = store["address"]["country"]["name"]
                latitude = store["geoPoint"]["latitude"]
                longitude = store["geoPoint"]["longitude"]
                if latitude == 0.0:
                    latitude = ""
                    longitude = ""
                hours_of_operation = ""
                try:
                    for item in store["openingHours"]["weekDayOpeningList"]:
                        if item["closed"] is True:
                            hrs = item["weekDay"] + ": Closed"
                        else:
                            hrs = (
                                item["weekDay"]
                                + ": "
                                + item["openingTime"]["formattedHour"]
                                + "-"
                                + item["closingTime"]["formattedHour"]
                            )
                        if hours_of_operation == "":
                            hours_of_operation = hrs
                        else:
                            hours_of_operation = hours_of_operation + " " + hrs
                except:
                    pass
                link = store["canonicalUrl"]

                sgw.write_row(
                    SgRecord(
                        locator_domain=locator_domain,
                        page_url=link,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip_code,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                        raw_address=raw_address,
                    )
                )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
