from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.storagewest.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="StateLink")
    locator_domain = "https://www.storagewest.com"

    all_links = []
    for item in items:
        link = item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        links = base.find_all(class_="divLocationsSearchResultFacilityName")
        for i in links:
            all_links.append(i.a["href"])

    for link in all_links:
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.strip()

        raw_address = list(
            base.find(class_="divFacilityContentTitleSmall").stripped_strings
        )
        street_address = raw_address[0].replace(",", "").strip()
        city = raw_address[-1][:-8].strip()
        state = raw_address[-1].strip()[-8:-6].strip()
        zip_code = raw_address[-1][-6:].strip()
        country_code = "US"
        location_type = ""
        store_number = base.article["id"].split("-")[-1]
        phone = base.find(class_="facilityInformationPhone").text.strip()
        hours_of_operation = " ".join(
            list(
                base.find(
                    class_="divContainerFlexColumn divFacilityContentHoursOfficeHours"
                )
                .find(class_="divFacilityContentContentSmall")
                .stripped_strings
            )
        )

        latitude = base.find(class_="divFacilityContentLocationGetDirection")[
            "data-tolat"
        ]
        longitude = base.find(class_="divFacilityContentLocationGetDirection")[
            "data-tolng"
        ]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
