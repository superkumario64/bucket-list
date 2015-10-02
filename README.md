# bucket-list
### I folowed this tutorial: http://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972
#### Here are some general thoughts, look at the code to see more specific:

* Pros
  * Flask looked pretty cool
  * I like how python forces sytax format
  * I had fun implementing the web app
* Cons
  * This guys code wasn't too DRY
  * Stored procedures don't scale well
    * Implement application/business logic first in JS then in Server-side language
    * Use caching techniques so js can check to see if username has been taken
    * Use foreign keys and constraints like unique to prevent certain cases in the DB
  * db password field was set to 20 chars, however the hashed password was larger so login wouldn't work
