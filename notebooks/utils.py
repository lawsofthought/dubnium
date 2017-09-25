from collections import Counter, defaultdict

class SwwNorms(object):
    
    def __init__(self, sww_norms_csv_fname):

        '''
        Parse the data from the small-world-of-words csv file. The contents of
        the `sww_norms_csv_fname` csv file should look like this:

            1;car;auto;driver;vehicle
            1;bill;waiter;money;restaurant
            1;Christmas;father;Jesus;red
            1;decide;woman;choice;options
            1;people;persons;crowd;street
            1;behind;after;butt;slacking

        * The first field is the participant identifier
        * The second is the stimulus (or cue) word
        * The following three fields are the associates that the participant 
          gave for the stimulus word.

        We will put each trial, i.e. row, in a dictionary with the keys, ctr,
        word, assoc_1, assoc_2, and assoc_3. Then, each dictionary goes in a
        list. 

        '''

        self.association_norms = []
        for row in open(sww_norms_csv_fname,
                        encoding='utf-8').read().strip().split('\n'):

            self.association_norms.append(
                dict(zip('ctr word assoc_1 assoc_2 assoc_3'.split(),
                         row.split(';')))
            )

    def __len__(self):
        'Return the number of trials in the association norms data.'
        return len(self.association_norms)

    def filter_norms_by_vocabulary(self, vocab_dictionary, in_place=False):

        '''
        Filtering the associations norms by keeping only those trials
        where the stimulus word and all three associates are in the given
        vocabulary.

        If in_place is True, then replace the association_norms attribute with
        this filtered list.
        '''

        def stimuli_in_bnc_vocab(trial_data):

            '''
            Return True if and only if the stimulus word and all 
            three associates are in the vocabulary.
            '''

            return all([
                trial_data[key].lower() in vocab_dictionary
                for key in ('word', 'assoc_1', 'assoc_2', 'assoc_3')
            ])


        _association_norms\
            = [trial_data for trial_data in self.association_norms 
               if stimuli_in_bnc_vocab(trial_data)]

        if in_place:
            self.association_norms = _association_norms
        else:
            return _association_norms

    def filter_norms_by_stimulus_counts(self, 
                                        minimum_cue_word_count,
                                        in_place=False):

        '''
        Filter the associations norms by keeping only those trials where the
        stimulus word occurs at least `minimum_cue_word_count` times in total.

        If in_place is True, then replace the association_norms attribute with
        this filtered list.
        '''

        cue_word_counts = Counter([trial_data['word'].lower() 
                                   for trial_data in self.association_norms])

        _association_norms = []
        for response_trial in self.association_norms:
            if cue_word_counts[response_trial['word']]\
                    >= minimum_cue_word_count:
                _association_norms.append(response_trial)

        if in_place:
            self.association_norms = _association_norms
        else:
            return _association_norms

    def gather_associates(self):

        '''
        For each stimulus word, gather all its associates. Create a new
        attribute, `associates`, that is a dictionary with all cue words as 
        keys and a sorted list of (associate, count) tuples as values.
        '''

        # Gather all (case-folded) associates of each (case-folded)
        # stimulus word
        associates = defaultdict(list)
        for response_trial in self.association_norms:

            word, assoc_1, assoc_2, assoc_3 =\
                [response_trial[key].lower() 
                 for key in 'word assoc_1 assoc_2 assoc_3'.split()]

            associates[word].extend([assoc_1, assoc_2, assoc_3])

        # For all associates of each stimulus word, count its number
        # of occurrences, and store the (associate, count) tuples in
        # a reverse sorted order.
        _associates = {}
        for cue_word in associates:

            associates_item = sorted(Counter(associates[cue_word]).items(),
                                     key=lambda item: item[1], 
                                     reverse=True)

            _associates[cue_word] = associates_item

        self.associates = _associates

    def filter_norms_by_associates(self, 
                                   minimum_number_of_associates,
                                   minimum_associate_count,
                                   in_place=True):

        '''
        Filter the norms by keeping only those cue words that have at least
        `minimum_number_of_associates`, with each associate having at least a
        `minimum_associate_count` occurrences.

        '''
        

        def has_frequent_associates(cue_associates_item,
                                    minimum_number_of_associates,
                                    minimum_associate_count):
            
            ''' Return True if there are `minimum_number_of_associates`
            associates and all of them occur at least `minimum_associate_count`
            times.  
            
            This method assumes that the (associate, word) set of each 
            stimulus are in a reverse sorted order.
            
            '''

            try:
                return cue_associates_item[minimum_number_of_associates-1][1]\
                        >= minimum_associate_count
            except IndexError:  # less than min no. of items
                return False

        _associates = {}
        for cue_word, associates_item in self.associates.items():

            if has_frequent_associates(associates_item, 
                                       minimum_number_of_associates,
                                       minimum_associate_count):

                _associates[cue_word] = associates_item

        if in_place:
            self.associates = _associates
        else:
            return _associates
