from bs4 import BeautifulSoup
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

    url = "https://www.bankwithunited.com/find-a-location.html"
    r = session.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "cmp-locationfinder__item"})
    for div in divlist:
        title = div.find("div", {"class": "cmp-locationfinder__item-title"}).text
        llist = div.find("ul", {"class": "cmp-locationfinder__item-amenities"}).findAll(
            "li"
        )
        ltype = ""
        for l in llist:
            ltype = ltype + l.text + " | "
        if len(ltype) < 2:
            ltype = "<MISSING>"
        else:
            ltype = ltype[0 : len(ltype) - 2]
        lat = div.find("div", {"class": "cmp-locationfinder__item-address"})[
            "data-cmp-item-latitude"
        ]
        longt = div.find("div", {"class": "cmp-locationfinder__item-address"})[
            "data-cmp-item-longitude"
        ]
        address = (
            str(div.find("div", {"class": "cmp-locationfinder__item-address"}))
            .split(">", 1)[1]
            .split("</div", 1)[0]
            .split("<br/>")
        )
        street = address[0].replace("\\n", "").lstrip()
        city, state, pcode = address[1].replace("\n", "").lstrip().split(", ")
        if len(state) < 2:
            state = "<MISSING>"
        state = state.replace("Washington ", "").strip()

        try:
            phone = div.find("div", {"class": "cmp-locationfinder__item-phone"}).text
        except:
            phone = "<MISSING>"
        try:
            hours = (
                div.find("div", {"class": "cmp-locationfinder__item-service-hours"})
                .text.replace("Lobby Hours: ", "")
                .replace("Lobby Hours:", "")
            )
        except:
            hours = "<MISSING>"
        try:
            hours = hours.split("Drive", 1)[0]
        except:
            pass
        if "Seasonal" in hours:
            hours = "<MISSING>"
        yield SgRecord(
            locator_domain="https://www.bankwithunited.com/",
            page_url="https://www.bankwithunited.com/find-a-location.html",
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
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
