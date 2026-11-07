# 5022CMD Advanced Algorithms – Portfolio

Source code for the 5022CMD Advanced Algorithms coursework (Coventry University, delivered at INTI International College Penang).
The portfolio has three command-line Python programs covering hashing, graphs and concurrent processing.

**Author:** Valerina Yeap Bei Qian

---

## Repository Contents

| File | Question | Description |
|------|----------|-------------|
| `Question1_Hashing.py` | Q1 – Hashing | Pharmacy inventory system built on a hash table that uses open addressing with linear probing |
| `Question2_Graph.py` | Q2 – Graph | University course-prerequisite system built on an unweighted directed graph |
| `Question3_ConcurrentProcess.py` | Q3 – Concurrent Process | Fibonacci timing experiment that runs the same work with and without multithreading |

---

## Requirements

- Python 3.8 or later
- No external libraries. Only the standard library is used (`time`, `threading`).

## How to Run

Clone the repository and run each program from the terminal:

```bash
git clone <repository-url>
cd <repository-folder>

python Question1_Hashing.py
python Question2_Graph.py
python Question3_ConcurrentProcess.py
```

> On some systems, use `python3` instead of `python`.

---

## Question 1 – Hashing (Pharmacy Inventory System)

A local storage system for a pharmacy retail outlet.

**Data structure**
- `HashTable` class (size 10) with hash function `key % size`
- Collisions are resolved with **open addressing and linear probing**
- Deleted slots are marked with a `DELETED` tombstone, so the probe path stays unbroken and later records can still be found
- `Product` entity class with the attributes `id`, `name`, `price` and `stock`

**Features**
1. Insert Product (duplicate IDs are rejected)
2. Search Product
3. Edit Product
4. Delete Product
5. Exit

Five predefined product records are loaded into the hash table and into a one-dimensional array at startup.

**Performance comparison**
Every search runs on both the hash table and the array, and the execution time of each lookup is measured with `time.perf_counter()`. This compares O(1) average-case hashing with O(n) linear search.

---

## Question 2 – Graph (Course Prerequisite System)

A menu-driven course-prerequisite system.

**Data structure**
- Generic `Graph` class stored as an adjacency list (dictionary of lists)
- Methods: `addVertex`, `addEdge`, `listIncomingAdjacentVertex`, `listOutgoingAdjacentVertex`
- The graph has no course-specific code, so it can be reused for any vertex type
- `Course` entity class with the attributes `courseCode`, `courseName`, `creditHours` and `level`

**Predefined courses and prerequisites**

| Course | Prerequisite(s) |
|--------|-----------------|
| CS101 – Introduction to Programming | – |
| CS201 – Data Structures | CS101 |
| CS301 – Algorithms | CS101, CS201 |
| CS302 – Database Systems | CS201 |
| CS401 – Software Engineering | CS301, CS302 |

**Features**
1. View All Courses
2. View Course Details
3. View Prerequisites of a Course (incoming edges)
4. View Courses Unlocked by a Course (outgoing edges)
5. Exit

---

## Question 3 – Concurrent Process (Fibonacci Multithreading)

The program calculates **Fibonacci(35)**, **Fibonacci(38)** and **Fibonacci(40)** using a recursive function (O(2ⁿ)).

**Experiments** (10 rounds each)
- **With multithreading:** 3 threads, one per Fibonacci number
- **Without multithreading:** the three calculations run one after another in the main thread

The time for each round is measured in nanoseconds with `time.perf_counter_ns()`:

```
T = End time of the thread that finished last − Start time of the thread that started first
```

The program prints T for each round, the average T for each experiment, and an observation comparing the two.

**Expected finding:** because of Python's **Global Interpreter Lock (GIL)**, only one thread can run Python bytecode at a time. Threads therefore run *concurrently*, not in *parallel*, and multithreading does not speed up this CPU-bound task.

> Note: Q3 takes a few minutes to complete because recursive Fibonacci(40) is computationally heavy.
