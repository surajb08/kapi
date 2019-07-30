from typing import Dict, List, Set

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

