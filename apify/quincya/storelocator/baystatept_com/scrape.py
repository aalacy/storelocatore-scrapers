from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("baystatept.com")


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    headers = {
        "authority": "locations.baystatept.com",
        "method": "GET",
        "scheme": "https",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers1 = {"User-Agent": user_agent}

    locator_domain = "https://baystatept.com/"

    off = 0
    stop = False
    for i in range(5):
        base_link = "https://locations.baystatept.com/search?l=en&per=50&offset=" + str(
            off
        )
        if stop:
            break
        stores = session.get(base_link, headers=headers).json()["response"]["entities"]
        if len(stores) == 50:
            off = off + 50
        else:
            stop = True

        for row in stores:
            store = row["profile"]

            location_name = store["name"]
            try:
                street_address = (
                    store["address"]["line1"] + " " + store["address"]["line2"]
                ).strip()
            except:
                street_address = store["address"]["line1"]
            city = store["address"]["city"]
            state = store["address"]["region"]
            zip_code = store["address"]["postalCode"]
            country_code = store["address"]["countryCode"]

            store_number = store["meta"]["id"]
            location_type = "<MISSING>"
            phone = store["mainPhone"]["display"]

            latitude = store["yextDisplayCoordinate"]["lat"]
            longitude = store["yextDisplayCoordinate"]["long"]

            try:
                link = store["c_baseURL"]
            except:
                link = store["websiteUrl"]

            logger.info(link)
            final_req = session.get(link, headers=headers1)
            base = BeautifulSoup(final_req.text, "lxml")

            try:
                hours_of_operation = (
                    (
                        " ".join(
                            list(base.find(class_="c-hours-details").stripped_strings)
                        )
                    )
                    .replace("Day of the Week Hours", "")
                    .strip()
                )
            except:
                hours_of_operation = (
                    " ".join(list(base.find(class_="business-hours").stripped_strings))
                    .replace("Hours of Operation:", "")
                    .replace("Hours of Operation", "")
                    .strip()
                )
            try:
                if "coming soon" in base.find(class_="l-row").text.lower():
                    continue
            except:
                pass

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
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
