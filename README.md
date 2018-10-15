# **Flask Favicon Finder (FFF)**
This is a simple Flask-based web-service to find favicon URLs and store them in a MongoDB collection.

### **Requirements**
```
mongodb 3.6+
pip 18.1+
python 2.7+
```

### **Installation**
Navigate to the top-level directory and run:
```
pip install -r requirements.txt
```
*Note: If you have different python versions (eg. `python` -> python2.7, `python3` -> python3.6) running, install with the following command:*
```
python -m pip install -r requirements.txt
```

### **Running the app**
Navigate to the top-level directory and run:
```
python appserver.py
```
*Note: The app assumes that MongoDB is running with default configuration (localhost:27017)*

---

### **Assumptions**
- Single-user mode for now
- User is allowed to enter a number for the initial db seeding

### **Usages + Features**

- **Finder**: http://localhost:5000
- **Finder (GET)**: http://localhost:5000/?url=python.org
- **Seeder**: http://localhost:5000/seed

---

### **Issues**
- Seeding takes extremely long even for a small number
- Single-user mode assumption

### **Considerations**
1. What happens if the website updates its favicon url?
2. How should 'get_fresh' be used?
3. What happens if a target website gets taken down?
4. How should redirects be handled? Currently favicon url cannot be found. For example `gooogle.com` redirects to `google.com`.
5. Some websites (eg. `ceap.br`) have favicon URLs, but the images don't exist.  How should this be handled?

---

### **TODOs**

**Testing**
- Add tests: `unittest` for unit tests, `pytest` for Flask REST endpoint tests
- Make the app into a rest-based service and write scripts to test the endpoint with multiple simultaneous requests to test reliability

**Seeding**
- Add indexing to db (on `id` field?)
- Add multi-threaded async processes for db-seeding
- Use `pandas` to read CSV in chunks (using the `chunkSize` feature) for parallel processing/seeding

**Frontend**
- Use regexp to validate user-input urls (has an extension, etc)
- Make a single page application (SPA) with loading gif, disable interactions, and clear out existing icon/state before making requests
- Add better feedback (ie. why icon was not found)
- Better handling for cases where favicons are not found (eg. googl.com)

**Backend**
- Add caching layer
- Add max timeout to requests
- Improve icon request logic without using 3rd party library: Request index.html file and crawl to find "shortcut icon" and "icon" link rels in the header.  Use web scrapers (scrapy, selenium, beautiful soup). Add url tester to see if url exists or not.
- Better redirect handling (eg. ceap.br redirects to ceap.br/v3, parumal.com redirects to google.com)
- Add some kind of request pooling for multi-users/requests use-case

---

### **Credits + License**

- [Flask](http://flask.pocoo.org/) - Python microframework allowing for rapid prototyping of web services.
- [Mongo](https://www.mongodb.com/) - Lightweight NoSQL database allowing for rapid prototyping data models.
- [pyfav](https://github.com/phillipsm/pyfav) - A module for finding favicon URLs.
- [PyMongo](https://api.mongodb.com/python/current/) - Python MongoDB wrapper.

Dual licensed under the [MIT license](https://opensource.org/licenses/MIT)  and [GPL license](http://www.gnu.org/licenses/gpl-3.0.html).

Copyright (c) 2018 Stanis Laus Billy