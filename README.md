# SpaceBlog
It's blog about space written in Python.

# A technology stack that is used when developing a blog
Languages: HTML&CSS,Python(framework django).

Database: MongoDB

Distributed Task Queue: Celery

Message broker: Redis

# What's embedded here?
1-Authorization(login + registration).

2-Confirm user email after registration.The letter is sent to the mail using celery.

3-Personal account.

4-Post feed.

5-Comments(only for user which authorised).

6-Likes and Dislikes(only for user which authorised).

7-Adding post(only for admin).
