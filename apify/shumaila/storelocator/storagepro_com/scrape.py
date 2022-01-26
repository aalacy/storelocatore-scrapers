import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "storagepro_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.storagepro.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        loclist = []
        states = ["arizona", "california", "nevada", "washington"]
        for temp_state in states:
            state_url = "https://www.storagepro.com/storage-units/" + temp_state
            r = session.get(state_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            linklist = soup.findAll("div", {"class": "title"})
            if not linklist:
                loc = r.url
                loclist.append(loc)
            else:
                for link in linklist:
                    loc = "https://www.storagepro.com" + link.find("a")["href"]
                    loclist.append(loc)
        for loc in loclist:
            page_url = loc
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            temp = soup.find("div", {"class": "facility-info"})
            location_name = temp.find("h2").text
            address = (
                temp.find("div", {"class": "facility-address"})
                .get_text(separator="|", strip=True)
                .replace("|", "")
            )
            phone = soup.find("span", {"class": "phone-number"}).text
            try:
                hours_of_operation = (
                    soup.find("div", {"class": "office-hours"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
            except:
                try:
                    hours_of_operation = (
                        soup.find("div", {"class": "callcenter-timings-content-row"})
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                    )
                except:
                    try:
                        hours_of_operation = (
                            soup.find("div", {"class": "gate-hours"})
                            .get_text(separator="|", strip=True)
                            .replace("|", " ")
                        )
                    except:

                        hours_of_operation = MISSING
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
