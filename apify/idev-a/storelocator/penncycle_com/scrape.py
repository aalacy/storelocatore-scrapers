from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.freewheelbike.com/"
    base_url = "https://www.freewheelbike.com/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        location_h3 = soup.find("h3", string=re.compile(r"Locations", re.IGNORECASE))
        locations = location_h3.find_next_siblings("a")
        for link in locations:
            soup1 = bs(session.get(link["href"], headers=_headers).text, "lxml")
            location_type = ""
            if re.search(
                r"Temporarily Closed",
                soup1.select_one("span.seStoreLocationDBA").text,
                re.IGNORECASE,
            ):
                location_type = "Temporarily Closed"
            latitude = soup1.select_one("div.seSingleStoreMap")["data-lat"]
            longitude = soup1.select_one("div.seSingleStoreMap")["data-long"]

            hours = []
            for tr in soup1.select("div.seStoreHours tbody tr"):
                time = tr.select("td")[0].text
                if time.lower() != "closed":
                    time = f"{tr.select('td')[0].text}-{tr.select('td')[1].text}"
                hours.append(f"{tr.th.text}: {time}")
            yield SgRecord(
                page_url=link["href"],
                location_name=soup1.select_one("span.seStoreName").text,
                street_address=soup1.select_one(
                    'div.seStoreAddress div[itemprop="streetAddress"]'
                ).text.strip(),
                city=soup1.select_one(
                    'div.seStoreAddress span[itemprop="addressLocality"]'
                ).text.strip(),
                state=soup1.select_one(
                    'div.seStoreAddress span[itemprop="addressRegion"]'
                ).text.strip(),
                zip_postal=soup1.select_one(
                    'div.seStoreAddress span[itemprop="postalCode"]'
                ).text.strip(),
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                phone=soup1.select_one('span[itemprop="telephone"]').text,
                country_code="US",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
