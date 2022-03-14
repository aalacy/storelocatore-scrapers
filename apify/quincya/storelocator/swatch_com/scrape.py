from bs4 import BeautifulSoup

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger("swatch.com")


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "https://www.swatch.com"

    countries_link = "https://www.swatch.com/de-at/choosecountry"
    req = session.get(countries_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    countries = base.find_all("span", attrs={"data-widget": "countrySelectorLocale"})

    found = []
    for country in countries:
        code = country["data-locale"]
        try:
            country["data-id"].split("-")[1]
        except:
            if "_BE" in code:
                code = "fr_BE"
            elif "_CH" in code:
                code = "fr_CH"
            else:
                code = "en_" + code.split("_")[1]
        if code in found:
            continue
        found.append(code)

        stores_link = (
            "https://www.swatch.com/" + code.replace("_", "-").lower() + "/stores"
        )
        log.info(stores_link)
        req = session.get(stores_link, headers=headers)
        try:
            base = BeautifulSoup(req.text, "lxml")
        except:
            continue

        swarp = (
            base.find(class_="b-search")["data-url"].split("store/")[1].split("/")[0]
        )

        token = base.find("div", attrs={"data-token-name": "csrf_token"})[
            "data-token-value"
        ]
        c_link = (
            "https://www.swatch.com/on/demandware.store/"
            + swarp
            + "/"
            + code
            + "/Stores-FindStores?csrf_token="
            + token[:-1]
            + "%3D"
        )
        items = session.get(c_link, headers=headers).json()["stores"]

        for item in items:

            location_name = item["name"]
            street_address = (
                (item["address1"] + " " + item["address2"]).strip().split(", AB")[0]
            )
            if location_name + street_address in found:
                continue
            found.append(location_name + street_address)

            city = item["city"]
            state = item["stateCode"]
            zip_code = item["postalCode"].replace("CA 94128", "94128")
            if len(zip_code.split()) == 3:
                zip_code = zip_code[-7:].strip()
            if zip_code in street_address:
                street_address = street_address.replace("zip_code", "").strip()
            if "TN1 2SR" in street_address:
                zip_code = "TN1 2SR"
                street_address = street_address.replace("TN1 2SR", "").strip()
            country_code = item["countryCode"]
            store_number = item["ID"]
            phone = item["phone"]
            # ----------Location Type -----------#
            brands = []
            for b in item["brands"]:
                brand = b["value"]
                brands.append(brand)
            location_type = (",").join(brands)

            latitude = item["lat"]
            longitude = item["lng"]
            if "." not in str(latitude):
                latitude = ""
                longitude = ""
            link = locator_domain + item["detailsUrl"]
            hours_of_operation = item["storeHours"]
            if not state:
                if "/united-states" in link:
                    state = (
                        link.split("united-states/")[1]
                        .split("/")[0]
                        .replace("-", " ")
                        .replace("1", "")
                        .strip()
                        .title()
                    )
                elif "/canada/" in link:
                    state = (
                        link.split("canada/")[1]
                        .split("/")[0]
                        .replace("-", " ")
                        .replace("1", "")
                        .strip()
                        .title()
                    )

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
