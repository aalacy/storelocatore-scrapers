import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "weldonbarber_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://weldonbarber.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://weldonbarber.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "vc_column-inner"})
        for loc in loclist:
            if loc.find("h3"):
                location_name = loc.find("h3").text
                address = loc.find("p").get_text(separator="|", strip=True).split("|")
                phone = address[-1]
                address = address[0] + " " + address[1]
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
                page_url = DOMAIN + loc.findAll("a")[-2]["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                coords = soup.select_one("a[href*=maps]")["href"]

                try:
                    temp = coords.split("@")[1].split(",")
                    latitude = temp[0]
                    longitude = temp[1]
                except:
                    try:
                        latitude, longitude = (
                            coords.split("ll=")[1].split("&")[0].split(",")
                        )
                    except:
                        coords = soup.select_one("iframe[src*=maps]")["src"]
                        longitude, latitude = (
                            coords.split("!2d")[1].split("!2m")[0].split("!3d")
                        )
                hours_of_operation = (
                    soup.findAll(
                        "div", {"class": "wpb_text_column wpb_content_element"}
                    )[1]
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                country_code = "US"
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone,
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
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
