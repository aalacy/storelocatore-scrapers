from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.btbautoparts.com"
base_url = "https://code.metalocator.com/index.php?option=com_locator&view=directory&force_link=1&tmpl=component&task=search_zip&framed=1&format=raw&no_html=1&templ[]=address_format&layout=_jsonfast&radius=304&interface_revision=453&user_lat=0&user_lng=0&Itemid=11595&preview=0&parent_table=&parent_id=0&search_type=point&_opt_out=&ml_location_override=&tab-group=on&limitstart=0&limit=50&show_distance=1&limitstart={}&limit=50"


def fetch_data():
    with SgRequests() as session:
        limit = 0
        while True:
            locations = session.get(base_url.format(limit), headers=_headers).json()
            for _ in locations:
                try:
                    page_url = bs(_["html"], "lxml").select_one(
                        "a.collapse_list_reveal"
                    )["href"]
                except:
                    break
                if not page_url.startswith("http"):
                    page_url = "https:" + page_url
                hours = []
                if _.get("fields"):
                    for hh in bs(_["fields"].get("hours").get("meta"), "lxml").select(
                        "meta"
                    ):
                        hours.append(hh["content"])
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["id"],
                    location_name=_["name"],
                    street_address=_.get("address"),
                    city=_.get("city"),
                    state=_.get("state"),
                    zip_postal=_.get("postalcode"),
                    country_code=_.get("country", "United States"),
                    phone=_.get("phone"),
                    latitude=_["lat"],
                    longitude=_["lng"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )

            if locations:
                limit += 50
            else:
                break


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
