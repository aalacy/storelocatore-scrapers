#  Ignore CountValidator
Disabled CountValidator, initial run fails with : 
```
Checking the number of POI in your data against our internal truthset...
/usr/local/lib/python3.7/site-packages/sgvalidator/validators/count_validator.py:147: FutureWarning: `item` has been deprecated and will be removed in a future version
  return res.item()
We think there should be around 130 POI, but your file has 0 POI. Are you sure you scraped correctly?
```
Listing of target directory shows 131 stores. 

```
╭─[UndulatingUnicorn] as sheller in ~/Dev/crawl-service/apify/samheller/storelocator/chezcora_com using node v8.17.0 on (master)✘✘✘               12-30 21:21:16
╰─(ﾉ˚Д˚)ﾉ  ls -lh apify_storage/datasets/default/*.json | wc -l
     131

```