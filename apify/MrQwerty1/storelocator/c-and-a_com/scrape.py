from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_countries():
    countries = []
    r = session.get("https://www.c-and-a.com/stores/es-es/index.html", headers=headers)
    tree = html.fromstring(r.text)
    options = tree.xpath("//select[@id='countrypicker']/option/@value")
    for option in options:
        countries.append(option.split("-")[0].upper())

    return countries


def fetch_data(sgw: SgWriter):
    countries = get_countries()
    for country in countries:
        api = f"https://www.c-and-a.com/stores/stormdata_{country}.json"
        r = session.get(api, headers=headers)
        js = r.json()

        for j in js:
            location_name = j.get("name")
            part = j.get("urlCountryCode")
            slug = j.get("url")
            page_url = f"https://www.c-and-a.com/stores/{part}/{slug}"
            adr1 = j.get("streetEnglishName") or ""
            adr2 = j.get("streetNumberText") or ""
            street_address = f"{adr1} {adr2}".strip()
            city = j.get("cityEnglishText")
            postal = j.get("zipCodeText")

            phone = j.get("phoneNumber") or ""
            if "/" in phone:
                phone = phone.split("/")[0].strip()
            latitude = j.get("lat")
            longitude = j.get("lng")
            location_type = j.get("storeType")
            store_number = j.get("storeCode")

            _tmp = []
            hours = j.get("openingHours") or []
            for h in hours:
                day = h.get("weekdayDescription")
                start = h.get("openingTime")
                end = h.get("closingTime")
                _tmp.append(f"{day}: {start}-{end}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=country,
                location_type=location_type,
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.c-and-a.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
