
import socket
import logging

import atom.service
import gdata.service
import gdata.spreadsheet
import gdata.spreadsheet.service
import gdata.spreadsheet.text_db

from munkres import Munkres

DUPE_POSTS = {
    'Frankfurt': 2,
    'Montevideo': 2,
    'Moscow': 2,
    'DC': 5
}

POSTS = {'Abu Dhabi': 0, 
         'Athens RCSO': 1,
         'Canberra': 2,
         'Dakar': 3,
         'Frankfurt1': 4,
         'Frankfurt2': 5,
         'Frankfurt RCSO': 6,
         'London': 7,
         'Mexico City': 8,
         'Montevideo1': 9,
         'Montevideo2': 10,
         'Moscow1': 11,
         'Moscow2': 12,
         'New Delhi': 13,
         'New Delhi RCSO': 14,
         'DC1': 15,
         'DC2': 16,
         'DC3': 17,
         'DC4': 18,
         'DC5': 19
         }

RPOSTS = dict((v,k) for k, v in POSTS.iteritems())

class GdocFetcher():

    def __init__(self, email, password):
        self.email = email
        self.password = password


    def add_dupe_posts(self, rankings):
        '''
        For each list of rankings, adds in multiple items for the posts that 
        have more than one slot (Frankfurt, Montevideo, Moscow, DC).
        '''
        new_rankings = {}
        for name, ranking in rankings.iteritems():
            # sort of inefficient to create a new list, but oh well
            new_ranking = []
            for post in ranking:
                if post in DUPE_POSTS:
                    dupes = DUPE_POSTS[post]
                    for i in range(1, dupes + 1):
                        new_ranking.append('{0}{1}'.format(post, i))
                else:
                    new_ranking.append(post)
            new_rankings[name] = new_ranking
        return new_rankings

    def get_assignments(self, rankings):
        rankings = self.add_dupe_posts(rankings)
        #print rankings

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

        matrix = [self.flip_ranks(ranking) for ranking in rankings.itervalues()]
        print matrix

        m = Munkres()
        indexes = m.compute(matrix)
        print indexes

        total = 0
        assignments = []
        for row, column in indexes:
            value = matrix[row][column]
            total += value
            print '{0} assigned to {1} (cost {2})'.format(name_map[row], RPOSTS[column], value)
            assignments.append([name_map[row], RPOSTS[column], value + 1])
        #print 'total cost=%d' % total    
        return assignments

    # NO LONGER USED! Bid lists are no longer stored in gdocs.
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

    # converts an indexed ordered list into a weighted list ordered by post
    # indices-- the first element is the weight for abu dhabi, second is for
    # canberra, etc.
    def flip_ranks(self, ranking):
        ret = []
        for i in range(0, len(POSTS)):
            weight = 0
            for post in ranking:
                if i == post:
                    #print 'found {0} at weight {1}'.format(i, weight)
                    ret.append(weight)
                    break
                else:
                    weight += 1
        return ret

if __name__ == "__main__":
    g = GdocFetcher("kennonator@gmail.com", "gobbledygook")
    #r = [11,12,0,1,7,3,4,5,6,2,8,9,10,13,14]
    #print r
    #print g.flip_ranks(r)
    print g.get_assignments(g.get_entries())
