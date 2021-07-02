from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "winestyles_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://winestyles.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://winestyles.com/store-locator/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "wpb_text_column wpb_content_element"})
        for loc in loclist[1::2]:
            temp = loc.findAll("p")
            page_url = temp[0].find("a")["href"]
            log.info(page_url)
            if len(temp) > 2:
                if len(temp) == 4:
                    hours_of_operation = (
                        temp[1].get_text(separator="|", strip=True).replace("|", " ")
                    )
                else:
                    hours_of_operation = (
                        temp[-2].get_text(separator="|", strip=True).replace("|", " ")
                        + " "
                        + temp[-1].get_text(separator="|", strip=True).replace("|", " ")
                    )
            else:
                hours_of_operation = (
                    temp[-1].get_text(separator="|", strip=True).replace("|", " ")
                )
            hours_of_operation = (
                hours_of_operation.split("Call")[0]
                .replace("Shop Online", "")
                .replace("COVID-19: UPDATED HOURS", "")
                .replace("HOURS", "")
            )
            temp = temp[0].get_text(separator="|", strip=True).split("|")
            location_name = temp[0]

            street_address = temp[1]
            address = temp[2].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            country_code = "US"
            phone = temp[3].replace("Phone:", "")
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
