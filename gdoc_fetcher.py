import socket
import logging
import atom.service
import gdata.service
import gdata.spreadsheet
import gdata.spreadsheet.service
import gdata.spreadsheet.text_db
                                                       
class GdocFetcher():
    def run(self, from_date=None, to_date=None):
        self.get_entries(from_date, to_date)

    def get_entries(self, from_date=None, to_date=None):                
        """
	    Sample code to fetch data from a Google Spreadsheet using a query and a sort, followed
	    by example of how to get the data out by column name.
	
	    This code assumes you have a spreadsheet that looks something like this:
	
	    Timestamp  		|	First Name	|	Last Name
	    8/16/2010 12:15:00  |	Michael		|	Woof
	    8/17/2010 14:25:35	|	John		|	Doe          
	
	    Google Spreadsheets normalizes the column names for the purposes of the API by stripping 
            all non-alphanumerics and lower-casing,
	    hence the column names used in the code as "timestamp", "firstname", and "lastname".
	"""
        gd_client = gdata.spreadsheet.service.SpreadsheetsService()
        gd_client.email = 'kennonator@gmail.com'
        gd_client.password = 'gobbledygook'
        gd_client.source = 'YOUR_APP_NAME'

        try:                    
	    # log in
            gd_client.ProgrammaticLogin()
        except socket.sslerror, e:
            logging.error('Spreadsheet socket.sslerror: ' + str(e))
            return False
	    
	key = '0Ag679of2C-6xdHB4Vjk0a01PZ0lkaXZlTTlqRkIzOHc'
	wksht_id = '0'
        
        q = gdata.spreadsheet.service.CellQuery()
        q['min-col'] = '2'
        q['max-col'] = '2'
        q['min-row'] = '2'
        q['max-row'] = '3'

        try:
            feed = gd_client.GetCellsFeed(key, query=q)            
        except gdata.service.RequestError, e:
            logging.error('Spreadsheet gdata.service.RequestError: ' + str(e))
            return False
        except socket.sslerror, e:
            logging.error('Spreadsheet socket.sslerror: ' + str(e))
            return False
        
        # Iterate over the rows
        for row_entry in feed.entry:
            print row_entry.ToString()
	    # to get the column data out, you use the text_db.Record class, then use the dict record.content
#            record = gdata.spreadsheet.text_db.Record(row_entry=row_entry)
#            print record

if __name__ == "__main__":
    GdocFetcher().run()
