from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://www.powr.io/wix/map/public.json?pageId=rda7c&compId=comp-k8s2ixwy&viewerCompId=comp-k8s2ixwy&siteRevision=1129&viewMode=site&deviceType=desktop&locale=en&tz=America%2FLos_Angeles&regionalLanguage=en&width=980&height=635&instance=02trTfJUnY80ZlVq9FmMn9I8a2QKvGYNBGclEoc8Vc0.eyJpbnN0YW5jZUlkIjoiZGE2MmZiOTMtZTNhYS00OTE5LWFmYTgtMTNiYzA0MjIyOTRlIiwiYXBwRGVmSWQiOiIxMzQwYzVlZC1hYWM1LTIzZWYtNjkzYy1lZDIyMTY1Y2ZkODQiLCJzaWduRGF0ZSI6IjIwMjEtMDktMzBUMDg6NDM6NDkuNDcwWiIsInZlbmRvclByb2R1Y3RJZCI6ImJ1c2luZXNzIiwiZGVtb01vZGUiOmZhbHNlLCJhaWQiOiJhMTQyMGU4OC1iMzU2LTQ1YWYtOThhOS0zYzY5MjUwYmNlOTgiLCJzaXRlT3duZXJJZCI6IjUxNzMzNWRhLTY4NTQtNDUzYS1iMjg2LTFmNWUxYjk5YjdkMyJ9&currency=USD&currentCurrency=USD&commonConfig=%7B%22brand%22%3A%22wix%22%2C%22bsi%22%3A%22715a0f8a-c878-4835-9e3a-6e40d0d9d08d%7C1%22%2C%22BSI%22%3A%22715a0f8a-c878-4835-9e3a-6e40d0d9d08d%7C1%22%7D&vsi=d3c88002-78ad-4643-ad46-6d92dd0acf3d&url=https://www.zerodegreescompany.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "zerodegreescompany.com"

    stores = session.get(base_link, headers=headers).json()["content"]["locations"]
    for store in stores:
        if "coming soon" in str(store).lower():
            continue
        location_name = BeautifulSoup(store["name"], "lxml").text
        raw_address = (
            store["address"]
            .replace("Vegas ", "Vegas,")
            .replace("United States ", "")
            .replace("Plano TX,", "Plano, TX")
            .replace("Irving TX,", "Irving, TX")
            .split(",")
        )
        if "USA" in raw_address[-1] or "United" in raw_address[-1]:
            raw_address.pop(-1)
        street_address = " ".join(raw_address[:-1])
        if "  " in street_address:
            city = street_address.split("  ")[-1].strip()
        else:
            city = street_address.split()[-1].strip()
        street_address = street_address.replace(city, "").replace("  ", " ").strip()
        state = raw_address[-1].split()[0].strip()
        zip_code = raw_address[-1].split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = store["number"].strip()
        if not phone:
            phone = BeautifulSoup(store["description"], "lxml").p.text
        hours_of_operation = ""
        latitude = store["lat"]
        longitude = store["lng"]
        link = "https://www.zerodegreescompany.com/locations"

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


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
