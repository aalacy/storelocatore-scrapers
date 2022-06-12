import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "wrenkitchens_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.wrenkitchens.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.wrenkitchens.com/showrooms"
        r = session.get(url, headers=headers)
        loclist = r.text.split('"intBranchAddressId"')[1:]
        for loc in loclist:
            loc = '{"intBranchAddressId"' + loc.split(',"objBranches"')[0] + "}"
            loc = json.loads(loc)
            location_name = loc["strFriendlyName"]
            store_number = loc["intBranchAddressId"]
            try:
                street_address = loc["strAddress1"] + " " + loc["strAddress2"]
            except:
                street_address = loc["strAddress1"]
            city = loc["strTown"]
            state = loc["strCounty"]
            zip_postal = loc["strPostcode"]
            country_code = "GB"
            latitude = loc["decLatitude"]
            longitude = loc["decLongitude"]
            temp = location_name.lower()
            if "-" in temp:
                temp = temp.split("-")[0].strip()
            elif "/" in temp:
                temp = temp.replace(" / ", "-")
            page_url = "https://www.wrenkitchens.com/showrooms/" + temp.replace(
                " ", "-"
            )
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            phone = (
                soup.find("span", {"class": "showroom-phone-number"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            hours_of_operation = (
                soup.find("table", {"class": "showroom-opening-times"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("\n", " ")
                .split("*10:30 ")[0]
            )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
