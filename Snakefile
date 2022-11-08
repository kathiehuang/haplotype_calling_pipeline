import pandas as pd

configfile: "config.yaml"

# update readme, delete unnecessary parameters from each rule, clean up code in general, delete old stuff

# modifiable parameters - change in config.yaml file
TARGET_TABLE = pd.read_table(config['target_file'])
TARGET = list(TARGET_TABLE.target.unique())
RECREATE_REF_FOLDER = config['recreate_ref_folder']
TRUNCQ_VALUES = config['truncQ_values']
CUTOFF = config['cutoff']
SEED = config['seed']
READ_DEPTH = config['read_depth']
PROPORTION = config['proportion']
READ_DEPTH_RATIO = config['read_depth_ratio']

# paths
REFS = config['refs']
PAIR1 = config['pair1']
PAIR2 = config['pair2']
FOWARD = config['forward']
REV = config['rev']
OUT = config['out']

rule all:
	input:
		# expand("{target}/{out}/fastqc_in", out=OUT, target=TARGET),
		# expand("{target}/{out}/trim", out=OUT, target=TARGET),
		# expand("{target}/{out}/fastq/all_samples", out=OUT, target=TARGET),
 		# expand("{target}/{out}/haplotype_output/{target}_{q_values}_trimAndFilterTable", out=OUT, target=TARGET, q_values=TRUNCQ_VALUES),
		# expand("{target}/{out}/haplotype_output/{target}_finalTrimAndFilterTable", out=OUT, target=TARGET),
		# expand("{target}/{out}/haplotype_output/{target}_trackReadsThroughPipeline.csv", out=OUT, target=TARGET),
		expand("{target}/{out}/haplotype_output/{target}_haplotype_table_censored_final_version.csv", out=OUT, target=TARGET),

rule call_fastqc:
	input:
		refs="refs/{target}.fasta",
		pair1=PAIR1,
		pair2=PAIR2,
		forward=expand("{forward}.fasta", forward=FOWARD),
		rev=expand("{rev}.fasta", rev=REV)
	output:
		out=directory("{target}/{out}/fastqc_in/"),
	params:
		recreate_ref_folder=RECREATE_REF_FOLDER,
		refs="refs/{target}.fasta",
		folder="{target}/{out}",
		pair1=PAIR1,
		pair2=PAIR2,
		forward=expand("{forward}.fasta", forward=FOWARD),
		rev=expand("{rev}.fasta", rev=REV),
		output="{target}/{out}",
		forward_samples="{target}/{out}/fastq/1",
		reverse_samples="{target}/{out}/fastq/2",
		haplotype_output="{target}/{out}/haplotype_output",
		out="{target}/{out}", # should be "{target}/{out}" i think
		pyscript="scripts/step1a_callFastqc.py",
	script:
		"{params.pyscript}"

rule call_trimmomatic:
	input:
		refs="refs/{target}.fasta",
		pair1=PAIR1,
		pair2=PAIR2,
		forward=expand("{forward}.fasta", forward=FOWARD),
		rev=expand("{rev}.fasta", rev=REV),
		inputDir="{target}/{out}/fastqc_in/",
	output:
		#directory(expand("{out}/fastq/{target}/1/", out=OUT, target=TARGET)),
		#directory(expand("{out}/fastq/{target}/2/", out=OUT, target=TARGET)),
		out=directory("{target}/{out}/trim/"),
	params:
		refs="refs/{target}.fasta",
		folder="{target}/{out}",
		pair1=PAIR1,
		pair2=PAIR2,
		forward=expand("{forward}.fasta", forward=FOWARD),
		rev=expand("{rev}.fasta", rev=REV),
		output="{target}/{out}/fastq/all_samples",
		forward_samples="{target}/{out}/fastq/1",
		reverse_samples="{target}/{out}/fastq/2",
		haplotype_output="{target}/{out}/haplotype_output",
		out="{target}/{out}", # should be "{target}/{out}" i think
		pyscript="scripts/step1b_callTrimmomatic.py"
	script:
		"{params.pyscript}"
		
rule synchronize_reads:
	input:
		refs="refs/{target}.fasta",
		pair1=PAIR1,
		pair2=PAIR2,
		forward=expand("{forward}.fasta", forward=FOWARD),
		rev=expand("{rev}.fasta", rev=REV),
		inputDir="{target}/{out}/trim/",
	output:
		#directory(expand("{out}/fastq/{target}/1/", out=OUT, target=TARGET)),
		#directory(expand("{out}/fastq/{target}/2/", out=OUT, target=TARGET)),
		out=directory("{target}/{out}/fastq/all_samples/"),
	params:
		recreate_ref_folder=RECREATE_REF_FOLDER,
		refs="refs/{target}.fasta",
		pair1=PAIR1,
		pair2=PAIR2,
		forward=expand("{forward}.fasta", forward=FOWARD),
		rev=expand("{rev}.fasta", rev=REV),
		output="{target}/{out}/fastq/all_samples",
		forward_samples="{target}/{out}/fastq/1",
		reverse_samples="{target}/{out}/fastq/2",
		haplotype_output="{target}/{out}/haplotype_output",
		out="{target}/{out}", # should be "{target}/{out}" i think
		pyscript="scripts/step1c_synchronizeReads.py",
		trimmed="{target}/{out}/trim",
		target="{target}",
	script:
		"{params.pyscript}"

# rule clean_sequencing_reads:
# 	input:
# 		refs="refs/{target}.fasta",
# 		pair1=PAIR1,
# 		pair2=PAIR2,
# 		forward=expand("{forward}.fasta", forward=FOWARD),
# 		rev=expand("{rev}.fasta", rev=REV)
# 	output:
# 		#directory(expand("{out}/fastq/{target}/1/", out=OUT, target=TARGET)),
# 		#directory(expand("{out}/fastq/{target}/2/", out=OUT, target=TARGET)),
# 		out=directory("{target}/{out}/fastq/all_samples/")
# 	params:
# 		recreate_ref_folder=RECREATE_REF_FOLDER,
# 		refs="refs/{target}.fasta",
# 		folder="{target}/{out}",
# 		pair1=PAIR1,
# 		pair2=PAIR2,
# 		forward=expand("{forward}.fasta", forward=FOWARD),
# 		rev=expand("{rev}.fasta", rev=REV),
# 		output="{target}/{out}/fastq/all_samples",
# 		forward_samples="{target}/{out}/fastq/1",
# 		reverse_samples="{target}/{out}/fastq/2",
# 		haplotype_output="{target}/{out}/haplotype_output",
# 		out="{target}/{out}", # should be "{target}/{out}" i think
# 		pyscript="scripts/step1_getReferences.py"
# 	run: # put this stuff all in the python script
# 		if params.recreate_ref_folder == True:
# 			shell("rm -rf ref")
# 		shell("perl scripts/step1_splitSyncReadsMultiRef.pl 1 {input.refs} {params.folder} {input.pair1} {input.pair2} {input.forward} {input.rev}")
# 		shell("mkdir {params.output}")
# 		# wait check these
# 		# ok fixed the params.formward_samples and stuff, rerun
# 		shell("mv {params.forward_samples}/*.fastq.gz {params.output} && mv {params.reverse_samples}/*.fastq.gz {params.output}")
# 		shell("rm -r {params.forward_samples} && rm -r {params.reverse_samples}")

rule trim_and_filter:
	input:
		all_samples="{target}/{out}/fastq/all_samples/",
	output:
		trim_filter_table="{target}/{out}/haplotype_output/{target}_{q_values}_trimAndFilterTable",
	params:
		all_samples="{target}/{out}/fastq/all_samples",
		read_count="{target}/{out}/haplotype_output/{target}_read_count",
		rscript="scripts/step2_trim_and_filter.R",
		q_values="{q_values}",
		haplotype_output="{target}/{out}/haplotype_output",
	script:
		"{params.rscript}"

rule optimize_reads:
	input:
		# all_samples="{target}/{out}/fastq/all_samples/",
		trim_filter_table=expand("{target}/{out}/haplotype_output/{target}_{q_values}_trimAndFilterTable", out=OUT, target=TARGET, q_values=TRUNCQ_VALUES),
		q_trim_filter=expand("{target}/{out}/haplotype_output/{target}_{q_values}_trimAndFilterTable", out=OUT, target=TARGET, q_values=TRUNCQ_VALUES),
	output:
		max_read_count="{target}/{out}/haplotype_output/{target}_max_read_count",
		final_trim_filter_table="{target}/{out}/haplotype_output/{target}_finalTrimAndFilterTable",
		final_q_value="{target}/{out}/haplotype_output/{target}_final_q_value",
	params:
		read_count="{target}/{out}/haplotype_output/{target}_read_count",
		max_read_count="{target}/{out}/haplotype_output/{target}_max_read_count",
		rscript="scripts/step3_optimize_reads.R",
		target="{target}",
		out="{out}",
		all_samples="{target}/{out}/fastq/all_samples",
		final_filtered="{target}/{out}/fastq/all_samples/final_filtered",
	script:
		"{params.rscript}"

rule call_haplotypes:
	input:
		# all_samples="{target}/{out}/fastq/all_samples/",
		trim_filter_table="{target}/{out}/haplotype_output/{target}_finalTrimAndFilterTable",
		# q_trim_filter=expand("{target}/{out}/haplotype_output/{target}_{q_values}_trimAndFilterTable", out=OUT, target=TARGET, q_values=TRUNCQ_VALUES),
	output:
		results="{target}/{out}/haplotype_output/{target}_haplotypes.rds",
		reads_table="{target}/{out}/haplotype_output/{target}_trackReadsThroughPipeline.csv",
	params:
		all_samples="{target}/{out}/fastq/all_samples",
		trim_filter_table="{target}/{out}/haplotype_output/{target}_finalTrimAndFilterTable",
		rscript="scripts/step4_call_haplotypes.R",
		cutoff=CUTOFF,
		seed=SEED,
	script:
		"{params.rscript}"

rule censor_haplotypes:
	input:
		"{target}/{out}/haplotype_output/{target}_haplotypes.rds",
	output:
		precensored_haplotype_table="{target}/{out}/haplotype_output/{target}_haplotype_table_precensored.csv",
		snps_between_haps="{target}/{out}/haplotype_output/{target}_snps_between_haps_within_samples.fasta",
		unique_seqs="{target}/{out}/haplotype_output/{target}_uniqueSeqs.fasta",
		aligned_seqs="{target}/{out}/haplotype_output/{target}_aligned_seqs.fasta",
		final_censored="{target}/{out}/haplotype_output/{target}_uniqueSeqs_final_censored.fasta",
		final_haplotype_table="{target}/{out}/haplotype_output/{target}_haplotype_table_censored_final_version.csv",
	params:
		rscript="scripts/step5_haplotype_censoring.R",
		haplotypes="{target}/{out}/haplotype_output/{target}_haplotypes.rds",
		depth=READ_DEPTH,
		proportion=PROPORTION,
		length=lambda wildcards: list(TARGET_TABLE.length[TARGET_TABLE.target == wildcards.target]),
		ratio=READ_DEPTH_RATIO,
	script:
		"{params.rscript}"