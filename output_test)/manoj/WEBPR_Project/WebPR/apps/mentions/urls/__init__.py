from itertools import chain

from .iso_urls import iso_pattern
from .merchant_urls import merchant_pattern
from .service_urls import service_pattern
from .tracker_urls import tracker_pattern
from .statistics_urls import statistics_pattern

urlpatterns = list(chain(iso_pattern, merchant_pattern, tracker_pattern,
                         service_pattern, statistics_pattern))
