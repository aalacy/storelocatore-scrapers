from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://theoriginalpizzaking.com/additional-pizza-king-locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "fl-callout-content"})
    url = "https://api.storerocket.io/api/user/3MZpoQ2JDN/locations?radius=250&units=miles"
    loclist = session.get(url, headers=headers).json()["results"]["locations"]
    for div in divlist:
        content = div.text.strip().splitlines()
        title = content[0]
        phone = content[1]
        street = content[2]

        try:
            city, state = content[3].split(", ", 1)
            state, pcode = state.strip().split(" ", 1)
        except:
            city = street.split(",")[-1].strip()
            state, pcode = content[3].split(" ", 1)
        link = "<MISSING>"
        try:
            link = div.find("a", {"class": "fl-button"})["href"]
        except:
            pass
        for loc in loclist:
            if (
                phone.replace("(", "")
                .replace(")", "")
                .replace(" ", "")
                .replace("-", "")
                .strip()
                == loc["phone"]
                .replace(" ", "")
                .replace("(", "")
                .replace(")", "")
                .replace("-", "")
                .strip()
            ):
                store = loc["id"]
                lat = loc["lat"]
                longt = loc["lng"]
                break
        if "Indiana" in state:
            state = "IN"
        elif "Illinois" in state:
            state = "IL"
        state = state.replace(",", "").replace(".", "").upper()
        yield SgRecord(
            locator_domain="https://theoriginalpizzaking.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode,
            country_code="US",
            store_number=str(store),
            phone=phone.strip(),
            location_type="<MISSING>",
            latitude=lat,
            longitude=longt,
            hours_of_operation="<MISSING>",
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
