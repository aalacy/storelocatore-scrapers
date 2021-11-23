import unicodedata
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "samssoutherneatery_com"
log = SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}
DOMAIN = "https://samssoutherneatery.com/"
MISSING = "<MISSING>"


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://samssoutherneatery.com/locations-list"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        divs = soup.findAll("div", {"class": "Index-page-content"})
        for div in divs[2:]:
            loclist = div.find_all("a")
            for loc in loclist:
                if "Southern Eatery" not in loc.text:
                    continue
                page_url = "https://samssoutherneatery.com" + loc["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, "html.parser")
                    temp = (
                        soup.find("div", {"class": "sqs-block-content"})
                        .get_text(separator="|", strip=True)
                        .split("|")
                    )
                    if len(temp) == 1:
                        temp = (
                            soup.find_all("div", {"class": "sqs-block-content"})[1]
                            .get_text(separator="|", strip=True)
                            .split("|")[1:-1]
                        )
                else:
                    templist = div.find_all("div", {"class": "col sqs-col-3 span-3"})[
                        22
                    ]

                    for temp in templist:
                        if temp.find("a").text == loc.text:
                            break
                    temp = (
                        temp.find("div", {"class": "sqs-block-content"})
                        .get_text(separator="|", strip=True)
                        .split("|")
                    )

                location_name = temp[0]
                location_name = strip_accents(location_name)
                street_address = temp[1]
                address = temp[2].split(",")
                city = address[0]
                address = address[1].split()
                state = address[0]
                country_code = "US"
                try:
                    zip_postal = address[1]
                except:
                    zip_postal = MISSING

                location_type = MISSING
                phone = temp[-1]
                if "OPENING SOON!" in temp[-1]:
                    phone = MISSING
                    location_type = "COMING SOON"
                if "Online Ordering Coming Soon!" in temp[-1]:
                    phone = MISSING
                    location_type = "COMING SOON"
                if "Coming soon!" in r.text:
                    location_type = "COMING SOON"
                if len(temp) == 3:
                    phone = MISSING
                try:
                    coords = r.text.split("mapLat&quot;:")[1].split("&")
                    latitude = coords[0].replace(",", "")
                    longitude = coords[2].replace("quot;:", "").replace(",", "")

                except:
                    latitude = MISSING
                    longitude = MISSING
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
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude.strip(),
                    longitude=longitude.strip(),
                    hours_of_operation=MISSING,
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
