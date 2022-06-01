from lxml import html

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    locator_domain = "landrover.ca"

    headers_landrover_ca = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
    }

    def get_store_urls():
        url = "https://inventory.landrover.ca/contact/?postcode=M4C+1A1&postcode-area=CA&distance=20000"
        with SgRequests(
            proxy_country="ca",
        ) as http:
            r = http.get(url, headers=headers_landrover_ca)
            pgtext = r.text
            sel = html.fromstring(pgtext)
            hrefs = sel.xpath(
                '//div[@class="location-no"]/a[contains(@href, "/inventory.landrover.ca/contact/")]/@href'
            )
            hrefs = ["https:" + i for i in hrefs]
            return hrefs

    store_urls = get_store_urls()

    session = SgRequests()

    found = []
    for link in store_urls:
        req = session.get(link, headers=headers_landrover_ca)
        base = BeautifulSoup(req.text, "lxml")
        location_name = base.find_all(class_="title")[-1].text
        if "Manasa" in location_name:
            continue
        try:
            street_address = (
                base.find(class_="address-line1").text.replace(",", "").strip()
            )
        except:
            continue
        city = base.find(class_="address-city").text.replace(",", "").strip()
        state = base.find(class_="address-county").text.replace(",", "").strip()
        try:
            zip_code = base.find(class_="address-postcode").text.strip()
        except:
            zip_code = ""
        try:
            phone = base.find(class_="nd-dynamo-telephony").text
        except:
            phone = ""
        if street_address == "5680 Parkwood Crescent" and not phone:
            continue
        if street_address + location_name in found:
            continue
        found.append(street_address + location_name)

        country_code = "CA"
        location_type = ""
        store_number = ""
        latitude = base.find(class_="location-directions module data-lat-long")[
            "data-latitude"
        ]
        longitude = base.find(class_="location-directions module data-lat-long")[
            "data-longitude"
        ]
        try:
            hours_of_operation = " ".join(
                list(base.find(class_="loc-hours-table").stripped_strings)
            )
        except:
            hours_of_operation = ""

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
