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


def curl_params_to_curl_exec_command(request_host: str,
                                     request_method: str,
                                     request_headers: Dict[str, str],
                                     request_body: str,
                                     timeout: str) -> List[str]:
    exec_command = ["curl",
                    "--connect-timeout", timeout,
                    "-s", "-o", "/dev/null",
                    "-w", "'%{http_code}'"]
    for header_name, header_value in request_headers.items():
        exec_command.append("--header")
        exec_command.append(f'"{header_name}: {header_value}"')

    exec_command.append("-X")
    exec_command.append(f'"{request_method}"')

    if request_body is not None:
        exec_command.append("--data")
        exec_command.append(f"'{request_body}'")

    exec_command.append(request_host)

    return exec_command



