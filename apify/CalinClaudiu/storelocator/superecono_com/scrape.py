import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "superecono_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.superecono.com/"
MISSING = "<MISSING>"


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.superecono.com/tiendas/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll(
            "div", {"class": "mpc-post__thumbnail mpc-post__thumbnail-full"}
        )
        for loc in loclist:
            page_url = loc["data-mpc_link"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            city = soup.find("h2").text
            temp = soup.find("ul", {"class": "info-tiendas"})
            hour_list = temp.findAll("li", {"class": "hora"})
            hours_of_operation = " ".join(x.text for x in hour_list)
            phone = temp.find("li", {"class": "tel"}).text
            street_address = temp.find("li", {"class": "dir"}).text.strip()
            street_address = strip_accents(street_address)
            if not street_address:
                street_address = MISSING
            street_address = street_address.replace("\n", "").replace("/li>", "")
            country_code = "US"
            coords_link = soup.find("div", {"class": "wpb_map_wraper"}).find("iframe")[
                "src"
            ]
            r = session.get(coords_link, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            temp_list = r.text.split("null,0,[[")[1].split("],")[0].split(",")[1:]
            location_name = temp_list[0].replace('"', "")
            latitude = temp_list[-2].replace("[", "").replace("]", "").replace("'", "")
            longitude = temp_list[-1].replace("]", "").replace("'", "")
            if street_address == MISSING:
                address = temp_list[1:-2]
                raw_address = " ".join(x for x in address)
            else:
                address = temp_list[2:-2]
                address = " ".join(x for x in address)
                raw_address = street_address + " " + address
            parsed = parse_address_intl(raw_address.replace('"', ""))
            city = parsed.city if parsed.city else "<MISSING>"
            zip_postal = parsed.postcode if parsed.postcode else "<MISSING>"
            state = parsed.country if parsed.postcode else "<MISSING>"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
