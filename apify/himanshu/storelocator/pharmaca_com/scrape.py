import json
from lxml import html
from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get("https://www.pharmaca.com/store-locator", headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "jsonLocations")]/text()'))
        .split("jsonLocations: ")[1]
        .split("imageLocations")[0]
        .strip()[:-1]
    )
    data = json.loads(jsblock)
    for obj in data["items"]:
        det = BeautifulSoup(obj["popup_html"], "lxml")
        page_url = "https://www.pharmaca.com" + det.a["href"]
        store_number = obj["id"]
        location_name = det.h4.text
        if "- CLOSED" in location_name:
            continue
        raw_address = list((det.p.stripped_strings))
        street_address = raw_address[0]
        city = raw_address[1].split(",")[0].split("(")[0].strip()
        state = raw_address[1].split(",")[1].strip()
        zip_code = raw_address[2]
        if not zip_code.isdigit():
            zip_code = page_url.split("-")[-1]
        country_code = "US"
        lat = obj["lat"]
        longit = obj["lng"]
        phone_number = raw_address[-1]
        location_type = "<MISSING>"

        try:
            req = session.get(page_url, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
        except:
            session = SgRequests()
            req = session.get(page_url, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

        hours1 = base.find(class_="row hours").table.find_all("tr")
        hours_of = ""
        for h in hours1:
            day = list(h.stripped_strings)[0]
            hours = list(h.stripped_strings)[1]
            hours_of = (hours_of + " " + day + " " + hours).strip()

        locator_domain = "https://www.pharmaca.com/"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone_number,
                location_type=location_type,
                latitude=lat,
                longitude=longit,
                hours_of_operation=hours_of,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
