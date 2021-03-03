from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
import re

locator_domain = "https://www.tgscolorado.com/"
base_url = "https://www.tgscolorado.com/stores"


def _valid1(val):
    if val:
        return (
            val.strip()
            .replace("–", "-")
            .encode("unicode-escape")
            .decode("utf8")
            .replace("\\xc3\\xa9", "e")
            .replace("\\xa0", "")
            .replace("\\xa0\\xa", "")
            .replace("\\xae", "")
        )
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url).text, "lxml")
        json_body = json.loads(
            soup.find("script", type="application/json").string.strip()
        )
        for key, result in (
            json_body.get("hydrate", {})
            .get("stores", {})
            .get("view_fields", {})
            .items()
        ):
            # if result.get('field_store_is_active', '') == '1':
            try:
                page_url = (
                    f"https://www.tgscolorado.com/stores/{result['field_store_code']}"
                )
                soup1 = bs(session.get(page_url).text, "lxml")
                hours_of_operation = (
                    soup1.find("h4", string=re.compile("Regular Store Hours"))
                    .next_sibling.text.replace("Open daily", "")
                    .strip()
                )
                longitude = ""
                latitude = ""
                if result.get("field_store_geolocation"):
                    latitude = result.get("field_store_geolocation").split(",")[0]
                    longitude = result.get("field_store_geolocation").split(",")[1]
                yield SgRecord(
                    page_url=page_url,
                    store_number=result.get("field_store_id"),
                    location_name=result.get("field_store_name"),
                    street_address=", ".join(
                        [
                            s
                            for s in [
                                result.get("field_store_address_address_line1", ""),
                                result.get("field_store_address_address_line2", ""),
                            ]
                            if s
                        ]
                    ),
                    city=result.get("field_store_address_locality", ""),
                    state=result.get("field_store_address_administrative_area", ""),
                    zip_postal=result.get("field_store_address_postal_code", ""),
                    country_code=result.get("field_store_address_country_code", ""),
                    phone=result.get("field_store_telephone"),
                    latitude=latitude,
                    longitude=longitude,
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                )
            except:
                import pdb

                pdb.set_trace()


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
