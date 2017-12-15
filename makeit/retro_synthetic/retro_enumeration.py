import rdkit.Chem as Chem
from rdkit.Chem import AllChem

class RetroResult:
    '''
    A class to store the results of a one-step retrosynthesis.
    '''
    
    def __init__(self, target_smiles):
        self.target_smiles = target_smiles
        self.precursors = []

    def add_precursor(self, precursor, prioritizer):
        '''
        Adds a precursor to the retrosynthesis result if it is a new and unique product
        '''
        # Check if the precursor set is new or old
        for old_precursor in self.precursors:
            if precursor.smiles_list == old_precursor.smiles_list:
                # Just need to add the fact that this template_id can make it
                old_precursor.template_ids |= set(precursor.template_ids)
                old_precursor.num_examples += precursor.num_examples
                return
        # New! Need to score and add to list
        precursor.prioritize(prioritizer)
        self.precursors.append(precursor)

    def return_top(self, n = 50):
        '''
        Returns the top n precursors as a list of dictionaries, 
        sorted by descending score
        '''
        top = []
        for (i, precursor) in enumerate(sorted(self.precursors, \
                key = lambda x: (x.retroscore, x.num_examples), reverse = True)):
            top.append({
                'rank': i + 1,
                'smiles': '.'.join(precursor.smiles_list),
                'smiles_split': precursor.smiles_list,
                'score': precursor.retroscore,
                'num_examples': precursor.num_examples,
                'tforms': sorted(list(precursor.template_ids)),
                'necessary_reagent': precursor.necessary_reagent,
                })
            if i + 1 == n: 
                break
        return top

class RetroPrecursor:
    '''
    A class to store a single set of precursor(s) for a retrosynthesis
    does NOT contain the target molecule information
    '''
    def __init__(self, smiles_list = [], template_id = -1, num_examples = 0, necessary_reagent = ''):
        self.retroscore = 0
        self.num_examples = num_examples
        self.smiles_list = smiles_list
        self.template_ids = set([template_id])
        self.necessary_reagent = necessary_reagent

    def prioritize(self, prioritizer):
        '''
        Calculate the score of this step as the worst of all precursors,
        plus some penalty for a large necessary_reagent
        '''
        self.retroscore = prioritizer.get_priority(self)