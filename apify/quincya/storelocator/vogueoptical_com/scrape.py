from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://vogueoptical.com/find-store/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(id="stores-section").find_all("li")
    locator_domain = "https://vogueoptical.com"

    for item in items:
        location_name = ""
        street_address = item.p.text.strip()
        city = item.find_all("p")[1].text.split(",")[0]
        state = (
            item.find_all("p")[1]
            .text.split(",")[1]
            .replace("PEI", "Prince Edward Island")
        )
        zip_code = ""

        if "(" in street_address:
            location_name = street_address.split("(")[0].strip()
            street_address = street_address.split("(")[1].split(")")[0].strip()

        country_code = "CA"
        store_number = item.a["class"][1]

        if "http" not in item.a["href"]:
            link = locator_domain + item.a["href"]
        else:
            link = item.a["href"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        if "store has merged" in base.text:
            continue

        if street_address.split()[-1] in ["Plaza", "Centre"]:
            street_address = base.find_all("h3")[1].text.split(",")[0]
            if "(" in street_address:
                location_name = street_address.split("(")[0].strip()
                street_address = street_address.split("(")[1].split(")")[0].strip()

        phone = (
            base.find("h5", string="Phone")
            .find_next()
            .text.replace("\xa0", " ")
            .strip()
        )
        location_type = ", ".join(
            list(base.find("h5", string="Services").find_next("ul").stripped_strings)
        )
        try:
            hours_of_operation = " ".join(
                list(base.find("h5", string="Hours").find_next("p").stripped_strings)
            )
        except:
            hours_of_operation = " ".join(
                list(
                    base.find(
                        class_="et_pb_column et_pb_column_4_4 et_pb_column_inner et_pb_column_inner_2 et-last-child"
                    ).stripped_strings
                )
            )

        try:
            map_link = base.iframe["src"]
            lat_pos = map_link.rfind("!3d")
            latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
            lng_pos = map_link.find("!2d")
            longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
