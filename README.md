# bucket-list
### I folowed this tutorial: http://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972
#### Here are some general thoughts, look at the code to see more specific:

* Likes
  * Flask looks pretty cool
  * I like how python forces sytax format
  * I had fun implementing the web app
* Dislikes
  * This guys code wasn't too DRY
  * Stored procedures don't scale well, in a site going for production I would:
    * Implement application/business logic first in JS then in Server-side language
    * Use caching techniques so js can poll to see if username has been taken
    * Use foreign keys and constraints like unique to prevent certain cases in the DB
  * db password field was set to 20 chars, however the hashed password was larger so login wouldn't work
  * CRUD/REST APIs could have been created for db interaction instead of creating a stored procedure for eveything.
