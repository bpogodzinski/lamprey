import shutil

def format_bytes(size):
    if size < 0:
        raise ValueError('size cannot be a negative number')
    power = 2**10
    postfix_counter = 0
    power_labels = {0 : '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        postfix_counter += 1
    return size, power_labels[postfix_counter]

def check_user_disk_space(trt_size, file_path):
    # Returns value in bytes
    _, _, disk_free = shutil.disk_usage(file_path)
    if trt_size > disk_free:
        raise EnvironmentError('Not enough space to download the file!')
    else:
        return True
