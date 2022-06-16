from bs4 import BeautifulSoup
import usaddress
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

log = sglog.SgLogSetup().get_logger(logger_name="mommagoldbergsdeli.com")


def fetch_data():
    url = "https://www.mommagoldbergsdeli.com/stores-sitemap.xml"
    with SgRequests(verify_ssl=False) as session:
        r = session.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.findAll("loc")[1:]
        for link in linklist:
            link = link.text
            r = session.get(link, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            content = (
                soup.find("div", {"class": "entry-content"})
                .find("div", {"class": "left"})
                .text.lstrip()
            )
            title = soup.find("h1", {"class": "entry-title"}).text
            address = content.split("ADDRESS:", 1)[1].split("\n", 1)[0].strip()
            address = usaddress.parse(address)
            i = 0
            street = ""
            city = ""
            state = ""
            pcode = ""
            while i < len(address):
                temp = address[i]
                if (
                    temp[1].find("Address") != -1
                    or temp[1].find("Street") != -1
                    or temp[1].find("Occupancy") != -1
                    or temp[1].find("Recipient") != -1
                    or temp[1].find("BuildingName") != -1
                    or temp[1].find("USPSBoxType") != -1
                    or temp[1].find("USPSBoxID") != -1
                ):
                    street = street + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    pcode = pcode + " " + temp[0]
                i += 1

            street = street.lstrip().replace(",", "")
            city = city.lstrip().replace(",", "")
            state = state.lstrip().replace(",", "")
            pcode = pcode.lstrip().replace(",", "")
            phone = content.split("PHONE:", 1)[1].split("\n", 1)[0].strip()
            hours = (
                content.split("HOURS:", 1)[1]
                .split("SOCIAL:", 1)[0]
                .replace("\n", "; ")
                .replace("\r", "")
                .strip()
            )
            if len(hours) > 0 and hours[-1] == ";":
                hours = "".join(hours[:-1]).strip()

            yield SgRecord(
                locator_domain="mommagoldbergsdeli.com",
                page_url=link,
                location_name=title,
                street_address=street,
                city=city,
                state=state,
                zip_postal=pcode,
                country_code="US",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude="<MISSING>",
                longitude="<MISSING>",
                hours_of_operation=hours,
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
