from bs4 import BeautifulSoup
import json
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

    url = "https://www.barresoul.com/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.find("div", {"class": "folder"}).findAll(
        "div", {"class": "collection"}
    )

    for link in linklist:
        flag = 0
        title = link.text
        link = "https://www.barresoul.com" + link.find("a")["href"]
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        divlist = soup.findAll("div", {"class": "map-block"})
        phonelist = soup.findAll("strong")
        phone = "<MISSING>"
        for ph in phonelist:

            if "(" in ph.text and ")" in ph.text and "-" in ph.text:
                phone = ph.text.replace("|", "").strip()
                break
        for div in divlist:
            content = div["data-block-json"]
            content = json.loads(content)["location"]
            if flag == 0:
                ttnow = title
                title = title.split("&")[0]
                flag = 1
            else:
                title = ttnow.split("&")[1]
            lat = content["mapLat"]
            longt = content["mapLng"]
            street = content["addressLine1"]
            city, state = content["addressLine2"].split(", ", 1)
            state, pcode = state.lstrip().split(" ", 1)
            state = state.replace(",", "")

            yield SgRecord(
                locator_domain="https://www.barresoul.com/",
                page_url=link,
                location_name=title.replace(",\n", "")
                .replace(")", "")
                .replace("(", "")
                .strip(),
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=SgRecord.MISSING,
                phone=phone.strip(),
                location_type=SgRecord.MISSING,
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=SgRecord.MISSING,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
