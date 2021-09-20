from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "rubytuesday_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}

DOMAIN = "https://rubytuesday.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    link = "https://rubytuesday.com/locations?address=AL"
    count = 1
    while True:
        r = session.get(link)
        soup = BeautifulSoup(r.text, "html.parser")
        divlist = soup.findAll("div", {"class": "restaurant-location-item"})
        for div in divlist:
            location_name = div.find("h1").text
            log.info(location_name)
            address = div.find("address").text.lstrip().splitlines()
            street_address = address[0]
            city = address[1].lstrip().replace(",", "")
            state = address[2].lstrip()
            zip_postal = address[3].lstrip()
            phone = div.find("a").text.strip()
            if phone.find("-") == -1:
                phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
            hourlist = div.find("table").findAll("tr", {"class": "hourstr"})
            hours_of_operation = " ".join(
                x.get_text(separator="|", strip=True).replace("|", " ")
                for x in hourlist
            )
            store_number = div["id"].split("-")[1]
            coord = div.find("div", {"class": "map_info"})
            latitude = coord["data-lat"]
            longitude = coord["data-lng"]
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://rubytuesday.com/locations",
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
                hours_of_operation=hours_of_operation,
            )
        try:
            nextlink = soup.find("ul", {"class": "pages"}).findAll("a")[-1]
            link = nextlink["href"]
            count = count + 1
        except:
            break


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
