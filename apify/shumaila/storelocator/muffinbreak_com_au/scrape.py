from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://muffinbreak.com.au/wp-json/store-locator/v1/store/?origLat=-25.274398&origLng=133.775136&origAddress=Australia&formattedAddress=Australia&boundsNorthEast=%7B%22lat%22%3A-9.187026399999999%2C%22lng%22%3A159.2872223%7D&boundsSouthWest=%7B%22lat%22%3A-54.83376579999999%2C%22lng%22%3A110.9510339%7D"
    loclist = session.get(url, headers=headers).json()
    for loc in loclist:
        store = loc["id"]
        title = loc["locname"]
        lat = loc["lat"]
        longt = loc["lng"]
        rawaddr = loc["address"] + " " + loc["address2"]
        phone = loc["phone"]
        link = loc["web"]
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            hours = (
                soup.find("table", {"class": "c-table"})
                .text.replace("  Day Hours   ", "")
                .strip()
            )
        except:
            hours = "<MISSING>"
        raw_address = rawaddr.replace("\n", " ").replace("AUSTRALIA", "").strip()
        pa = parse_address_intl(raw_address)
        street_address = pa.street_address_1
        street = street_address if street_address else MISSING
        city = pa.city
        city = city.strip() if city else MISSING
        state = pa.state
        state = state.strip() if state else MISSING
        zip_postal = pa.postcode
        pcode = zip_postal.strip() if zip_postal else MISSING

        if MISSING in pcode or MISSING in state:
            r = session.get(link, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            address = soup.find("span", {"itemprop": "streetAddress"}).text
            raw_address = address.replace("\n", " ").strip()
            pa = parse_address_intl(raw_address)
            street_address = pa.street_address_1
            street = street_address if street_address else MISSING
            city = pa.city
            city = city.strip() if city else MISSING
            state = pa.state
            state = state.strip() if state else MISSING
            zip_postal = pa.postcode
            pcode = zip_postal.strip() if zip_postal else MISSING
        if "coming-soon" in link:
            continue
        yield SgRecord(
            locator_domain="https://muffinbreak.com.au",
            page_url=link,
            location_name=title,
            street_address=street.replace(",", "").strip(),
            city=city.replace(",", "").strip(),
            state=state,
            zip_postal=pcode.replace(",", "").strip(),
            country_code="AU",
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
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
