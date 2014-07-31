def has_class(element, class_name):
    return class_name in element.attrib.get('class', '')