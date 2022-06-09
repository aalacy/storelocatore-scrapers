from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import sglog

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def fetch_data(sgw: SgWriter):

    locator_domain = "https://commercebank.com/"
    api_url = "https://locations.commercebank.com/locations/modules/multilocation/?near_location=10001&threshold=4000&distance_unit=miles&limit=20000&services__in=&language_code=en-us&published=1&within_business=true"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = None
    with SgRequests() as session:
        r = SgRequests.raise_on_err(session.get(api_url)).json()
        js = r["objects"]
        for j in js:

            page_url = j.get("location_url") or "<MISSING>"
            if page_url == "<MISSING>" or not page_url:
                try:
                    page_url = j["location_url"]
                except Exception as e:
                    logzilla.error(
                        f"page_url\n{str(page_url)}\n\n\n\n{str(j)}", exc_info=e
                    )

            if page_url == "<MISSING>" or not page_url:
                logzilla.error(f"page_url\n{str(page_url)}\n\n\n\n{str(j)}")

            location_name = j.get("location_name") or "<MISSING>"
            ad = j.get("formatted_address")
            location_type = "<MISSING>"
            try:
                if page_url.find("atm") != -1:
                    location_type = "atm"
                if page_url.find("branch") != -1:
                    location_type = "branch"
                if page_url.find("commercial-office") != -1:
                    location_type = "commercial office"
            except Exception:
                logzilla.error(f"page_url\n{str(page_url)}\n\n\n\n{str(j)}", exc_info=e)
            street_address = (
                f"{j.get('street')} {j.get('street2') or ''}".replace(
                    "None", ""
                ).strip()
                or "<MISSING>"
            )
            state = j.get("state") or "<MISSING>"
            postal = j.get("postal_code") or "<MISSING>"
            country_code = "US"
            city = j.get("city") or "<MISSING>"
            store_number = j.get("id") or "<MISSING>"
            latitude = j.get("lat") or "<MISSING>"
            longitude = j.get("lon") or "<MISSING>"
            phone = j.get("phones")[0].get("number") or "<MISSING>"
            try:
                if page_url != "<MISSING>":
                    r = SgRequests.raise_on_err(session.get(page_url, headers=headers))
                    tree = html.fromstring(r.text)

                    hours_of_operation = (
                        " ".join(
                            tree.xpath(
                                '//h2[text()="Location Hours"]/following-sibling::div[1]//text()'
                            )
                        )
                        .replace("\n", "")
                        .strip()
                    )
                    hours_of_operation = (
                        " ".join(hours_of_operation.split()) or "<MISSING>"
                    )
                else:
                    raise
            except Exception:
                try:
                    hoo = j["formatted_hours"]["primary"]["grouped_days"]
                    hoz = []
                    for i in hoo:
                        hoz.append(str(i["label_abbr"] + ": " + i["content"]))
                    hours_of_operation = "; ".join(hoz)
                except Exception:
                    hours_of_operation = "<MISSING>"

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
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
