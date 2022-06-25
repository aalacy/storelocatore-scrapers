from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "la-mesa_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://la-mesa.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://la-mesa.com/locations/"
        r = session.get(url, headers=headers)
        loclist = r.text.split('<div class="et_pb_module et_pb_code')[1:]
        for loc in loclist:
            loc = '<div class="et_pb_module et_pb_code' + loc
            loc = BeautifulSoup(loc, "html.parser")
            try:
                coords = loc.select_one("iframe[src*=maps]")["src"]
            except:
                continue
            longitude, latitude = (
                coords.split("!2d", 1)[1].split("!2m", 1)[0].split("!3d")
            )
            phone = loc.select_one("a[href*=tel]").text
            loc = loc.find("p").get_text(separator="|", strip=True).split("|")
            location_name = loc[0]
            street_address = loc[1]
            address = loc[2].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            temp = street_address.lower().replace(" ", "-")
            if "," in street_address:
                temp = temp.split(",")[0]
            page_url = (
                "https://la-mesa.com/locations/"
                + city.lower().replace(" ", "-")
                + "/"
                + temp
            )
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                try:
                    hours_of_operation = soup.findAll(
                        "div", {"class": "et_pb_text_inner"}
                    )[-3]

                except:
                    hours_of_operation = soup.find("div", {"class": "et_pb_text_inner"})
                if "About La Mesa Mexican" in str(hours_of_operation):
                    hours_of_operation = soup.findAll(
                        "div", {"class": "et_pb_text_inner"}
                    )[4]
                hours_of_operation = (
                    hours_of_operation.get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("Hours", "")
                )
            else:
                hours_of_operation = MISSING
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
