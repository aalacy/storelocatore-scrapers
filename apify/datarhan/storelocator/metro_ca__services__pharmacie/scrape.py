# -*- coding: utf-8 -*-
from lxml import etree
from time import sleep
from random import uniform

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(verify_ssl=False, proxy_country="ca")

    start_url = "https://www.metro.ca/services/pharmacie"
    domain = "metro.ca/services/pharmacie"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cookie": "METRO_ANONYMOUS_COOKIE=b975efcb-0fb7-423a-99c5-af6a42b9a488; show-store-banner=true; hprl=fr; _gcl_au=1.1.1319138759.1643572989; _ga_RSMJC35YH9=GS1.1.1643618692.3.0.1643618692.0; _ga=GA1.2.37340879.1643572989; _gid=GA1.2.252549056.1643572992; _scid=8da50d9e-5ba8-4bc1-adf7-2edf58a03e63; _pin_unauth=dWlkPU9EYzNNR015T1RndFl6QXpOQzAwTWpNd0xXRTFNMlF0Tmpjd1lUYzVPVGhpWm1JMg; AMCV_67A50FC0539F0BBD0A490D45%40AdobeOrg=1256414278%7CMCMID%7C00565062424333861975626463347878803925%7CMCAID%7CNONE%7CMCAAMLH-1644177796%7C7%7CMCAAMB-1644177796%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y; _fbp=fb.1.1643572995096.1657750437; _hjSessionUser_423760=eyJpZCI6IjQyMjU1MjE4LTZjZmItNTU4ZS05N2E5LTFlODg1NDE2NWQzNyIsImNyZWF0ZWQiOjE2NDM1NzI5OTU3NzgsImV4aXN0aW5nIjp0cnVlfQ==; _sctr=1|1643497200000; cookie-consent=true; firstPageAlreadyVisited=false; ADRUM_BTa=R:0|g:5db2c6a7-93bb-4d69-88c5-f54097437d1f|n:metrorichelieuinc-prod_c22980fa-c09c-4712-b489-98164bef9f11; SameSite=None; ADRUM_BT1=R:0|i:268193|e:94; JSESSIONID=58E719AFCCE9DBD369FD254C86D377D2; APP_D_USER_ID=hPypLkRu-1450624308; NSC_JOqrpj5ubudv2fpeodwdbrdxp2rrpei=ffffffff09023b0345525d5f4f58455e445a4a423660; __cf_bm=0egmuBOYliBB_EHx2PB4dyJFlhtK8aMC46qOF9cn.ec-1643618692-0-AdAeebp4kGusfFwED6nqy0bLMPIzzYtfYqNVwttpFeZLp00yyko/b5AktYz2+9ZCMYTiA6vtmH0ypzhd5wmAZiDKuoRJEZq6AoWwGxWboTYxi+JB5O3L+Ngx7kjQPmVabT/cQz0zrCdiz/clJOaR+MZ0olZGpvjEtPUrhhRCBXDXwYxwLxbtCTGqzQebOyfWpQ==; _dc_gtm_UA-664008-1=1; _hjIncludedInSessionSample=1; _hjSession_423760=eyJpZCI6IjU4NDQyMDAyLWE5NmUtNDRiYy05NWY2LTJkNzkzODE4NjZlNCIsImNyZWF0ZWQiOjE2NDM2MTg2OTQxNTIsImluU2FtcGxlIjp0cnVlfQ==; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=0; _gat_UA-664008-1=1",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "",
        "Sec-Fetch-User": "?1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "trailers",
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="hide-city"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath("@id")[0].capitalize()
        page_url = poi_html.xpath(".//a/@href")
        page_url = page_url[0] if page_url else ""
        raw_address = poi_html.xpath(".//p/text()")[0].split(", ")
        if len(raw_address) == 4:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        phone = ""
        latitude = ""
        longitude = ""
        zip_code = " ".join(raw_address[-1].split()[1:])
        state = raw_address[-1].split()[0]
        if len(zip_code) == 3:
            zip_code = raw_address[-1]
            state = "Ontario"
        store_number = ""
        city = raw_address[1]
        city = city.replace(zip_code, "").strip()
        if page_url:
            store_number = page_url.split("/")[-1]
            sleep(uniform(5, 30))
            loc_response = session.get(page_url, headers=hdr)
            loc_dom = etree.HTML(loc_response.text)
            phone = loc_dom.xpath('//div[@class="telephone"]/div/text()')[-1]
            geo = (
                loc_dom.xpath('//a[@id="get-directions-button"]/@href')[0]
                .split("/@")[-1]
                .split("&")[0]
                .split(",")
            )
            latitude = geo[0]
            longitude = geo[1]
        hoo = poi_html.xpath('.//div[@class="store-hours"]//text()')[1:]
        hoo = (
            " ".join([e.strip() for e in hoo if e.strip()]).split("Heures d")[0].strip()
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="CA",
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
