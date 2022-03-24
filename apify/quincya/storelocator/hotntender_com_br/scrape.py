from bs4 import BeautifulSoup

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.powr.io/wix/map/public.json?pageId=c1dmp&compId=comp-kjlksy6d&viewerCompId=comp-kjlksy6d&siteRevision=2339&viewMode=site&deviceType=desktop&locale=pt&regionalLanguage=pt&width=980&height=405&instance=wnf4vAu9a8rhb0mCuAKDFQApoST3EUFD9Y7rtPeOO8w.eyJpbnN0YW5jZUlkIjoiMjJmMmIxNTUtYzJkOS00NjMxLTljNzUtN2Y0MzgwODhiYTljIiwiYXBwRGVmSWQiOiIxMzQwYzVlZC1hYWM1LTIzZWYtNjkzYy1lZDIyMTY1Y2ZkODQiLCJzaWduRGF0ZSI6IjIwMjItMDMtMjJUMDY6Mjg6MjUuODcyWiIsImRlbW9Nb2RlIjpmYWxzZSwiYWlkIjoiNzBkYzY0NWMtOWY3Mi00YTRlLTk0YzgtMzRjMzA3MDA1MzYxIiwic2l0ZU93bmVySWQiOiIxYjY1MzY4NS1hODIzLTQxMjctYWFiZC03YjUzMDU3NzczZDkifQ&currency=BRL&currentCurrency=BRL&commonConfig=%7B%22brand%22%3A%22wix%22%2C%22bsi%22%3A%225656670f-088e-49cd-af01-a7762b552a68%7C1%22%2C%22BSI%22%3A%225656670f-088e-49cd-af01-a7762b552a68%7C1%22%7D&vsi=e173e3b8-6713-4707-87a7-9159cbf5f913&url=https://www.hotntender.com.br/"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["content"]["locations"]

    locator_domain = "https://www.hotntender.com.br/"

    for store in stores:
        location_name = BeautifulSoup(store["name"], "lxml").text
        raw_address = store["address"]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        city = addr.city
        state = addr.state
        try:
            if "Rio De Janeiro" in state:
                state = "RJ"
        except:
            pass
        zip_code = addr.postcode
        country_code = "BR"
        store_number = store["idx"].split("_")[1]
        location_type = ""
        phone = store["number"].split("/")[0]
        hours_of_operation = (
            BeautifulSoup(store["description"], "lxml")
            .text.split(";")[0]
            .replace("Horário de funcionamento:", "")
            .strip()
        )
        if "Delivery" in hours_of_operation:
            hours_of_operation = ""
        latitude = store["lat"]
        longitude = store["lng"]
        link = store["website"]
        if not link:
            link = "https://www.hotntender.com.br/"

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
                raw_address=raw_address,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
