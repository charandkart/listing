import re

def clean_price_tag(text):
    return ''.join(e for e in text if e.isnumeric() or e == ".")

def text_clean_up(text):
    text = text.strip().strip("\n").strip("\t")
    return re.sub(r'[^\x00-\x7F]+',' ', text)


def amazon_data_scrap(soup):
    errors = ""

    product = soup.find("div", attrs={"id": "dp"})
    
    try:
        product_title = product.find("span", attrs={"id":"productTitle"}).text
        product_title = text_clean_up(product_title)
    except:
        product_title = None
        errors+="Product Title, "
        
    try:
        price = product.find("div", attrs= {"id": "corePriceDisplay_desktop_feature_div"})

        try:    
            sp = price.find("span", attrs={"class": "priceToPay"}).find("span", attrs={"class":"a-offscreen"}).text
            sp = clean_price_tag(sp)
        except:
            sp = 0

        try:
            mrp = price.find("span", attrs={"class": "basisPrice"}).find("span", attrs={"class":"a-offscreen"}).text
            mrp = clean_price_tag(mrp)
        except:
            mrp = sp
    except:
        mrp = 0
        sp = 0
        errors+="Product Title, "
    
    try:
        bullet_points = product.find("div", attrs={"id":"feature-bullets"})
        points = bullet_points.find_all("li")
        bullet_points = dict()
        for i, point in enumerate(points, 1):
            bullet_points.update({f'Bullet Point {i}': text_clean_up(point.text)})
    except:
        bullet_points = {}
        errors+="Bullet Points, "
      
    try:
        product_details = product.find("div", attrs = {"id": "productOverview_feature_div"})
        product_details = product_details.find("table")
        product_details = product_details.find("tbody")
        details = product_details.find_all("tr")
        product_details = dict()
        for detail in details:
            row = detail.find_all("td")
            product_details.update({text_clean_up(row[0].text): text_clean_up(row[1].text)})
    except:
        product_details = {}
        errors+="Product Details, "
    
    prod_details = product.find("div", attrs={"id":"prodDetails"})

    try:        
        technical_details = prod_details.find("table", attrs={"id":"productDetails_techSpec_section_1"})
        technical_details = technical_details.find("tbody")
        details = technical_details.find_all("tr")
        technical_details = dict()
        for detail in details:
            row = detail.find_all()
            technical_details.update({text_clean_up(row[0].text): text_clean_up(row[1].text)})
    except:
        technical_details = {}
        errors+="Technical Details"

    try:
        additional_details = prod_details.find("table", attrs={"id":"productDetails_detailBullets_sections1"})
        additional_details = additional_details.find("tbody")
        details = additional_details.find_all("tr")
        additional_details = dict()
        for detail in details:
            row = detail.find_all()
            additional_details.update({text_clean_up(row[0].text): text_clean_up(row[1].text)})
    except:
        additional_details = {}
        errors+="Additional Details"
    try:    
        images = product.find("div", attrs={"id":"altImages"})
        images_ = images.find_all("li", attrs = {"class": "imageThumbnail"})
        images = dict()
        for i, image in enumerate(images_, 1):
            images.update({f"Image {i}": image.find("img")['src'].replace("SS40", "SX679")})
    except:
        images = None
        errors+="Images, "
        
    return {
        "Errors": errors.strip(", "),
        "Product_Title": product_title,
        "Bullet_Points": bullet_points,
        "Specifications": {
            **product_details,
            **technical_details,
            **additional_details
        },
        "Images": images,
        "Price": {
            "MRP": mrp,
            "Selling Price": sp
        }
    }

def flipkart_scrap_data(soup):
    errors = ""

    try:
        details = soup.find("div", {"class":"_1YokD2 _2GoDe3"})
    except:
        errors+="details error"

    try:
        breadcrumbs = ""
        group = details.find("div", {"class": "_1MR4o5"})
        for cat in group.find_all("div", {"class": "_3GIHBu"}):
            breadcrumbs+=f'{cat.text} > '
        breadcrumbs = text_clean_up(breadcrumbs)
    except:
        breadcrumbs = None
        errors+='Breadcrumbs, '

    try:
        price = details.find("div", {"class": "_25b18c"})
        selling_price = clean_price_tag(price.find("div", {"class": "_16Jk6d"}).text)
        mrp = clean_price_tag(price.find("div", {"class": "_2p6lqe"}).text)
    except:
        mrp = None
        selling_price = None
        errors+='price, '

    try:
        title = text_clean_up(details.find("span", {"class": "B_NuCI"}).text)
    except:
        title = None
        errors+='title, '

    options_group = dict()

    try:
        options = details.find("div", {"class":"_3wmLAA"})
        variants = options.find_all("div", {"class":"ffYZ17"})
    except:
        variants = []
        errors+='varaints, '

    for variant in variants:
        key = text_clean_up(variant.find("span").text)
        value = list()
        for i in variant.find_all("li", {"class": "_3V2wfe"}):
            link = i.find("a")
            value.append(link.text or i.text)
        options_group.update({key: value})

    try: 
        descriptions = details.find("div", {"class":"RmoJUa"}).text
    except:
        descriptions = None
        errors+='desrciption, '

    try:
        all_x = details.find("div", {"class":"_3dtsli"})

        all_specs_ = all_x.find_all("table", {"class":"_14cfVK"})
        
        specifications = dict()
        for all_specs in all_specs_:
            specs = all_specs.find_all("tr", {"class": "row"})

            for s in specs:
                x = s.find_all("td", {"class":"col"})                
                try:
                    key = text_clean_up(x[0].text)
                    value = text_clean_up(x[1].text)
                    specifications.update({key: value})
                except:
                    continue
    except :
        specifications = {}
        errors+='specification, '

    try:
        all_specs = details.find("div", {"class":"X3BRps"})
        specs = all_specs.find_all("div", {"class": "row"})
        product_details = {}
        for s in specs:
            x = s.find_all("div", {"class":"col"})
            try:
                key = text_clean_up(x[0].text)
                value = text_clean_up(x[1].text)
                product_details.update({key: value})
            except:
                continue
    except:

        product_details = {}
        errors+='product details, '

    try:
        images_section = soup.find("div", {"class": "_2FHWw4"})
        thumbnails = images_section.find_all("img")
        images = dict()
        for i, img in enumerate(thumbnails, 1):
            if img.has_attr("src"):
                path = img['src']
                images.update({f"Image {i}": path.replace("/128/128", "/416/416")})
    except:
        images = []
        errors+="images, "

    return {
        "Errors": errors.strip(", "),
        "Breadcrumbs": breadcrumbs or None,
        'Product_Title':title or None,
        'Description': descriptions or None,
        "Options_Group": options_group or None,
        "Specifications": {
            **specifications, 
            **product_details
        },
        'Images': images or None,
        'Price': {
            'MRP': mrp or None,
            'Selling Price': selling_price or None
        }
    }

def ecom_scrap_data(soup):
    product = soup.find("main", attrs={"id":"maincontent"})
    
    product_title = product.find("h1", attrs={"class":"page-title"})
    product_title = text_clean_up(product_title.text)

    description = product.find("div", attrs={"class":"product attribute overview"})
    description = text_clean_up(description.text)

    price_info = product.find("div", attrs={"class":"product-info-price"})
    mrp = clean_price_tag(price_info.text)

    return {
        'product_title': product_title,
        'description': description,
        'price_info': {
            'mrp': mrp
        }
    }

def jiostore_scrap_data(soup):
    errors = ""
    body = soup.find("body")
    
    title = text_clean_up(body.find("span", attrs={"class":"product-name"}).text)
    
    highlits = body.find("div", attrs={"class":"highlights"})
    points_ = [text_clean_up(item.text) for item in highlits.find_all("div", attrs={"class":"highlight_item"})]
    points = dict()
    for i, point in enumerate(points_, 1):
        points.update({f'Bullet Points {i}': point})
        
    images_sec = body.find("div", attrs={"class":"image-carousal"})
    images_ = [img['src']for img in images_sec.find_all("img")]
    images = dict()
    for i, image in enumerate(images_, 1):
        images.update({f'Image {i}': image})
    
    specs_sec = body.find("div", attrs={"class":"attribute-group-cont"})
    specs = dict()
    for sec in specs_sec.find_all("div", attrs={'class':'group-attr'}):
        spec = sec.find_all("div")
        specs.update({text_clean_up(spec[0].text): text_clean_up(spec[1].text)})
        
    price = body.find("div", attrs={"class":"price"})
    try:
        
        mrp = price.find("div", attrs={"class":"price-effective"}).text
        mrp = clean_price_tag(mrp)
    except:
        mrp = None
        errors+="MRP,"
        
    try:
        sp = price.find("div", attrs={"class":"price-marked"}).text
        sp = clean_price_tag(sp)
    except:
        sp = None
        errors+="Selling Price,"
    
    return {
        "Product_Title":title,
        "Description": None,
        "Bullet_Points":points,
        "Images":images,
        "Specifications": specs,
        "Price": {
            "MRP": mrp,
            "Selling Price": sp
        }
    }