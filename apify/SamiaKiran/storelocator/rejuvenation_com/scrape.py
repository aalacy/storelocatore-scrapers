import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "rejuvenation_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.rejuvenation.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.rejuvenation.com/landing/store-search"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll(
            "div",
            {
                "class": "cms-equal_width_column_control-col cms-image-block-col mobile-only"
            },
        )
        for loc in loclist[:-1]:
            if "PERMANENTLY CLOSED" in loc.text:
                continue
            temp = loc.findAll("p")
            try:
                page_url = (
                    loc.findAll("button")[1]["onclick"]
                    .replace("window.location.href = '", "")
                    .replace("';", "")
                )
            except:
                continue
            if DOMAIN not in page_url:
                page_url = DOMAIN + page_url
            r = session.get(page_url, headers=headers)
            latitude = r.text.split('"latitude": "')[1].split('"')[0]
            longitude = r.text.split('"longitude": "')[1].split('"')[0]
            soup = BeautifulSoup(r.text, "html.parser")
            log.info(page_url)
            location_name = temp[1].text
            phone = loc.select_one("a[href*=tel]").text
            hours_of_operation = (
                temp[5].get_text(separator="|", strip=True).replace("|", " ")
            )
            raw_address = temp[2].get_text(separator="|", strip=True).replace("|", " ")
            address = raw_address.replace(",", " ")
            address = usaddress.parse(address)
            i = 0
            street_address = ""
            city = ""
            state = ""
            zip_postal = ""
            while i < len(address):
                temp = address[i]
                if (
                    temp[1].find("Address") != -1
                    or temp[1].find("Street") != -1
                    or temp[1].find("Recipient") != -1
                    or temp[1].find("Occupancy") != -1
                    or temp[1].find("BuildingName") != -1
                    or temp[1].find("USPSBoxType") != -1
                    or temp[1].find("USPSBoxID") != -1
                ):
                    street_address = street_address + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    zip_postal = zip_postal + " " + temp[0]
                i += 1
            country_code = "US"
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
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
