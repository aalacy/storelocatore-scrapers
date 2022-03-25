import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "carryout_ie"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.carryout.ie/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.carryout.ie/find-your-local-store/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "gv-field-8-9"})
        for loc in loclist:
            page_url = loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            temp = r.text.split('"markers_info":[')[1].split('],"map_id_prefix"')[0]
            temp = json.loads(temp)
            store_number = temp["entry_id"]
            latitude = temp["lat"]
            longitude = temp["long"]
            html = BeautifulSoup(temp["content"], "html.parser")
            location_name = html.find("h4").text
            temp = html.findAll("p")
            raw_address = temp[0].text.replace("Address:", "")
            try:
                phone = (
                    temp[1]
                    .get_text(separator="|", strip=True)
                    .split("|")[1]
                    .replace("053-9481660 053-9481665", "053-9481660")
                )
            except:
                phone = MISSING
            address = raw_address.split(",")[:-1]
            address = ", ".join(address)
            pa = parse_address_intl(address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            state = pa.state
            state = state.strip() if state else MISSING
            try:
                zip_postal = raw_address.split(",")
                city = zip_postal[-2]
                zip_postal = zip_postal[-1]
            except:
                zip_postal = MISSING
                city = MISSING
            country_code = "Ireland"
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
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=MISSING,
                raw_address=raw_address,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
