from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup


session = SgRequests()
website = "iombank_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Cookie": "ApplicationGatewayAffinity=031e25b65450db90b3bc1edb3b0fc505; ApplicationGatewayAffinityCORS=031e25b65450db90b3bc1edb3b0fc505"
}
DOMAIN = "https://iombank.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    search_url = "https://www.iombank.com/global/find-a-branch.html"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    loc_block = soup.find("div", {"id": "branch-locator"}).findAll(
        "div",
        {
            "class": "col-xs-11 col-sm-6 col-md-6 col-lg-7 single-content multi-content flt__item"
        },
    )
    for loc in loc_block:
        title = loc.find("h3").text.strip()
        address = loc.find("div", {"class": "h4"}).find("span").text
        details = loc.findAll("li")
        phone = details[0].text
        try:
            hours = details[2].text
        except IndexError:
            hours = "<MISSING>"

        if address != "Our mobile branch":
            state = MISSING
            address = address.split(",")
            street = address[0].strip()
            city = address[1].strip()
            pcode = address[2].strip()
            country = "UK"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=DOMAIN,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code=country,
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID(
            {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.HOURS_OF_OPERATION}
        )
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
