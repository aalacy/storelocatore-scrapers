from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _phone(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://boombozz.com"
    base_url = "https://boombozz.com/wp-admin/admin-ajax.php?action=store_search&lat=38.23184&lng=-85.71014&max_results=500&search_radius=500&autoload=1"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            desc = bs(_["description"], "lxml")
            ps = desc.select("p")
            if "This location is an" in ps[0].text or "DINE IN" in ps[0].text:
                del ps[0]
            block = list(ps[0].stripped_strings)
            hours = []
            for hh in block:
                if "Delivery" in hh:
                    break
                if "Dine In" in hh:
                    continue
                text = (
                    hh.replace("–", "-")
                    .replace("&", "-")
                    .replace("|", ":")
                    .replace("\xa0", " ")
                )
                if text.split("-")[0].strip() in days:
                    hours.append(text)
                elif hours:
                    last = hours.pop()
                    hours.append(last + text)
            page_url = ""
            if desc.select("a.yelpReview"):
                page_url = desc.select("a.yelpReview")[1]["href"]
            location_type = ""
            if "Temporarily Closed" in _["description"]:
                location_type = "Temporarily Closed"
            if page_url and not page_url.startswith("http"):
                page_url = locator_domain + page_url
            if not page_url:
                page_url = "https://boombozz.com/locations/"
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["store"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                phone=_["phone"],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
