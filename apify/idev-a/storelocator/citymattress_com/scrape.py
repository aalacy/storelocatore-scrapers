from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data():
    locator_domain = "https://www.citymattress.com/"
    base_url = "https://www.citymattress.com/pages/stores"
    with SgRequests() as session:
        soup = bs(session.get(base_url).text, "lxml")
        locations = soup.select(".store-items article.store-item")
        for location in locations:
            page_url = urljoin(
                "https://www.citymattress.com",
                location.select_one("a.store-item__title")["href"],
            )
            location_name = location.select_one("a.store-item__title").text.strip()
            address = list(location.select_one(".store-item__address").stripped_strings)
            street_address = (
                " ".join(address[:-1])
                .replace("Wellington Green Square", "")
                .replace("Pines City Center", "")
                .strip()
            )
            city = address[-1].split(",")[0]
            if "9293 Glades Rd" in city:
                street_address = "9293 Glades Rd"
                city = city.replace("9293 Glades Rd", "").strip()
            hours = [
                _
                for _ in location.select_one(".store-item__hours").text.split("\n")
                if _.strip() and "appointment" not in _.lower()
            ]

            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=address[-1].split(",")[1].strip().split(" ")[0],
                zip_postal=address[-1].split(",")[1].strip().split(" ")[1],
                country_code="US",
                latitude=location["data-lat"],
                longitude=location["data-lng"],
                phone=location.select_one(".store-item__phone a").text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours)
                .replace("\xa0", " ")
                .replace("–", "-")
                .replace("GRAND OPENING", "")
                .replace("pmS", "pm S")
                .strip(),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
