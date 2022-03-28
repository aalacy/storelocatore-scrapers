from bs4 import BeautifulSoup
import re
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
    url = "https://dougashy.com/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.find("ul", {"class": "sub-menu"}).findAll("li")
    maplink = "https://dougashy.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxRqlWqBQCnUQoG"
    coordlist = session.get(maplink, headers=headers).json()["markers"]
    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    for link in linklist:
        link = link.find("a")["href"]
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        divlist = soup.findAll("div", {"class": "fl-rich-text"})
        for div in divlist:
            if div.text.find("Address") > -1:
                title = div.find("h2").text
                det = div.findAll("p")
                address = re.sub(cleanr, "\n", str(det[0]))
                address = re.sub(pattern, "\n", address).strip().splitlines()

                street = address[1]
                state = address[2].replace(", , ", ", ")
                city, state = state.split(", ", 1)
                state = state.lstrip()
                state, pcode = state.split(" ")
                phone = div.find("a").text
                for mp in det:
                    if mp.text.find("Hours") > -1:
                        hours = (
                            mp.text.replace("\n", " ")
                            .replace("Store Hours", "")
                            .lstrip()
                        )
                lat = SgRecord.MISSING
                longt = SgRecord.MISSING
                for coord in coordlist:
                    if (
                        pcode in coord["address"]
                        and street.strip().split(" ")[0] in coord["address"]
                    ):
                        lat = coord["lat"]
                        longt = coord["lng"]
                        break
                yield SgRecord(
                    locator_domain="https://dougashy.com/",
                    page_url=link,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode.strip(),
                    country_code="US",
                    store_number=SgRecord.MISSING,
                    phone=phone.strip(),
                    location_type=SgRecord.MISSING,
                    latitude=lat,
                    longitude=longt,
                    hours_of_operation=hours,
                )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
