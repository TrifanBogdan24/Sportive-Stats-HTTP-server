"""Module for classifying the requests for proecssing data"""

from enum import Enum

class JobType(Enum):
    """
    Enumeration class for classifying the HTTP requests that require data processing.
    Each enum member corresponds to a specific API endpoint.
    """
    GET_RESULTS = "/api/get_results"
    STATES_MEAN = "/api/states_mean"
    STATE_MEAN = "/api/state_mean"
    BEST_5 = "/api/best5"
    WORST_5 = "/api/worst5"
    GLOBAL_MEAN = "/api/global_mean"
    DIFF_FROM_MEAN = "/api/diff_from_mean"
    STATE_DIFF_FROM_MEAN = "api/state_diff_from_mean"
    MEAN_BY_CATEGORY = "api/mean_by_category"
    STATE_MEAN_BY_CATEGORY = "api/state_mean_by_category"
