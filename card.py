import requests


class Photo():
    def __init__(self, skill_id, auth_token, id=None, file=None, title='', description='', button=None):
        self.skill_id = skill_id
        self.AUTH_TOKEN = auth_token
        if id is not None:
            self.id = id

        if file is not None:
            self.file = file
        self.title = title
        self.description = description
        self.button = button
    
    def upload_image(self):
        with open(self.file, 'rb') as img:
            info = requests.post('https://dialogs.yandex.net/api/v1/skills/f3760eb7-94ec-43f1-8d19-eb5a0ce1caa7/images', 
                     files={'file': (self.file, img)}, 
                     headers={'Authorization': self.AUTH_TOKEN}).json()
            
            print(info)
            self.id = info['image']['id']
            self.size = info['image']['size']
            self.createdAt = info['image']['createdAt']
    
    def delete(self):
         requests.delete(f'https://dialogs.yandex.net/api/v1/skills/{self.skill_id}/images/{self.id}', headers={
                         'Authorization': self.AUTH_TOKEN
                             })

    def get_info(self):
        response = {'image_id': self.id, 'title': self.title, 'description': self.description}
        if self.button is not None:
            response['button'] = self.button.get_button_object()
        return response
        

class BigImage():
    def __init__(self, photo):
        self.photo = photo
        self.title = photo.title
        self.description = photo.description
        self.button = photo.button

    def get_card_object(self):
        response = {'type': 'BigImage',
                   'image_id': self.photo.id,
                   'title': self.title,
                   'description': self.description}
        if self.button is not None:
            response['button'] = self.button.get_button_object()

        return response


class ItemList():
    def __init__(self, header_text, photos, footer_button=None, footer_text=None):
        self.header_text = header_text
        self.photos = photos
        self.footer_button = footer_button
        self.footer_text = footer_text

    def get_card_object(self):
        response = {'type': 'ItemsList', 'header': {'text': self.header_text},
                   'items': [photo.get_info() for photo in self.photos]}
         
        if self.footer_text is not None:
            response['footer']['text'] = self.footer_text
        
        if self.footer_button is not None:
            response['footer']['button'] = self.footer_button.get_button_object()
        
        return response