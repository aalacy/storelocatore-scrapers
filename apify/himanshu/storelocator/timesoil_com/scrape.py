import re
from sgrequests import SgRequests
from bs4 import BeautifulSoup

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data(sgw: SgWriter):
    base_url = "http://timesoil.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    r = session.get(base_url + "/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    main = soup.find("div", {"class": "elementor-section-wrap"}).find_all(
        "section", {"class": "elementor-element"}
    )
    del main[0]
    for sec in main:
        main1 = list(
            sec.find("div", {"class": "elementor-icon-box-content"}).stripped_strings
        )
        name = main1[0].strip()
        country = "US"
        lat = ""
        lng = ""
        hour = ""
        city = ""
        storeno = name.split("-")[0].replace("#", "").strip()
        madd = main1[1].strip().split(",")
        addr = parse_address_intl(re.sub(r"\s+", " ", str(madd[0])))
        address = addr.street_address_1
        city = addr.city

        try:
            state = madd[1].strip().split(" ")[0].strip()
        except:
            madd = main1[2].strip().split(",")
            city = madd[0]
            state = madd[1].strip().split(" ")[0].strip()

        zip = madd[1].split()[1].strip()

        if not city:
            city = address.split()[-1]
            address = address.replace(city, "").strip()

        phone = re.findall(
            r"[\d]{3}-[\d]{3}-[\d]{4}",
            str(sec),
        )[0]

        sgw.write_row(
            SgRecord(
                locator_domain=base_url,
                page_url=base_url + "/locations/",
                location_name=name,
                street_address=address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code=country,
                store_number=storeno,
                phone=phone,
                location_type="<MISSING>",
                latitude=lat,
                longitude=lng,
                hours_of_operation=hour,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
