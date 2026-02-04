def has_specie(image_path):
    name = get_name(image_path)
    names = name.split(" ")
    return len(names) > 2 and names[0][0].isupper() and names[1][0].islower()

def get_name(path):
    return ".".join(path.split("/")[-1].split(".")[:-1])
