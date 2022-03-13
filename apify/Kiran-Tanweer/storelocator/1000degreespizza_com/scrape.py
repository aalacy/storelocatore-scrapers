from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "1000degreespizza_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.1000degreespizza.com",
    "method": "GET",
    "path": "/pizza-place-near-me-locations/",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "identity",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "_ga=GA1.2.151889300.1611623194; _gid=GA1.2.2137413542.1611623194; _gat=1",
    "referer": "https://www.1000degreespizza.com/pizza-place-near-me-locations/",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}

DOMAIN = "www.1000degreespizza.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.1000degreespizza.com/pizza-place-near-me-locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        locations = soup.findAll("div", {"class": "location-1000d"})
        for info in locations:
            atgs = info.findAll("a")
            details = info.text.strip()
            details = details.split("\n")
            if len(details) == 4:
                title = details[0].strip()
                street = details[1].strip()
                locality = details[2].strip()
                phone = details[3].strip()
            if len(details) == 5:
                if details[-1].find("CLOSED TEMPORARILY") != -1:
                    title = details[0].strip()
                    street = details[1].strip()
                    locality = details[2].strip()
                    phone = details[3].strip()
                elif details[-1].find("NOW OPEN!") != -1:
                    title = details[0].strip()
                    street = details[1].strip()
                    locality = details[2].strip()
                    phone = details[3].strip()
                else:
                    title = details[0].strip()
                    street = details[-3].strip()
                    locality = details[-2].strip()
                    phone = details[-1].strip()
            if phone == "OPENING SOON!":
                phone = "<MISSING>"
                hours = "OPENING SOON!"
            else:
                if details[-1].find("CLOSED TEMPORARILY") != -1:
                    hours = details[-1]
                else:
                    hours = "<MISSING>"
            try:
                link = atgs[-1]
                link = str(link)
                link = link.split("<picture>")[0]
                link = link.replace('<a href="', "")
                link = link.replace('" style="margin-top: 20px;">', "")
                link = link.replace("</a>", "")
                if link.find("/<img alt") != -1:
                    link = link.split("/<img alt")[0]
                if link.find("revelup.com") != -1:
                    link = SgRecord.MISSING
                if link.find("..") != -1:
                    link = link.replace("..", "https://www.1000degreespizza.com")
            except IndexError:
                link = SgRecord.MISSING
            locality = locality.split(",")

            city = locality[0].strip()
            state = locality[1].strip()

            if state == "Delaware":
                state = "DE"
            if state == "Florida":
                state = "FL"
            if state == "Georgia":
                state = "GA"
            if state == "Iowa":
                state = "IA"
            if state == "Michigan":
                state = "MI"
            if state == "Minnesota":
                state = "MN"
            if state == "New Jersey":
                state = "NJ"
            if state == "South Dakota":
                state = "SD"
            if state == "Tennessee":
                state = "TN"
            if state == "Texas":
                state = "TX"
            if state == "Utah":
                state = "UT"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=link,
                location_name=title,
                street_address=street,
                city=city,
                state=state,
                zip_postal=MISSING,
                country_code="US",
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
