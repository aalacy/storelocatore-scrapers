import httpx
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):
    with SgRequests() as http:
        api_url = (
            "https://www.miumiu.com/us/en/store-locator.miumiu.getAllStoresByBrand.json"
        )

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = http.get(url=api_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        js = r.json()["allStores"]

        for j in js.values():
            country_code = j.get("country")
            if country_code != "US":
                continue
            slug = "".join(j.get("storeName"))
            page_url = f"https://www.miumiu.com/us/en/store-detail.{slug}.html"
            try:
                location_name = j.get("Description")[0].get("displayStoreName")
            except:
                location_name = j.get("Description").get("displayStoreName")
            ad = "".join(j.get("addressLine")[0]).replace(
                "9700 Collins Avenue,", "9700 Collins Avenue"
            )
            phone = j.get("telephone1")
            a = parse_address(USA_Best_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = ad.split(",")[-1].strip()
            postal = a.postcode or "<MISSING>"
            country_code = "US"
            city = j.get("city")
            hours_of_operation = f'Sunday {j.get("Attribute").get("WH_DAY").get("sunday")} Saturday {j.get("Attribute").get("WH_DAY").get("saturday")} Tuesday {j.get("Attribute").get("WH_DAY").get("tuesday")} Friday {j.get("Attribute").get("WH_DAY").get("friday")} Wednesday {j.get("Attribute").get("WH_DAY").get("wednesday")} Thursday {j.get("Attribute").get("WH_DAY").get("thursday")} Monday {j.get("Attribute").get("WH_DAY").get("monday")}'
            latitude = j.get("latitude")
            longitude = j.get("longitude")

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.miumiu.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
