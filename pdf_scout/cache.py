from joblib import Memory

CACHE_DIR = "./.cache"
memory = Memory(CACHE_DIR, verbose=0)


def cache(input_function):
    """
    Only works with pure functions
    """
    return memory.cache(input_function)
