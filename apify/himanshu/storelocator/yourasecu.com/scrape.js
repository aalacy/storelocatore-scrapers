const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'https://yourasecu.com/locations';
async function scrape(){

  return new Promise(async (resolve,reject)=>{
 
request(url,(err,res,html)=>{

  if(!err && res.statusCode==200){
 
        const $  =cheerio.load(html);
        var items=[];
   
        

       
        function mainhead(i)

        {
          if(9>i)

            {

          var location_name =$('.container').find('.branchTitle').find('h1').eq(i).text(); 
          var address_tmp = $('.container').find('.row ').find('.six:first-child').eq(i).html().trim();
          var address_tmp1 = address_tmp.split('<br>');
          var address = address_tmp1[1].replace(/\r?\n/g, "");
         
          var state_tmp = address_tmp1[2];
          var state_tmp1 = state_tmp.split(' ');
          var city  = state_tmp1[0].replace(',','').replace(/\r?\n/g, "");
          var state = state_tmp1[1];
          var zip = state_tmp1[2];
          var phone = address_tmp1[3].replace(/<[^>]*>?/gm, '').replace('Phone:','').replace(/\r?\n/g, "").trim();
          var latitude_tmp = $('.container').find('.row ').find('.six:first-child').eq(i).find('a:nth-child(2)').attr('href');
          var latitude_tmp1 = latitude_tmp.split(',');
          var latitude_tmp2 = latitude_tmp1[2].split('/@');
          var latitude = latitude_tmp2[1];
          var longitude = latitude_tmp1[3];
           
          var hour_tmp = $('.container').find('.row ').find('.six:nth-child(2)').eq(i).html().trim();
          var hour_tmp1 = hour_tmp.split('</p>');
          var hour1 = hour_tmp1[0].replace(/<[^>]*>?/gm, '').replace('Lobby Hours','').replace('Hours','').replace(/\r?\n/g, "");
          
          items.push({  

            locator_domain: 'https://yourasecu.com/', 

            location_name: location_name, 

            street_address: address,

            city: city, 

            state: state,

            zip:  zip,

            country_code: 'US',

            store_number: '<MISSING>',

            phone: phone,

            location_type: 'yourasecu',

            latitude: latitude,

            longitude: longitude, 

            hours_of_operation: hour1}); 
            
            
        


        
        mainhead(i+1);
       
   
      } 
  
      else{
     
        resolve(items);
    
       }
    } 
    
    mainhead(0);

 
 }
});
});

}
 

Apify.main(async () => {

    

    const data = await scrape();
     
 
    await Apify.pushData(data);
  
  });
