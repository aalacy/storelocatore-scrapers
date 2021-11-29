from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("holidaystationstores_com")

session = SgRequests()


def fetch_data(sgw: SgWriter):
    data = {
        "Lat": 45.755799,
        "Lng": -93.6544079,
        "Diesel": "false",
        "E85": "false",
        "NonOxygenated": "false",
        "Carwash": "false",
        "UnlimitedCarWashPass": "false",
        "Open24Hours": "false",
        "ATM": "false",
        "Cub": "false",
        "UnattendedFueling": "false",
        "TruckStop": "false",
        "DEF": "false",
        "Propane": "false",
        "CNG": "false",
        "SearchMethod": "City",
        "SearchValue": "MN",
    }

    headers = {
        "Accept": "text/html, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9,gu;q=0.8,es;q=0.7",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    r = session.post(
        "https://www.holidaystationstores.com/Locations/Results/",
        data=data,
        headers=headers,
    )
    soup = BeautifulSoup(r.text, "html.parser")
    s = set()
    for name in soup.find_all("a", {"class": "HolidayHoverNone"}):
        location_name = name.find(
            "div", {"class": "col-12 HolidayFontColorRedHover font-weight-bold"}
        ).text.strip()
        store_number = location_name.split("#")[-1]
        phone = "<INACCESSIBLE>"
        hours_of_operation = "<INACCESSIBLE>"
        longitude = name["data-lng"]
        latitude = name["data-lat"]
        country_code = "US"
        street_address = name.find_all("div")[1].text
        raw = name.find_all("div")[-1].text
        city = raw.split(",")[0]
        state = raw.split(",")[1].split()[0]
        try:
            zipp = raw.split(",")[1].split()[1]
        except:
            zipp = "<MISSING>"
        page_url = (
            "https://www.holidaystationstores.com/Locations/Detail?storeNumber="
            + str(store_number)
        )
        line = location_name
        if line in s:
            continue
        s.add(line)

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zipp,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.holidaystationstores.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
