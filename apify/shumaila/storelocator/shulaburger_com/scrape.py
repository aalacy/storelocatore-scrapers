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

    url = "https://shulassteakhouse.com/#locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "shula-menu__location"})

    for div in divlist:
        if "shulaburger" in div.find("a")["href"]:
            pass
        else:
            continue
        link = div.find("a")["href"]

        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        hours = lat = longt = phone = "<MISSING>"
        if "tampa" in link:
            title = soup.find("div", {"class": "shula-block-split-content-title"}).text
            content = soup.find(
                "div", {"class": "shula-block-split-content-body"}
            ).findAll("p")
            hours = content[0].text + " " + content[1].text
            address = "500 S Howard Ave a, Tampa, FL 33606 [27.939573,-82.48267]"
            address, coord = address.split(" [", 1)
            lat, longt = coord.split("]", 1)[0].split(",", 1)
            street, city, state = address.split(", ")
            state, pcode = state.lstrip().split(" ", 1)
            yield SgRecord(
                locator_domain="https://shulaburger.com/",
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
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours,
            )
        else:

            try:
                content = soup.find(
                    "div", {"class": "shula-block-split-content-body"}
                ).findAll("p")
            except:
                continue
            for i in range(1, len(content)):
                det = content[i].text.splitlines()

                title = det[0]
                street = det[1]

                try:
                    city, state = det[2].split(", ")
                except:
                    street = street + " " + det[2]
                    city, state = det[3].split(", ")
                    state, pcode = state.lstrip().split(" ", 1)
                yield SgRecord(
                    locator_domain="https://shulaburger.com/",
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
