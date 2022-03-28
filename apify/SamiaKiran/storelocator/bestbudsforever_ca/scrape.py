from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "bestbudsforever_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://bestbudsforever.ca/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        r = session.get(DOMAIN, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("ul", {"class": "nav-dropdown nav-dropdown-default"})[
            2
        ].findAll("li")
        for loc in loclist:
            location_name = loc.text
            page_url = loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                temp = r.text.split('<script type="application/ld+json">')[1].split(
                    "</script>"
                )[0]
                street_address = temp.split('"streetAddress": "')[1].split('"')[0]
                city = temp.split('"addressLocality": "')[1].split('"')[0]
                state = temp.split('"addressRegion": "')[1].split('"')[0]
                zip_postal = temp.split('"postalCode": "')[1].split('"')[0]
                latitude = temp.split('"latitude":')[1].split(",")[0]
                longitude = (
                    temp.split(' "longitude": ')[1].split("}")[0].replace("\n", "")
                )
                phone = temp.split('"telephone":"+')[1].split('"')[0]
            except:
                address = (
                    soup.find("div", {"class": "map_inner"})
                    .get_text(separator="|", strip=True)
                    .split("|")[1:-1]
                )
                if "-" in address[-1]:
                    phone = address[-1]
                else:
                    phone = soup.select_one("a[href*=tel]").text
                street_address = address[0]
                temp_address = address[1].split(",")
                city = temp_address[0]
                state = temp_address[1]
                zip_postal = address[2]
                coords = r.text.split("LatLng(")[1].split(")")[0].split(",")
                latitude = coords[0]
                longitude = coords[1]
            hours_of_operation = (
                soup.findAll("div", {"class": "col-inner text-left"})[1]
                .findAll("p")[1]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            if "," in city:
                city = city.split(",")[1]
            country_code = "CA"
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
