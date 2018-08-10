import utime
import threading


def target(name, count):
    for idx in range(count):
        utime.sleep(0.5)
        print("Hello from {} - {}".format(name, threading.get_ident()))


def main():
    print("begin...")
    t = threading.Thread(target=target, args=("THREAD", 10))
    t.start()
    target("MAIN", 3)
    t.join()
    print("end.")


if __name__ == '__main__':
    main()
