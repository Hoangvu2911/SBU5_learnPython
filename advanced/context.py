import time
with open("file.txt", "r") as file:
    start = time.time()
    print(file.read())
    end = time.time()
    print(f"Time taken: {end - start} seconds")
    
    