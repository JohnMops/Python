import time            


def retry(func, retries: int = 2, delay: int | float = 1):
    def wrapper():
        for r in range(1, 1 + retries): 
            try:
                print(f'Try ({r}): {func.__name__}')
                return func()
            except Exception as e:
                if r == retry:
                    print(f'Error: {repr(e)}')
                    break
                else:
                    print(f'Error {repr(e)} ->> Retrying...')
                    time.sleep(delay)
    return wrapper

@retry
def connect():
    print("connecting")
    raise Exception("Dummy Exception")

def main():
    connect()

if __name__ == '__main__':
    main()