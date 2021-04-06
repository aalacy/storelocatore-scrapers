from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://chop.ca"
    base_url = "https://chop.ca/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select(
            "div.location-block div.location-block__all__container li.location-block__location a"
        )
        for link in links:
            if not link["href"].startswith("/"):
                continue
            page_url = locator_domain + link["href"]
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            location_name = soup1.select_one("h1.title").text
            street_address = soup1.select_one(
                'div.location-wrap span[itemprop="streetAddress"]'
            ).text.strip()
            city = soup1.select_one(
                'div.location-wrap span[itemprop="addressLocality"]'
            ).text.strip()
            state = soup1.select_one(
                'div.location-wrap span[itemprop="addressRegion"]'
            ).text.strip()
            zip_postal = soup1.select_one(
                'div.location-wrap span[itemprop="postalCode"]'
            ).text.strip()
            phone = soup1.find("a", href=re.compile(r"tel:"))["href"].split(":")[1]
            hours = []
            temp = list(soup1.select_one("div.hours-wrapper div").stripped_strings)
            for x in range(0, len(temp), 2):
                hours.append(f"{temp[x]} {temp[x+1]}")

            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
