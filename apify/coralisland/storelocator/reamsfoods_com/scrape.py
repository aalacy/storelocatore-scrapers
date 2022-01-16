from bs4 import BeautifulSoup
import re
import usaddress
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "reamsfoods.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    pattern = re.compile(r"\s\s+")
    url = "https://reamsfoods.com/"
    with SgRequests(verify_ssl=False) as session:

        r = session.get(url, headers=headers)
        stores_sel = lxml.html.fromstring(r.text)
        divlist = stores_sel.xpath(
            '//ul[@id="top-menu"]/li[./a[contains(text(),"LOCATIONS")]]/ul/li/a'
        )
        for div in divlist:
            title = "".join(div.xpath("text()")).strip().replace("Location", "").strip()
            page_url = "".join(div.xpath("@href")).strip()
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            content = (
                soup.text.split("Address", 1)[1]
                .split("\n", 1)[1]
                .split("Location", 1)[0]
            )
            longitude, latitude = (
                soup.find("iframe")["src"]
                .split("!2d", 1)[1]
                .split("!2m", 1)[0]
                .split("!3d", 1)
            )
            content = re.sub(pattern, "\n", content).strip()
            address = content.split("\n", 1)[0]
            phone = (
                content.split("Phone", 1)[1].split("Main")[0].replace(":", "").strip()
            )
            try:
                phone = phone.split("Store", 1)[0]
            except:
                pass
            hours = (
                content.split("Hours", 1)[1].replace("\n", " ").replace(":", "").strip()
            )
            if hours.find("Winter") != -1:
                hours = hours.split("Winter")[0].strip()
            address = address.replace("\n", " ").strip()
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

            if len(city) < 2:
                city = title

            yield SgRecord(
                locator_domain=website,
                page_url=page_url,
                location_name=title,
                street_address=street,
                city=city,
                state=state,
                zip_postal=pcode,
                country_code="US",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude=latitude,
                longitude=longitude,
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
