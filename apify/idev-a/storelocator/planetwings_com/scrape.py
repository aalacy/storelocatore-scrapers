from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs


locator_domain = "https://planetwings.com"


def fetch_data():
    with SgRequests() as session:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "cookie": "_ga=GA1.2.1212088468.1614120720; _gid=GA1.2.48523111.1614120720; _gat=1; _gat_UA-74712390-1=1; _fbp=fb.1.1614120720364.506007364; pum-952=true",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
        }
        res = session.get("https://planetwings.com/locations2", headers=headers)
        store_list = bs(res.text, "lxml").select("div.vc_tta-panel")
        for store in store_list:
            page_url = "https://planetwings.com/locations2"
            location_name = store.select_one("span.vc_tta-title-text").string
            try:
                address_detail = (
                    store.select_one("span.wpsl-city").text.strip().split(" ")
                )
                zip = address_detail.pop()
                state = address_detail.pop()
                street_address = store.select_one("span.wpsl-street").text.strip()
                country_code = store.select_one("span.wpsl-country").text.strip()
            except:
                address = store.select_one("div.wpb_wrapper h2").text
                address = address.split(", ")
                address_detail = address.pop().split(" ")
                country_code = address_detail.pop()
                zip = address_detail.pop()
                street_address = " ".join(address)
            state = location_name.split(", ").pop()
            city = location_name.split(", ")[0]
            try:
                phone = store.select_one(".wpsl-contact-details").text.replace(
                    "T: ", ""
                )
            except:
                try:
                    phone = (
                        store.select_one("div.wpb_wrapper")
                        .select("h3")
                        .pop()
                        .text.replace("T: ", "")
                    )
                except:
                    phone = (
                        store.select_one("div.wpb_wrapper")
                        .select("h1")
                        .pop()
                        .text.replace("T: ", "")
                    )
            record = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=zip,
                state=state,
                phone=phone.replace("WING", ""),
                locator_domain=locator_domain,
                country_code=country_code,
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
