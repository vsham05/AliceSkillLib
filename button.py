class Button():
    def __init__(self, title, payload=None, url=None, hide=False):
        self.title = title
        self.payload = payload
        self.url = url
        self.hide = hide
    
    def get_button_object(self):
        answer = {'title': self.title, 'hide': self.hide, 'text': self.title}
        if self.url is not None:
            answer['url'] = self.url
        if self.payload is not None:
            answer['payload'] = self.payload
        
        return answer