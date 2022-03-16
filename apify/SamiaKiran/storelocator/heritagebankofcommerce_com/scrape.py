from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "heritagebankofcommerce_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}

DOMAIN = "https://heritagebankofcommerce.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.heritagebankofcommerce.bank/Locations-and-Hours.aspx"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("table", {"class": "Table-Simple-Alternate"})
        for loc in loclist:
            temp = loc.findAll("p")
            location_name = loc.find("h2").text
            log.info(location_name)
            if "ATM Available" in temp[3].text:
                del temp[3]
            if "(Former Presidio Bank Office)" in temp[0].text:
                del temp[0]
            if len(temp) > 4:
                address = temp[3]
            else:
                address = temp[2]
            phone = temp[0].text.replace("Phone:", "")
            hours_of_operation = (
                temp[1].get_text(separator="|", strip=True).replace("|", " ")
            )
            hours_of_operation = hours_of_operation.replace("Hours:", "")
            address = address.get_text(separator="|", strip=True).split("|")[1:]
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            country_code = "US"
            try:
                if "maps" in loc.find("a")["href"]:
                    coords = loc.find("a")["href"].split("!1d")[1].split("!2d")
                    latitude = coords[1]
                    longitude = coords[0]
                else:
                    coords = loc.find("a")["href"].split(",")
                    latitude = coords[0].split("-")[-1]
                    longitude = coords[1].split("&")[0]
            except:
                latitude = MISSING
                longitude = MISSING

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name.strip(),
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
