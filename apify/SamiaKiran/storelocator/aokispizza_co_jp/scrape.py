from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "aokispizza_co_jp"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.aokispizza.co.jp"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.aokispizza.co.jp/page/shop/index.html"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.find("div", {"id": "submenu"}).findAll("li")
        for link in linklist:
            url = "https://www.aokispizza.co.jp/page/shop/" + link.find("a")["href"]
            r = session.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.find("table").findAll("tr")
            for loc in loclist:
                location_name = loc.find("th", {"class": "shop_name"}).text
                log.info(location_name)
                temp = loc.find("td", {"class": "shop_info"})
                hours_of_operation = temp.get_text(separator="|", strip=True).replace(
                    "|", " "
                )
                try:
                    hours_of_operation = hours_of_operation.split("11：")[1]
                except:
                    hours_of_operation = hours_of_operation.split("11:")[1]
                hours_of_operation = "11：" + hours_of_operation
                temp = temp.get_text(separator="|", strip=True).split("|")
                phone = temp[0].replace("☎", "")
                raw_address = temp[1] + " " + temp[2]

                if "11" in raw_address:
                    raw_address = raw_address.split("11")[0]

                pa = parse_address_intl(raw_address)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING

                country_code = "JP"
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=url,
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
