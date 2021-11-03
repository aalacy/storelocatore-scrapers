from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list
from sgscrape.sgpostal import parse_address_intl

session = SgRequests()
website = "vanheusen_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://vanheusen.com/"
MISSING = "<MISSING>"


def fetch_data():
    zips = static_zipcode_list(country_code=SearchableCountries.USA, radius=5)
    identities = set()
    for zip in zips:
        log.info(("Pulling zip Code %s..." % zip))
        url = f"https://secure.gotwww.com/gotlocations.com/vanheusendev/index.php?address={zip}"
        r = session.get(url, headers=headers, timeout=15)
        if "L.marker" not in r.text:
            continue
        loclist = r.text.split("L.marker(")[1:]
        for loc in loclist:
            coords = loc.split(", {icon: customIcon}", 1)[0]
            coords = coords.split(",")
            latitude = coords[0].split("[", 1)[1]
            longitude = coords[1].split("]", 1)[0]
            temploc = (
                loc.split("numtoshow.push", 1)[0]
                .split(".bindPopup('", 1)[1]
                .split("');", 1)[0]
            )
            location_name = temploc.split('<div class="maptexthead">', 1)[1].split(
                "</div>", 1
            )[0]
            location_name = location_name.split("  ", 1)[0]
            templist = temploc.split("<br>")[1:5]
            if "US" not in templist[2]:
                continue
            address_raw = templist[0] + " " + templist[1] + " " + templist[2]

            # Find the raw address
            address_raw = " ".join(address_raw.split())

            # Parse the address
            pa = parse_address_intl(address_raw)

            street_address = pa.street_address_1
            if street_address is None:
                street_address = pa.street_address_2
            if pa.street_address_2:
                street_address = street_address + ", " + pa.street_address_2

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            tempzip = "+" + state + "," + "+"
            zip_postal = temploc.split(tempzip, 1)[1].split(",+US", 1)[0]
            phone = templist[3].split("Phone:", 1)[1].strip()
            country_code = "US"
            identity = (
                str(latitude)
                + ","
                + str(longitude)
                + ","
                + str(street_address)
                + ","
                + str(phone)
            )
            page_url = (
                "https://vanheusen.partnerbrands.com/en/customerservice/store-locator"
            )
            if identity not in identities:
                identities.add(identity)
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name.strip(),
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone,
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=MISSING,
                    raw_address=address_raw,
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


if __name__ == "__main__":
    scrape()
