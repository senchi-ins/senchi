from .question_master import QuestionMaster
from .grader import RiskGrader
from .recommendations import RecommendationEngine
from .camera import RiskPhotoManager, RiskPhotoValidator
from .geoencoding import GoogleMapsGeocoder
from .risk_lookup import RiskLookup

question_master = QuestionMaster()
grader = RiskGrader()
recommendation_engine = RecommendationEngine()
photo_manager = RiskPhotoManager()
photo_validator = RiskPhotoValidator()
geocoder = GoogleMapsGeocoder()
risk_lookup = RiskLookup()

services = {
    'question_master': question_master,
    'grader': grader,
    'recommendation_engine': recommendation_engine,
    'photo_manager': photo_manager,
    'photo_validator': photo_validator,
    'geocoder': geocoder,
    'risk_lookup': risk_lookup,
}
