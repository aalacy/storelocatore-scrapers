from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://westsuburbanbank.com/locations.php"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "westsuburbanbank.com"

    raw_hours = base.find(class_="table")
    rows = raw_hours.find_all("tr")[1:]
    lobby_hours = ""
    for row in rows:
        day = row.find_all("td")[1].text.strip()
        lobby = row.find_all("td")[2].text.strip()
        lobby_hours = (lobby_hours + " " + day + " " + lobby).strip()

    raw_hours = base.find_all(class_="table")[1]
    rows = raw_hours.find_all("tr")[1:]
    wsb_hours = ""
    for row in rows:
        day = row.find_all("td")[1].text.strip()
        lobby = row.find_all("td")[2].text.strip()
        wsb_hours = (wsb_hours + " " + day + " " + lobby).strip()

    items = base.find(id="nav-tabContent").find_all(class_="tab-pane")

    for item in items:
        location_name = item.h3.text
        stores = item.find_all(class_="col-12")
        for store in stores:
            street_address = store.h5.text
            city_line = store.p.text.split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            country_code = "US"
            store_number = "<MISSING>"
            phone = base.find(class_="footer-widget").find_all("a")[-1].text
            try:
                location_type = store.small.text.split(".")[0]
            except:
                location_type = "<MISSING>"
            hours_of_operation = lobby_hours
            if "Xpress hour" in location_type:
                hours_of_operation = wsb_hours
            latitude = "<MISSING>"
            longitude = "<MISSING>"

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=base_link,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
