import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "authority": "api-v2.ilovekickboxing.com",
    "method": "POST",
    "path": "/api/v1",
    "scheme": "https",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "authorization": "bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImM2NjFkOTY4YjAyMTY0ZmQ2NmE1ZjVjZTcwZTQyNjY4NWQzNDczYmNkMjhhNDE2ZWViZTE0MTY0N2U2NDVlMGUxZmFiOWJhNmRjYTM3NjA3In0.eyJhdWQiOiIxIiwianRpIjoiYzY2MWQ5NjhiMDIxNjRmZDY2YTVmNWNlNzBlNDI2Njg1ZDM0NzNiY2QyOGE0MTZlZWJlMTQxNjQ3ZTY0NWUwZTFmYWI5YmE2ZGNhMzc2MDciLCJpYXQiOjE1NTA2MTE5ODUsIm5iZiI6MTU1MDYxMTk4NSwiZXhwIjoxNTgyMTQ3OTg1LCJzdWIiOiIxIiwic2NvcGVzIjpbXX0.PpnxXee7PdBtqXvWqXPHCA65_xH7O2JkwxrNyWoFsOvpq-nxCJkOgjLCd79jcHKQmOy4I_SWw1A65ZTW4kocOoblhoz3EF-tb-wyjPszMKVrhIrlBrenlpuoggYxRNolCtdq0sAisjkhrsIoPnv6J-eLi95VsQ5ZQdrrffcQb93ur45PY2-omgOfUrmsfytC5ab2vFgp11vAONd_s-rxgQ60helB5pTPbpatyiFxaBa6cfUYUqcyT1sEgG0eRVixqXdnmCu7gG8st91hWw0LHODYgyESh50Swc_Y35Bto2fyxzcuPJwSDcaNaQdW2cfCyUPTbVjUEjGMKB8qopTlGZwlKqCadQ8ctzlY5qQShtsiBsxuqxej8KILyGnOD2Q4WvJkz5LdDztl7SpKTEPGrucnVKvo6Vvw3fg9b7omcYnyx8J7iAW-M5UufQKE8ZIgQCYUxsHilsC8OhmMyyRul7zBlLTUkNX-2HR0NSxxfgfcuwwaZwjKdMO6LigqPSREZqo1MekhSR7vkfs3my9eG9fx3tGZ3wswRoX50Fx0h-l2UaekNnvLz0wkJoYNoqIO1l1y1uThioIxJK03g0GspYedizc3G7WadP_2-axFNSDpvqcD8mXOwmZnsUg3Bshbc1Iyq3eiTf805Bewt7Pr0iEfhOTKzJEy0ubT3A03ECM",
    "content-length": "692",
    "content-type": "application/json",
    "origin": "https://www.ilovekickboxing.com",
    "referer": "https://www.ilovekickboxing.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
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
    myobj = {
        "query": "query{locations(first:500 active:true orderBy:[{field: NAME, order: ASC}]){paginatorInfo{total} data {ID Name City lat lng Line1 ZipCode distance phone state { ID Code }url_slug phone}}}"
    }

    url = "https://api-v2.ilovekickboxing.com/api/v1"
    p = 0
    loclist = session.post(url, json=myobj, headers=headers).json()["data"][
        "locations"
    ]["data"]
    for loc in loclist:
        store = loc["ID"]
        title = loc["Name"]
        city = loc["City"]
        street = loc["Line1"]
        lat = loc["lat"]
        longt = loc["lng"]
        pcode = loc["ZipCode"]
        phone = loc["phone"]
        state = loc["state"]["Code"]
        link = "https://www.ilovekickboxing.com/" + loc["url_slug"]

        try:
            if "-" in phone:
                pass
            else:
                phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
        except:
            phone = "<MISSING>"
        ccode = "US"
        if pcode.isdigit():
            pass
        else:
            pcode = pcode.replace("-", " ")
            ccode = "CA"
        data.append(
            [
                "https://www.ilovekickboxing.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                "<MISSING>",
            ]
        )

        p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
