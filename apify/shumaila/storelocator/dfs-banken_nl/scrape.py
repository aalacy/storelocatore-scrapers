from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

session = SgRequests()

MISSING = SgRecord.MISSING


def fetch_data():

    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
    }
    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    base_url = "https://www.dfs-banken.nl/"
    r = session.get("https://www.dfs-banken.nl/content/winkel", headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    mainlist = soup.findAll("main", {"id": "storeDetailsPage"})
    k = 1
    for mn in mainlist:
        divlist = mn.findAll("section")
        for div in divlist:
            title = div.find("h1").text.strip()
            raw_address = div.find("p")
            raw_address = re.sub(cleanr, "\n", str(raw_address))
            raw_address = re.sub(pattern, "\n", str(raw_address))
            raw_address = raw_address.replace("\n", " ").strip()

            phone = div.find("p", {"class": "phoneDetails"}).text.split(" ", 1)[1]
            hours = div.find("ol").text
            hours = re.sub(pattern, " ", str(hours)).strip()
            longt, lat = (
                div.find("iframe")["src"]
                .split("!2d", 1)[1]
                .split("!2m", 1)[0]
                .split("!3d", 1)
            )
            try:
                lat = lat.split("!", 1)[0]
            except:
                pass
            try:
                store = (
                    div.find("a", {"class": "apptBtn"})["href"]
                    .split("location/", 1)[1]
                    .split("/", 1)[0]
                )
            except:
                store = "<MISSING>"
            hours = hours.encode("ascii", "ignore").decode("ascii")
            if k == 1:
                ccode = "NL"
            elif k == 2:
                ccode = "ES"
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            pcode = zip_postal.strip() if zip_postal else MISSING
            yield SgRecord(
                locator_domain=base_url,
                page_url="https://www.dfs-banken.nl/content/winkel",
                location_name=title,
                street_address=street.replace("Ekkersrijt Ekkersrijt", "Ekkersrijt"),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code=ccode,
                store_number=str(store),
                phone=phone.strip(),
                location_type=SgRecord.MISSING,
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours.replace(" â€¦", "").strip(),
                raw_address=raw_address,
            )
        k = k + 1


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS}),
            duplicate_streak_failure_factor=5,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
