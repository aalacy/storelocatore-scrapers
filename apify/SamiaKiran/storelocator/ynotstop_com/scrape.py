from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "ynotstop_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

DOMAIN = "https://www.ynotstop.com/"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}


def fetch_data():
    if True:
        url = "http://www.ynotstop.com/stores"
        r = session.get(url, headers=headers)
        coords = (
            r.text.split(
                "var companyMarker = new Array();",
            )[1]
            .split("var contentString = ", 1)[0]
            .strip()
        )
        coords = coords.replace("\n", "").replace("\t", "").replace('"', "")
        coords = coords.split("new google.maps.Marker({")[1:]
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "store-text"})
        for loc, temp_coords in zip(loclist, coords):
            if "Coming soon!" in loc.text:
                continue
            page_url = loc.find("div", {"class": "store-btn"}).find("a")["rel"][0]
            store_number = loc.find("a", {"class": "PlanRoute"})["data-rel"].split("~")[
                0
            ]
            address = (
                loc.find("div", {"class": "link location"})
                .get_text(separator="|", strip=True)
                .split("|")
            )
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            state = address[1]
            zip_postal = address[2]
            country_code = "US"
            try:
                phone = loc.find("div", {"class": "link tel"}).text
            except:
                phone = MISSING
            location_name = loc.find("div", {"class": "store-heading"}).find("h6").text
            log.info(page_url)
            try:
                hours_of_operation = (
                    loc.find("div", {"class": "desc FParagraph EditorText"})
                    .find("li")
                    .text.split("|")[0]
                )
            except:
                loc.find("div", {"class": "desc FParagraph EditorText"}).find("li").text
            latitude, longitude = (
                temp_coords.split("LatLng(")[1].split("),", 1)[0].split(",")
            )
            if hours_of_operation == "Licensed Store":
                hours_of_operation = MISSING
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
