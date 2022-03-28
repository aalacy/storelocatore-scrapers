from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup

session = SgRequests()
website = "steaknshake_it"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://steaknshake.it/"
MISSING = SgRecord.MISSING


def fetch_data():
    search_url = "http://www.steaknshake.it/#location"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    loc = soup.find("div", {"class": "row location"})
    loc_block = loc.findAll("div", {"class": "content"})
    coords_block = soup.findAll("div", {"class": "marker"})

    phones = loc.findAll("ul")

    for loc, coords, ph in zip(loc_block, coords_block, phones):
        title = loc.find("h3").text
        address = loc.findAll("p")[1].text
        details = address.split("\n")
        if len(details) == 3:
            street = details[0] + " " + details[1]
            locality = details[-1].strip()
        else:
            street = details[0]
            locality = details[-1].strip()
        street = street.rstrip(",").strip()
        locality = locality.split(", ")
        city = locality[0]
        if len(locality) == 3:
            state = locality[1]
            if state == "SO":
                state = "Sondrio"
        else:
            state = MISSING
        pcode = MISSING
        hours = loc.findAll("tr")
        hoo = ""
        for hr in hours:
            hoo = hoo + " " + hr.text.replace("\n", " ")
        hoo = hoo.strip()
        hoo = hoo.replace("  ", " ")
        hoo = hoo.replace("Every day", "Mon-Sun")
        lat = coords["data-lat"]
        lng = coords["data-lng"]
        phone = ph.text.strip()
        phone = phone.replace("Aperto a Google Maps", "").strip()
        if phone == "":
            phone = "<MISSING>"
        else:
            phone = phone.split("Telefono ")[1].strip()

        if city.find("Via") != -1:
            city = city.split("Via")[1].strip()

        hoo = hoo.replace("Ã¬ â€“", "i ")
        hoo = hoo.replace("â€“ ", " ")

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=DOMAIN,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state,
            zip_postal=pcode,
            country_code="IT",
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hoo.strip(),
        )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID(
            {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.HOURS_OF_OPERATION}
        )
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
