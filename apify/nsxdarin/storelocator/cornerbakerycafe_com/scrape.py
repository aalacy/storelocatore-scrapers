from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("cornerbakerycafe_com")


def fetch_data(sgw: SgWriter):
    locs = []
    url = "https://cornerbakerycafe.com/locations/all"
    r = session.get(url, headers=headers)
    website = "cornerbakerycafe.com"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line)
        if '<a href="/location/' in line:
            locs.append(
                "https://cornerbakerycafe.com" + line.split('href="')[1].split('"')[0]
            )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        typ = ""
        phone = ""
        lat = ""
        lng = ""
        store = "<MISSING>"
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2)
            if '"name": "' in line2 and name == "":
                name = line2.split('"name": "')[1].split('"')[0]
            if '"telephone": "' in line2 and phone == "":
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"latitude": ' in line2:
                lat = line2.split('"latitude": ')[1].split(",")[0]
            if '"longitude": ' in line2:
                lng = (
                    line2.split('"longitude": ')[1]
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\t", "")
                    .strip()
                )

        if not phone:
            continue

        base = BeautifulSoup(r2.text, "lxml")
        if "Temporarily Closed" in base.find(id="main-content").text:
            hours = "Temporarily Closed"
        else:
            hours = " ".join(list(base.find(class_="dl-hours").stripped_strings))

        try:
            add = (
                base.find(class_="loc-icon-home")
                .get_text(" ")
                .replace("\r\n", "")
                .replace("Temporarily Closed", "")
            )
            add = add[: add.rfind(city)].split("ENTRANCE")[0].strip()
        except:
            pass

        sgw.write_row(
            SgRecord(
                locator_domain=website,
                page_url=loc,
                location_name=name,
                street_address=add,
                city=city,
                state=state,
                zip_postal=zc,
                country_code=country,
                store_number=store,
                phone=phone,
                location_type=typ,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
