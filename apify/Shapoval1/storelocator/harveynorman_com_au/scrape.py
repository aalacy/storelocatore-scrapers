from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://harveynorman.com.au/"
    api_urls = [
        "https://harvey-norman-nz.locally.com/stores/conversion_data?has_data=true&company_id=143427&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=-35.719922768896936&map_center_lng=174.33000000000078&map_distance_diag=3000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=0112&zoom_level=11&lang=en-en&forced_coords=1",
        "https://harvey-norman-au.locally.com/stores/conversion_data?has_data=true&company_id=143426&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=-35.26877099797615&map_center_lng=149.13000000000275&map_distance_diag=3000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&zoom_level=9&lang=en-en&forced_coords=1",
    ]
    for api_url in api_urls:
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        js = r.json()["markers"]
        for j in js:
            slug = j.get("slug")
            page_url = f"https://stores.harveynorman.com.au/shop/{slug}"
            location_name = j.get("name") or "<MISSING>"
            location_type = j.get("disclaimer") or "<MISSING>"
            street_address = j.get("address") or "<MISSING>"
            state = j.get("state") or "<MISSING>"
            postal = j.get("zip") or "<MISSING>"
            country_code = j.get("country") or "<MISSING>"
            if country_code == "NZ":
                locator_domain = "https://www.harveynorman.co.nz/"
            city = j.get("city") or "<MISSING>"
            store_number = j.get("id") or "<MISSING>"
            latitude = j.get("lat") or "<MISSING>"
            longitude = j.get("lng") or "<MISSING>"
            phone = j.get("phone") or "<MISSING>"
            hours_of_operation = "<MISSING>"
            hours = j.get("display_dow")
            tmp = []
            if hours:
                for h in hours.values():
                    day = h.get("label")
                    times = h.get("bil_hrs")
                    line = f"{day} {times}"
                    tmp.append(line)
                hours_of_operation = "; ".join(tmp)

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
