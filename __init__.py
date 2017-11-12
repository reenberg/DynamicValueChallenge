import os
import math
from CTFd.plugins.challenges import CTFdStandardChallenge, CHALLENGE_CLASSES
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.keys import get_key_class
from CTFd.models import db, Solves, WrongKeys, Keys, Challenges, Files, Tags, Teams
from CTFd import utils

from pymitter import EventEmitter

PLUGIN_FOLDER = os.path.basename(os.path.dirname(__file__))


class DynamicValueChallenge(CTFdStandardChallenge):
    id = "dynamic"  # Unique identifier used to register challenges
    name = "dynamic"  # Name of a challenge type
    templates = {  # Handlebars templates used for each aspect of challenge editing & viewing
        'create': '/plugins/{}/assets/dynamic-challenge-create.hbs'.format(PLUGIN_FOLDER),
        'update': '/plugins/{}/assets/dynamic-challenge-update.hbs'.format(PLUGIN_FOLDER),
        'modal': '/plugins/{}/assets/dynamic-challenge-modal.hbs'.format(PLUGIN_FOLDER),
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        'create': '/plugins/{}/assets/dynamic-challenge-create.js'.format(PLUGIN_FOLDER),
        'update': '/plugins/{}/assets/dynamic-challenge-update.js'.format(PLUGIN_FOLDER),
        'modal': '/plugins/{}/assets/dynamic-challenge-modal.js'.format(PLUGIN_FOLDER),
    }
    ee = EventEmitter(new_listener=False)

    @ee.on("challenge.onPreSolve")
    def onPreSolve(ns, *args, **kwargs):
        # Only needed if this line is not removed
        # https://github.com/CTFd/CTFd/blob/master/CTFd/utils.py#L477
        # ns.chal = DynamicChallenge.query.get(ns.chal.id)

        # We don't need to change the actual `chal` reference only its members
        # (which are already references), so there is no need to reference it as
        # `ns.chal` for the rest of this function.  All variables used here is
        # local to the calculation.
        chal = ns.chal
        solve_count = Solves.query \
            .join(Teams, Solves.teamid == Teams.id) \
            .filter(Solves.chalid == chal.id, Teams.banned == False).count()  # noqa

        value = (
            ((chal.minimum - chal.initial) / (chal.decay**2)) * (solve_count**2)
        ) + chal.initial
        value = math.ceil(value)

        if value < chal.minimum:
            value = chal.minimum

        chal.value = value


class DynamicChallenge(Challenges):
    __mapper_args__ = {'polymorphic_identity': DynamicValueChallenge.id}
    # CASCADE makes sure our rows will be deleted, when the foreign key gets
    # deleted (see https://stackoverflow.com/a/23945146)
    id = db.Column(None, db.ForeignKey('challenges.id', ondelete="CASCADE"),
                   primary_key=True)
    initial = db.Column(db.Integer)
    minimum = db.Column(db.Integer)
    decay = db.Column(db.Integer)

    def __init__(self, value, minimum=1, decay=50, **kwargs):
        self.type = DynamicValueChallenge.id
        self.initial = self.value = value
        self.minimum = minimum
        self.decay = decay

        for col in DynamicChallenge.__mapper__.columns:
            if col.name in kwargs:
                self.__setattr__(
                    col.name, kwargs[col.name]
                )


def load(app):
    """Plugin initialisation code.

    Called by `CTFd.plugins.init_plugins()` when iterating over all available
    plugins.

    """
    app.db.create_all()
    # Register our Challenge type
    CHALLENGE_CLASSES[DynamicValueChallenge.id] = \
        (DynamicValueChallenge, DynamicChallenge)
    register_plugin_assets_directory(
        app, base_path='/plugins/{}/assets/'.format(PLUGIN_FOLDER)
    )
