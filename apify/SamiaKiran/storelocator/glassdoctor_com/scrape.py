import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "glassdoctor_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://glassdoctor.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://glassdoctor.com/locations-sitemap"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "view-content"}).findAll(
            "div", {"class": "field-content"}
        )
        for loc in loclist:
            page_url = loc.find("a")["href"]
            if loc.find("a").text == "Michigan":
                continue
            log.info(page_url)
            r = session.get(page_url, headers=headers, allow_redirects=True)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("h1").text.replace("\n", "")
            try:
                street_address = soup.find("span", {"itemprop": "streetAddress"}).text
                city = soup.find("span", {"itemprop": "addressLocality"}).text
                state = soup.find("span", {"itemprop": "addressRegion"}).text
                zip_postal = soup.find("span", {"itemprop": "postalCode"}).text
                phone = soup.select_one("a[href*=tel]").text.replace("Call", "")
                if "Click to" in phone:
                    phone = soup.find("a", {"class": "fnt_phn"}).text
            except:
                continue
            if re.search("[a-zA-Z]", zip_postal):
                country_code = "CA"
            else:
                country_code = "US"
            try:
                coords = soup.select_one("iframe[src*=maps]")["src"]
                r = session.get(coords, headers=headers)
                coords = r.text.split("],0],")[0].rsplit("[null,null,", 1)[1].split(",")
                latitude = coords[0]
                longitude = coords[1]
                if "null" in latitude:
                    coords = (
                        r.text.split("],5],")[0].rsplit("[null,null,", 1)[1].split(",")
                    )
                    latitude = coords[0]
                    longitude = coords[1]
                    if "null" in latitude:
                        coords = r.text.split("],")[3].rsplit(",[", 1)[1].split(",")
                        latitude = coords[0]
                        longitude = coords[1]
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
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
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
