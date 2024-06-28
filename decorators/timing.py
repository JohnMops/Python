import time
import datetime

def get_time(func):
    def wrapper():
        begin = datetime.datetime.now()
        func()
        end = datetime.datetime.now()
        took = end - begin
        print(f"{func.__name__} took {took.seconds:.3f} seconds")
    return wrapper

@get_time
def some():
    print("Operation Starting")
    time.sleep(2)
    print("Operation completed")

def main():
    some()

if __name__ == '__main__':
    main()