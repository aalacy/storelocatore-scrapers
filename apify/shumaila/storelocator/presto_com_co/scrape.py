from bs4 import BeautifulSoup
import unidecode
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://presto.com.co/encuentranos"
    r = session.get(url, headers=headers)
    coordlist = r.text.split("mapa1.agregarMarker(")[1:]

    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("li", {"class": "ico1"})[2:]
    for i in range(0, len(coordlist)):
        loc = coordlist[i].split(",")
        lat = loc[0]
        longt = loc[1]
        title = loc[3].split("<b>", 1)[1].split("</b>", 1)[0]
        street = loc[3].split("<br> ", 1)[1].replace('"', "").strip()
        loc = loclist[i].text.strip().splitlines()[-1]
        if "24 Horas" in loc:
            city = loc.split("24 Horas", 1)[0]
            hours = "24 Horas"
        else:
            city, hours = loc.split("De ", 1)
        city = unidecode.unidecode(city).strip()
        city = city.replace("\n", "").strip()
        title = unidecode.unidecode(title)
        street = unidecode.unidecode(street)

        yield SgRecord(
            locator_domain="https://presto.com.co/",
            page_url=url,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code="CO",
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
