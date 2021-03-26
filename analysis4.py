import os,sys
import argparse

import random
from collections import defaultdict

from modules import indexing2, help_functions

from time import time

def print_stats(acc, datastructure, all_mers, k_size, total_mers):
    abundances = list(all_mers.values())
    del all_mers
    unique = abundances.count(1)
    percent_unique = round(100*unique/total_mers, 1)
    mean = sum(abundances)/len(abundances)
    ab_sorted = sorted(abundances)
    lower_75 = ab_sorted[1*len(abundances)//4]
    median = ab_sorted[len(abundances)//2]
    upper_75 = ab_sorted[3*len(abundances)//4]
    data = ",".join([str(d) for d in [k_size, datastructure, acc, mean, median, lower_75, upper_75, percent_unique]])
    print(data)


def time_datastructure(all_strings, args, k_size, w_size):
    # w_1 = 25
    # w_2 = 25 
    w = 1
    w_low = 25
    w_high = 50
    elapsed = time()
    all_mers = defaultdict(int)
    if args.kmers:
        datastructure = "kmers"
        for i in range(len(seq) - k_size +1):
            all_mers[hash(seq[i:i+k_size])] += 1

    if args.spaced_dense:
        datastructure = "spaced_dense"
        span_size = k_size+k_size//2
        positions = set(random.sample(range(1, span_size - 1 ), k_size-2)) 
        positions.add(0)
        positions.add(span_size - 1) # asserts first and last position is sampled so that we have a spaced kmer of length span size
        for s in indexing2.spaced_kmers_iter(seq, k_size, span_size, positions):
            all_mers[s] += 1

    if args.spaced_sparse:
        datastructure = "spaced_sparse"
        span_size = 3*k_size
        positions = set(random.sample(range(1, span_size - 1 ), k_size-2)) 
        positions.add(0)
        positions.add(span_size - 1) # asserts first and last position is sampled so that we have a spaced kmer of length span size
        for s in indexing2.spaced_kmers_iter(seq, k_size, span_size, positions):
            all_mers[s] += 1

    elif args.minstrobes2:
        datastructure = "minstrobes2"
        for s in indexing2.minstrobes_iter(seq, k_size, w_low, w_high, w, order = 2, buffer_size = 10000000):
            all_mers[s] += 1

    elif args.minstrobes3:
        datastructure = "minstrobes3"
        for s in indexing2.minstrobes_iter(seq, k_size, w_low, w_high, w, order = 3, buffer_size = 10000000):
            all_mers[s] += 1

    elif args.randstrobes2:
        datastructure = "randstrobes2"
        for s in seq_to_randstrobes2_iter(seq, k_size, strobe_w_min_offset, strobe_w_max_offset, prime, w): # (seq, k_size, order = 2, w_1 = 50 ):
            all_mers[s] += 1

    elif args.randstrobes3:
        datastructure = "randstrobes3"
        for s in indexing2.randstrobes_iter(seq, k_size, w_low, w_high, w, order = 3, buffer_size = 10000000):
            all_mers[s] += 1

    print_stats(acc, datastructure, all_mers, k_size, total_mers)



def main(args):

    genome = {acc: seq for (acc, (seq, _)) in help_functions.readfq(open(args.fasta, 'r'))}

    for acc,seq in genome.items():
        acc = acc.split()[0]
        # print(acc)
        genome[acc] = seq.replace("N", "") # remove Ns

    print(len(genome), sum([len(v) for k,v in genome.items()]))

    print("datastructure,k,acc,mean,median,lower_75,upper_75,\%-unique")

    all_strings = [ "".join([random.choice("ACGT") for i in range(L)]) for j in range(1000) ]

    for k_size in [30,60]: #[18,24,30]:
        for w_size in [20,30,40,50]: #[18,24,30]:
            start = time()
            for s in all_strings:
                time_datastructure(s, args, k_size, w_size)
            kmer_time = time() - elapsed
            print("kmers", k_size, w_size,  kmer_time)
            seq_to_randstrobes2_iter(seq, k_size, strobe_w_min_offset, strobe_w_max_offset, prime, w)






if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Calc identity", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--fasta', type=str,  default=False, help='Path to consensus fastq file(s)')
    parser.add_argument('--kmers',  action="store_true", help='Kmer size')
    parser.add_argument('--minstrobes2', action="store_true", help='Kmer size')
    parser.add_argument('--minstrobes3',  action="store_true", help='Kmer size')
    parser.add_argument('--randstrobes2',  action="store_true", help='Kmer size')
    parser.add_argument('--randstrobes3',  action="store_true", help='Kmer size')
    parser.add_argument('--spaced_dense',  action="store_true", help='Kmer size')
    parser.add_argument('--spaced_sparse',  action="store_true", help='Kmer size')
    # parser.add_argument('--k', type=int, default=13, help='Kmer size')
    # parser.add_argument('--w', type=int, default=20, help='Window size')
    # parser.add_argument('--outfolder', type=str,  default=None, help='A fasta file with transcripts that are shared between samples and have perfect illumina support.')
    # parser.add_argument('--pickled_subreads', type=str, help='Path to an already parsed subreads file in pickle format')
    # parser.set_defaults(which='main')
    args = parser.parse_args()



    if len(sys.argv)==1:
        parser.print_help()
        sys.exit()

    main(args)