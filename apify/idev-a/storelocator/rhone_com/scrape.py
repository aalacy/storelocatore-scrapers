from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs

locator_domain = "https://www.rhone.com"


def fetch_data():
    with SgRequests() as session:
        res = session.get("https://www.rhone.com/pages/find-retail-location")
        store_list = bs(res.text, "lxml").select("div.swiper-slide")
        for store in store_list:
            index = int(store["data-value"])
            if index > 4:
                continue
            detail = bs(res.text, "lxml").select("ul.store-locator-links li")[index - 1]
            page_url = "https://www.rhone.com/pages/find-retail-location"
            location_name = detail.text.split("\n")[0]
            addr = parse_address_intl(store.select("h4")[0].text)
            zip = addr.postcode
            city = addr.city
            state = addr.state
            street_address = addr.street_address_1
            country_code = addr.country
            phone = detail.select_one("a.call-btn")["href"].split(":").pop().strip()
            geo = detail.select("a.call-btn")[1]["href"].split("@").pop().split(",")
            latitude = geo[0]
            longitude = geo[1]
            try:
                hours_of_operation = store.select("h4")[1].text
                hours_of_operation = (
                    hours_of_operation.replace("\n", " ").split("Pickup").pop().strip()
                )
            except:
                hours_of_operation = store.select("div.boxes-info")[1].text
            record = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                phone=phone,
                locator_domain=locator_domain,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
