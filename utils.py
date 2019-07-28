
def api_label_filters_to_kube_api_label_selector(api_label_filters):
    return ",".join([api_label_filter.replace(":", "=") for api_label_filter in api_label_filters])

def label_dict_to_kube_api_label_selector(data):
    return ",".join(["=".join([key, str(val)]) for key, val in data.items()])