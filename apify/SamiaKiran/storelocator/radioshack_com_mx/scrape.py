import math
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "radioshack_com_mx"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.radioshack.com.mx"
MISSING = SgRecord.MISSING


def get_data(loc):
    location_name = loc["displayName"]
    store_number = loc["name"]
    phone = loc["WhatsApp"]
    street_address = loc["line1"]
    city = loc["town"]
    zip_postal = loc["postalCode"]
    phone = loc["phone"]
    latitude = loc["latitude"]
    longitude = loc["longitude"]
    if latitude == "0.0":
        if longitude == "0.0":
            latitude, longitude = (
                loc["url"].split("lat=")[1].split("&q=")[0].split("&long=")
            )
    hours_of_operation = (
        str(loc["openings"])
        .replace("', '", " ")
        .replace("': '", " ")
        .replace("{'", "")
        .replace("'}", "")
    )
    if "-  jue  -  vie  -" in hours_of_operation:
        hours_of_operation = MISSING
    return (
        location_name,
        store_number,
        phone,
        street_address,
        city,
        zip_postal,
        phone,
        latitude,
        longitude,
        hours_of_operation,
    )


def fetch_data():
    if True:
        url = "https://www.radioshack.com.mx/store/radioshack/en/store-finder"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        state_list = soup.find("select", {"id": "address.region"}).findAll("option")[1:]
        for temp_state in state_list:
            state = temp_state["value"]
            api_url = (
                "https://www.radioshack.com.mx/store/radioshack/en/store-finder?q="
                + state.replace(" ", "+")
                + "&page=0"
            )
            r = session.get(api_url, headers=headers).json()
            loclist = r["data"]
            total = r["total"]
            country_code = "Mexico"
            if total > 10:
                page_list = math.ceil(total / 10)
                for page in range(page_list):
                    api_url = (
                        "https://www.radioshack.com.mx/store/radioshack/en/store-finder?q="
                        + state.replace(" ", "+")
                        + "&page="
                        + str(page)
                    )
                    r = session.get(api_url, headers=headers).json()
                    loclist = r["data"]
                    for loc in loclist:
                        (
                            location_name,
                            store_number,
                            phone,
                            street_address,
                            city,
                            zip_postal,
                            phone,
                            latitude,
                            longitude,
                            hours_of_operation,
                        ) = get_data(loc)
                        log.info(location_name)
                        yield SgRecord(
                            locator_domain=DOMAIN,
                            page_url=url,
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
                            hours_of_operation=hours_of_operation.strip(),
                        )
            else:
                for loc in loclist:
                    (
                        location_name,
                        store_number,
                        phone,
                        street_address,
                        city,
                        zip_postal,
                        phone,
                        latitude,
                        longitude,
                        hours_of_operation,
                    ) = get_data(loc)
                    log.info(location_name)
                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=url,
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
                        hours_of_operation=hours_of_operation.strip(),
                    )


def scrape():
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
