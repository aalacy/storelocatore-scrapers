import json
import html
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "9round_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.9round.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.9round.com/locations/directory"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("li", {"class": "pb-1"})
        for loc in loclist:
            url = "https://www.9round.com" + loc.find("a")["href"]
            r = session.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            state_list = soup.findAll("a", {"class": "lead"})
            for link in state_list:
                page_url = "https://www.9round.com" + link["href"]
                if (
                    "https://www.9round.com/locations/nj/south-plainfield/stelton-rd"
                    in page_url
                ):
                    continue
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                log.info(page_url)
                try:
                    temp = r.text.split("<script type='application/ld+json'>")[1].split(
                        "</script>", 1
                    )[0]
                    temp = json.loads(temp)
                    location_name = html.unescape(temp["name"])
                    latitude = temp["geo"]["latitude"]
                    longitude = temp["geo"]["longitude"]
                    hours_of_operation = temp["openingHours"]
                    try:
                        phone = (
                            soup.select_one("a[href*=tel]")
                            .text.replace("\n", "")
                            .replace("Call: ", "")
                        )
                    except:
                        phone = "<MISSING>"
                    street_address = html.unescape(temp["address"]["streetAddress"])
                    city = html.unescape(temp["address"]["addressLocality"])
                    state = temp["address"]["addressRegion"]
                    zip_postal = temp["address"]["postalCode"]
                except:
                    try:
                        try:
                            address = soup.find("li", {"class": "pb-1"}).text
                            location_name = soup.find("h2").text.replace("\n", "")
                        except:
                            address = link.text
                            location_name = MISSING

                        address = address.split("-")
                        street_address = address[1]
                        address = address[0].split(",")
                        city = address[0]
                        state = address[1]
                        zip_postal = MISSING
                        phone = MISSING
                        hours_of_operation = MISSING
                        latitude = MISSING
                        longitude = MISSING
                    except:
                        continue
                country_code = "US"
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
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
