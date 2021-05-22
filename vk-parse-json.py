import vk_api
import string
import re
import nltk

from login_with_password import *

OWNER_ID = -29534144
COUNT_OF_POSTS = 400

nltk.download('stopwords')
nltk.download('punkt')

russian_stopwords = nltk.corpus.stopwords.words("russian")
russian_stopwords.extend(['—', '–', 'это'])

spec_chars = string.punctuation + '"' + '«' + "»" + "✹" + "•"
print(f"Excess chars {spec_chars}")

def remove_chars_from_text(text, chars):
    return "".join([ch for ch in text if ch not in chars])

def delete_emojify(data):
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)

class VkClient:
    def __init__(self, login, password):
        self.vk_session = vk_api.VkApi(login, password)
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()

    def get_posts(self, owner_id=-29534144, count=10, offset=0):
        self.owner_id = owner_id
        posts = self.vk.wall.get(owner_id=owner_id, offset=offset, count=count)
        return posts

    def get_comments_of_post(self, owner_id=-29534144, post_id=15428313, count=2000, thread_items_count=10):
        comments = self.vk.wall.getComments(owner_id=owner_id, post_id=post_id, count=count, thread_items_count=thread_items_count)
        return comments

    def get_all_post_id(self, posts_json):
        post_ids = []
        for post in posts_json['items']:
            if 'attachments' in post.keys():
                type_of_post = post['attachments'][0]['type']
                if 'post_id' in post['attachments'][0][type_of_post].keys():
                    post_ids.append(post['attachments'][0][type_of_post]['post_id'])

        return post_ids

    def get_text_all_words_in_posts(self, posts_json):
        text_posts_words = ''
        for post in posts_json['items']:
            text = post['text'].lower()
            text = text.replace("\n", " ")
            text_posts_words += " " + remove_chars_from_text(text, spec_chars)

        return text_posts_words

    def get_text_all_words_in_comments(self, posts_json, post_ids):
        main_comments = ''
        answer_comments = ''

        for post_id in post_ids:
            try:
                comments_json = self.get_comments_of_post(owner_id=self.owner_id, post_id=post_id, count=2000, thread_items_count=10)
                print(f"Geting comments from {post_id} post...")

                for comment_post in comments_json['items']:
                    main_comment = comment_post['text'].lower()
                    main_comment = delete_emojify(main_comment)
                    main_comment = main_comment.replace("\n", " ")
                    main_comments += " " + remove_chars_from_text(main_comment, spec_chars)

                    for answ_comment in comment_post['thread']['items']:
                        answ_comment = answ_comment['text'].lower()
                        answ_comment = delete_emojify(answ_comment)
                        answ_comment = answ_comment.replace("\n", " ")
                        answer_comments += " " + remove_chars_from_text(answ_comment, spec_chars)
            except Exception as e:
                    pass

        return main_comments, answer_comments

    def remove_stop_words(self, tokens, stopwords):
        return [word for word in tokens if word not in stopwords
                and "http" not in word
                and "club" not in word
                and "org" not in word
                and "id" not in word]


if __name__ == '__main__':
    vk_client = VkClient(login=login, password=password)
    posts = vk_client.get_posts(owner_id=OWNER_ID, count=COUNT_OF_POSTS)
    posts_words_together = vk_client.get_text_all_words_in_posts(posts_json=posts)

    post_ids = vk_client.get_all_post_id(posts_json=posts)
    main_comments_together, answer_comments_together = vk_client.get_text_all_words_in_comments(posts_json=posts,
                                                                                     post_ids=post_ids)

    text_tokens = nltk.word_tokenize(posts_words_together)
    main_comments_tokens = nltk.word_tokenize(main_comments_together)
    answer_comments_tokens = nltk.word_tokenize(answer_comments_together)

    filtered_text_words = vk_client.remove_stop_words(text_tokens, russian_stopwords)
    filtered_main_words = vk_client.remove_stop_words(main_comments_tokens, russian_stopwords)
    filtered_answ_words = vk_client.remove_stop_words(answer_comments_tokens, russian_stopwords)

    print(filtered_text_words)