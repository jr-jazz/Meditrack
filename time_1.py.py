from os import name
import matplotlib.pyplot as plt

def parse_timing_data(filename):
    quicksort_half, quicksort_full = [], []
    mergesort_half, mergesort_full = [], []
    heapsort_half, heapsort_full = []
    sizes = []

    with open(filename, "r") as f:
        for line in f:
            parts = line.strip().split(", ")
            algo = parts[0].split(" - ")[0]
            half_time = float(parts[0].split(": ")[1][:-1])
            full_time = float(parts[1].split(": ")[1][:-1])
            size = int(parts[2].split(": ")[1])

            if algo == "QuickSort":
                quicksort_half.append(half_time)
                quicksort_full.append(full_time)
            elif algo == "MergeSort":
                mergesort_half.append(half_time)
                mergesort_full.append(full_time)
            elif algo == "HeapSort":
                heapsort_half.append(half_time)
                heapsort_full.append(full_time)
            sizes.append(size)

    return (sizes, 
            (quicksort_half, quicksort_full), 
            (mergesort_half, mergesort_full), 
            (heapsort_half, heapsort_full))

def plot_performance(sizes, quicksort, mergesort, heapsort):
    plt.figure(figsize=(12, 8))

    # Plot half data
    plt.plot(sizes[:len(quicksort[0])], quicksort[0], label="QuickSort (Half)", marker='o')
    plt.plot(sizes[:len(mergesort[0])], mergesort[0], label="MergeSort (Half)", marker='o')
    plt.plot(sizes[:len(heapsort[0])], heapsort[0], label="HeapSort (Half)", marker='o')

    # Plot full data
    plt.plot(sizes[:len(quicksort[1])], quicksort[1], label="QuickSort (Full)", marker='x')
    plt.plot(sizes[:len(mergesort[1])], mergesort[1], label="MergeSort (Full)", marker='x')
    plt.plot(sizes[:len(heapsort[1])], heapsort[1], label="HeapSort (Full)", marker='x')

    plt.xlabel("Data Size")
    plt.ylabel("Time (seconds)")
    plt.title("Sorting Algorithm Performance Comparison")
    plt.legend()
    plt.grid(True)
    plt.savefig("sorting_performance.png")
    plt.show()

if name == "main":
    filename = "sorting_times.txt"
    sizes, quicksort, mergesort, heapsort = parse_timing_data(filename)
    plot_performance(sizes, quicksort, mergesort, heapsort)