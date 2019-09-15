#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
the objective of this script is to generate copy numbre files in a nice format.
the original files are hg19 CN calls from ASCAT from a personal communication
from Peter Van Loo and Kerstin Haase. Then liftover with the package
segment_liftover https://github.com/baudisgroup/segment-liftover
"""

""" command line commands to run before the script
liftover_path=~/Documents/PhD/liftOver
segment_liftover -l $liftover_path -i ASCAT_TCGA -o liftover_ASCAT_TCGA -c hg19ToHg38 -si BLCA.ascat.segments.txt -so BLCA.ascat.segments.hg38.txt
segment_liftover -l $liftover_path -i ASCAT_TCGA -o liftover_ASCAT_TCGA -c hg19ToHg38 -si BRCA.ascat.segments.txt -so BRCA.ascat.segments.hg38.txt
segment_liftover -l $liftover_path -i ASCAT_TCGA -o liftover_ASCAT_TCGA -c hg19ToHg38 -si HNSC.ascat.segments.txt -so HNSC.ascat.segments.hg38.txt
"""

import pandas as pd

# next step is to merge all those files, and put them in wanted format
# ASCAT copy number
colnames = ['participant', 'chromosome', 'start', 'stop', 'major', 'minor']
cancer_locs = ['BRCA', 'BLCA', 'HNSC']
liftover_tables = dict()
for loc in cancer_locs:
    table = pd.read_csv(
        'data/pancancer/liftover_ASCAT_TCGA/{}.ascat.segments.hg38.txt'.format(loc),
        sep='\t', header=None, names=colnames)
    table = table.assign(type=loc)
    table = table.assign(minor=table.minor.round(0).astype(int))
    table = table.assign(major=table.major.round(0).astype(int))
    liftover_tables[loc] = table

big_table = pd.concat(liftover_tables.values())
big_table = big_table.assign(key=big_table.participant+'_'+big_table.chromosome)
big_table_m = pd.merge(big_table, big_table, left_on='key',
                     right_on='key', how='left',
                     suffixes=['', '_right'])
bb = big_table_m[(big_table_m.start < big_table_m.stop_right) &
                 (big_table_m.stop > big_table_m.start_right) &
                 (big_table_m.start <= big_table_m.start_right)]
bb = bb.assign(stop_new=bb.apply(lambda x: x.start_right-1 if
                                 (x.start < x.start_right < x.stop) else x.stop,
                                 axis=1))
bbsub = bb.drop_duplicates(subset=['key', 'start'], keep='last')
bbsub = bbsub.assign(stop=bbsub.stop_new)

bbsub[big_table.columns].to_csv('data/pancancer/liftover_ASCAT_TCGA/cnasHg38.tsv', sep='\t', index=False)

# ABSOLUTE copy number
absolute_cn = pd.read_csv(
    'external_data/TCGA_mastercalls.abs_segtabs.fixed.liftover_output.txt',
    sep='\t')
absolute_cn = absolute_cn.assign(
    key=absolute_cn.Sample+'_'+absolute_cn.Chromosome.astype(str))
absolute_cn_m = pd.merge(absolute_cn, absolute_cn, left_on='key',
                         right_on='key', how='left',
                         suffixes=['', '_right'])
aa = absolute_cn_m[(absolute_cn_m.Start < absolute_cn_m.End_right) &
                   (absolute_cn_m.End > absolute_cn_m.Start_right) &
                   (absolute_cn_m.Start <= absolute_cn_m.Start_right)]
aa = aa.assign(End_new=aa.apply(lambda x: x.Start_right-1 if
                                (x.Start < x.Start_right < x.End)
                                else x.End, axis=1))
aasub = aa.drop_duplicates(subset=['key', 'Start'], keep='last')
aasub = aasub.assign(End=aasub.End_new)

aasub[absolute_cn.columns].to_csv('data/pancancer/ABSOLUTE_cnasHg38.tsv',
                                  sep='\t', index=False)


