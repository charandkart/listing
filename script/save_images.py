import requests
import pandas as pd
import os

def image_uploader(sellerId, filename):
    name = filename.split("\\")[-1].split(".")[0]
    def download_image(url, save_path):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(save_path, 'wb') as file:
                    file.write(response.content)
                print("Image downloaded successfully!")
            else:
                print("Failed to download the image.")
        except:
            print("error")


    def upload_image(image_path, sku_name):
        url = "https://srv.dolphinskart.com/product-feed-service/image"

        
        form_data = {
            
            'sellerSku': sku_name,
            'sellerId':sellerId
        }
        files = {
            'file': open(image_path, 'rb')
        }
    
        headers = {
            'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhbXIuZG9scGhpbkBnbWFpbC5jb20iLCJzY29wZXMiOlsiUk9MRV9BRE1JTiIsIlJPTEVfVVNFUiJdLCJpc3MiOiJodHRwOi8vZG9scGhpbnNrYXJ0LWxvY2FsLmNvbSIsImF1ZCI6Imh0dHA6Ly93d3cuZG9scGhpbnNrYXJ0LmNvbS8iLCJpYXQiOjE2ODU1MzY1NDEsImV4cCI6MTY4NTYyMjk0MX0.T6V7pB-Xb-7m3UkrhiCRnuBNByOd9Sjo6a6b3b6SgY5fCvn0JNqStgaTgCMKXPrtlK8WmFSL6oKIbyY2wJ_7Dg'
        }

        response = requests.post(url,headers=headers, data=form_data,  files=files)

        # Check response status code
        if response.status_code == 201:
            print("Image upload successful.")
            return response.json()['mediaUrl']
        else:
            print("Image upload failed with status code:", response.status_code, response.text)
            return None


    def save_images(rec):
        folder_name = f"images/{sellerId}/{name}/{rec['Sub Category']}/{rec['Seller SKU']}"
        count = 1
        images = dict()
        print(folder_name)
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        for key, value in rec.items():
            if key.startswith("Image"):
                try:
                    if len(value) > 10:
                        local_path = f"{folder_name}/image_{count}.jpg"
                        download_image(value, local_path)
                        image_path = upload_image(local_path, rec['Seller SKU'])
                        images.update({f'Images {count}':image_path})
                        count+=1
                except:
                    break
        return images

    directory = f"{filename}"
    df = pd.read_csv(directory)
    result = df.to_dict('records')

    for i, rec in enumerate(result):
        print("processing item #",i+1)
        images = save_images(rec)
        result[i].update({**images})

    df1 = pd.DataFrame(result)
    if not os.path.exists("/processed"):
        os.makedirs("/processed")
    df1.to_csv(f"processed/{name}.csv", index=False)

