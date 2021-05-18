from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter


website = "wahlburgers_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://wahlburgers.com/all-locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.find("div", {"class": "cell medium-6"}).findAll("a")
        for link in linklist:
            page_url = "https://wahlburgers.com" + link["href"]
            log.info(page_url)
            if "Coming soon" in page_url:
                continue
            if "canada" in page_url:
                country_code = "Canada"
            elif "germany" in page_url:
                country_code = "Germany"
            else:
                country_code = "USA"
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.find("div", {"class": "cell"}).findAll(
                "a", {"class": "fadey"}
            )
            for loc in loclist:
                try:
                    page_url = "https://wahlburgers.com" + loc["href"]
                    r = session.get(page_url, headers=headers)
                    if "Coming soon" in r.text:
                        continue
                    soup = BeautifulSoup(r.text, "html.parser")
                    temp = soup.find("div", {"class": "insideThing"}).findAll("div")
                except:
                    continue
                log.info(page_url)
                location_name = (
                    soup.find("div", {"class": "location whitepage"})
                    .find("h1")
                    .text.replace("@", "")
                    .replace("\n", "")
                    .split()
                )
                location_name = " ".join(x for x in location_name)
                if "General Manager:" in temp[-1].text:
                    del temp[-1]
                if len(temp) > 3:
                    temp = temp[1:]
                phone = temp[0].find("a")["href"].replace("tel:", "")
                address = temp[1].get_text(separator="|", strip=True).split("|")[1:]
                hours_of_operation = (
                    temp[2].get_text(separator="|", strip=True).replace("|", " ")
                )
                street_address = address[0]
                address = address[1].split("\n")
                city = address[0].replace(",", "")
                state = address[1]
                zip_postal = address[2]
                longitude, latitude = (
                    soup.select_one("iframe[src*=maps]")["src"]
                    .split("!2d", 1)[1]
                    .split("!3m", 1)[0]
                    .split("!3d")
                )
                yield SgRecord(
                    locator_domain="https://wahlburgers.com/",
                    page_url=page_url,
                    location_name=location_name.strip(),
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number="<MISSING>",
                    phone=phone,
                    location_type="<MISSING>",
                    latitude=latitude.strip(),
                    longitude=longitude.strip(),
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
