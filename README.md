# ebay

# Google API keys
- Firstly, create a spreadsheet. I called my spreadsheet Inventory, but you may call it whatever you want to. In this spreadsheet, name your first workbook whatever you want to. I called mine Inventory. Follow the format I used with the SKU in the 1st column, and the size in the second column. The third column must be present, however, you can put whatever field you want here. Having this column allows you to verify your inputs before the bot attempts to list them. Once satisfied with your sku + size inputs, type anything into the third column. In the fourth column, you will put a "Listed-Status". Do not touch this column. The bot uses this column to keep track of what has and has not been added. Below I have attached an image of what I did. Follow precisely for best results.
- Next go to the following url: https://console.cloud.google.com/apis/credentials. Enable access to the sheets API here if that is not already enabled. This link provides some more information on how to do that: https://developers.google.com/workspace/guides/create-project. Follow precisely.
- Once Api Access is enabled for google sheets, create a service account with Editing permissions. That can be done under this drop down. Make sure to download the service account info as JSON after the creation process is completed. Rename the file "client_secret.json" and put that in the same directory as the other files. You have now completed the google stage of setup.
<img width="686" alt="Screen Shot 2021-04-26 at 10 16 20 PM" src="https://user-images.githubusercontent.com/61530695/116174767-0bbf4600-a6dd-11eb-89f6-812f96e3230a.png">


# Ebay API keys
- Firstly, create an account at https://developer.ebay.com/ using your ebay.com username / password of your choosing.
- Once your developer account is approved (24-48 hrs), go to https://developer.ebay.com/my/keys and create a production keyset. In this keyset you will find your AppID, CertID, and DevID. 
- Next go to https://developer.ebay.com/my/auth?env=production&index=0, and retrieve an Auth'n'Auth key upon logging into your ebay account. This key serves as your AuthID.
- With these keys, fill in ebay-config.json. You are done setting the script up and are now ready to go ahead and launch it.
