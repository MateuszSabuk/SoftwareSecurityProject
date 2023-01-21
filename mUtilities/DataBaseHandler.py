import sqlite3


class DataBaseHandler:
    def __init__(self):
        self.url_array = []
        self.file_name = "hello"

    def add_url_req_to_db(self, url_dict):
        # Create a connection to the database
        conn = sqlite3.connect(f'{self.file_name}.db')
        c = conn.cursor()

        c.execute(f'''CREATE TABLE IF NOT EXISTS crawled_links
                (id INTEGER PRIMARY KEY,
                url TEXT NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL NOT NULL,
                elapsed REAL NOT NULL,
                status INTEGER NOT NULL,
                reason TEXT NOT NULL
                )''')

        c.execute(f'''INSERT INTO crawled_links 
                (url,start_time,end_time,elapsed,status,reason)
                VALUES (?,?,?,?,?,?)''', (
            url_dict["url"],
            url_dict["start_time"],
            url_dict["end_time"],
            url_dict["elapsed"],
            url_dict["status"],
            url_dict["reason"],
        ))
        conn.commit()
        print(f"{url_dict['url']} added to the database")

        # Close the connection to the database
        c.close()
        conn.close()

    # END OF add_url_req_to_db

    def run_tests_for_links(self, run_tests):
        # Create a connection to the database
        conn = sqlite3.connect(f'{self.file_name}.db')
        c = conn.cursor()

        c.execute(f'''CREATE TABLE IF NOT EXISTS crawled_links
                        (id INTEGER PRIMARY KEY,
                        url TEXT NOT NULL,
                        start_time REAL NOT NULL,
                        end_time REAL NOT NULL,
                        elapsed REAL NOT NULL,
                        status INTEGER NOT NULL,
                        reason TEXT NOT NULL
                        )''')

        # Get an array of all the URLs from the crawled_links table
        c.execute("SELECT url FROM crawled_links")
        url_array = [url[0] for url in c.fetchall()]

        # Close the connection to the database
        c.close()
        conn.close()

        if len(url_array) > len(self.url_array):
            url_to_test = set(url_array) - set(self.url_array)
            for url in url_to_test:
                run_tests(url)
            self.url_array = url_array
            self.run_tests_for_links(run_tests)

    # END OF run_tests_for_links
