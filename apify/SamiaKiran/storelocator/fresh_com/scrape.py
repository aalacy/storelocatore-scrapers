from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "fresh_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
session = SgRequests()
headers = {
"authority": "www.fresh.com",
"method": "GET",
"path": "/us/customer-service/USShops.html",
"scheme": "https",
"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
"accept-encoding": "gzip, deflate, br",
"accept-language": "en-US,en;q=0.9",
"cache-control": "max-age=0",
"sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
"sec-ch-ua-mobile":"?0",
"sec-fetch-dest": "document",
"sec-fetch-mode": "navigate",
"sec-fetch-site": "none",
"sec-fetch-user": "?1",
"upgrade-insecure-requests": "1",
"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    if True:
        url = "https://www.fresh.com/us/customer-service/USShops.html"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "col-10 col-lg-12 mx-auto text-left"})
        for loc in loclist:
            if len(loc) < 5:
                continue
            else:
                location_name= loc.find("p", {"class": "subheader1 privacy-info-question"})
                page_url = location_name.find("a")["href"]
                log.info(page_url)
                location_name = location_name.text
                address = (
                    loc.findAll("div")[1].get_text(separator="|", strip=True).split("|")
                )
                street_address = address[0]
                phone = address[-1]
                address = address[1].split(",")
                city = address[0]
                address = address[1].split()
                state = address[0]
                zip_postal = address[1]
                hours_of_operation = "<INACCESSIBLE>"
                r = session.get(page_url, headers=headers, verify=False)
                coords = r.text.split("center=")[1].split("&amp;", 1)[0]
                latitude = coords.split("%2C")[0]
                longitude = coords.split("%2C")[1]
                yield SgRecord(
                    locator_domain="https://www.fresh.com/",
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code="US",
                    store_number="<MISSING>",
                    phone=phone.strip(),
                    location_type="<MISSING>",
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
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
