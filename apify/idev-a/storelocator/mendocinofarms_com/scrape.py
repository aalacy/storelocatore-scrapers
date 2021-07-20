from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests

base_url = "https://www.mendocinofarms.com"
locator_domain = "https://www.mendocinofarms.com"


def fetch_data():
    with SgRequests() as session:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "cache-control": "max-age=0",
            "cookie": "__cfduid=d3c33b3d234c70a282402815e541789581611362267; _ga=GA1.2.1283152201.1611362281; _gid=GA1.2.689218067.1611362281; _gcl_au=1.1.1633464259.1611362283; _fbp=fb.1.1611362284226.313923769; XSRF-TOKEN=eyJpdiI6IkdsbHpDbUpKSVJ2SDloZWhOdVRBUFE9PSIsInZhbHVlIjoiczVoVVdVa1lKVW9IMk83YjhjaVNwakVRalwvbk1CcVJQbnB4QVQ3M092OFBXenRcL0xnY212SHlpNllvQ2Zsd3FlIiwibWFjIjoiZWIxNDA4MzY5ZmNmMGQyYzRjYTVjMGQ1OGRhMzUzNjE3NGQzMTlmNDY0YjFhNTU0N2NmZGFkNjAzN2ZjNzExMCJ9; laravel_session=eyJpdiI6IkdsQkxmNllhM29wRTNMRlJPZjBUSnc9PSIsInZhbHVlIjoiSGlCdGtGT0dFMW1wUkhQczMxVk9rTVN1akJWZ3BqWHN5bjlJS3YrUlFKTEk0OXhhQmwzN0FmK29tdndqZUJnQyIsIm1hYyI6ImMyMTlhMzUzODQ3MDY2MDYwNjViNzUwMWVkNDU3YmQyY2I3OTFkYzNjNTVhNWYxZDI5MThjMDAyZGM0MWQyNWQifQ%3D%3D",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        }
        soup = bs(
            session.get(
                "https://www.mendocinofarms.com/locations/", headers=headers
            ).text,
            "lxml",
        )
        store_list = soup.select("div.locations-all a")
        for store in store_list:
            page_url = store["href"]
            if "Opening" in store.text:
                continue
            res1 = session.get(page_url, headers=headers)
            try:
                detail = json.loads(
                    res1.text.split('<script type="application/ld+json">')[1].split(
                        "</script>"
                    )[0]
                )
            except:
                detail_text = (
                    res1.text.split('<script type="application/ld+json">')[1]
                    .split("</script>")[0]
                    .replace("\n", "")
                    .replace("\t", "")
                )
                detail_text = detail_text[:394] + detail_text[395:]
                detail = json.loads(detail_text)

            street_address = detail["address"]["streetAddress"].replace(
                "(Century Park  Courtyard), ", ""
            )
            hours_of_operation = (
                bs(res1.text, "lxml")
                .select("div.location-details")
                .pop()
                .select_one("div")
                .contents[:-3]
                .pop()
                .text.replace("\n", " ")
                .replace("Phone lines open at 8am", "")
                .strip()
            )
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
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
