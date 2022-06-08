import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "pizzarock_com_tw"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "http://www.pizzarock.com.tw"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "http://www.pizzarock.com.tw/pizza-rock-locations.html"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("table", {"class": "wsite-multicol-table"})
        for loc in loclist:
            temp = loc.findAll("strong")
            phone = temp[-1].text
            temp_var = loc.get_text(separator="|", strip=True).replace("|", " ")
            temp_var = temp_var.split("Business Hours")
            raw_address = (
                temp_var[0].replace(phone, "").replace("( 02) 8952-6977", "")
            )  # .split('精誠店')[1]
            raw_address = re.split(r"(^[^\d]+)", raw_address)
            location_name = raw_address[1]
            log.info(location_name)
            raw_address = raw_address[-1]
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            if "Hsinchu" in phone:
                phone = "(03) 577-5705"
            if "0" not in phone:
                phone = MISSING

            try:
                hours_of_operation = (
                    temp_var[1]
                    .split("Last Call")[0]
                    .replace("營業時間：", "")
                    .replace("營業時間:", "")
                )
            except:
                hours_of_operation = MISSING
            if "Open during games" in hours_of_operation:
                hours_of_operation = MISSING
            coords = loc.find("iframe")["src"]
            longitude = coords.split("long=")[1].split("&")[0]
            latitude = coords.split("lat=")[1].split("&")[0]
            country_code = "TW"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
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
