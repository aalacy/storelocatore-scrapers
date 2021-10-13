from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.swatch.com/en-us/stores"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://www.swatch.com"

    token = base.find("div", attrs={"data-token-name": "csrf_token"})[
        "data-token-value"
    ]

    countries = ["United States", "Canada", "United Kingdom"]
    codes = ["us", "ca", "gb"]

    for i, country in enumerate(countries):
        code = codes[i].upper()

        c_link = (
            "https://www.swatch.com/on/demandware.store/Sites-swarp-AM-Site/en_"
            + code
            + "/Stores-FindStores?csrf_token="
            + token[:-1]
            + "%3D"
        )

        items = session.get(c_link, headers=headers).json()["stores"]

        for item in items:

            location_name = item["name"]
            street_address = (item["address1"] + " " + item["address2"]).strip()
            city = item["city"]
            state = item["stateCode"]
            if "CA 941" in item["postalCode"]:
                state = "CA"
            zip_code = item["postalCode"].replace("CA 94128", "94128")
            if len(zip_code.split()) == 3:
                zip_code = zip_code[-7:].strip()
            if zip_code in street_address:
                street_address = street_address.replace("zip_code", "").strip()
            if "TN1 2SR" in street_address:
                zip_code = "TN1 2SR"
                street_address = street_address.replace("TN1 2SR", "").strip()
            country_code = codes[i].upper()
            store_number = item["ID"]
            phone = item["phone"]
            location_type = ""
            latitude = item["lat"]
            longitude = item["lng"]
            link = locator_domain + item["detailsUrl"]
            hours_of_operation = item["storeHours"]

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
