from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import dirtyjson as json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

base_url = "https://www.mendocinofarms.com/locations/"
locator_domain = "https://www.mendocinofarms.com"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "__cfduid=d3c33b3d234c70a282402815e541789581611362267; _ga=GA1.2.1283152201.1611362281; _gid=GA1.2.689218067.1611362281; _gcl_au=1.1.1633464259.1611362283; _fbp=fb.1.1611362284226.313923769; XSRF-TOKEN=eyJpdiI6IkdsbHpDbUpKSVJ2SDloZWhOdVRBUFE9PSIsInZhbHVlIjoiczVoVVdVa1lKVW9IMk83YjhjaVNwakVRalwvbk1CcVJQbnB4QVQ3M092OFBXenRcL0xnY212SHlpNllvQ2Zsd3FlIiwibWFjIjoiZWIxNDA4MzY5ZmNmMGQyYzRjYTVjMGQ1OGRhMzUzNjE3NGQzMTlmNDY0YjFhNTU0N2NmZGFkNjAzN2ZjNzExMCJ9; laravel_session=eyJpdiI6IkdsQkxmNllhM29wRTNMRlJPZjBUSnc9PSIsInZhbHVlIjoiSGlCdGtGT0dFMW1wUkhQczMxVk9rTVN1akJWZ3BqWHN5bjlJS3YrUlFKTEk0OXhhQmwzN0FmK29tdndqZUJnQyIsIm1hYyI6ImMyMTlhMzUzODQ3MDY2MDYwNjViNzUwMWVkNDU3YmQyY2I3OTFkYzNjNTVhNWYxZDI5MThjMDAyZGM0MWQyNWQifQ%3D%3D",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def fetch_data():
    with SgRequests() as session:
        soup = bs(
            session.get(base_url, headers=headers).text,
            "lxml",
        )
        store_list = soup.select("div.locations-all a")
        for store in store_list:
            page_url = store["href"]
            logger.info(page_url)
            res1 = session.get(page_url, headers=headers)
            sp1 = bs(res1.text, "lxml")
            small = sp1.select_one("h1.location-title small")
            if small and "Opening" in small.text:
                continue
            detail = json.loads(sp1.find("script", type="application/ld+json").string)

            street_address = detail["address"]["streetAddress"].replace(
                "(Century Park  Courtyard), ", ""
            )
            hours = ""
            if sp1.select_one('span[aria-label="Location Hours"]'):
                hours = sp1.select_one('span[aria-label="Location Hours"]').text.strip()
            elif sp1.select_one("h2#joinUs"):
                for bb in (
                    sp1.select_one("h2#joinUs").find_next_sibling().stripped_strings
                ):
                    if bb.startswith("Open"):
                        hours = bb.replace("Open", "").strip()
                        break

            yield SgRecord(
                page_url=page_url,
                location_name=detail["name"].replace("&amp;", ""),
                street_address=street_address,
                city=detail["address"]["addressLocality"],
                state=detail["address"]["addressRegion"],
                zip_postal=detail["address"]["postalCode"],
                country_code=detail["address"]["addressCountry"],
                phone=detail["telephone"],
                locator_domain=locator_domain,
                latitude=detail["geo"]["latitude"],
                location_type=detail["@type"][0],
                longitude=detail["geo"]["longitude"],
                hours_of_operation=hours,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
