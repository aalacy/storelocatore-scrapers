import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "outofthecloset_org"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
}

DOMAIN = "https://outofthecloset.org/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://locations.outofthecloset.org/"
        r = session.get(url, headers=headers)
        loclist = r.text.split(
            '"dataLocations":{"collection":{"type":"FeatureCollection","features":'
        )[1].split('},"uiLocationsList"')[0]
        loclist = json.loads(loclist)
        for loc in loclist:
            location_name = loc["properties"]["name"]
            coords = loc["geometry"]["coordinates"]
            latitude = coords[1]
            longitude = coords[0]
            page_url = (
                "https://locations.outofthecloset.org/" + loc["properties"]["slug"]
            )
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            loc = r.text.split('"callToAction":null},')[1].split(',"cmsFeature')[0]
            loc = json.loads("{" + loc + "}")
            try:
                street_address = loc["addressLine1"] + " " + loc["addressLine2"]
            except:
                street_address = loc["addressLine1"]
            city = loc["city"]
            state = loc["province"]
            zip_postal = loc["postalCode"]
            country_code = loc["country"]
            phone = loc["phoneLabel"]
            hours_of_operation = ""
            hours_of_operation = str(loc["hoursOfOperation"])
            hours_of_operation = (
                hours_of_operation.replace("', '", "-")
                .replace("[[", "")
                .replace("]]", "")
                .replace("'", "")
                .replace(",", " ")
                .replace("{", "")
                .replace("}", "")
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
                phone=phone,
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
