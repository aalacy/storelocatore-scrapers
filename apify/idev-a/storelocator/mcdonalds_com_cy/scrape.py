from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mcdonalds.com.cy"
base_url = "https://mcdonalds.com.cy/locate"


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "ul.restaurant-location-list > li"
        )
        for _ in locations:
            href = _.select_one(".restaurant-location__title a")["href"]
            page_url = locator_domain + href
            raw_address = (
                " ".join(_.select_one(".restaurant-location__address").stripped_strings)
                .replace("\n", " ")
                .replace("\r", "")
                .replace(",", " ")
                .replace("Cyprus", "")
                .strip()
            )
            street_address = city = zip_postal = ""
            _addr = [aa.strip() for aa in raw_address.split(" ") if aa.strip()][::-1]
            for xx, addr in enumerate(_addr):
                if addr.isdigit():
                    zip_postal = addr
                    city = " ".join(_addr[:xx][::-1])
                    break
            if city:
                x = raw_address.find(zip_postal)
                street_address = raw_address[:x].strip()
            if not city:
                city = _addr[xx + 1]
                x = raw_address.find(city)
                street_address = raw_address[:x].strip()
            hours = []
            for hh in _.select_one(
                "div.restaurant-location__hours-set div.hours-table"
            ).select("div.divTableRow"):
                hours.append(f"{' '.join(hh.stripped_strings)}")
            location_type = ""
            if (
                "closed"
                in _.select_one(
                    "div.restaurant-location__hours-set div.special-hours"
                ).text.lower()
            ):
                location_type = "closed"
            coord = (
                _.select_one("a.restaurant-location__directions-link")["href"]
                .split("&daddr=")[1]
                .split(",")
            )
            phone = ""
            if _.select_one("a.phone"):
                phone = _.select_one("a.phone").text.strip()

            yield SgRecord(
                page_url=page_url,
                store_number=href.split("key=")[-1],
                location_name=_.select_one(".restaurant-location__title").text.strip(),
                street_address=street_address,
                city=city,
                zip_postal=zip_postal,
                latitude=coord[0],
                longitude=coord[1],
                country_code="Cyprus",
                phone=phone,
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
