from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
import re

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


MISSING = SgRecord.MISSING


def fetch_data():
    pattern = re.compile(r"\s\s+")
    url = "https://tonyromas.com/sitemap.html"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.select("a[href*=locations-]")

    for div in divlist:
        div = div["href"]
        r = session.get(div, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.select("a[href*=location]")
        for link in linklist:
            link = link["href"]
            r = session.get(link, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.find("div", {"class": "page-title"}).text

            address = soup.find("div", {"class": "ad1"}).text.replace("\n", " ").strip()
            phone = (
                soup.find("div", {"class": "phone"}).text.replace("Phone:", "").strip()
            )
            hours = (
                soup.find("div", {"class": "hours"})
                .text.replace("\n", " ")
                .replace("day", "day ")
                .replace("CLOSED", "CLOSED ")
                .replace("PM", "PM ")
                .replace("pm", "pm ")
                .strip()
            )
            if len(hours) < 4:
                hours = "<MISSING>"
            if len(phone) < 4:
                phone = "<MISSING>"
            ltype = "<MISSING>"
            if "coming-soon" in link:
                ltype = "Coming Soon"
            coordlink = soup.find("iframe")["src"]
            r = session.get(coordlink, headers=headers)
            try:
                lat, longt = (
                    r.text.split('",null,[null,null,', 1)[1]
                    .split("]", 1)[0]
                    .split(",", 1)
                )
            except:
                lat = longt = "<MISSING>"
            try:

                if len(address) < 5:

                    address = (
                        r.text.split('"Tony Roma')[3].split(", ", 1)[1].split('"', 1)[0]
                    )
                    if "family-friendly steakhouse" in address:
                        address = (
                            r.text.split('"Tony Roma')[3]
                            .split("[", 1)[1]
                            .split("]", 1)[0]
                        )
                        address = (
                            " ".join(address[0:]).replace(",", "").replace('"', "")
                        )
            except:
                continue
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

            ccode = pa.country
            ccode = ccode.strip() if ccode else MISSING

            yield SgRecord(
                locator_domain="https://tonyromas.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code=ccode,
                store_number=SgRecord.MISSING,
                phone=phone.strip(),
                location_type=ltype,
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
