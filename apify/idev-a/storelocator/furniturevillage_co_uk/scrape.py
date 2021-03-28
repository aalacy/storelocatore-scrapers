from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.furniturevillage.co.uk"
    base_url = "https://www.furniturevillage.co.uk/stores/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        for link in soup.find(
            "div", {"class": "col-xs-12 select-store no-pd"}
        ).find_all("option"):
            if not link["value"]:
                continue
            page_url = base_url + link["value"]
            r1 = session.get(page_url, headers=_headers)
            soup1 = bs(r1.text, "lxml")
            location_name = soup1.select_one("h1.content-title").text
            street_address = soup1.find("span", {"itemprop": "streetAddress"}).text
            city = soup1.find("span", {"itemprop": "addressLocality"}).text.strip()
            state = soup1.find("span", {"itemprop": "addressRegion"}).text.strip()
            zipp = soup1.find("span", {"itemprop": "postalCode"}).text.strip()
            phone = soup1.find("meta", {"itemprop": "telephone"})["content"]
            latitude = soup1.find("meta", {"itemprop": "latitude"})["content"]
            longitude = soup1.find("meta", {"itemprop": "longitude"})["content"]
            hours = []
            location_type = ""
            for hour in soup1.select("div.item-hours p"):
                if re.search(r"This store reopens on", hour.text, re.IGNORECASE):
                    location_type = "Closed"
                    continue
                if re.search(r"temporarily closed", hour.text, re.IGNORECASE):
                    location_type = "Closed"
                    continue
                hours.append(": ".join(hour.stripped_strings))

            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                latitude=latitude,
                longitude=longitude,
                zip_postal=zipp,
                country_code="Uk",
                phone=phone,
                locator_domain=locator_domain,
                location_type=location_type,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
