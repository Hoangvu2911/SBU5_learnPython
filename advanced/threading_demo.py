# import threading

# def print_numbers():
#     for num in range(20):
#         print(num, end=" ", flush=True)

# def print_letters():
#     for letter in 'abcdefghij':
#         print(letter, end=" ", flush=True)

# def print_lettersz():
#     for letter in 'zxcvbnmasdfghjklqwertyuiop':
#         print(letter, end=" ", flush=True)

# thread1 = threading.Thread(target=print_numbers)
# thread2 = threading.Thread(target=print_letters)
# thread3 = threading.Thread(target=print_lettersz)

# thread1.start()
# thread2.start()
# thread3.start()

# thread1.join()
# thread2.join()
# thread3.join()

# print("\nDone!")


import queue
import threading
import time


URLS = ["url1", "url2", "url3", "url4"]
DELAY = 1.0

def fake_download(url: str) -> int:
    time.sleep(DELAY)
    return len(url)


def run_sequential(urls: list[str]) -> list[int]:
    return [fake_download(u) for u in urls]


def run_threaded(urls: list[str], workers: int) -> list[int]:
    q: queue.Queue[tuple[int, str]] = queue.Queue()
    results = [0] * len(urls)

    for i, u in enumerate(urls):
        q.put((i, u))

    def worker_loop():
        while True:
            try:
                i, u = q.get_nowait()
            except queue.Empty:
                break
            results[i] = fake_download(u)

    threads: list[threading.Thread] = []
    for _ in range(workers):
        t = threading.Thread(target=worker_loop)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return results


if __name__ == "__main__":
    workers = min(10, len(URLS))

    t0 = time.perf_counter()
    seq = run_sequential(URLS)
    t_seq = time.perf_counter() - t0

    t0 = time.perf_counter()
    th = run_threaded(URLS, workers)
    t_threaded = time.perf_counter() - t0

    print(f"Sequential: {t_seq:.3f}s | total={sum(seq)}")
    print(f"Threaded:   {t_threaded:.3f}s | total={sum(th)} | workers={workers}")
    print("Nhanh hơn:", "threaded" if t_threaded < t_seq else "sequential")
