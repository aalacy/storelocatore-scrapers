from bs4 import BeautifulSoup
import re
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
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")

    url = "https://tonyromas.com/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("div", {"id": "locations-directory"}).findAll("a")

    for div in divlist:

        url = "https://tonyromas.com/wp-admin/admin-ajax.php"
        dataobj = {
            "the_location": div.text,
            "search_distance": "100",
            "current_lat": "",
            "current_lng": "",
            "current_page": "1",
            "action": "locationsubmit",
        }
        r = session.post(url, headers=headers, data=dataobj).json()
        coordlist = r["newresults"]

        coordlist = BeautifulSoup(coordlist, "html.parser").findAll(
            "div", {"class": "a-location-data"}
        )
        loclist = r["newresults2"]
        loclist = BeautifulSoup(loclist, "html.parser").findAll(
            "div", {"class": "a-result"}
        )

        for i in range(0, len(loclist)):

            lat = coordlist[i]["data-lat"]
            longt = coordlist[i]["data-lng"]
            title = loclist[i].find("div", {"class": "title"}).text
            address = str(loclist[i].find("div", {"class": "address"}))
            address = re.sub(cleanr, " ", str(address)).strip()
            try:
                phone = loclist[i].find("div", {"class": "phone"}).text
            except:
                phone = "<MISSING>"
            try:
                hours = loclist[i].find("div", {"class": "hours"}).text
            except:
                hours = "<MISSING>"
            link = loclist[i].find("a", {"class": "visit"})["href"]

            ltype = "<MISSING>"
            if "COMING SOON" in title:
                ltype = "COMING SOON"
            try:
                phone = phone.split(":", 1)[1].strip()
            except:
                pass
            try:
                hours = hours.split(":", 1)[1].strip()
            except:
                pass
            raw_address = address
            raw_address = raw_address.replace("\n", " ").strip()
            raw_address = re.sub(pattern, " ", raw_address).strip()

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
                locator_domain="https://tonyromas.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code=div.text,
                store_number=SgRecord.MISSING,
                phone=phone.strip(),
                location_type=ltype,
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours,
                raw_address=raw_address.replace("\n", " ").strip(),
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
