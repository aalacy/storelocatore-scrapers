import re
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


def fetch_data(sgw: SgWriter):

    pattern = re.compile(r"\s\s+")
    url = "https://www.sterlingoptical.com/locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.select('a:contains("Store Details")')

    for div in divlist:
        link = div["href"]
        r = session.get(link, headers=headers)
        if r.status_code == 404 and "pottstown" in link:
            link = "https://www.sterlingoptical.com/locations/pottstown-details/"
            r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        title = (
            soup.find("a", {"class": "location-page-link-city"})
            .text.replace("\n", " ")
            .strip()
        )
        try:
            street = (
                soup.find("span", {"class": "street-address"})
                .text.replace(" , ", ", ")
                .split(", Cross")[0]
                .split(", Jefferson")[0]
                .strip()
            )
        except:
            continue
        city = soup.find("span", {"class": "locality"}).text
        state = soup.find("span", {"class": "region"}).text
        pcode = soup.find("span", {"class": "postal-code"}).text
        try:
            phone = soup.find("a", {"class": "tel"}).text.replace("Phone:", "").strip()
        except:
            if "Coming Soon!" in soup.find("span", {"class": "is-coming-soon"}):
                continue
        store_number = soup.find(class_="location-modal")["id"].replace("location", "")
        try:
            hours = soup.find("ul", {"class": "location-hours-list"}).text
            hours = re.sub(pattern, " ", hours).replace("\n", " ").strip()
            hours = hours.split("-----")[0].split("alternative")[0].strip()
        except:
            hours = "<MISSING>"

        sgw.write_row(
            SgRecord(
                locator_domain="https://www.sterlingoptical.com/",
                page_url=link,
                location_name=title,
                street_address=street,
                city=city,
                state=state,
                zip_postal=pcode,
                country_code="US",
                store_number=store_number,
                phone=phone,
                location_type="",
                latitude="",
                longitude="",
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
