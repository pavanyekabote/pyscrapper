## PyScrapper
### Introduction
PyScrapper is a web scrapping tool. It helps to scrape webpages and form a meaningful json object, as per the given configuration. Configuration is what tells the scrapper, which blocks of the html needs to be parsed and how they should be structurized for ease of use.	

---
### Installation
 To install from pip
```
pip install pyscrapper
```

---
### Documentation
####  **scrape_content(url, config, to_string=False)**
- import : from pyscrapper.scrapper import scrape_content
- Params : 
	- url : url of webpage to be scraped
	- config : An object containing the scraping information. If you want to scrape a list, you have to use the listItem selector:
		- `listItem (string | object)`: The list item selector.
		- `data (string | object)`: The fields to include in the list objects:
		 -  `<fieldName>(string | object)`: The selector or an object containing:
			 1. `selector (string)`: The selector.
			 2. `attr (string)`: If provided, the value will be taken based on the attribute name.
			 3. `eq (int)`: If provided, it will select the nth element.
    - window_size : Specify browser window size in which the url to be loaded
        - default: (1366, 784) # all url's are loaded in 1366, 784 sized browser window by default
 ---
### Usage : 

In the following example, we are scrapping an URL with the configuration
```python
from pyscrapper.scrapper import scrape_content

# Right angular bracket ">" is used,
# to select hierarchal sub elements in html
# Eg : <div class=".header"><h1>Header</h1></div>
# To Select h1 tag value, define .header > h1 
# as h1 is subelement/child of .header

# Configuration
config = {  
    "title": ".header > h1",  
    "desc": ".header > h2",  
    "avatar": {  
        "selector": ".header > img",  
        "attr": "src"  
  }  
}  
# URL of the webpage to be scrapped
URL = "https://ionicabizau.net"  

# to_string=True allows to return dict converted to json string 
print(scrape_content(URL, config, to_string=True))
```
```javascript
// Output: 
{
  "title": "Ionică Bizău",
  "desc": "Programmer,  Pianist,  Jesus follower",
  "avatar": "/@/bloggify/public/images/logo.png"
}
```
---
List Example: 
```python

from pyscrapper.scrapper import scrape_content

config ={  
  "pages": {  
    "listItem": "li .page",  
    "data": {  
      "title": "a",  
      "url": {  
        "selector": "a",  
        "attr": "href"  
  }  
    }  
  }  
}  
  
URL = "https://ionicabizau.net"  
print(scrape_content(URL, config, to_string=True))
```
```javascript
// Output
{
  "pages": [
    {
      "title": "Blog",
      "url": "/"
    },
    {
      "title": "About",
      "url": "/about"
    },
    {
      "title": "FAQ",
      "url": "/faq"
    },
    {
      "title": "Training",
      "url": "/training"
    },
    {
      "title": "Donate",
      "url": "/donate"
    },
    {
      "title": "Contact",
      "url": "/contact"
    },
    {
      "title": "CV",
      "url": "/cv"
    }
  ]
}
```

Developed with :heart: by  <b>Pavan Kumar Yekabote</b>.
