
def dict_to_comma_separated_values(data):
    return ",".join(["=".join([key, str(val)]) for key, val in data.items()])