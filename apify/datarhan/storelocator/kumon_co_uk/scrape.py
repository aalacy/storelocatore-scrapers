from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "kumon.co.uk"
    hdr = {"Content-Type": "application/x-www-form-urlencoded"}

    all_domains = {
        "kumon.co.uk": "https://www.kumon.co.uk/find-a-tutor/",
        "kumon.ad": "https://www.kumon.ad/centre-search/",
        "kumon.co.at": "https://www.kumon.co.at/lerncenter-finden/",
        "be.kumon.eu": "https://be.kumon.eu/vind-een-leercentrum/",
        "kumon.bg": "https://www.kumon.bg/namerete-mestniya-tsentur/",
        "kumon.hr": "https://www.kumon.hr/centre-search/",
        "kumon.fr": "https://www.kumon.fr/trouver-un-centre/",
        "kumon.de": "https://www.kumon.de/lerncenter-finden/",
        "kumon.com.gr": "https://www.kumon.com.gr/vreite-ena-kedro-meletes/",
        "kumon.co.hu": "https://www.kumon.co.hu/oktatasi-kozpont-keresese/",
        "kumon.ie": "https://www.kumon.ie/find-a-tutor/",
        "kumon.it": "https://www.kumon.it/cerca-il-centro/",
        "kumon.lu": "https://www.kumon.lu/trouver-un-centre/",
        "nl.kumon.eu": "https://nl.kumon.eu/centre-search/",
        "pl.kumon.eu": "https://pl.kumon.eu/centre-search/",
        "kumon.pt": "https://www.kumon.pt/procure-o-seu-centro-kumon-mais-proximo/",
        "kumon.com.ro": "https://www.kumon.com.ro/gasire-centru-educational/",
        "kumon.es": "https://www.kumon.es/busca-tu-centro-kumon-mas-cercano/",
        "ch.kumon.org": "https://ch.kumon.org/lerncenter-finden/",
        "kumon.org/botswana": "https://www.kumon.org/botswana/find-a-centre/",
        "kumon.org/kenya": "https://www.kumon.org/kenya/find-a-centre/",
        "kumon.org/namibia": "https://www.kumon.org/namibia/find-a-centre/",
        "kumon.co.za": "https://www.kumon.co.za/find-a-centre/",
        "kumon.org/zambia": "https://www.kumon.org/zambia/find-a-centre/",
        "kumon.org/bahrain": "https://www.kumon.org/bahrain/find-a-centre/",
        "kumon.org/dubai": "https://www.kumon.org/dubai/find-a-centre/",
    }
    for domain, start_url in all_domains.items():
        code = domain.replace("kumon.", "").split("/")[-1]
        formdata = {
            "latlon": "0,0",
            "centre_search": code,
            "chosen_options[1][days_open_monday]": "0",
            "chosen_options[1][days_open_tuesday]": "0",
            "chosen_options[1][days_open_wednesday]": "0",
            "chosen_options[1][days_open_thursday]": "0",
            "chosen_options[1][days_open_friday]": "0",
            "chosen_options[1][days_open_saturday]": "0",
            "chosen_options[1][days_open_sunday]": "0",
            "chosen_options[2][1]": "0",
            "chosen_options[2][2]": "0",
            "chosen_options[3][104]": "0",
            "chosen_options[3][136]": "0",
            "chosen_options[3][138]": "0",
            "widget_search_centres": "",
        }
        response = session.post(start_url, data=formdata, headers=hdr)
        dom = etree.HTML(response.text)

        scraped_urls = []
        all_locations = dom.xpath('//a[contains(@class, "choose-centre-button")]/@href')
        next_page = dom.xpath('//a[small[i[@class="fa fa-chevron-right"]]]/@href')
        while next_page:
            if next_page[0] not in scraped_urls:
                formdata = {
                    "centre_search": code,
                    "page": next_page[0].split("=")[-1],
                    "chosen_filters": "chosen_options%5B1%5D%5Bdays_open_monday%5D=0&chosen_options%5B1%5D%5Bdays_open_tuesday%5D=0&chosen_options%5B1%5D%5Bdays_open_wednesday%5D=0&chosen_options%5B1%5D%5Bdays_open_thursday%5D=0&chosen_options%5B1%5D%5Bdays_open_friday%5D=0&chosen_options%5B1%5D%5Bdays_open_saturday%5D=0&chosen_options%5B1%5D%5Bdays_open_sunday%5D=0&chosen_options%5B2%5D%5B1%5D=0&chosen_options%5B2%5D%5B2%5D=0&chosen_options%5B3%5D%5B104%5D=0&chosen_options%5B3%5D%5B136%5D=0&chosen_options%5B3%5D%5B138%5D=0",
                    "latlon": "0,0",
                }
                response = session.post(start_url, data=formdata, headers=hdr)
                scraped_urls.append(next_page[0])
                dom = etree.HTML(response.text)
                all_locations += dom.xpath(
                    '//a[contains(@class, "choose-centre-button")]/@href'
                )
                next_page = dom.xpath(
                    '//a[small[i[@class="fa fa-chevron-right"]]]/@href'
                )
                if next_page and next_page[0] in scraped_urls:
                    next_page = None

        for store_url in list(set(all_locations)):
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)
            if "/" in domain:
                country_code = domain.split("/")[-1]
            if len(domain.split(".")[0]) == 2:
                country_code = domain.split(".")[0]
            else:
                country_code = domain.split(".")[-1]
            country_code = country_code.split("/")[-1]

            location_name = loc_dom.xpath('//h1[@class="text-center"]/text()')[0]
            street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')[
                0
            ]
            city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')[0]
            state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
            state = state[0] if state else SgRecord.MISSING
            zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
            zip_code = zip_code[0] if zip_code else SgRecord.MISSING
            phone = loc_dom.xpath('//span[@class="number"]/text()')
            phone = phone[0] if phone else SgRecord.MISSING
            latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')
            latitude = latitude[0] if latitude else SgRecord.MISSING
            longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')
            longitude = longitude[0] if longitude else SgRecord.MISSING
            hoo = loc_dom.xpath('//table[@class="centre-timings"]//text()')
            hoo = [elem.strip() for elem in hoo if elem.strip()]
            hours_of_operation = " ".join(hoo) if hoo else SgRecord.MISSING

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
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
