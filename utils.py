from typing import Dict, List, Set
import datetime

def api_label_filters_to_kube_api_label_selector(api_label_filters):
    return ",".join([api_label_filter.replace(":", "=") for api_label_filter in api_label_filters])

def api_label_filters_to_dict(api_label_filters: List[str]) -> Dict[str, Set[str]]:
    result_dict = {}
    for api_label_filter in api_label_filters:
        [key, value] = api_label_filter.split(':')

        if key not in result_dict:
            result_dict[key] = set([value])
        else:
            result_dict[key].add(value)
    return result_dict

def label_dict_to_kube_api_label_selector(data):
    return ",".join(["=".join([key, str(val)]) for key, val in data.items()])


def get_age_string_from_datetime(past_datetime):
    now = datetime.datetime.now()
    diff = now - past_datetime

    days, seconds = diff.days, diff.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    return f"{days}d{hours}h{minutes}m{seconds}s"