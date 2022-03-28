import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://nativerootscannabis.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://nativerootscannabis.com/"

    script = base.find("script", attrs={"type": "application/json"}).contents[0]
    stores = json.loads(script)["props"]["pageProps"]["locations"]

    for store in stores:
        location_name = store["name"]
        try:
            street_address = store["address1"] + " " + store["address2"]
        except:
            street_address = store["address1"]
        city = store["city"]
        state = store["state"]
        zip_code = store["postalCode"]
        country_code = "US"
        store_number = ""
        location_type = ""
        phone = store["phone"]
        latitude = store["gpsLocation"]["lat"]
        longitude = store["gpsLocation"]["lon"]

        link = "https://nativerootscannabis.com/locations/" + store["slug"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        script = base.find("script", attrs={"type": "application/json"}).contents[0]
        loc = json.loads(script)["props"]["pageProps"]["page"]["contentTop"]["json"][
            "content"
        ]

        hours_of_operation = ""
        hours_found = False
        for i in loc:
            if not hours_found:
                try:
                    if i["content"][0]["value"] == "Hours":
                        hours_found = True
                except:
                    pass
            else:
                try:
                    hours_of_operation = (
                        hours_of_operation.strip()
                        + " "
                        + i["content"][0]["value"].strip()
                    )
                except:
                    break
        hours_of_operation = hours_of_operation.split("Delivery")[0].strip()

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
