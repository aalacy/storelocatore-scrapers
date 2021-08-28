import json

from bs4 import BeautifulSoup as bs

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    addressess = []
    locator_domain = "https://unikwax.com"
    r = session.get(
        "https://unikwax.com/studio-locations/?address%5B0%5D&tax%5Bregion%5D%5B0%5D&post%5B0%5D=location&distance=300&form=1&per_page=50&units=imperial&lat&lng",
        headers=headers,
    )
    soup = bs(r.text, "lxml")
    stores = json.loads(
        str(soup).split("var gmwMapObjects = ")[1].split("}}};")[0] + "}}}"
    )["1"]["locations"]
    for dt in stores:
        adr = bs(dt["info_window_content"], "lxml")
        location_name = list(bs(dt["info_window_content"], "lxml").stripped_strings)[0]
        state = (
            list(bs(dt["info_window_content"], "lxml").stripped_strings)[1]
            .split(",")[-2]
            .strip()
            .split()[0]
        )
        zipp = (
            list(bs(dt["info_window_content"], "lxml").stripped_strings)[1]
            .split(",")[-2]
            .strip()
            .split()[1]
        )
        city = (
            list(bs(dt["info_window_content"], "lxml").stripped_strings)[-3]
            .replace(", NJ", "")
            .strip()
        )
        page_url = adr.find("a")["href"]
        latitude = dt["lat"]
        longitude = dt["lng"]

        location_type = ""
        phone = ""

        base = bs(session.get(page_url, headers=headers).text, "lxml")
        if "has closed due" in base.text:
            continue
        try:
            street_address = base.find(class_="address").text.strip()
        except:
            street_address = base.find(class_="info").p.text.split("  ")[0].strip()
            if "temporarily closed" in street_address:
                location_type = "Temporarily Closed"
                street_address = list(
                    base.find(class_="info").find_all("p")[1].stripped_strings
                )[1]
                city = list(base.find(class_="info").find_all("p")[1].stripped_strings)[
                    2
                ].split(",")[0]
                phone = list(
                    base.find(class_="info").find_all("p")[1].stripped_strings
                )[-1]
            else:
                city = (
                    base.find(class_="info")
                    .p.text.split("  ")[1]
                    .split("FL")[0]
                    .strip()
                )
        hours_of_operation = ""

        if not phone:
            try:
                phone = base.find(class_="number").text.strip()
            except:
                phone = (
                    base.find(class_="col-sm-12")
                    .div.find(class_="row")
                    .p.text.split()[-1]
                    .strip()
                )

        try:
            hours_of_operation = " ".join(
                list(
                    bs(session.get(page_url, headers=headers).text, "lxml")
                    .find("h5", text="Studio Hours")
                    .parent.stripped_strings
                )
            ).replace("Studio Hours ", "")
        except:
            hours_of_operation = "<MISSING>"
        store_number = dt["ID"]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code="US",
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
