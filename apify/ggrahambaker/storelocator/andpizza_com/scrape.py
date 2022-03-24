from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "andpizza_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://andpizza.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://andpizza.com/wp-content/themes/andpizza/assets/js/scripts.js?ver=06072021"
    log.info("Fetching the Bearer Token...")
    r = session.get(url, headers=headers)
    Bearer = r.text.split("'Authorization','")[1].split("');},")[0]
    api_url = "https://api.andpizza.com/webapi/v100/partners/shops"
    headers_2 = {
        "authority": "api.andpizza.com",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        "accept": "*/*",
        "authorization": Bearer,
        "sec-ch-ua-mobile": "?1",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Mobile Safari/537.36",
        "sec-ch-ua-platform": '"Android"',
        "origin": "https://andpizza.com",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://andpizza.com/",
        "accept-language": "en-US,en;q=0.9",
    }
    loclist = session.get(api_url, headers=headers_2).json()["data"]
    for loc in loclist:
        location_name = loc["name"]
        log.info(location_name)
        addy = loc["location"]
        street_address = addy["address1"]
        if addy["address2"] is not None:
            street_address += " " + addy["address2"]
        street_address = street_address.replace("3041 3041", "3041").strip()
        city = addy["city"]
        state = addy["state"]
        zip_postal = addy["zipcode"]
        phone = addy["phone"]
        latitude = addy["latitude"]
        longitude = addy["longitude"]
        hours = ""
        for day in loc["service_schedule"]["general"]:
            hours += day["label"] + " " + day["value"] + " "
        country_code = "US"
        page_url = "https://andpizza.com/locations/"
        store_number = loc["id"]
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours,
        )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
