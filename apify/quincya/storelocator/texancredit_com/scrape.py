from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://texancredit.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="tsI_txt").find_all("a")
    locator_domain = "https://texancredit.com"

    for item in items:
        if "http" not in item["href"]:
            link = locator_domain + item["href"]
        else:
            link = item["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.find(id="section_2").a.text
        raw_address = list(base.find(id="section_2").p.stripped_strings)
        if not raw_address:
            raw_address = list(base.find(id="section_3").p.stripped_strings)

        if "940-692-0600" in raw_address[-2]:
            raw_address.pop(-2)

        if "2Elsa" in raw_address[0]:
            street_address = (
                raw_address[0].split("Elsa")[0].replace("AvenueSuite", "Avenue Suite")
            )
            city = "Elsa"
            state = "TX"
            zip_code = "78543"
        elif "phone" in str(raw_address).lower():
            street_address = " ".join(raw_address[:-3]).strip()
            city_line = raw_address[-3].strip().split(",")
            city = city_line[0].strip()
            state = city_line[1].split()[0].strip()
            zip_code = " ".join(city_line[1].split()[1:]).strip()
        else:
            street_address = " ".join(raw_address[:-3]).strip()
            city_line = raw_address[-2].strip().split(",")
            city = city_line[0].strip()
            state = city_line[1].split()[0].strip()
            zip_code = " ".join(city_line[1].split()[1:]).strip()

        street_address = street_address.replace("Texan Credit Corporation", "").strip()
        state = state.replace(".", "")

        if "345 Bibb Drive" in city:
            street_address = "345 Bibb Drive"
            city = "Eagle Pass"

        if "TX" in city:
            city = city.replace("TX", "").strip()
            zip_code = state
            state = "TX"

        country_code = "US"
        location_type = ""
        store_number = ""
        phone = raw_address[-1].strip()
        hours_of_operation = ""

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
