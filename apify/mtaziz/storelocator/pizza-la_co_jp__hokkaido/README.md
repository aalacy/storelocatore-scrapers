
# Areas listed below:

- Hokkaido and Tohoku ＞ https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=1
- Kanto ＞ https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=2
- Koshinetsu / Hokuriku ＞ https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=3
- Tokai ＞ https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=4
- Kinki ＞ https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=5
- Chugoku / Shikoku＞https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=6 
- Kyushu-Okinawa＞https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=7

# How the crawler works:
The entire Japan based on volume is split into 7 areas as listed above.
Each of the area refers to a single scrape.

## Steps to be followed by the crawler to extract the data from earch page_url.
The crawler traverses the following multi-level steps. 

1. Each area (i.e., Hokkaido and Tohoku) contains list of prefectures.
2. Prefecture selection
3. the initials of the city name	
4. Please select a city
5. Please select the first letter of the next address name.
6. Please select the next address name.	
7. Please select the following address	
8. This is where store_url