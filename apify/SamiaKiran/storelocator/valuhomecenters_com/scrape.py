from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "authority": "valuhomecenters.com",
    "content-type": "application/json; charset=UTF-8",
    "method": "POST",
    "origin": "https://valuhomecenters.com",
    "path": "/StoreLocator/HeaderDialogMyStore",
    "referer": "https://valuhomecenters.com/south-cheektowaga-ny",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "x-mod-sbb-ctype": "xhr",
    "x-requested-with": "XMLHttpRequest",
}

session = SgRequests()
website = "valuhomecenters_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

DOMAIN = "https://valuhomecenters.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://valuhomecenters.com/locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "HTMLContent"}).findAll("li")
        url_hours = "https://valuhomecenters.com/StoreLocator/HeaderDialogMyStore"
        hours_of_operation = session.post(url_hours, headers=headers).json()[
            "Response"
        ]["HeaderDialogMyStoreContent"]
        hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
        hours_of_operation = " ".join(x.text for x in hours_of_operation.findAll("li"))
        for loc in loclist:
            page_url = "https://valuhomecenters.com" + loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            if "Coming Spring" in r.text:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("h1", {"class": "PageHeaderTitle"}).text
            address = (
                soup.find("div", {"class": "HTMLContent"})
                .find("p")
                .get_text(separator="|", strip=True)
                .split("|")
            )
            phone = address[2].replace("Phone:", "")
            street_address = address[0]
            address = address[1].replace("NY", "NY ").split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
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
                latitude=MISSING,
                longitude=MISSING,
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
