import re
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bickfordseniorliving_com")

session = SgRequests()


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.bickfordseniorliving.com/"
    country_code = "US"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    r = session.get("https://www.bickfordseniorliving.com/", headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    token = soup.find("input", {"name": "_token"})["value"]
    branches_list = [
        "Illinois",
        "Indiana",
        "Iowa",
        "Kansas",
        "Michigan",
        "Missouri",
        "Nebraska",
        "Ohio",
        "Pennsylvania",
        "Virginia",
    ]
    for state in branches_list:
        data = {"searchString": str(state), "radius": "90", "_token": str(token)}

        r = session.post(
            "https://www.bickfordseniorliving.com/search", data=data, headers=headers
        ).json()
        branch_list = BeautifulSoup(r["branchList"], "html.parser")
        marker_data = r["markerData"]
        lat_list = []
        lng_list = []
        for coord in marker_data:
            lat_list.append(coord["lat"])
            lng_list.append(coord["lon"])

        for loc in branch_list.find_all("div", class_="searchBranch"):

            full_address = list(loc.find("div", class_="branch_info").stripped_strings)
            location_name = full_address[0]
            street_address = full_address[2]
            city = full_address[3].split(",")[0]
            state = full_address[3].split(",")[1].split()[0]
            zipp = full_address[3].split(",")[1].split()[-1]
            phone = full_address[5]
            location_type = full_address[1]
            page_url = (
                "https://www.bickfordseniorliving.com"
                + loc.find("a", text=re.compile("view branch"))["href"]
            )
            latitude = ""
            longitude = ""
            if lat_list:
                latitude = lat_list.pop(0)
            if lng_list:
                longitude = lng_list.pop(0)

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=SgRecord.MISSING,
                raw_address=f"{street_address} {city}, {state} {zipp}",
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
