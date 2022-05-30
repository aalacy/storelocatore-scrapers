from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.sarovarhotels.com/sitemap.xml"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    linklist = soup.findAll("loc")
    MISSING = SgRecord.MISSING
    for link in linklist:
        if (
            len(link.text.split("/")[-1]) == 0
            and len(link.text.replace("https://www.sarovarhotels.com/", "")) != 0
        ):

            link = link.text
            r = session.get(link, headers=headers)
            content = r.text.split('<script type="application/ld+json">', 1)[1].split(
                "</script>", 1
            )[0]
            content = json.loads(content)
            title = content["name"]
            phone = content["telephone"]
            raw_address = content["address"]["streetAddress"].replace("\n", " ").strip()
            city = content["address"]["addressLocality"]
            ccode = content["address"]["addressCountry"]

            if "India" in ccode:
                ccode = "IN"
            state = pcode = "<MISSING>"
            lat = content["geo"]["latitude"]
            longt = content["geo"]["longitude"]

            pa = parse_address_intl(raw_address)

            street = pa.street_address_1
            street = street if street else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            pcode = zip_postal.strip() if zip_postal else MISSING

            yield SgRecord(
                locator_domain="https://www.sarovarhotels.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=SgRecord.MISSING,
                zip_postal=pcode.strip(),
                country_code=ccode,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=SgRecord.MISSING,
                raw_address=raw_address,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
