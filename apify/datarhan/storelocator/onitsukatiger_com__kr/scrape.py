from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.onitsukatiger.com/{}/amlocator/index/ajax/?p={}"
    domain = "onitsukatiger.com/kr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
    }
    country_codes = ["kr/ko-kr", "sg/en-sg", "my/en-my", "th/en-th"]
    for code in country_codes:
        frm = {
            "lat": "0",
            "lng": "0",
            "radius": "0",
            "product": "0",
            "category": "0",
            "sortByDistance": "false",
        }
        for page in range(1, 10):
            data = session.post(
                start_url.format(code, page), headers=hdr, data=frm
            ).json()
            for poi in data["items"]:
                page_url = f"https://www.onitsukatiger.com/{code}/store-finder/{poi['url_key']}/"
                hoo = ""
                if poi["attributes"].get("weekday_openings_day"):
                    hoo_week_days = poi["attributes"]["weekday_openings_day"][
                        "frontend_label"
                    ]
                    hoo_week_time = poi["attributes"]["weekday_openings_times"][
                        "option_title"
                    ]
                    hoo = f"{hoo_week_days} - {hoo_week_time}"
                    if poi["attributes"].get("weekend_openings_times"):
                        hoo_weekend = poi["attributes"]["weekend_openings_times"][
                            "frontend_label"
                        ]
                        hoo_weekend_time = poi["attributes"]["weekend_openings_times"][
                            "option_title"
                        ]
                        hoo += f", {hoo_weekend} - {hoo_weekend_time}"
                state = poi["state"]
                if state and state.isdigit():
                    state = ""

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=poi["name"],
                    street_address=poi["address"],
                    city=poi["city"],
                    state=state,
                    zip_postal=poi["zip"],
                    country_code=poi["country"],
                    store_number=poi["id"],
                    phone=poi["phone"],
                    location_type="",
                    latitude=poi["lat"],
                    longitude=poi["lng"],
                    hours_of_operation=hoo,
                )

                yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
