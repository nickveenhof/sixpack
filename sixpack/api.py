from models import Experiment, Alternative, Client
from config import CONFIG as cfg


def participate(experiment, experiment_type, alternatives, client_id,
    force=None,
    traffic_fraction=None,
    explore_fraction=None,
    prefetch=False,
    datetime=None,
    redis=None):

    exp = Experiment.find_or_create(experiment, experiment_type, alternatives, traffic_fraction=traffic_fraction, explore_fraction=explore_fraction, redis=redis)

    alt = None
    if force and force in alternatives:
        alt = Alternative(force, exp, redis=redis)
        policy = 'excluded'
    elif not cfg.get('enabled', True):
        alt = exp.control
        policy = 'excluded'
    elif exp.winner is not None:
        alt = exp.winner
        policy = 'excluded'
    else:
        client = Client(client_id, redis=redis)
        alt,policy = exp.get_alternative(client, dt=datetime, prefetch=prefetch)

    return alt, policy


def convert(experiment, experiment_type, client_id, reward,
    kpi=None,
    datetime=None,
    redis=None):

    exp = Experiment.find(experiment, redis=redis)

    if cfg.get('enabled', True):
        client = Client(client_id, redis=redis)
        alt = exp.convert(client, reward, dt=datetime, kpi=kpi)
    else:
        alt = exp.control

    return alt
