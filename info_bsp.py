
"""
info_bsp.py
Simulasi Penyebaran Informasi menggunakan model BSP (Bulk Synchronous Parallel)
Setiap proses worker memegang sebagian node dan mensimulasikan penyebaran informasi
secara sinkron.

Usage:
    python info_bsp.py --workers 3 --iters 5
"""

from multiprocessing import Process, Manager, Barrier
import argparse
import time

def partition_nodes(nodes, k):
    parts = [[] for _ in range(k)]
    for i, n in enumerate(nodes):
        parts[i % k].append(n)
    return parts

def worker(wid, part_nodes, graph, known, new_known, barrier, iters):
    for step in range(iters):
        local_spread = set()
        # Penyebaran informasi
        for node in part_nodes:
            if known[node]:
                for neighbor in graph.get(node, []):
                    local_spread.add(neighbor)
        # Update info ke shared dict
        for v in local_spread:
            new_known[v] = True

        barrier.wait()  # tunggu semua worker selesai menyebar

        # Worker 0 melakukan merge
        barrier.wait()
        if wid == 0:
            for n in known.keys():
                if new_known.get(n, False):
                    known[n] = True
            new_known.clear()
        barrier.wait()

def build_social_graph():
    # Graph unik untuk simulasi: setiap mahasiswa boleh ubah strukturnya
    return {
        'A': ['B', 'C'],
        'B': ['C', 'D'],
        'C': ['D', 'E'],
        'D': ['E', 'F'],
        'E': ['F'],
        'F': ['G'],
        'G': [],
    }

def run_simulation(graph, initial_sources, workers=2, iters=5):
    manager = Manager()
    nodes = sorted(graph.keys())
    known = manager.dict({n: (n in initial_sources) for n in nodes})
    new_known = manager.dict()
    barrier = Barrier(workers)
    parts = partition_nodes(nodes, workers)

    procs = []
    start = time.time()
    for wid in range(workers):
        p = Process(target=worker, args=(wid, parts[wid], graph, known, new_known, barrier, iters))
        p.start()
        procs.append(p)
    for p in procs:
        p.join()
    elapsed = time.time() - start
    return dict(known), elapsed

def main():
    parser = argparse.ArgumentParser(description="BSP Information Diffusion Simulation")
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--iters', type=int, default=5)
    args = parser.parse_args()

    graph = build_social_graph()
    initial_sources = ['A']  # sumber awal informasi
    print("Sumber awal:", initial_sources)

    known, elapsed = run_simulation(graph, initial_sources, args.workers, args.iters)

    print("\nStatus akhir setelah", args.iters, "superstep:")
    for n, status in known.items():
        print(f"  {n}: {'Tahu informasi' if status else 'Belum tahu'}")
    print(f"\nWaktu eksekusi: {elapsed:.3f}s")

if __name__ == "__main__":
    main()
