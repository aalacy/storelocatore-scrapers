from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://mobile.incentivio.com/incentivio-mobile-api/locations?count=10000&latitude=0&longitude=0&page=0&radius=11029160&sortby=title&sortdirection=DESC&langCode=en&iscatering=false"

    session = SgRequests()

    headers = {
        "authority": "mobile.incentivio.com",
        "method": "GET",
        "path": "/incentivio-mobile-api/locations?count=10000&latitude=0&longitude=0&page=0&radius=11029160&sortby=title&sortdirection=DESC&langCode=en&iscatering=false",
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "clientid": "d5aa1ae6-68f4-4823-a5f0-9c9c2044ae93",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }

    stores = session.get(base_link, headers=headers).json()["stores"]

    locator_domain = "urbanbrickskitchen.com"

    for store in stores:
        location_name = store["title"]
        try:
            street_address = (
                store["address"]["streetAddress1"]
                + " "
                + store["address"]["streetAddress2"]
            ).strip()
        except:
            street_address = store["address"]["streetAddress1"]
        city = store["address"]["city"]
        state = store["address"]["region"]
        if city == "San Antonio":
            state = "Texas"
        zip_code = store["address"]["postalCode"]
        country_code = store["address"]["country"]
        store_number = store["storeCode"].replace("STR:", "")
        location_type = "<MISSING>"
        phone = store["phoneNumber"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        link = "https://order.incentivio.com/c/urbanbrickspizza/"

        hours_of_operation = ""
        raw_hours = store["pickupOrderHours"]
        for hours in raw_hours:
            day = hours["dayOfWeek"]
            if len(day[0]) != 1:
                day = " ".join(hours["dayOfWeek"])
            opens = hours["startTime"]
            closes = hours["endTime"]
            if opens != "" and closes != "":
                clean_hours = day + " " + opens + "-" + closes
                hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
