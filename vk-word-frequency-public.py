import vk_api
import string
import re
import nltk
import pymorphy2
import time
import csv
import os

# from login_with_password import login, password
login, password = "your login", "your password"

OWNER_ID = -29534144
COUNT_OF_POSTS = 500

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


class VkFrequency:
    def __init__(self, login, password):
        self.vk_session = vk_api.VkApi(login, password)
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()

        self.morph = pymorphy2.MorphAnalyzer()

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

    def get_text_all_words_in_comments(self, post_ids):
        main_comments = ''
        answer_comments = ''

        k = 0
        for post_id in post_ids:
            k += 1
            print(f"{k} Geting comments from {post_id} post...")

            try:
                comments_json = self.get_comments_of_post(owner_id=self.owner_id, post_id=post_id, count=2000, thread_items_count=10)

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

    def morphy_words(self, words):
        return [self.morph.parse(word)[0].normal_form for word in words]

    def get_clean_morphy_words(self, words_together, stopwords):
        words_tokens = nltk.word_tokenize(words_together)
        filtered_words = self.remove_stop_words(words_tokens, stopwords)
        morphied_words = self.morphy_words(filtered_words)
        cleaned_words = self.remove_stop_words(morphied_words, stopwords)
        return cleaned_words

    def get_frequency_words_field(self, words, count_of_most=50):
        words_nltked = nltk.Text(words)
        fdist_words = nltk.probability.FreqDist(words_nltked)
        return fdist_words.most_common(count_of_most)

    def get_frequency_words_in_public(self, owner_id, count_of_post=10):
        self.count_of_post = count_of_post

        if count_of_post <= 100:
            posts = self.get_posts(owner_id=owner_id, count=count_of_post)
            posts_words_together = self.get_text_all_words_in_posts(posts_json=posts)
            post_ids = self.get_all_post_id(posts_json=posts)
        else:
            posts = self.get_posts(owner_id=owner_id, count=1, offset=0)
            if posts['count'] < count_of_post:
                count_of_post = posts['count']

            post_ids = []
            posts_words_together = ''
            for i in range(count_of_post // 100):
                posts = self.get_posts(owner_id=owner_id, count=100, offset=100*i)
                posts_words_together += self.get_text_all_words_in_posts(posts_json=posts)
                post_ids += self.get_all_post_id(posts_json=posts)

            posts = self.get_posts(owner_id=owner_id, count=count_of_post % 100, offset=100*i)
            posts_words_together += self.get_text_all_words_in_posts(posts_json=posts)
            post_ids += self.get_all_post_id(posts_json=posts)

        main_comments_together, answer_comments_together = self.get_text_all_words_in_comments(post_ids=post_ids)

        morphied_filtered_post_words = self.get_clean_morphy_words(words_together=posts_words_together,stopwords=russian_stopwords)
        morphied_filtered_main_comm_words = self.get_clean_morphy_words(words_together=main_comments_together, stopwords=russian_stopwords)
        morphied_filtered_answ_comm_words = self.get_clean_morphy_words(words_together=answer_comments_together, stopwords=russian_stopwords)

        self.frequency_post_words = dict(nltk.probability.FreqDist(nltk.Text(morphied_filtered_post_words)))
        self.frequency_main_comm_words = dict(nltk.probability.FreqDist(nltk.Text(morphied_filtered_main_comm_words)))
        self.frequency_answ_comm_words = dict(nltk.probability.FreqDist(nltk.Text(morphied_filtered_answ_comm_words)))

        return self.frequency_post_words, self.frequency_main_comm_words, self.frequency_answ_comm_words

    def save_results_to_csv(self):
        complete_path = os.getcwd() + "/results/"

        if not os.path.exists(complete_path):
            os.mkdir(complete_path)

        path_post_words = f"frequency_post_words_in_{self.count_of_post}_posts.csv"
        path_main_comm_words = f"frequency_main_comm_words_in_{self.count_of_post}_posts.csv"
        path_answ_comm_words = f"frequency_answ_comm_words_in_{self.count_of_post}_posts.csv"

        path_post_words = os.path.join(complete_path, path_post_words)
        path_main_comm_words = os.path.join(complete_path, path_main_comm_words)
        path_answ_comm_words = os.path.join(complete_path, path_answ_comm_words)

        print(f"All len unique post words {len(self.frequency_post_words)}")
        print(f"All len unique main comments words {len(self.frequency_main_comm_words)}")
        print(f"All len unique answer comments words {len(self.frequency_answ_comm_words)}")

        with open(path_post_words, "w") as f:
            writer = csv.writer(f)
            for key, value in self.frequency_post_words.items():
                writer.writerow([key, value])

        with open(path_main_comm_words, "w") as f:
            writer = csv.writer(f)
            for key, value in self.frequency_main_comm_words.items():
                writer.writerow([key, value])

        with open(path_answ_comm_words, "w") as f:
            writer = csv.writer(f)
            for key, value in self.frequency_answ_comm_words.items():
                writer.writerow([key, value])


if __name__ == '__main__':
    time_start = time.time()

    vk_freq = VkFrequency(login=login, password=password)

    frequency_post_words, \
    frequency_main_comm_words, \
    frequency_answ_comm_words = \
        vk_freq.get_frequency_words_in_public(owner_id=OWNER_ID, count_of_post=COUNT_OF_POSTS)

    vk_freq.save_results_to_csv()

    print(time.time() - time_start)