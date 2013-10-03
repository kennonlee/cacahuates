
import socket
import logging

import atom.service
import gdata.service
import gdata.spreadsheet
import gdata.spreadsheet.service
import gdata.spreadsheet.text_db

from munkres import Munkres

# bad things happen in prettify_dupes() if theres a post with more than 9 slots!
DUPE_POSTS = {
    'Frankfurt': 2,
    'Montevideo': 2,
    'Moscow': 2,
    'DC': 7
}

# the actual index ranges of dupe posts; used for forcing assignments
DUPE_POST_RANGES = {
    'Frankfurt': [3, 5],
    'Montevideo': [8, 10],
    'Moscow': [10, 12],
    'DC': [13, 20]
}

POSTS = {'Abu Dhabi': 0, 
         'Canberra': 1,
         'Dakar': 2,
         'Frankfurt1': 3,
         'Frankfurt2': 4,
         'Frankfurt RCSO': 5,
         'London': 6,
         'Mexico City': 7,
         'Montevideo1': 8,
         'Montevideo2': 9,
         'Moscow1': 10,
         'Moscow2': 11,
         'New Delhi': 12,
         'DC1': 13,
         'DC2': 14,
         'DC3': 15,
         'DC4': 16,
         'DC5': 17,
         'DC6': 18,
         'DC7': 19
         }

RPOSTS = dict((v,k) for k, v in POSTS.iteritems())

class BidSolver():

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

    
    def prettify_dupes(self, post, rank):
        '''
        Bad things would happen here if theres a post with more than 9 slots!

        There's a weak attempt to fudge the rankings but it doesnt really work.
        For instance, if we have 3 people that bid Moscow (2 slots), the person
        that doesnt get Moscow will get his second bid, but it will show as #3.

        The only real way to fix this is to revert the bids to their unduped
        state when determining the assignment rank. But thats harder.
        '''
        if post[:-1] in DUPE_POSTS:
            base_rank = rank - int(post[-1]) + 1
            return [post[:-1], base_rank]
        return [post, rank]

    def get_assignments(self, rankings, forced={'Kennon':'London', 'DaveG':'Canberra'}):
        #print '###1', rankings

        rankings = self.add_dupe_posts(rankings)
        #print '###2', rankings

        errors = self.validate_rankings(rankings)
        if len(errors) != 0:
            print errors
            raise Exception(errors)
        #print '###3', rankings

        errors = self.validate_forced(forced)
        if len(errors) != 0:
            print errors
            raise Exception(errors)
        #print '###4', rankings

        names = []
        for name, ranking in rankings.items():
            names.append(name)
            # converts post names to their alphabetical index
            converted = [POSTS[post] for post in ranking]                
            rankings[name] = converted
        #print rankings

        # name_map maps matrix row to the person whose rankings the row represents
        count = 0
        name_map = {}
        for name in names:
            name_map[count] = name
            count += 1
        print 'name_map:', name_map

        matrix = [self.flip_ranks(ranking) for ranking in rankings.itervalues()]
#        print 'unforced matrix:', matrix

        # assign very low cost values to force the algorithm to make certain
        # assignments
        reverse_name_map = dict((v,k) for k, v in name_map.iteritems())
        
        for forced_person, forced_post in forced.items():
            # the forced person hasnt actually saved a bid list; make a fake one
            if forced_person not in reverse_name_map:
                name_map[count] = forced_person
                reverse_name_map[forced_person] = count
                matrix.append([0] * len(POSTS))
                count += 1
            person_index = reverse_name_map[forced_person]
            # the forced post is a dupe one; assign a low cost to each dupe
            if forced_post in DUPE_POST_RANGES:
                dupe_post_range = DUPE_POST_RANGES[forced_post]
                for i in range(dupe_post_range[0], dupe_post_range[1]):
                    matrix[person_index][i] = -100
            else:
                post_index = POSTS[forced_post]
                matrix[person_index][post_index] = -100
        print 'matrix:', matrix

        m = Munkres()
        indexes = m.compute(matrix)
        print indexes

        total = 0
        assignments = []
        for row, column in indexes:
            value = matrix[row][column]
            total += value
            print '{0} assigned to {1} (cost {2})'.format(name_map[row], RPOSTS[column], value)
            prettified = self.prettify_dupes(RPOSTS[column], value + 1)
            assignments.append([name_map[row], prettified[0], prettified[1]])
        #print 'total cost=%d' % total    
        return assignments


    def validate_rankings(self, rankings):
        '''
        Throws an error if the given rankings are invalid-- that is, if:
        - the list is too short 
        - the list is too long
        - the chosen cities dont match the actual list of possible assignments    
        '''
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

    def validate_forced(self, forced):
        '''TODO'''
        errors = []
        return errors

    def flip_ranks(self, ranking):
        '''
        Converts an indexed ordered list into a weighted list ordered by post
        indices-- the first element is the weight for Abu Dhabi, second is for
        Athens, then Canberra, etc.

        '''
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
    g = BidSolver()
    #r = [11,12,0,1,7,3,4,5,6,2,8,9,10,13,14]
    #print r
    #print g.flip_ranks(r)
    print g.get_assignments(g.get_entries())
