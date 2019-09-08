def is_a_cat(request, view, action, name: str):
    if name == "Garfield":
        return True
    return False
