# About LeetEnglish
Hi, Welcome to leetEnglish, LeetEnglish is an app that allows users to increase their vocabulary level by reading. In this app, you will be able to read articles shared by another user as public articles, you will be able to read through the entire content and get definitions as well as add an image to help your memorization of the vocabulary. Besides that, you will be able to import your own article into the app, and you also able to implement the whole feature as public articles, get definitions, memorization vocabulary with images, and getting practice with the vocabulary.

Most importantly, In leetEnglish you will be able to connect with another user, adding your own tweets, share your moment with another user!, let diving in!

---

# APIs Usecase

leetEngish use two APIs, WordsAPI and GoogleSeach API(serpapi)

[WordsAPI](https://www.wordsapi.com/): get the definition for the unknown vocabulary

[GoogleSearch API](https://serpapi.com/): retrieve unknown vocabulary memorize images

if you would like to see more detail of my code, making sure to retrieve the API key for both APIs to prevent any unnecessary errors. on the root directly of the file create a file name "api_keys.py", under this file type of the following variable:

```python
wordsapi = "your_api_key"
serpapi = "your_api_key" 

```

---
# How to run the app locally
download the file from this repository, on your computer type the following command on your terminal:
```python
source venv/bin/activate
```
under the virtual environment terminal type the following commands:

```python

pip install -r requirements.txt

export FLASK_ENV=development

flask run
```

## database
create to databases in your computer call "leetenglish" and "leetenglish-test"

leetenglish for general storage and leetenglish-test for testing

```python
CREATE DATABASE leetenglish

CREATE DATABASE leetenglish-test
```

# Database Schema
leetEnglish have 18 tables under leetenglish database: 
* User
* Follows
* Quotes
* Articles
* Categories
* VocabularyFromArticle
* UserFinishReading
* VocabularyListName
* VocabularyList
* ImportCategory
* ImportArticles
* FinishImportReading
* ImportCategoryArticles
* VocabularyFromImportArticle
* Message
* CommentMessage
* Likes
* CommentLikes
  
![alt database schema1](https://drive.google.com/file/d/1MUD1hq0T3nA9OEDE-d5LjZEpHYxncEn-/view?usp=sharing)
![alt database schema2](https://drive.google.com/file/d/1Ax0z11BghaRgAQnkeOXS7P9DKTq2HDEX/view?usp=sharing)
![alt database schema3](https://drive.google.com/file/d/1lmfZg52kWxpLLJFvUVP3PSXkVfUqmQ5_/view?usp=sharing)


