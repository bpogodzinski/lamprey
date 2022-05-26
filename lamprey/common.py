def format_bytes(size):
    if size < 0:
        raise ValueError('size cannot be a negative number')
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return size, power_labels[n]