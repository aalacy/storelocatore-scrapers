import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.germainhotels.com/en/alt-hotel"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    # Get geo data to map with links
    j_data = []

    js = json.loads(base.find(id="__NEXT_DATA__").contents[0])["props"]["pageProps"][
        "globalData"
    ]["hotels"]
    for j in js:
        link = j["uri"]
        if "alt-hotel" in link:
            geo = j["geolocation"]
            j_data.append([link, geo["lat"], geo["lng"]])

    items = base.find_all("a", string="Visit website")

    locator_domain = "germainhotels.com"

    for item in items:
        try:
            link = "https://www.germainhotels.com" + item["href"]
        except:
            continue

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.find(class_="css-2wc3p2").get_text(" ").strip()

        raw_address = base.find(class_="css-16jqdh").text.split(",")
        if len(raw_address) > 4:
            street_address = raw_address[0].strip() + " " + raw_address[1].strip()
        else:
            street_address = raw_address[0]

        city = raw_address[-3].strip()
        state = raw_address[-2].strip()
        zip_code = raw_address[-1].strip()
        if zip_code == "TG2 0G1":
            zip_code = "T2G 0G1"
        if zip_code == "K1P OC8":
            zip_code = "K1P 0C8"

        country_code = "CA"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        phone = base.find(class_="css-wrulco").text.strip()

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        for j in j_data:
            if j[0] in link:
                latitude = j[1]
                longitude = j[2]
                break

        hours_of_operation = "<MISSING>"

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
