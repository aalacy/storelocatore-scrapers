
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

1. Each area (i.e., Hokkaido and Tohoku) contains list of prefectures. => https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=1
2. Prefecture selection => https://www.pizza-la.co.jp/TenpoTop.aspx?M=CK&C=01
3. the initials of the city name => https://www.pizza-la.co.jp/TenpoTop.aspx?M=CS&C=01&K=%82%A0
4. Please select a city => https://www.pizza-la.co.jp/TenpoTop.aspx?M=TK&C=01204
5. Please select the first letter of the next address name => https://www.pizza-la.co.jp/TenpoTop.aspx?M=TS&C=01204&K=%82%A0
6. Please select the next address name.	=> https://www.pizza-la.co.jp/TenpoTop.aspx?M=AS&C=01204020
7. 
7. Please select the following address => https://www.pizza-la.co.jp/Tenpo.aspx?M=TS&C=01204020001&B=M%3dAS%26C%3d01204020
   - Note: At 7th step, source page might have `store URL` or list of sub-sub-area ( `1-chome`) containing multiple store URLs. 

8. This is where store_url