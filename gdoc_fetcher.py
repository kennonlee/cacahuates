import socket
import logging
import atom.service
import gdata.service
import gdata.spreadsheet
import gdata.spreadsheet.service
import gdata.spreadsheet.text_db
                                                       
class GdocFetcher():

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def run(self):
        print self.get_entries()

    def get_entries(self):                
        """
	"""
        gd_client = gdata.spreadsheet.service.SpreadsheetsService()
        gd_client.email = self.email
        gd_client.password = self.password
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
        q['max-col'] = '3'
        q['min-row'] = '2'
        q['max-row'] = '20'

        try:
            feed = gd_client.GetCellsFeed(key, query=q)            
        except gdata.service.RequestError, e:
            logging.error('Spreadsheet gdata.service.RequestError: ' + str(e))
            return False
        except socket.sslerror, e:
            logging.error('Spreadsheet socket.sslerror: ' + str(e))
            return False
        
        # Iterate over the rows 
        name_indices = {}
        rankings = {}
        for row_entry in feed.entry:
            cell = row_entry.cell 
            cell_row = int(cell.row)
            cell_col = int(cell.col)
            cell_text = cell.text

            # this cell is someone's name. Make a new dict entry for them.
            if cell_row == 2:
                name_indices[cell_col] = cell_text
                rankings[cell_text] = []
            else:
                ranking = rankings[name_indices[cell_col]]
                ranking.append(cell_text)
        return rankings

    # Throws an error if the given rankings are invalid-- that is, if:
    # - the list is too short 
    # - the list is too long
    # - the chosen cities dont match the actual list of possible assignments
    def validate_rankings(self, rankings):
        return

if __name__ == "__main__":
    GdocFetcher("kennonator@gmail.com", "gobbledygook").run()
