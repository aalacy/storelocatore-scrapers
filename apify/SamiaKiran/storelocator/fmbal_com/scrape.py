from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "fmbal_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://fmbal.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.fmbal.com/about/our-locations/"
        r = session.get(url, headers=headers)
        loclist = r.text.split("var myLatLng = new google.maps.LatLng(")[1:]
        for loc in loclist:
            latitude, longitude = loc.split(");")[0].split(",")
            loc = loc.split('<div class="row one-location">')[1].split("</table>")[0]
            loc = '<div class="row one-location">' + loc + "</table>"
            soup = BeautifulSoup(loc, "html.parser")
            location_name = soup.find("h2").text
            if "ATM" in location_name:
                continue
            log.info(location_name)
            temp = soup.findAll("p")
            address = temp[0].text.strip().split("\n")
            phone = (
                temp[1]
                .get_text(separator="|", strip=True)
                .split("|")[0]
                .replace("phone", "")
            )
            hours_of_operation = (
                soup.find("table").get_text(separator="|", strip=True).replace("|", " ")
            )
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            country_code = "US"
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
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
