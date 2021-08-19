from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import sglog
import html
from bs4 import BeautifulSoup

website = "countrystyle_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.countrystyle.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1615704674870"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("store").findAll("item")
        x = 0
        for loc in loclist:
            location_name = loc.find("location").text
            store_number = loc.find("storeid").text

            raw_address = loc.find("address").text

            raw_address = raw_address.replace(
                " NEW lunch program, different offerings, custom LTO panel", ""
            )
            if "," in raw_address:
                x = x + 1
                street_address = raw_address.split(",")[0].split("  ")[0]
                city_parts = raw_address.split(",")[1].split(" ")[:-1]
                city = ""
                for part in city_parts:
                    city = city + part + " "
                city = city.strip()

            else:
                city = raw_address.split(" ")[-2]
                street_address_parts = raw_address.split(" ")[:-2]
                street_address = ""
                for part in street_address_parts:
                    street_address = street_address + part + " "
                street_address = street_address.split("  ")[0]
                try:
                    city = street_address.split("  ")[1] + city
                except Exception:
                    pass

            street_address = html.unescape(street_address)

            zip_postal = loc.find("telephone").text.split(" (")[0]
            if not zip_postal:
                zip_postal = "<MISSING>"
            state = loc.find("country").text
            latitude = loc.find("latitude").text
            longitude = loc.find("longitude").text
            phone = loc.find("fax").text
            if not phone:
                phone = "<MISSING>"

            yield SgRecord(
                locator_domain="https://www.countrystyle.com/",
                page_url="https://www.countrystyle.com/stores/",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="CA",
                store_number=store_number,
                phone=phone,
                location_type="<MISSING>",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="<MISSING>",
                raw_address=raw_address,
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


scrape()
