import vk_api
from login_with_password import *

OWNER_ID = -29534144
COUNT_OF_POSTS = 400

def remove_chars_from_text(text, chars):
    return "".join([ch for ch in text if ch not in chars])

class VkClient:
    def __init__(self, login, password):
        self.vk_session = vk_api.VkApi(login, password)
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()

    def get_json_posts(self, owner_id=-29534144, count = 10, offset=0):
        posts_json = self.vk.wall.get(owner_id=owner_id, offset=offset, count=count)
        return posts_json

    def get_json_comments_of_post(self, owner_id=-29534144, post_id=15428313, count = 2000, thread_items_count=10):
        comments_json = self.vk.wall.getComments(owner_id=owner_id, post_id=post_id, count=count, thread_items_count=thread_items_count)
        return comments_json


if __name__ == '__main__':
    parser = VkClient(login=login, password=password)
    posts_json = parser.get_json_posts(owner_id=OWNER_ID, count=COUNT_OF_POSTS)
    print(posts_json)