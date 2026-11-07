#Question 3: Concurrent process
#calculates Fibonacci(35), Fibonacci(38), Fibonacci(40) in 10 rounds,
#once with multithreading (3 threads, 1 per number) and once without,
#then compares the average time taken (T, in nanoseconds) of both experiments
import threading, time

#settings kept in one place, so nothing is hardcoded twice
#NUMBERS: the Fibonacci numbers to calculate, one thread each in the threaded experiment
NUMBERS = [35, 38, 40]
#ROUNDS: how many times each experiment is repeated
ROUNDS = 10
#IO_SECONDS: how long each task waits in the I/O demo
IO_SECONDS = 1

#lock: only one thread at a time may write into the shared containers
#with the GIL, a single append is already safe, but the lock makes the rule
#explicit and keeps the data correct even if the write grows into several steps
#(e.g. read a value, change it, write it back), which threads could interleave
lock = threading.Lock()

#Each number is the sum of the two before it
#count starts from 0

#why recursive instead of iterative?
#1. it matches the definition directly: F(n) = F(n-1) + F(n-2)
#2. recursive is O(2^n): every call makes 2 more calls, and many values are recalculated
#   -> F(35), F(38), F(40) take seconds, so each thread gets a heavy CPU-bound task
#3. iterative is O(n): F(40) only loops 40 times and finishes in microseconds
#   -> creating and starting a thread would take longer than the calculation itself,
#      so the timing would measure thread overhead, not the work
#4. a heavy task lets the experiment show the effect of the GIL (Global Interpreter Lock):
#   - the GIL allows only ONE thread to run Python code at a time
#   - the 3 threads take turns on one core (concurrent, not parallel)
#   - total work stays the same, plus switching cost
#   -> so multithreading does NOT make this CPU-bound task faster
def fibonacci(n):
    #base case: give the first real values, F(0)=0, F(1)=1
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2) #F(n) = F(n-1) + F(n-2)

#runs inside each thread: time one fibonacci call and store the result
#threads cannot return values, so results and times are saved into shared containers
#results: dict, n -> fibonacci(n)
#starts : list, start time (ns) of every calculation
#ends   : list, end time (ns) of every calculation
def _fib_worker(n, results, starts, ends):
    #read the clock first, outside the lock, so waiting for the lock is not counted as work
    start = time.perf_counter_ns()
    value = fibonacci(n)
    end = time.perf_counter_ns()

    #write all 3 values together while holding the lock
    #another thread cannot write in the middle, so the shared data stays consistent
    with lock:
        starts.append(start)
        results[n] = value
        ends.append(end)

#one round WITH multithreading: 3 threads, 1 per number
def _threaded_round(results, starts, ends):
    threads = []
    for n in NUMBERS:
        #t is the thread object that holding a function call but haven't run anything yet
        t = threading.Thread(target = _fib_worker, args = (n, results, starts, ends))
        #to remember all thread for later operations
        #because the loop reusing name t
        threads.append(t)

    for t in threads:
        #object run its job in background
        #so main does not wait and moves straight to next thread
        t.start()

    for t in threads:
        #main wait all 3 thread objects done until this thread is finished
        #if no wait, main will race ahead while thread are still calculating
        t.join()

#one round WITHOUT multithreading: the main thread runs the 3 calculations one after another
def _sequential_round(results, starts, ends):
    for n in NUMBERS:
        _fib_worker(n, results, starts, ends)

#runs one experiment for ROUNDS rounds and returns the average T
#title    : text shown in the heading, e.g. "With Multithreading"
#run_round: the function that does one round (_threaded_round or _sequential_round)
#passing the round function in lets both experiments share this one loop (no duplicate code)
def run_experiment(title, run_round):
    print(f"\n=== Fibonacci Computation ({title}) ===")
    #T of every round, used for total and average
    times = []

    for round_no in range(1, ROUNDS + 1):
        #fresh container every round
        results = {}
        starts = []
        ends = []

        run_round(results, starts, ends)

        #T = end of last finished calculation - start of first started calculation
        T = max(ends) - min(starts)
        times.append(T)

        #build "Fib(35)=..., Fib(38)=..., Fib(40)=..." from NUMBERS, not typed by hand
        values = ", ".join(f"Fib({n})={results[n]}" for n in NUMBERS)
        print(f"Round {round_no:>2} : {values} | T = {T:,} ns")

    total = sum(times)
    average = total / len(times)
    print(f"Total T   ({title}) : {total:,} ns")
    print(f"Average T ({title}) : {average:,.0f} ns")
    return average

def showObservation(avg_thread, avg_no_thread):
    #differences smaller than this are treated as timing noise
    THRESHOLD = 1.0  #percent

    #positive -> multithreading faster
    #negative -> multithreading slower
    change = (avg_no_thread - avg_thread) / avg_no_thread * 100

    print()
    if abs(change) < THRESHOLD:
        print("Observation: No significant difference. Multithreading did not noticeably change the average time.")
    elif change > 0:
        print(f"Observation: Multithreading reduced the average completion time by approximately {change:.2f}%.")
    else:
        print(f"Observation: Multithreading increased the average completion time by approximately {abs(change):.2f}%.")

#I/O-bound demo: a situation where multithreading DOES help (report question 5 iv)
#time.sleep stands in for waiting on a file, a database or a website
#while a thread waits, it releases the GIL, so the other threads can run
#3 tasks of IO_SECONDS each:
#without threads -> the waits happen one after another, about 3 x IO_SECONDS
#with threads    -> the waits overlap, about 1 x IO_SECONDS
def _io_task():
    time.sleep(IO_SECONDS)

def io_demo():
    print(f"\n=== I/O-bound Demo (3 tasks, each waits {IO_SECONDS}s) ===")

    start = time.perf_counter_ns()
    for _ in NUMBERS:
        _io_task()
    sequential = time.perf_counter_ns() - start

    start = time.perf_counter_ns()
    threads = [threading.Thread(target = _io_task) for _ in NUMBERS]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    threaded = time.perf_counter_ns() - start

    print(f"Without Multithreading : {sequential:,} ns")
    print(f"With Multithreading    : {threaded:,} ns")


def main():
    avg_thread = run_experiment("With Multithreading", _threaded_round)
    avg_no_thread = run_experiment("Without Multithreading", _sequential_round)

    showObservation(avg_thread, avg_no_thread)
    io_demo()

if __name__ == '__main__':
    main()