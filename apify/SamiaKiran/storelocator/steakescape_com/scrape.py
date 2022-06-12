import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "steakescape_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}
session = SgRequests()
DOMAIN = "https://steakescape.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://steakescape.com/locations/"
        session = SgRequests()
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "location-detail py1"})
        for loc in loclist:
            store_number = loc["data-store-id"]
            latitude = loc["data-lat"]
            longitude = loc["data-lng"]
            location_name = loc.find("h4").text
            address_url = loc.select_one("a[href*=ubereats]")
            if address_url:
                try:
                    address_url = (
                        loc.select_one("a[href*=ubereats]").get("href").split("?pl")[0]
                    )
                except:
                    loc.select_one("a[href*=ubereats]").get("href")
                session = SgRequests()
                r = session.get(address_url, headers=headers)
                if r.status_code != 410:
                    soup = BeautifulSoup(r.text, "html.parser")
                    try:
                        temp = r.text.split('"address":')[1].split("</script>")[0]
                        street_address = temp.split('"streetAddress":"')[1].split('"')[
                            0
                        ]
                        city = temp.split('"addressLocality":"')[1].split('"')[0]
                        state = temp.split('"addressRegion":"')[1].split('"')[0]
                        zip_postal = temp.split('"postalCode":"')[1].split('"')[0]
                        phone = temp.split('"telephone":"')[1].split('"')[0]
                    except:
                        continue

                    try:
                        hours_of_operation = (
                            soup.findAll("table", {"class": "ga gb"})[-1]
                            .get_text(separator="|", strip=True)
                            .replace("|", " ")
                            .replace("<!-- --> <!-- -->- <!-- -->", "-")
                        )
                    except:
                        hours_of_operation = (
                            "Every day "
                            + temp.split('"opens":"')[1].split('"')[0]
                            + "0"
                            + "-"
                            + temp.split('"closes":"')[1].split('"')[0]
                            + "0"
                        )

            else:
                hours_of_operation = MISSING
                address = (
                    loc.find("address")
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                address = address.replace(",", " ")
                address = usaddress.parse(address)
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
                try:
                    phone = loc.select_one("a[href*=tel]").text
                except:
                    phone = MISSING
            log.info(street_address)
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
