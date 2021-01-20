import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "cookie": "plid=6da32a85631f3bd7a92248aba8b45125; visid_incap_2126372=E+omZcm3SaGaQY5vONGjjo/8BmAAAAAAQUIPAAAAAAAf5cCYtYFoqPj0siQq4UHZ; BIGipServeraem.affiliate.com=!6eEMvz+ZcWNYiMYS3eIE54fMXQANJnijcO80kVMLYrrSg4oQZrzBT3jsfr+fzwekX1P9MeNyjDgqGw==; lid=a5a657b9a270ab215b0e7d4e77b2b878; TS01b3f61e=0129c692f562af91e7b2ec8d3c54125de2a48f6e28c8b5e51058e69686deb631d964c2d9f00f962f79d8ebd79a522c3775575a78f9da28ce67ce14cf30003a0d408da7e8aa; nlbi_2126372=W7GweqRJakDBaVuHS7IMNwAAAAA3m7lID7Jnt2fcJqUwxP7S; incap_ses_1221_2126372=A1WDCS00QFnmhfTLON3xEOYtCGAAAAAALfVUzPOSwAt0uT9DIfVyOw==; AMCVS_FFE376A8532209960A490D44%40AdobeOrg=1; AMCV_FFE376A8532209960A490D44%40AdobeOrg=359503849%7CMCIDTS%7C18647%7CMCMID%7C85533411210797807144298294497144925669%7CMCAAMLH-1611753586%7C3%7CMCAAMB-1611753586%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1611155986s%7CNONE%7CvVersion%7C5.0.1; s_cc=true; incap_ses_965_2126372=nmppGyLecUcyVHpall5kDfEtCGAAAAAA7RlSWPtDCJmoBeuE0kIuUg==; s_sq=%5B%5BB%5D%5D; nlbi_2126372_2147483646=ZB+5TjDUuWl0YsHTS7IMNwAAAABfTG+Ox13OKsT8SjMQGGcz; reese84=3:yZtcitOUc/IAJbcdzyl/Vg==:/0vZIU/B0WqywJn846dhAC6TGKQQo4nKuGgegA3gs/4d7KPiMuUQaxncvUJN5IG/cJJiRb0zZjHfH/zJ5sWoAld6Webwf4/HhMsvyfofwdvCppBf8je+gqJdxRzhNSuETNMYlhP8DThyxbetCsaMmLTs1rNQ1dob0VpHCzjtn3Huoa22o61dztkKWGcRPKXFGVpySHYjwrD403MR2d0wI3+3pZn8mrc4AoNlH2QdOQRVTQKShybsO/2Qa/1W1TRTv3aGzfrWJCxSALO6TZcMwoGsSsLfSJTHgZV0E0gHP+U2G1nxFWROwrUvEN30atD//CC0jO+OUMExxftXr5iXbJUcmRppqryVhjQuDhdrTcxg5k1YXvmKRztcJRTJ/029XwKU52ly2NQJrf8nmX43m92ipG+Hx2fp7wSsZV7Hjqg=:vkO1e3Vi9LgOb2KvrQk8fLAnWEPDVuEqJwvP0UFfl20=; s_ips=1070.7999877929688; BIGipServerwww.affiliate.com-dp=!Qhxy42wqzWiX3N8S3eIE54fMXQANJsC9RuCHO44fSF/kyykj8NDA4kMaml74BFBNaLctOSCej+2hYw==; TS01ee6ffb=0129c692f5ed7c6f594ec5791a2ae2cb7f9a9fa4cac8b5e51058e69686deb631d964c2d9f0bc662c14c54a72b65cb627674a3fe7a6e445d31118eef9fdc13151153af71f830907745aba698d90833a518fcd5d0490; s_tp=1577; s_ppv=branch-locator%257C%2C79%2C68%2C1238%2C2%2C3; s_nr365=1611148809475-Repeat",
}
headers = {
    "authority": "www.nsbank.com",
    "method": "POST",
    "path": "/locationservices/searchwithfilter",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-length": "403",
    "content-type": "application/json",
    "cookie": "plid=6da32a85631f3bd7a92248aba8b45125; visid_incap_2126372=E+omZcm3SaGaQY5vONGjjo/8BmAAAAAAQUIPAAAAAAAf5cCYtYFoqPj0siQq4UHZ; BIGipServeraem.affiliate.com=!6eEMvz+ZcWNYiMYS3eIE54fMXQANJnijcO80kVMLYrrSg4oQZrzBT3jsfr+fzwekX1P9MeNyjDgqGw==; lid=a5a657b9a270ab215b0e7d4e77b2b878; TS01b3f61e=0129c692f562af91e7b2ec8d3c54125de2a48f6e28c8b5e51058e69686deb631d964c2d9f00f962f79d8ebd79a522c3775575a78f9da28ce67ce14cf30003a0d408da7e8aa; nlbi_2126372=W7GweqRJakDBaVuHS7IMNwAAAAA3m7lID7Jnt2fcJqUwxP7S; incap_ses_1221_2126372=A1WDCS00QFnmhfTLON3xEOYtCGAAAAAALfVUzPOSwAt0uT9DIfVyOw==; AMCVS_FFE376A8532209960A490D44%40AdobeOrg=1; AMCV_FFE376A8532209960A490D44%40AdobeOrg=359503849%7CMCIDTS%7C18647%7CMCMID%7C85533411210797807144298294497144925669%7CMCAAMLH-1611753586%7C3%7CMCAAMB-1611753586%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1611155986s%7CNONE%7CvVersion%7C5.0.1; s_cc=true; incap_ses_965_2126372=nmppGyLecUcyVHpall5kDfEtCGAAAAAA7RlSWPtDCJmoBeuE0kIuUg==; s_sq=%5B%5BB%5D%5D; nlbi_2126372_2147483646=ZB+5TjDUuWl0YsHTS7IMNwAAAABfTG+Ox13OKsT8SjMQGGcz; reese84=3:yZtcitOUc/IAJbcdzyl/Vg==:/0vZIU/B0WqywJn846dhAC6TGKQQo4nKuGgegA3gs/4d7KPiMuUQaxncvUJN5IG/cJJiRb0zZjHfH/zJ5sWoAld6Webwf4/HhMsvyfofwdvCppBf8je+gqJdxRzhNSuETNMYlhP8DThyxbetCsaMmLTs1rNQ1dob0VpHCzjtn3Huoa22o61dztkKWGcRPKXFGVpySHYjwrD403MR2d0wI3+3pZn8mrc4AoNlH2QdOQRVTQKShybsO/2Qa/1W1TRTv3aGzfrWJCxSALO6TZcMwoGsSsLfSJTHgZV0E0gHP+U2G1nxFWROwrUvEN30atD//CC0jO+OUMExxftXr5iXbJUcmRppqryVhjQuDhdrTcxg5k1YXvmKRztcJRTJ/029XwKU52ly2NQJrf8nmX43m92ipG+Hx2fp7wSsZV7Hjqg=:vkO1e3Vi9LgOb2KvrQk8fLAnWEPDVuEqJwvP0UFfl20=; s_ips=1070.7999877929688; BIGipServerwww.affiliate.com-dp=!Qhxy42wqzWiX3N8S3eIE54fMXQANJsC9RuCHO44fSF/kyykj8NDA4kMaml74BFBNaLctOSCej+2hYw==; TS01ee6ffb=0129c692f5ed7c6f594ec5791a2ae2cb7f9a9fa4cac8b5e51058e69686deb631d964c2d9f0bc662c14c54a72b65cb627674a3fe7a6e445d31118eef9fdc13151153af71f830907745aba698d90833a518fcd5d0490; s_tp=1577; s_ppv=branch-locator%257C%2C79%2C68%2C1238%2C2%2C3; s_nr365=1611148809475-Repeat",
    "origin": "https://www.nsbank.com",
    "referer": "https://www.nsbank.com/branch-locator/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    data = []
    url = "https://www.nsbank.com/locationservices/searchwithfilter"
    p = 0
    myobj = {
        "channel": "Online",
        "schemaVersion": "1.0",
        "clientUserId": "ZIONPUBLICSITE",
        "clientApplication": "ZIONPUBLICSITE",
        "transactionId": "txId",
        "affiliate": "0018",
        "searchResults": "100",
        "username": "ZIONPUBLICSITE",
        "searchAddress": {
            "address": "CA",
            "city": "",
            "stateProvince": "",
            "postalCode": "",
            "country": "",
        },
        "distance": "3000",
        "searchFilters": [
            {"fieldId": "1", "domainId": "118", "displayOrder": 1, "groupNumber": 1}
        ],
    }
    loclist = session.post(url, headers=headers, json=myobj, verify=False).json()[
        "location"
    ]

    for loc in loclist:

        store = loc["locationId"]
        title = loc["locationName"]
        street = loc["address"]
        city = loc["city"]
        state = loc["stateProvince"]
        pcode = loc["postalCode"]
        lat = loc["lat"]
        longt = loc["long"]
        ccode = loc["country"]
        phone = loc["phoneNumber"]
        hours = loc["locationAttributes"][0]["value"]

        data.append(
            [
                "https://www.nsbank.com/",
                "https://www.nsbank.com/branch-locator/",
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
                phone,
                "Branch",
                lat,
                longt,
                hours,
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
