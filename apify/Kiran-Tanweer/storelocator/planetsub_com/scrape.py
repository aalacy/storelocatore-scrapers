from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser


session = SgRequests()
website = "planetsub_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "planetsub.com",
    "method": "POST",
    "path": "/contact/find-a-location/",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "identity",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "content-length": "14",
    "content-type": "application/x-www-form-urlencoded",
    "cookie": "PHPSESSID=lnpc04bv70tij3suieb2ngo1o0; __utmc=230204893; __utmz=230204893.1611633760.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _fbp=fb.1.1611633760304.649577070; __utma=230204893.1389812213.1611633760.1611775008.1611806536.3; __utmt=1; __utmb=230204893.2.10.1611806536",
    "origin": "https://planetsub.com",
    "referer": "https://planetsub.com/contact/find-a-location/",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
}

DOMAIN = "https://planetsub.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    lat = []
    lng = []
    form_data = {"location": "85713"}
    url = "https://planetsub.com/contact/find-a-location/"
    r = session.post(url, headers=headers, data=form_data)
    soup = BeautifulSoup(r.text, "html.parser")
    locations = soup.find("div", {"id": "mapContainer"})
    loc = locations.findAll("div", {"class": "popup"})

    locations = str(locations)
    info = locations.split("var locations = ")[1].split(
        "locations = JSON.parse(locations);"
    )[0]
    coords = info.split("],[")
    j = 0
    for c in range(1, 22):
        index = '",' + str(c) + "',"
        centre = coords[c - 1].split(index)[0]
        centre = centre.split('","')
        lat.append(centre[1])
        lng.append(centre[2])

    for store in loc:
        title = store.find("span", {"class": "franchise_title_name"}).text.strip()
        address = store.find("span", {"class": "franchise_address"}).text.strip()
        address = address.replace(",", "")
        parsed = parser.parse_address_usa(address)
        street1 = parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
        street = (
            (street1 + ", " + parsed.street_address_2)
            if parsed.street_address_2
            else street1
        )
        city = parsed.city if parsed.city else "<MISSING>"
        state = parsed.state if parsed.state else "<MISSING>"
        pcode = parsed.postcode if parsed.postcode else "<MISSING>"

        hours = store.find("span", {"class": "franchise_hours"}).text.strip()
        hours = hours.replace("\n", " ")
        hours = hours.rstrip(" NOW OPEN")
        hours = hours.replace("\r", "")
        phone = store.find("span", {"class": "franchise_phone"}).text.strip()
        phone = phone.lstrip("Phone: ").strip()
        latitude = lat[j].strip()
        longitude = lng[j].split('",')[0].strip()

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=url,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode,
            country_code="US",
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours.strip(),
        )
        j = j + 1


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME})
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
