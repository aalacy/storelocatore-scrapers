from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "bagels4u_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.bagels4u.com/locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find(
            "div", {"data-mesh-id": "Containerma4c9inlineContent-gridContainer"}
        ).findAll("div", {"data-testid": "richTextElement"})[1:-1]
        for loc in loclist:
            temp = loc.get_text(separator="|", strip=True).split("|")
            if "\u200b" in temp[-1]:
                temp = temp[:-1]
            if "Tel.:" in temp[-2]:
                del temp[-2]
            location_name = temp[0]
            log.info(location_name)
            phone = temp[-1].replace("Tel.: ", "").replace("Tel.:  ", "")
            street_address = " ".join(x for x in temp[1:-2])
            address = temp[-2].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]

            yield SgRecord(
                locator_domain="https://www.bagels4u.com/",
                page_url="https://www.bagels4u.com/locations",
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="US",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude="<MISSING>",
                longitude="<MISSING>",
                hours_of_operation="<MISSING>",
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
