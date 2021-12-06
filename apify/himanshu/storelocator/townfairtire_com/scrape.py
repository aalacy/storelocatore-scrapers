import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "townfairtire_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}

DOMAIN = "https://townfairtire.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://townfairtire.com/store/tires/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "storeLocations"}).findAll("a")
        temp_list = soup.findAll("div", {"class": "panel panel-default storePanel"})
        for loc in loclist:
            if "NO URL" in loc["href"]:
                name = loc.text
                for temp in temp_list:
                    if name in temp.find("h4").find("span").text:
                        page_url = url
                        log.info(page_url)
                        location_name = temp.find("h4").find("span").text
                        address = temp.find(
                            "div", {"class": "col-md-6 col-sm-7 col-xs-6"}
                        )
                        hours_of_operation = (
                            address.find("div")
                            .get_text(separator="|", strip=True)
                            .replace("|", " ")
                        )
                        address = address.get_text(separator="|", strip=True).split("|")
                        phone = (
                            temp.select_one("button[onclick*=tel]")["onclick"]
                            .replace('location.href="tel:', "")
                            .replace('"', "")
                        )
                        street_address = address[0]
                        address = address[1].split(",")
                        city = address[0]
                        address = address[1].split()
                        state = address[0]
                        zip_postal = address[1]
                        country_code = "US"
                        latitude = MISSING
                        longitude = MISSING
                        break

            else:
                page_url = DOMAIN + loc["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                if soup.find("script", {"type": "application/ld+json"}) is None:
                    continue
                loc = json.loads(
                    soup.find("script", {"type": "application/ld+json"}).text
                )
                location_name = loc["name"]
                address = loc["address"]
                phone = loc["telephone"]
                street_address = address["streetAddress"]
                city = address["addressLocality"]
                state = address["addressRegion"]
                zip_postal = address["postalCode"]
                country_code = address["addressCountry"]
                coords = loc["geo"]
                latitude = coords["latitude"]
                longitude = coords["longitude"]
                hours_of_operation = (
                    soup.find("div", {"class": "storeHours"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("Store Hours", "")
                )
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
