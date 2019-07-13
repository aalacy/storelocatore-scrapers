var url="https://stores.beallsoutlet.com/az/apachejunction/";
const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');
const fs=require('fs');
request(url,function(err,res,body){
    if(!err && res.statusCode==200){
        fs.writeFileSync('./cs.txt',body);

    }
})