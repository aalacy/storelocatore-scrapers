from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "oberweis"
log = sglog.SgLogSetup().get_logger(logger_name=website)

url = "https://www.oberweis.com/api/StoreFinder"

payload = '{"latitude":41.79818400000001,"longitude":-88.348431,"searchOberweis":true,"searchRetail":true,"distance":320}'
headers = {
    "authority": "www.oberweis.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json;charset=UTF-8",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://www.oberweis.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.oberweis.com/search/find-a-store",
    "accept-language": "en-US,en;q=0.9",
}

DOMAIN = "https://www.oberweis.com/"
MISSING = SgRecord.MISSING


def get_stores(loc):
    location_name = loc["name"]
    try:
        page_url = loc["location"]
        page_url = page_url.replace(" ", "%20")
        page_url = "https://oberweis.com/ice-cream-and-dairy-stores/" + page_url
    except:
        page_url = "https://www.oberweis.com/search/find-a-store"
    log.info(location_name)
    try:
        phone = loc["phone"]
    except:
        phone = MISSING
    street_address = loc["address"].replace("DELIVERY TO:", "")
    city = loc["city"]
    state = loc["state"]
    zip_postal = loc["zipCode"]
    try:
        longitude = loc["coordinates"]["longitude"]
        latitude = loc["coordinates"]["latitude"]
    except:
        latitude = MISSING
        longitude = MISSING
    try:
        hours = loc["description"]
        hours = hours.replace("<br>", " ").replace("<b>", "").replace("</b>", " ")
        hours = hours.split("Store Hours", 1)
        phone = hours[0].split("Phone:", 1)[1].split("Email", 1)[0].strip()
        hours_of_operation = hours[1]
        if "This location is" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("This location")[0]
    except:
        hours_of_operation = MISSING

    country_code = "US"
    return (
        location_name,
        page_url,
        street_address,
        city,
        state,
        zip_postal,
        latitude,
        longitude,
        hours_of_operation,
        country_code,
        phone,
    )


def fetch_data():
    if True:
        loclist = session.post(url, data=payload, headers=headers).json()
        oberweis = loclist["oberweis"]
        retail = loclist["retail"]
        for loc in oberweis:
            (
                location_name,
                page_url,
                street_address,
                city,
                state,
                zip_postal,
                latitude,
                longitude,
                hours_of_operation,
                country_code,
                phone,
            ) = get_stores(loc)
            location_type = "Oberweis"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        for loc in retail:
            (
                location_name,
                page_url,
                street_address,
                city,
                state,
                zip_postal,
                latitude,
                longitude,
                hours_of_operation,
                country_code,
                phone,
            ) = get_stores(loc)
            location_type = "Retail"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
