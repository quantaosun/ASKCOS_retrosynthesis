'''
The role of a context_worker is to take in an attempted reaction and return
a set of conditions to (try to) run the reaction in. Each worker will
load a pre-trained nearest neighbor model. For each request, this worker
must query the database to get details about the instance.
'''

from __future__ import absolute_import, unicode_literals, print_function
from celery import shared_task
from celery.signals import celeryd_init
from makeit.synthetic.context.nn_context_recommender import NNContextRecommender
import makeit.global_config as gc

CORRESPONDING_QUEUE = 'cr_nn_worker'

@celeryd_init.connect
def configure_worker(options={}, **kwargs):
    if 'queues' not in options: 
        return 
    if CORRESPONDING_QUEUE not in options['queues'].split(','):
        return
    print('### STARTING UP A NEAREST NEIGHBOR CONTEXT RECOMMENDER WORKER ###')

    global recommender

    # Get Django settings
    from django.conf import settings

    # Database
    from database import db_client

    # Setting logging low
    from rdkit import RDLogger
    lg = RDLogger.logger()
    lg.setLevel(RDLogger.CRITICAL)
    try:
        recommender = NNContextRecommender()
        recommender.load_nn_model(model_path = gc.CONTEXT_REC['model_path'], info_path = gc.CONTEXT_REC['info_path'])
    except Exception as e:
        print(e)
    print('Loaded context recommendation model')

    print('### NEAREST NEIGHBOR CONTEXT RECOMMENDER STARTED UP ###')


@shared_task
def get_n_conditions(rxn, n=10, singleSlvt=True, with_smiles=True):
    '''Retrieve a context recommendation given the reaction to attempt.

    rxn = [reacants, products], where each is a list of SMILES
    n = number of contexts to return'''

    global NN_PREDICTOR

    print('Context recommender worker got a request for rxn {} and n {}'.format(
        rxn, n))

    res =  recommender.get_n_conditions(rxn, n=n, singleSlvt=singleSlvt, with_smiles=with_smiles)
    print('Task completed, returning results.')
    return res