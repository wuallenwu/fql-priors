from agents.fql import FQLAgent
from agents.fql_prior import FQLPriorAgent
from agents.ifql import IFQLAgent
from agents.iql import IQLAgent
from agents.rebrac import ReBRACAgent
from agents.sac import SACAgent

agents = dict(
    fql=FQLAgent,
    fql_prior=FQLPriorAgent,
    ifql=IFQLAgent,
    iql=IQLAgent,
    rebrac=ReBRACAgent,
    sac=SACAgent,
)
