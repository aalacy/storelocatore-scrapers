from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests


def fetch_data():
    locator_domain = "https://www.hamleys.com"
    base_url = "https://www.hamleys.com/find-a-store"
    with SgRequests() as session:
        soup = bs(session.get(base_url).text, "lxml")
        page_links = soup.select("div.find-store ul a")
        for link in page_links:
            headers = {
                "accept": "*/*",
                "content-length": "22",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "cookie": 'PHPSESSID=cfd91cbd4919579ecbc54d020ca5fa66; form_key=3vGnmitjNYaPDoHn; mage-banners-cache-storage=%7B%7D; mage-cache-storage=%7B%7D; mage-cache-storage-section-invalidation=%7B%7D; mage-cache-sessid=true; mage-messages=; recently_viewed_product=%7B%7D; recently_viewed_product_previous=%7B%7D; recently_compared_product=%7B%7D; recently_compared_product_previous=%7B%7D; product_data_storage=%7B%7D; PHPSESSID=cfd91cbd4919579ecbc54d020ca5fa66; form_key=3vGnmitjNYaPDoHn; _ga=GA1.2.792531740.1610704921; _gid=GA1.2.45376347.1610704921; _fbp=fb.1.1610704924086.422481675; _hjTLDTest=1; _hjid=c3a50b1e-7c57-43ba-86ab-6cb1c8f8639a; _hjFirstSeen=1; _hjAbsoluteSessionInProgress=1; _sp_ses.fe1b=*; smc_uid=1610704935159409; smc_tag=eyJpZCI6MTk1NSwibmFtZSI6ImhhbWxleXMuY29tIn0=; smc_refresh=13184; smc_sesn=1; smc_not=default; private_content_version=c90fd986e5db7a9065440a499265516f; _uetsid=b62ee020571811eb8e6df30fa29e85fa; _uetvid=b62ef3b0571811ebb7a047247ac08a75; smc_spv=4; smc_tpv=4; smct_last_ov=[{"id":40665,"loaded":1610706257235,"open":null,"eng":null,"closed":null}]; smc_v4_40665={"timer":0,"start":1610704941651,"last":1610704941651,"disp":null,"close":null,"reset":null,"engaged":null,"active":1610706258730,"cancel":null,"fm":null}; section_data_ids=%7B%7D; _sp_id.fe1b=762307b8-9a5b-4ec2-88bb-a90e6fcef14c.1610704928.1.1610706794.1610704928.135d30fa-3546-44c7-8f07-475d257e9913; smct_session={"s":1610704936174,"l":1610706829522,"lt":1610706829523,"t":1621,"p":734}',
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
                "x-requested-with": "XMLHttpRequest",
            }
            payload = {"id": "store." + link["href"]}
            html = json.loads(
                session.post(
                    "https://www.hamleys.com/ajaxcms", data=payload, headers=headers
                ).text
            )["html"]
            if not html:
                continue
            soup = bs(
                html,
                "lxml",
            )
            store = json.loads(soup.select_one("div.find-store-map")["data-locations"])[
                0
            ]
            hours = []
            for hour in soup.select("div.pagebuilder-column table tbody tr")[1:]:
                hours.append(
                    f"{hour.select('td')[0].text}: {hour.select('td')[1].text}-{hour.select('td')[2].text}"
                )

            yield SgRecord(
                page_url=base_url,
                location_name=store["location_name"],
                street_address=store["address"],
                city=store["city"],
                state=store["state"],
                latitude=store["position"]["latitude"],
                longitude=store["position"]["longitude"],
                zip_postal=store["zipcode"],
                country_code=store["country"],
                phone=store["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
