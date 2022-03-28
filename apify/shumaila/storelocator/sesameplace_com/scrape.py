from bs4 import BeautifulSoup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://sesameplace.com/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select('a:contains("Visit")')
    for link in linklist:
        title = link.text.split("in ", 1)[1]
        link = link["href"]
        r = session.get(link, headers=headers)
        if r.text.find("coming soon") > -1:
            continue
        address = r.text.split("All Rights Reserved. ", 1)[1].split("<", 1)[0]
        street, city, state = address.split(", ")
        state, pcode = state.lstrip().split(" ", 1)
        ltype = "<MISSING>"
        try:
            phone = r.text.split("tel:", 1)[1].split('"')[0]
        except:
            phone = "<MISSING>"
            if r.text.find("/opening-") > -1:
                ltype = "Opening Soon"
        try:
            lat = r.text.split('"ParkCenterpointLatitude":', 1)[1].split(",", 1)[0]
        except:
            lat = "<MISSING>"
        try:
            longt = str(
                (float)(
                    r.text.split('"ParkCenterpointLongitude":', 1)[1].split(",", 1)[0]
                )
            ).replace(".", "")
            longt = longt[0:3] + "." + longt[3 : len(longt)]
        except:

            longt = "<MISSING>"
        yield SgRecord(
            locator_domain="https://sesameplace.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=ltype,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation="<INACCESSIBLE>",
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
