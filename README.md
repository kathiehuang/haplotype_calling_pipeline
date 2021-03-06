# Running the haplotype calling pipeline with Snakemake

Overview: Using human or mosquito samples from Webuye, Kenya, evaluate the extent to which there are unique haplotypes among two polymorphic gene targets: AMA, CSP.

Method: Targeted amplicon deep sequencing which produces forward and reverse fastq files for each sample.

[Snakemake](https://snakemake.readthedocs.io/en/stable) is a workflow manager
that enables massively parallel and reproducible
analyses.
Snakemake is a suitable tool to use when you can break a workflow down into
discrete steps, with each step having input and output files.

We provide this example workflow as a template to get started running the pipeline with Snakemake.
To adjust to your specific data, you can customize the config.yaml file.

For more details on Snakemake, see the
[Snakemake tutorial](https://snakemake.readthedocs.io/en/stable/tutorial/tutorial.html).

## The Workflow

The [`Snakefile`](Snakefile) contains rules which define the output files we want and how to make them.
Snakemake automatically builds a directed acyclic graph (DAG) of jobs to figure
out the dependencies of each of the rules and what order to run them in.
This workflow processes the data set by cleaning the sequencing reads, performing haplotype calling, and censoring the haplotypes to render numerous data analysis outputs, resulting in a final table that contains the resulting haplotypes after censoring.

![dag](dag.png)

`clean_sequencing_reads` cleans, filters, and maps the raw reads. It uses BBmap to map all reads from the reference sequences to differentiate between the two targets, CutAdapt to trim the primers and adapter sequences from sequencing reads, and Trimmomatic to quality filter reads if average of every 4 nucleotides had a Phred Quality Score < 15 or was less than 80 nucleotides long. This is the first step in read processing on the cluster.

`organize_folders` creates an all_samples folder within the out/fastq/{target} folder and moves all forward and reverse sequences into that folder.

`call_haplotypes` call haplotypes for your target using the DADA2 program. This is the second step in the read processing on the cluster.

`censor_haplotypes` censors falsely detected haplotypes. Censoring criteria is applied in this order:
1. Haplotypes that occur in < 250 of the sample???s reads are removed. You can change this criteria in the config file ("read_depth").
2. Haplotypes that occur in < 3% of the sample???s reads are removed. You can change this criteria in the config file ("proportion").
3. Haplotypes that are a different length than the majority of haplotypes (300 nucleotides for pfama1, 288 nucleotides for pfcsp. You can change the length in the config file ("haplotype_length").
4. For haplotypes that have 1 SNP difference, occur in the same sample, and have a > 8 times read depth difference between them within that sample, removed the hapltoype with the lower read depth from that sample. You can change the 8 to a different read depth ratio in the config file ("read_depth_ratio").
5. If a haplotype is defined by a single variant position that is only variable within that haplotype, then it is removed.

## Quick Start

1. Clone or download this repo.

    ``` sh
    git clone https://github.com/kathiehuang/haplotype_calling_pipeline.git
    ```
    Alternatively, if you're viewing this on GitHub,
    you can click the green `Use this template` button to create
    your own version of the repo on GitHub, then clone it.

1. Install the dependencies.

    1. If you don't have conda yet, we recommend installing 
       [miniconda](https://docs.conda.io/en/latest/miniconda.html).
       
    1. Next, install [mamba](https://mamba.readthedocs.io/en/latest/), 
       a fast drop-in replacement for conda:
       
       ``` sh
       conda install mamba -n base -c conda-forge
       ```
       
    1. Finally, create the environment and activate it:
    
       ``` sh
       mamba env create -f environment.yaml # you only have to do this once
       conda activate haplotype_calling # you have to do this every time
       ```
       
    - Alternatively, you can install the dependencies listed in
    [`environment.yaml`](environment.yaml) however you like.

1. Edit the configuration file [`config.yaml`](config.yaml).
    - `target`: the polymorphic gene target.
    - `refs`: the path to the folder containing reference sequences for the polymorphic gene target that will be used to map the raw reads to the appropriate gene targets of interest
    - `pair1`: the path to the folder containing the forward reads.
    - `pair2`: the path to the folder containing the reverse reads.
    - `forward`: the path to the file with the list of forward primers.
    - `rev`: the path to the file with the list of reverse primers.
    - `out`: the name of desired output folder.
    - `cutoff`: cutoff for which samples with less than this number of reads after sampling should be removed.
    - `seed`: seed of R's random number generator for the purpose of obtaining a reproducible random result.
    - `haplotype_length`: the length of the majority of haplotypes for the target.

    You can leave these options as-is if you'd like to first make sure the
    workflow runs without error on your machine before using your own dataset
    and custom parameters.

1. Do a dry run to make sure the snakemake workflow is valid.

    ``` sh
    snakemake -n
    ```

1. Run the workflow.

    Run it **locally** with:
    ``` sh
    snakemake --cores {NCORES} # NCORES = number of cores, ie. without parallelization use snakemake --cores 1
    ```

    To run the workflow on an **HPC with Slurm**:

    1. Edit your email address (`YOUR_EMAIL_HERE`) in:

        - [`scripts/submit_slurm.sh`](scripts/submit_slurm.sh)

    1. Submit the snakemake workflow with:

        ``` sh
        sbatch scripts/submit_slurm.sh
        ```

        Slurm output files will be written to `logs/`. You will receive an email when the job is finished.

## Usage Examples

Below shows what output files looked like after running this pipeline with a small sample of haplotypes.

`clean_sequencing_reads` should produce two folders in the {out}/fastq/{target} folder labeled **1** and **2** containing the cleaned and mapped fastq files. **1** contains the forward reads, **2** contains the reverse reads. It also produces {out}/fastqc_in, a folder that contains the FastQC reports for each input fastq file. To open the .zip files, download and extract the files.

After running this rule with a small sample of haplotypes, the **1** folder contained these files:
```
BF1_AMA_1.fastq.gz

BF2_AMA_1.fastq.gz

BF3_AMA_1.fastq.gz

BF4_AMA_1.fastq.gz

BF5_AMA_1.fastq.gz

BF6_AMA_1.fastq.gz

BF7_AMA_1.fastq.gz

BF8_AMA_1.fastq.gz

BF9_AMA_1.fastq.gz

BF10_AMA_1.fastq.gz
```

`organize_folders` should produce an all_samples folder within the out/fastq/{target} folder. It is essentially a combination of the **1** and **2** folders.

`call_haplotypes` should produce a haplotype_output in the {out} folder. It will contain 3 files: `{target}_trimAndFilterTable`, `{target}_haplotypes.rds`, and `{target}_trackReadsThroughPipeline.csv`. 
- `{target}_trimAndFilterTable`: summarizes read trimming and filtering
- `{target}_haplotypes.rds`: R file that stores the haplotype results data set for furthermore manipulation in `censor_haplotypes`. 
- `{target}_trackReadsThroughPipeline.csv`: tracks the reads, looking at the number of reads that made it through each step of the pipeline.

With our small sample, the trimAndFilter table looked like this:
|                      | reads.in | reads.out |
|----------------------|----------|-----------|
| BF1_AMA_1.fastq.gz   | 13072    | 8297      |
| BF10_AMA_1.fastq.gz  | 14875    | 9243      |
| BF2_AMA_1.fastq.gz   | 15269    | 10247     |
| BF3_AMA_1.fastq.gz   | 10116    | 5075      |
| BF4_AMA_1.fastq.gz   | 13672    | 8852      |
| BF5_AMA_1.fastq.gz   | 12650    | 7720      |
| BF6_AMA_1.fastq.gz   | 14591    | 9754      |
| BF7_AMA_1.fastq.gz   | 12760    | 8208      |
| BF8_AMA_1.fastq.gz   | 11474    | 7382      |
| BF9_AMA_1.fastq.gz   | 12432    | 6318      |

And the trackReadsThroughPipeline table looked like this:

|      | merged | tabled | nonchim |
|------|--------|--------|---------|
| BF1  | 8296   | 8296   | 8296    |
| BF10 | 9241   | 9241   | 9241    |
| BF2  | 10239  | 10239  | 10239   |
| BF3  | 5056   | 5056   | 5056    |
| BF4  | 8850   | 8850   | 8850    |
| BF5  | 7614   | 7614   | 7210    |
| BF6  | 9752   | 9752   | 9752    |
| BF7  | 8125   | 8125   | 7795    |
| BF8  | 7378   | 7378   | 7378    |
| BF9  | 6317   | 6317   | 6317    |

`censor_haplotypes` should add six files to the {out}/haplotype_output folder: `{target}_haplotype_table_precensored.csv`, `{target}_snps_between_haps_within_samples.fasta`, `{target}_uniqueSeqs.fasta`, `{target}_aligned_seqs.fasta`, `{target}_uniqueSeqs_final_censored.fasta`, and `{target}_haplotype_table_censored_final_version.csv`. 
- `{target}_haplotype_table_precensored.csv`: outputs the haplotype data set prior to beginning the censoring process (essentially `{target}_haplotypes.rds` in a formatted csv file). 
- `{target}_snps_between_haps_within_samples.fasta`: fasta file of the haplotypes after the first three steps of the censoring process are completed. This is used to tally up the number of SNPs between all haplotype pairings. 
- `{target}_uniqueSeqs.fasta`: fasta file of the haplotypes after the fourth step of the censoring process is completed. 
- `{target}_aligned_seqs.fasta`: fasta file of the sequences after alignment. 
- `{target}_uniqueSeqs_final_censored.fasta`: fasta file of the haplotype results after all five steps of the censoring process are completed. 
- `{target}_haplotype_table_censored_final_version.csv`: outputs the final censored haplotype data set in a formatted table.

With our small sample, the haplotype_table_precensored file looked like this:

| H1    | H2   | H3   | H4   | H5   | H6   | H7   | H8 | MiSeq.ID |
|-------|------|------|------|------|------|------|----|----------|
| 0     | 0    | 0    | 0    | 8296 | 0    | 0    | 0  | BF1      |
| 0     | 0    | 0    | 9241 | 0    | 0    | 0    | 0  | BF10     |
| 10218 | 0    | 0    | 13   | 0    | 0    | 0    | 8  | BF2      |
| 0     | 5056 | 0    | 0    | 0    | 0    | 0    | 0  | BF3      |
| 11    | 8833 | 6    | 0    | 0    | 0    | 0    | 0  | BF4      |
| 180   | 0    | 6872 | 0    | 0    | 158  | 0    | 0  | BF5      |
| 9748  | 0    | 0    | 4    | 0    | 0    | 0    | 0  | BF6      |
| 0     | 444  | 7351 | 0    | 0    | 0    | 0    | 0  | BF7      |
| 0     | 0    | 0    | 0    | 0    | 7378 | 0    | 0  | BF8      |
| 32    | 0    | 0    | 0    | 0    | 0    | 6285 | 0  | BF9      |

The snps_between_haps_within_samples file looked like this:
```
>Seq1
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAACACCGGTAGCTACGGGAAATCAATATTTAAAAGATGGAGGTTTTGCTTTTCCTCCAACAGAACCTCATATGTCACCAATGACATTAGATGAAATGAGACATTTTTATAAAGATAATAAATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGATTCCAGATAATGATAAAAATTCAAATTATAAATATCCAGCTGTTTATGATGACAAAGATAAAAAGTGTCATATATTATATATTG

>Seq2
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAAAACCGGTAGCTACGGGAAATCAAGATTTAAAAGATGGAGGTTTTGCTTTTCCTCCAACAAATCCTCTTATATCACCAATGACATTAAATGGTATGAGAGATTTTTATAAAAATAATGAATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAATGATGAAAATTCAAATTATAAATATCCAGCTGTTTATGATGACAAAGATAAAAAGTGTCATATATTATATATTG

>Seq3
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAAAACCGGTAGCTACGGGAAATCAAGATTTAAAAGATGGAGGTTTTGCTTTTCCTCCAACAGAACCTCTTATATCACCAATGACATTAGATGATATGAGAGATTTTTATAAAAATAATGAATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAATGATCAAAATTCAAATTATAAATATCCAGCTGTTTATGATTACGAAGATAAAAAGTGTCATATATTATATATTG

>Seq4
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAACACCGGTAGCTACGGGAAAACAAGATTTAAAAGATGGAGGTTTTGCTTTTCCTCCAACAAATCCTCTTATATCACCAATGACATTAGATCATATGAGAGATTTTTATAAAAAAAATGAATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAATGATGAAAATTCAAATTATAAATATCCAGCTGTTTATGATTACAAAGATAAAAAGTGTCATATATTATATATTG

>Seq5
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAAAACCGGTAGCTACGGGAAATCAAGATTTAAAAGATGGAGGTTTTGCTTTTCCTCCAACAGAACCTCTTATATCACCAATGACATTAAATGGTATGAGAGATTTATATAAAAATAATGAAGATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAATGATAAAAATTCAAATTATAAATATCCAGCTGTTTATGATGACAAAAATAAAAAGTGTCATATATTATATATTG

>Seq6
GTAAAGGTATAATTATTGAGAATTCAAAAACTACTTTTTTAACACCGGTAGCTACGGAAAATCAAGATTTAAAAGATGGAGGTTTTGCTTTTCCTCCAACAAATCCTCCTATGTCACCAATGACATTAAATGGTATGAGAGATTTATATAAAAATAATGAATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAATGATAAAAATTCAAATTATAAATATCCAGCTGTTTATGATTACAATGATAATAAGTGTCATATATTATATATTG

>Seq7
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAAAACCGGTAGCTACGGGAAATCAAGATTTAAAAGATGGAGGTTTTGCTTTTCCTCCAACAGAACCTCTTATATCACCAATGACATTAAATGGTATGAGAGATTTTTATAAAAATAATGAATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAAGGATGAAAATTCAAATTATAAATATCCAGCTGTTTATGATGACAAAGATAAAAAGTGTCATATATTATATATTG

>Seq8
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAACACCGGTAGCTACGGAAAATCAAGATTTAAAAGATGGAGGTTTTGCTTTTCCTCCAACAAAACCTCTTATGTCACCAATGACATTAGATCAAATGAGACATTTTTATAAAGATAATAAATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGATTCCAGATAATGATAAAAATTCAAATTATAAATATCCAGCTGTTTATGATGACAAAGATAAAAAGTGTCATATATTATATATTG
```

The uniqueSeqs file looked like this: 
```
>Seq1
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAACACCGGTAGCTACGGGAAATCAATATTTAAAAGATGGAGGTTTTGCTTTTCCTCCAACAGAACCTCATATGTCACCAATGACATTAGATGAAATGAGACATTTTTATAAAGATAATAAATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGATTCCAGATAATGATAAAAATTCAAATTATAAATATCCAGCTGTTTATGATGACAAAGATAAAAAGTGTCATATATTATATATTG

>Seq2
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAAAACCGGTAGCTACGGGAAATCAAGATTTAAAAGATGGAGGTTTTGCTTTTCCTCCAACAAATCCTCTTATATCACCAATGACATTAAATGGTATGAGAGATTTTTATAAAAATAATGAATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAATGATGAAAATTCAAATTATAAATATCCAGCTGTTTATGATGACAAAGATAAAAAGTGTCATATATTATATATTG

>Seq3
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAAAACCGGTAGCTACGGGAAATCAAGATTTAAAAGATGGAGGTTTTGCTTTTCCTCCAACAGAACCTCTTATATCACCAATGACATTAGATGATATGAGAGATTTTTATAAAAATAATGAATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAATGATCAAAATTCAAATTATAAATATCCAGCTGTTTATGATTACGAAGATAAAAAGTGTCATATATTATATATTG

>Seq4
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAACACCGGTAGCTACGGGAAAACAAGATTTAAAAGATGGAGGTTTTGCTTTTCCTCCAACAAATCCTCTTATATCACCAATGACATTAGATCATATGAGAGATTTTTATAAAAAAAATGAATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAATGATGAAAATTCAAATTATAAATATCCAGCTGTTTATGATTACAAAGATAAAAAGTGTCATATATTATATATTG

>Seq5
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAAAACCGGTAGCTACGGGAAATCAAGATTTAAAAGATGGAGGTTTTGCTTTTCCTCCAACAGAACCTCTTATATCACCAATGACATTAAATGGTATGAGAGATTTATATAAAAATAATGAAGATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAATGATAAAAATTCAAATTATAAATATCCAGCTGTTTATGATGACAAAAATAAAAAGTGTCATATATTATATATTG

>Seq6
GTAAAGGTATAATTATTGAGAATTCAAAAACTACTTTTTTAACACCGGTAGCTACGGAAAATCAAGATTTAAAAGATGGAGGTTTTGCTTTTCCTCCAACAAATCCTCCTATGTCACCAATGACATTAAATGGTATGAGAGATTTATATAAAAATAATGAATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAATGATAAAAATTCAAATTATAAATATCCAGCTGTTTATGATTACAATGATAATAAGTGTCATATATTATATATTG

>Seq7
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAAAACCGGTAGCTACGGGAAATCAAGATTTAAAAGATGGAGGTTTTGCTTTTCCTCCAACAGAACCTCTTATATCACCAATGACATTAAATGGTATGAGAGATTTTTATAAAAATAATGAATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAAGGATGAAAATTCAAATTATAAATATCCAGCTGTTTATGATGACAAAGATAAAAAGTGTCATATATTATATATTG
```

The aligned_seqs file looked like this:

```
>Seq5
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAAAACCGGTAGCTACGGGAAATCAAGATTTAAAAGATGGA
GGTTTTGCTTTTCCTCCAACAGAACCTCTTATATCACCAATGACATTAAATGGTATGAGAGATTTATATAAAAATAATGA
AGATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAATGATAAAAATTCAA
ATTATAAATATCCAGCTGTTTATGATGACAAAAATAAAAAGTGTCATATATTATATATTG

>Seq6
GTAAAGGTATAATTATTGAGAATTCAAAAACTACTTTTTTAACACCGGTAGCTACGGAAAATCAAGATTTAAAAGATGGA
GGTTTTGCTTTTCCTCCAACAAATCCTCCTATGTCACCAATGACATTAAATGGTATGAGAGATTTATATAAAAATAATGA
ATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAATGATAAAAATTCAA
ATTATAAATATCCAGCTGTTTATGATTACAATGATAATAAGTGTCATATATTATATATTG

>Seq4
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAACACCGGTAGCTACGGGAAAACAAGATTTAAAAGATGGA
GGTTTTGCTTTTCCTCCAACAAATCCTCTTATATCACCAATGACATTAGATCATATGAGAGATTTTTATAAAAAAAATGA
ATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAATGATGAAAATTCAA
ATTATAAATATCCAGCTGTTTATGATTACAAAGATAAAAAGTGTCATATATTATATATTG

>Seq1
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAACACCGGTAGCTACGGGAAATCAATATTTAAAAGATGGA
GGTTTTGCTTTTCCTCCAACAGAACCTCATATGTCACCAATGACATTAGATGAAATGAGACATTTTTATAAAGATAATAA
ATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGATTCCAGATAATGATAAAAATTCAA
ATTATAAATATCCAGCTGTTTATGATGACAAAGATAAAAAGTGTCATATATTATATATTG

>Seq2
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAAAACCGGTAGCTACGGGAAATCAAGATTTAAAAGATGGA
GGTTTTGCTTTTCCTCCAACAAATCCTCTTATATCACCAATGACATTAAATGGTATGAGAGATTTTTATAAAAATAATGA
ATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAATGATGAAAATTCAA
ATTATAAATATCCAGCTGTTTATGATGACAAAGATAAAAAGTGTCATATATTATATATTG

>Seq3
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAAAACCGGTAGCTACGGGAAATCAAGATTTAAAAGATGGA
GGTTTTGCTTTTCCTCCAACAGAACCTCTTATATCACCAATGACATTAGATGATATGAGAGATTTTTATAAAAATAATGA
ATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAATGATCAAAATTCAA
ATTATAAATATCCAGCTGTTTATGATTACGAAGATAAAAAGTGTCATATATTATATATTG

>Seq7
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAAAACCGGTAGCTACGGGAAATCAAGATTTAAAAGATGGA
GGTTTTGCTTTTCCTCCAACAGAACCTCTTATATCACCAATGACATTAAATGGTATGAGAGATTTTTATAAAAATAATGA
ATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAAGGATGAAAATTCAA
ATTATAAATATCCAGCTGTTTATGATGACAAAGATAAAAAGTGTCATATATTATATATTG
```

The uniqueSeqs_final_censored file looked like this:
```
>Seq1
GTAAAGGTATAATTATTGAGAATTCAAATACTACTTTTTTAACACCGGTAGCTACGGGAAAACAAGATTTAAAAGATGGAGGTTTTGCTTTTCCTCCAACAAATCCTCTTATATCACCAATGACATTAGATCATATGAGAGATTTTTATAAAAAAAATGAATATGTAAAAAATTTAGATGAATTGACTTTATGTTCAAGACATGCAGGAAATATGAATCCAGATAATGATGAAAATTCAAATTATAAATATCCAGCTGTTTATGATTACAAAGATAAAAAGTGTCATATATTATATATTG
```

And the haplotype_table_censored_final table looked like this:

| H2   | MiSeq.ID |
|------|----------|
| 5056 | BF3      |
| 8833 | BF4      |
| 444  | BF7      |

## More resources

- [Snakemake tutorial](https://snakemake.readthedocs.io/en/stable/tutorial/tutorial.html)
- [conda user guide](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html)