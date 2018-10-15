import csv
import requests
import time

from datetime import datetime
from flask import Flask, jsonify, render_template, request
from pyfav import get_favicon_url, parse_markup_for_favicon
from urlparse import urlparse

from db.mongodb_client import MongoDbClient



# ------------------------------------------------------------------
# SETUP
# ------------------------------------------------------------------

# Init application object
app = Flask(__name__)

# Init db info
db = None

# Constants
DB_NAME = 'favdb'
COLLECTION_NAME = 'favs'
SEED_COUNT_MAX = 200000



# ------------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------------

@app.route('/')
def index():
    '''
    GET usage example:
    http://localhost:5000/?url=http://www.google.com/index.html

    Sample response:
    {
        "error_msg": "", 
        "favicon_url": "http://www.google.com/favicon.ico"
    }
    '''
    if request.args:
        result = fetch_favicon_url(url=request.args['url'])
        print(result)
        return jsonify(result)
    else:
        return render_main()


@app.route('/', methods=['POST'])
def index_post():
    '''
    index.html form submission receiver.

    Expected parameters:
    url -- URL whose favicon should be fetched.

    Returns:
    Renders index.html back with updated values.
    '''
    url = request.form['url']
    result = fetch_favicon_url(url=url, get_fresh=True)
    print(result)
    return render_main(result['favicon_url'], result['error_msg'], url)


@app.route("/seed")
def seed():
    '''
    Renders seeder.html file with default values.

    Wait for response in this format:
    <n> rows seeded in <x> seconds
    '''
    return render_template('seeder.html')


@app.route("/seed", methods=['POST'])
def seed_post():
    '''
    seeder.html form submission receiver.

    Expected parameters:
    seed_num -- # of urls from 'top-1m.csv' which should be used to seed the db

    Returns:
    Renders seeder.html back with updated values.
    '''

    # Determine the # of seeds
    seed_num = request.form['seed_num'] # see if the value is passed in request
    seed_num = int(seed_num) if seed_num else SEED_COUNT_MAX

    # Drop the collection first
    db.drop(coll_name=COLLECTION_NAME)

    # Read csv file line-by-line and insert as document into mongo
    rows_read = 1
    seed_time = 0
    with open('files/top-1m.csv') as csvfile:
        readcsv = csv.reader(csvfile, delimiter=',')
        start_time = datetime.now()
        for row in readcsv:
            if rows_read > seed_num:
                break
            id = int(row[0])
            url = row[1]
            result = fetch_favicon_url(url=url, record_id=id)
            print(rows_read, result)
            rows_read += 1
        end_time = datetime.now()
        seed_time = (end_time - start_time).total_seconds()
    resp = '{0} rows seeded in {1} seconds'.format(rows_read-1, seed_time)
    print(resp)

    return render_template('seeder.html', result=resp)



# ------------------------------------------------------------------
# HELPER METHODS
# ------------------------------------------------------------------

def fetch_favicon_url(url='', record_id=None, get_fresh=False):
    '''
    Main app logic, consists of the following steps:
    1. Sanitize the URL received

    URL sanitizing steps:
    1. Check if the http protocol exists and add if it doesn't
    2. Check if the path starts with www and add if it doesn't
    3. Append the protocol and the domain/netloc only for search/store
        and ignore the path (eg. "/index.html", "/blah/blah/blah")
    
    Using these steps, all following are stored as "http://www.google.com":
    - google.com
    - google.com/index.html
    - http://google.com
    - http://google.com/index.html
    - www.google.com
    - www.google.com/index.html
    - http://www.google.com
    - http://www.google.com/index.html

    Arguments:
    url -- URL whose favicon should be fetched
    record_id -- id associated with the url (an integer).
    get_fresh -- Whether favicon_url in db should be refreshed (boolean). 
                Defaults to False.

    Returns:
    A dictionary in this format:
    {
        "favicon_url": "",
        "error_msg": ""
    }
    '''

    # URL shouldn't be empty
    if not url:
        return {'favicon_url':'', 'error_msg':'URL is empty!'}

    # Break url down into tokens
    parsed_url = urlparse(url)

    # Check if url contains the http protocol and prepend if it doesn't
    if not parsed_url.scheme:
        url = 'http://{}'.format(url)
        parsed_url = urlparse(url)

    # Check if the domain part contains 'www.' and prepend if it doesn't
    if not parsed_url.netloc.startswith('www.'):
        url = '{0}://www.{1}'.format(parsed_url.scheme, parsed_url.netloc)
        parsed_url = urlparse(url)

    # Sanitize the url one last time to only include scheme + netloc
    url = '{0}://{1}'.format(parsed_url.scheme, parsed_url.netloc)

    favicon_url = ''
    error_msg = ''
    if get_fresh:
        # If get_fresh flag is on, update if doc exists, otherwise insert
        try:
            favicon_url = get_favicon_url(url)
            if favicon_url:
                doc = db.find_one(coll_name=COLLECTION_NAME, 
                                search_terms={'url':url}
                        )
                if doc:
                    db.update_one(coll_name=COLLECTION_NAME,
                                filter_terms={'id': doc['id']},
                                updates={'favicon_url': favicon_url}
                    )
                else:
                    # Find max id value in db, and increment for the new record
                    max_id = db.get_max_id(coll_name=COLLECTION_NAME)
                    row_id = max_id+1
                    db.insert_one(coll_name=COLLECTION_NAME,
                                doc={'id': row_id, 
                                    'url': url, 
                                    'favicon_url': favicon_url
                                    }
                    )
            else:
                error_msg = "Unable to find favicon :("
        except Exception as e:
            error_msg = str(e)
    else:
        # Try to find url in the db first. Try to fetch and save if not found.
        doc = db.find_one(coll_name=COLLECTION_NAME, search_terms={'url':url})
        if doc:
            # If document exists, just return the existing favicon url
            favicon_url = doc['favicon_url']
        else:
            # If document doesn't exist, find the favicon url and save it
            try:
                favicon_url = get_favicon_url(url)
                if favicon_url:
                    if record_id:
                        row_id = record_id
                    else:
                        max_id = db.get_max_id(coll_name=COLLECTION_NAME)
                        row_id = max_id+1
                    db.insert_one(coll_name=COLLECTION_NAME,
                                doc={'id': row_id, 
                                    'url': url, 
                                    'favicon_url': favicon_url
                                    }
                    )
                else:
                    error_msg = "Unable to find favicon :("
            except Exception as e:
                error_msg = str(e)

    result = {}
    result['favicon_url'] = favicon_url
    result['error_msg'] = error_msg
    return result


def render_main(icon_url='', error_msg='', input_value=''):
    '''
    Helper method to render the main (index) html file.
    Create an object from arguments to pass to the template before 
    rendering it.

    Arguments:
    error_msg -- Error message if icon could not be found. Empty otherwise.
    icon_url -- Favicon url to be rendered.
    input_value -- The value for the input text box.

    Returns:
    render_template() method call with 'index.html' and a dictionary.
    '''
    obj = {}
    obj['input_value'] = input_value
    obj['error_msg'] = error_msg
    obj['favicon_url'] = icon_url
    return render_template('index.html', obj=obj)


def init_mongo():
    '''
    Helper method to initialize the MongoDB client. Should be called
    before running the app.
    '''
    global db
    db = MongoDbClient(host='localhost', port=27017, db_name=DB_NAME)



if __name__ == "__main__":
    init_mongo()
    app.run(host='0.0.0.0', port=5000, debug=True)