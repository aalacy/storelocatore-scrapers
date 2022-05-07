from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "triumphmotorcycles.com"

    start_url = "https://www.triumphmotorcycles.com/api/v2/places/alldealers?LanguageCode={}&SiteLanguageCode=en-US&Skip=0&Take=500&CurrentUrl=www.triumphmotorcycles.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_countries = session.get(
        "https://www.triumphmotorcycles.com/api/v2/places/countries", headers=hdr
    ).json()
    for c in all_countries:
        data = session.get(start_url.format(c["LanguageCode"]), headers=hdr).json()
        all_locations = data["DealerCardData"]["DealerCards"]
        for poi in all_locations:
            page_url = poi["DealerUrl"]
            if "http" not in page_url:
                page_url = "https:" + page_url
            if "usa/" in page_url:
                page_url = "https://www.triumphmotorcycles.com" + poi["DealerUrl"]
            if page_url == "https:":
                page_url = ""
            location_name = poi["Title"]
            raw_address = f"{poi['AddressLine1']} {poi['AddressLine2']} {poi['AddressLine3']} {poi['AddressLine4']}"
            addr = parse_address_intl(raw_address.replace("<br/>", " "))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if street_address:
                street_address = street_address.replace("None", "")
            city = addr.city
            state = addr.state
            zip_code = addr.postcode
            if zip_code == "00000":
                zip_code = ""
            if not zip_code:
                zip_code = poi["PostCode"]
            phone = poi["Phone"]
            if phone and phone.strip() == ".":
                phone = ""
            if phone:
                phone = phone.split(" (+")[0]
            latitude = poi["Latitude"]
            if latitude == "0" or latitude == "0.000000":
                latitude = ""
            longitude = poi["Longitude"]
            if longitude == "0" or longitude == "0.000000":
                longitude = ""
            hoo = []
            if poi["OpeningTimes"]:
                hoo = etree.HTML(poi["OpeningTimes"]).xpath("//text()")
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = (
                " ".join(" ".join(hoo).split())
                .split("Showroom:")[-1]
                .split("Service")[0]
                .split("In den")[0]
                .split("GmbH")[-1]
                .split("Schlaak")[-1]
                .split("gszeiten:")[-1]
                .split("Winter")[0]
                .split("(Schautag")[0]
                .split("Borchardt")[-1]
                .split("Zweiradtechnik")[-1]
                .split("Uhr von")[0]
                .split("Uhr 24")[0]
                if hoo
                else ""
            )
            if not hours_of_operation:
                loc_response = session.get(page_url, headers=hdr)
                if loc_response.status_code == 200:
                    loc_dom = etree.HTML(loc_response.text)
                    hoo = loc_dom.xpath(
                        '//ul[@class="dealer-location__opening-times"]//text()'
                    )
                    hours_of_operation = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=c["CountryName"],
                store_number="",
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
