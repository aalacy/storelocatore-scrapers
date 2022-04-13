import json
from bs4 import BeautifulSoup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests

session = SgRequests(dont_retry_status_codes=([404]))


def fetch_data(sgw: SgWriter):
    headers = {
        "authority": "sambabraziliansteakhouse.com",
        "cache-control": "max-age=0",
        "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    }
    base_url = "https://www.sambabraziliansteakhouse.com/"
    locator_domain = base_url
    r = session.get("https://www.sambabraziliansteakhouse.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    script = soup.find_all("script", {"type": "application/ld+json"})[-1]
    l1 = json.loads(script.contents[0])
    location_name = l1["name"]
    street_address = l1["address"]["streetAddress"]
    city = l1["address"]["addressLocality"]
    state = l1["address"]["addressRegion"]
    zip_code = l1["address"]["postalCode"]
    country_code = "US"
    store_number = ""
    phone = soup.find("p", {"data-aid": "FOOTER_PHONE_RENDERED"}).text
    location_type = "<MISSING>"
    latitude = l1["geo"]["latitude"]
    longitude = l1["geo"]["longitude"]
    hours = l1["openingHoursSpecification"]
    hours_list = []
    for hour in hours:
        days = hour["dayOfWeek"]
        for d in days:
            time = hour["opens"] + " - " + hour["closes"]
            hours_list.append(d + ":" + time)

    hours_of_operation = (
        "; ".join(hours_list).strip().replace("00:00 - 00:00", "Closed")
    )

    sgw.write_row(
        SgRecord(
            locator_domain=locator_domain,
            page_url=base_url,
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
