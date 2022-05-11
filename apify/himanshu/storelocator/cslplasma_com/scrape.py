from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data(sgw: SgWriter):
    base_url = "https://www.cslplasma.com"
    r = session.get(base_url + "/find-a-donation-center")
    soup = BeautifulSoup(r.text, "lxml")
    for option in soup.find("select", {"name": "SelectedState"}).find_all("option")[1:]:
        if option["value"] == "":
            continue
        location_request = session.get(base_url + option["value"])
        lcoation_soup = BeautifulSoup(location_request.text, "lxml")
        for location in lcoation_soup.find_all("div", {"class": "center-search-item"}):
            store = []
            location_address = list(
                location.find(
                    "div", {"class": "center-search-item-addr"}
                ).stripped_strings
            )
            if (
                location_address[1] != "Coming Soon"
                and location_address[1] != "Coming soon"
            ):
                name = location.find(class_="center-search-item-name").text
                street_address = location_address[1].strip()
                if "coming soon" in street_address.lower():
                    continue
                city = location_address[-1].split(",")[0].strip()
                state = location_address[-1].split(",")[-1].split()[0].strip().upper()
                zipp = location_address[-1].split(",")[-1].split()[-1].strip()
                if "" == city:
                    city = "<MISSING>"
                location_hours = list(
                    location.find(
                        "div", {"class": "center-search-item-contact"}
                    ).stripped_strings
                )
                phone = ""
                if "Ph:" in location_hours:
                    phone = location_hours[location_hours.index("Ph:") + 1]
                else:
                    phone = "<MISSING>"
                hours = location_hours[-1]
                if "Contact Info" in hours:
                    hours = ""
                page_url1 = location.find_all("a")[1]["href"]
                if "javascript:togglePreferredCenter" in page_url1:
                    page_url1 = location.find_all("a")[0]["href"]
                page_url = base_url + page_url1
                data_8 = page_url.split("-")[0].split("/")[-1]
                if len(data_8) == 3 and data_8.isdigit():
                    store_number = data_8.replace("eau", "<MISSING>")
                else:
                    store_number = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                if "30721" in zipp:
                    city = "Dalton"
                if "83651" in zipp:
                    city = "Nampa"
                if "62702" in zipp:
                    city = "Springfield"
                if "79924" in zipp:
                    city = "El Paso"
                if "65202" in zipp:
                    city = "columbia"
                if "23502" in zipp:
                    city = "norfolk"

                sgw.write_row(
                    SgRecord(
                        locator_domain="https://www.cslplasma.com",
                        page_url=page_url,
                        location_name=name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zipp,
                        country_code="US",
                        store_number=store_number,
                        phone=phone,
                        location_type="",
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours,
                    )
                )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
