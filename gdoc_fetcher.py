import socket
import logging

import atom.service
import gdata.service
import gdata.spreadsheet
import gdata.spreadsheet.service
import gdata.spreadsheet.text_db

from munkres import Munkres, print_matrix

POSTS = {'Abu Dhabi': 0, 
         'Canberra': 1,
         'Dakar': 2,
         'Frankfurt1': 3,
         'Frankfurt2': 4,
         'Frankfurt RCSO': 5,
         'Athens RCSO': 6,
         'London': 7,
         'Mexico City': 8,
         'Montevideo1': 9,
         'Montevideo2': 10,
         'Moscow1': 11,
         'Moscow2': 12,
         'New Delhi': 13,
         'New Delhi RCSO': 14,
         }

RPOSTS = dict((v,k) for k, v in POSTS.iteritems())

class GdocFetcher():

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def get_assignments(self):
        rankings = self.get_entries()
        errors = self.validate_rankings(rankings)
        if len(errors) != 0:
            raise Exception(errors)
        #print rankings

        names = []
        for name, ranking in rankings.iteritems():
            names.append(name)
            converted = [POSTS[post] for post in ranking]
            rankings[name] = converted
        #print rankings

        # name_map maps matrix row to the person whose rankings the row represents
        count = 0
        name_map = {}
        for name in names:
            name_map[count] = name
            count += 1
        print name_map

        matrix = [ranking for ranking in rankings.itervalues()]
        #print matrix

        m = Munkres()
        indexes = m.compute(matrix)

#        print_matrix(matrix, msg='Lowest cost through this matrix:')
        total = 0
        assignments = []
        for row, column in indexes:
            value = matrix[row][column]
            total += value
            print '{0} assigned to {1} (cost {2})'.format(name_map[row], RPOSTS[column], value)
            assignments.append([name_map[row], RPOSTS[column], value + 1])
        print 'total cost=%d' % total    
        return assignments

    def get_entries(self):                
        """
        Returns a dictionary of names to ranking lists. No error checking is
        done on the contents of the lists.
	"""
        gd_client = gdata.spreadsheet.service.SpreadsheetsService()
        gd_client.email = self.email
        gd_client.password = self.password
        gd_client.source = 'my app poops'

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
        q['max-col'] = '10'
        q['min-row'] = '2'
        q['max-row'] = '21'

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
        errors = []
        for name, ranking in rankings.iteritems():
            if len(ranking) != len(POSTS):
                errors.append("{0} lists {1} posts, but requires {2}".format(name, len(ranking), len(POSTS)))
            errors.extend(self.validate_ranking_contents(name, ranking))
        return errors

    def validate_ranking_contents(self, name, ranking):
        errors = []
        checklist = dict((k, 1) for k in POSTS)
        for post in ranking:
            try:
                checklist.pop(post)
            except KeyError:
                errors.append('{0} has duplicate post {1} in list'.format(name, post))
        if len(checklist) != 0:
            for k in checklist.iterkeys():
                errors.append('{0} is missing post {1}'.format(name, k))
        return errors

    def convert_to_indices(self, ranking):        
        return [POSTS[p] for p in ranking]

if __name__ == "__main__":
    print GdocFetcher("kennonator@gmail.com", "gobbledygook").get_assignments()
