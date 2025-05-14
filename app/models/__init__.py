#Importaciones de los modelos
from .user.user import User
from .user.admin import Admin
from .user.coordinator import Coordinator
from .user.student import Student

from .document.document import Document
from .document.template import Template 
from .document.release_letter import ReleaseLetter  
from .document.report import Report
from .document.report_cycle import ReportCycle
from .document.report_cycle_item import ReportCycleItem

from .institution.institution import Institution
from .institution.program import Program

from .request.request import Request
