from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests(timeout_config=5)

    start_url = "https://www.targetoptical.com/wcs/resources/store/12001/storelocator/filtered/latitude/{}/longitude/{}?pageSize=100&offset=0"
    domain = "targetoptical.com"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json;charset=utf-8",
        "X-NewRelic-ID": "VQ4GVFNbChABXVNRBQQHV1U=",
        "Cookie": "JSESSIONID=0000oE-C3bmsWnzKetLhzgMfuKk:1cm5l3sc3; WC_PERSISTENT=Gqy4vn1ONXnO6x2odKqbIYjPDzxPRu51mw8HD7ePngM%3D%3B2021-12-23+09%3A22%3A17.262_1640251337262-63724_0; TS011b4fd0=0198a40b2459307e73b6f9947841a01588ca91caf0cb53083aaf7a1e7be9dc7adbb1334ad360ae114fa5c692f08fc1cf5c599a57eaf48bf57ca19f8fde6d9af11cba34cbe83fa3a0a608b282ccbb2e239f93d4b931; TS019c59be=0198a40b2480211409fae5d7dbc97a3b5255a23d7ccb53083aaf7a1e7be9dc7adbb1334ad368c797c6b4cfcb1f294ed6d4f8c159707f5b0340a0d7e86dce0adb5e19ced427e6c27ff18d64892bf2f648a50c25bc619b68164850e86be648989a9ee395d2eeb12e1729ff6bcc16105589e60ef7c17894f18db759710f57f13d259bda0aaf04e13591d8996a000e246390e0ec2135b3527f4a36117304fda07df4782f5b79bdb7adcd80cd1cafc445c4c82225dfd096; ak_bmsc=5646139B2AEC4737E769E25E33735662~000000000000000000000000000000~YAAQRc1aaJjSzrd9AQAAzkaZ5g4NSHKnazWBeyQgQS+IrkxkxM1WsFY5T8LavLL3g816HKW21M/4QipdzWLEA1v2kd+D1bmIcwb0Qa+KmImPIq+tHEuOpdljvS5LWyT2b5RUtZOItnU/L/ESZkpvfSUzcAtgRh/vSs0FLJoZ9FmSyKSAXqhvN/nwUIyVvKd1enGgUnmx/Om1Wv25VhDDrwgTU1jTOG4f7qDhZ7WBdv/EXwZv4WKb627GpfQ3eis2JE7/TymZAu+6yox5znxuUSZNGEf2SALlWyT8i5iDlAQhj3R15HKQ8h6HYfb89eUdeX9YNRivB4H1aLT8Q/Vg5l44B6TdNrDl7M2lcYUvoulLIw2b+w2487zQ9HvMryVcTj3165ojAiehVN+joFrumctLy20WV30cFZkVSIocyFG7t60zTEpeQVVCJaiU6SVcAeT+cudrLgU7shpPlNJVic4XM0q4+n1cVS4E/L17fSF1OPZszPW76TeW6T5fwggIad6He+3ya3lpkZrY/64yeUw=; mt.v=2.588085503.1640251342349; tracker_device=08151e91-4f5c-42e4-83cc-49644e5befb5; utag_main=v_id:017de699478700621df5a77c925c00052001e00f00838$_sn:1$_se:8$_ss:0$_st:1640253163544$ses_id:1640251344778%3Bexp-session$_pn:2%3Bexp-session$vapi_domain:targetoptical.com$dc_visit:1$dc_event:3%3Bexp-session$dc_region:eu-central-1%3Bexp-session; tealium_data_session_timeStamp=1640251344796; TrafficSource_Override=1; AMCV_125138B3527845350A490D4C%40AdobeOrg=-1303530583%7CMCIDTS%7C18985%7CMCMID%7C57743169419379616601044636620912464513%7CMCAAMLH-1640856145%7C6%7CMCAAMB-1640856145%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1640258545s%7CNONE%7CMCAID%7CNONE%7CMCSYNCSOP%7C411-18992%7CvVersion%7C3.3.0; _cs_mk=0.8202673793609019_1640251345005; AMCVS_125138B3527845350A490D4C%40AdobeOrg=1; s_cc=true; hic_popup=true; CONSENTMGR=consent:true%7Cts:1640251358417; s_sq=%5B%5BB%5D%5D; bm_sv=CB54813712088CFDCC646297B844064E~CB0pIiRRuJYko1KKWgawHBnBVFg/+MSsU8V/hKk6c2mzlwG2ZC+X/+J5+kZNNrdwetyaPFhNQEjj4quljlBJGaNAO1X+UOP2Y7boR/e+NTPYOi3/UprsYT79bbGFn7WzKe8KxvpyhqQhO2roz/asfwVevVZ32CTmXuyz5/rvdmQ=; MGX_UC=JTdCJTIyTUdYX1AlMjIlM0ElN0IlMjJ2JTIyJTNBJTIyMjRlMmJmMDctNGYwZS00YWFjLTlhMzgtMzA3YjJlYmNjMmViJTIyJTJDJTIyZSUyMiUzQTE2NDA3NzY5NjkwOTglN0QlMkMlMjJNR1hfUFglMjIlM0ElN0IlMjJ2JTIyJTNBJTIyODUxY2FlZTgtZjA5Mi00MDU2LTlmMzktZGNiZWRmNDM4NTdlJTIyJTJDJTIycyUyMiUzQXRydWUlMkMlMjJlJTIyJTNBMTY0MDI1MzE3MTc1NiU3RCUyQyUyMk1HWF9DSUQlMjIlM0ElN0IlMjJ2JTIyJTNBJTIyY2Q0M2NiYWEtOWZkMi00OGY4LWFhNDgtOTViMWZiMTA3OWU4JTIyJTJDJTIyZSUyMiUzQTE2NDA3NzY5NjU4NzclN0QlMkMlMjJNR1hfVlMlMjIlM0ElN0IlMjJ2JTIyJTNBMSUyQyUyMnMlMjIlM0F0cnVlJTJDJTIyZSUyMiUzQTE2NDAyNTMxNzE3NTYlN0QlMkMlMjJNR1hfRUlEJTIyJTNBJTdCJTIydiUyMiUzQSUyMm5zX3NlZ18wMDAlMjIlMkMlMjJzJTIyJTNBdHJ1ZSUyQyUyMmUlMjIlM0ExNjQwMjUzMTcxNzU2JTdEJTdE; _cs_c=1; _cs_id=be286596-1ed3-a18a-aaa4-30a085fc7f47.1640251365.1.1640251365.1640251365.1.1674415365989; _cs_s=1.0.0.1640253165989; BVImplmain_site=13762; _uetsid=e3d8301063d111ecba1fe5fb7584b4b5; _uetvid=47afdae0250811ec86ed75ea738f8db6; _gcl_au=1.1.1975184588.1640251366; _ga_QHYKKF40Z7=GS1.1.1640251366.1.0.1640251366.0; _ga=GA1.2.694930811.1640251369; BVBRANDID=99cfef07-b5d8-404a-891d-8b4c89cbeb77; BVBRANDSID=407df1b8-4484-46d7-9fc3-f588b9327101; _gid=GA1.2.1886179642.1640251371; _gat_UA-163505969-1=1; _clck=1sjdw37|1|exi|0; _fbp=fb.1.1640251372697.2130028377; cto_bundle=2Bu_7V9zYnpVc0xndE84SnFFcFZPeGZYdjZwZG0lMkJybVU2cUElMkZsQ05wNVlkZ2pldXNmSWNrcHlLJTJGZWdjM3FrUk1OaUVuZzduRXF0c1d6aVVkQUswanlFbGJzYXROZ0IzSnlMQXR3UVpEN0p6OW9uWGxVNjlsbzRocFdtdldmWnMyWjlaclhQQ0ZyVW1TR3BJMndPTHA2VnFPcUUlMkIxMEhMVDJtNUFXendOSXFZUnRXZ01KOXBrS2FMRkxYa1U4OFk0OWxHa1RDTzNNNDE4U0MyYlFwNEREUUNYanclM0QlM0Q; _hjid=2e9456ad-ee54-4da0-a54f-a10f94ff04de; _hjSessionUser_515366=eyJpZCI6IjQ1MTZlMzM1LWNkNjUtNWJiNi1iYjVhLWIwYTBmY2RiMDA0YyIsImNyZWF0ZWQiOjE2NDAyNTEzNzUyMjYsImV4aXN0aW5nIjp0cnVlfQ==; _hjSession_515366=eyJpZCI6ImZjNmI1OTM1LWVjMjAtNDAyNC04ZDZiLTc1ZDk5MGQ4ZDMzZCIsImNyZWF0ZWQiOjE2NDAyNTEzNzU0MDZ9; _hjIncludedInSessionSample=1; _hjAbsoluteSessionInProgress=0; _clsk=1cb393z|1640251375636|1|1|b.clarity.ms/collect",
    }
    session.get("https://www.targetoptical.com/to-us/eye-exams")
    frm = {
        "selectedInsuranceFilters": [],
        "selectedLanguageFilters": [],
        "selectedOpeningFilters": [],
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    for lat, lng in all_coords:
        data = session.post(start_url.format(lat, lng), json=frm, headers=hdr)
        if data.status_code != 200:
            continue
        data = data.json()
        if not data.get("PhysicalStore"):
            continue
        all_locations = data["PhysicalStore"]
        for poi in all_locations:
            location_name = poi["Description"][0]["displayStoreName"]
            hours = [e for e in poi["Attribute"] if e["name"] == "StoreHours"][0][
                "displayValue"
            ].split("; ")
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            hoo = list(map(lambda d, h: d + " " + h, days, hours))
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.targetoptical.com/to-us/locations",
                location_name=location_name,
                street_address=" ".join(poi["addressLine"]),
                city=poi["city"],
                state=poi["stateOrProvinceName"],
                zip_postal=poi["postalCode"],
                country_code=poi["country"],
                store_number=poi["storeName"],
                phone=poi["telephone1"],
                location_type="",
                latitude=poi["latitude"],
                longitude=poi["longitude"],
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
