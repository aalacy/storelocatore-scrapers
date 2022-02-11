import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "oportun_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://oportun.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://oportun.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        statelist = soup.findAll("section", {"class": "location-state"})
        for state in statelist:
            url = state.find("a")["href"]
            r = session.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("div", {"class": "location-card"})
            for loc in loclist:
                location_name = loc.get_text(separator="|", strip=True).split("|")[0]
                page_url = loc.findAll("a")[-1]["href"]
                r = session.get(page_url, headers=headers)
                if r.status_code != 200:
                    location_name = loc.find("h3").text
                    address = (
                        loc.find("address")
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                    )
                    phone = loc.find("p", {"class": "phone"}).find("a").text
                    hours_of_operation = MISSING
                else:
                    page_url = r.url
                    log.info(page_url)
                    soup = BeautifulSoup(r.text, "html.parser")
                    temp = soup.find("div", {"class": "location-intro__content"})
                    if temp is None:
                        address = loc.get_text(separator="|", strip=True).split("|")
                        phone = address[4]
                        address = address[1] + " " + address[2]
                        hours_of_operation = MISSING
                    else:
                        phone = temp.select_one("a[href*=tel]").text
                        address = (
                            temp.find("address")
                            .get_text(separator="|", strip=True)
                            .replace("|", " ")
                        )
                        hours_of_operation = (
                            temp.find("p", {"class": "hours"})
                            .get_text(separator="|", strip=True)
                            .replace("|", " ")
                        )
                raw_address = address.replace(",", " ")
                address = usaddress.parse(raw_address)
                i = 0
                street_address = ""
                city = ""
                state = ""
                zip_postal = ""
                while i < len(address):
                    temp = address[i]
                    if (
                        temp[1].find("Address") != -1
                        or temp[1].find("Street") != -1
                        or temp[1].find("Recipient") != -1
                        or temp[1].find("Occupancy") != -1
                        or temp[1].find("BuildingName") != -1
                        or temp[1].find("USPSBoxType") != -1
                        or temp[1].find("USPSBoxID") != -1
                    ):
                        street_address = street_address + " " + temp[0]
                    if temp[1].find("PlaceName") != -1:
                        city = city + " " + temp[0]
                    if temp[1].find("StateName") != -1:
                        state = state + " " + temp[0]
                    if temp[1].find("ZipCode") != -1:
                        zip_postal = zip_postal + " " + temp[0]
                    i += 1
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
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
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
