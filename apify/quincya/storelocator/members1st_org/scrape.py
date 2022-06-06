from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://webapps.members1st.org/BranchLocatorApi/finder/location/40.1732512/-76.9988669/200?CrowFliesDistanceOnly=false"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["items"]

    locator_domain = "https://www.members1st.org/"

    for store in stores:
        if store["locationTypeName"] != "Branch":
            continue
        location_name = store["name"]
        street_address = store["address"]
        city = store["city"]
        state = store["state"]
        zip_code = store["zip"]
        country_code = "US"
        store_number = ""
        location_type = ""
        latitude = store["latitude"]
        longitude = store["longitude"]
        try:
            link = (
                "https://www.members1st.org/atm-and-locations/"
                + store["branchPageUrlId"]
            )
        except:
            continue

        hours_of_operation = ""
        try:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            phone = (
                base.find("span", attrs={"itemprop": "telephone"})
                .text.replace("Phone:", "")
                .strip()
            )
            hours_of_operation = " ".join(
                list(base.find(class_="lobby-hours").table.stripped_strings)
            )
        except:
            raw_hours = store["timeframes"]
            for row in raw_hours:
                if row["serviceTypeName"] == "Lobby":
                    day = row["dayName"]
                    if row["openTime"]:
                        hours = row["openTime"] + "-" + row["closeTime"]
                    else:
                        hours = "Closed"
                    hours_of_operation = (
                        hours_of_operation + " " + day + " " + hours
                    ).strip()

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
