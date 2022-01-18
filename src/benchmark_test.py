from core import update_listinginfo

import  time,\
        memory_profiler


def benchmark_main_exec():
    i_mem = memory_profiler.memory_usage()
    start = time.time()

    update_listinginfo(test=True)

    end = time.time()
    f_mem = memory_profiler.memory_usage()
    elapsed = end - start
    mem_diff = f_mem[0] - i_mem[0]

    print(f'Finished jobs in {elapsed} consuming a total of {mem_diff} MB to complete')


benchmark_main_exec()