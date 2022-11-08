#!/usr/bin/perl
# Written by Joe Saelens
# Updated on 11/20/2020 to include read pair synchronization
# Updated on 10/25/2022 by Kathie Huang - converted to Python and split into 3 separate scripts

import os
import subprocess

# defining functions

def getReference(numRef, refPaths):
    i = 0
    print(numRef)
    print(refPaths)
    
    refs = refPaths.split(',')
    refNames = [None] * len(refs)
    referenceFastas = [None] * len(refs)
    for ref in refs:
        referenceFastas[i] = ref
        # remove leading and trailing whitespace
        referenceFastas[i] = referenceFastas[i].strip()
        if not os.path.exists(referenceFastas[i]):
            sys.exit("**Reference file does not exist**")
        refSplit = referenceFastas[i].split('/')
        x = len(refSplit)
        nameIndex = x - 1
        refFasta = refSplit[nameIndex].split('\.')
        refNames[i] = refFasta[0]
        i += 1
    return referenceFastas, refNames

def makeOutDirs(out, refs):

    os.system('mkdir -p {}/cut'.format(out))
    os.system('mkdir -p {}/cut/1'.format(out))
    os.system('mkdir -p {}/cut/2'.format(out))
    print ("\tAdapter cut reads temporarily stored in {}/cut".format(out))

    os.system('mkdir -p {}/trim'.format(out))
    os.system('mkdir -p {}/trim/1'.format(out))
    os.system('mkdir -p {}/trim/2'.format(out))
    os.system('mkdir -p {}/trim/fastqcTrim'.format(out))
    os.system('mkdir -p {}/trim/Log'.format(out))
    os.system('mkdir -p {}/trim/singleton'.format(out))
    os.system('mkdir -p {}/trim/Summary'.format(out))
    print ("\tTrimmed reads stored in /{}/trim".format(out))

    os.system('mkdir -p {}/fastqc_trim_split'.format(out))
    print ("\tFastqc .html files of trimmed reads stored in /{}/fastqc_trim_split\n".format(out))

    # if not os.path.exists("/" + out + "/cut"):
    #     os.system('mkdir {}/cut'.format(out))
    #     os.system('mkdir {}/cut/1'.format(out))
    #     os.system('mkdir {}/cut/2'.format(out))
    #     print ("\tAdapter cut reads temporarily stored in {}/cut".format(out))

    # if not os.path.exists("/" + out + "/trim"):
    #     os.system('mkdir {}/trim'.format(out))
    #     os.system('mkdir {}/trim/1'.format(out))
    #     os.system('mkdir {}/trim/2'.format(out))
    #     os.system('mkdir {}/trim/fastqcTrim'.format(out))
    #     os.system('mkdir {}/trim/Log'.format(out))
    #     os.system('mkdir {}/trim/singleton'.format(out))
    #     os.system('mkdir {}/trim/Summary'.format(out))
    #     print ("\tTrimmed reads stored in /{}/trim".format(out))

    # if not os.path.exists("/" + out + "/fastqc_trim_split"):
    #     os.system('mkdir {}/fastqc_trim_split'.format(out))
    #     print ("\tFastqc .html files of trimmed reads stored in /{}/fastqc_trim_split\n".format(out))

def getReads(readsDir):
    if os.path.exists(readsDir):
        reads = os.listdir(readsDir)
    else:
        sys.exit("\t**Reads not found**")
    reads.sort()
    return reads

def trimReads(read1Dir, read2Dir, outDir, reads1, reads2, forward, reverse):
    size = len(reads1)
    size2 = len(reads2)
    if size != size2:
        sys.exit("\t***Paired-end read file names unequal***")
    print(reads1)
    # for i, file in enumerate(sorted(os.listdir(read1Dir))):
    #     print(i)
    #     print(file)

    for i in range(size):
        currRead1 = reads1[i]
        PRE = currRead1.split('_')
        prefix = PRE[0]
        print("\t Trimming {} reads".format(prefix))
        currRead2 = reads2[i]
        PRE2 = currRead2.split('_')
        prefix2 = PRE2[0]
        if prefix == prefix2:
            forwardElem = forward[0]
            reverseElem = reverse[0]
            os.system('cutadapt -g file:{0} -G file:{1} -o {2}/cut/1/{3}.1.fastq.gz -p {2}/cut/2/{3}.2.fastq.gz {4}/{5} {6}/{7}'.format(forwardElem, reverseElem, outDir, prefix, read1Dir, currRead1, read2Dir, currRead2))

            os.system('trimmomatic PE -phred33 -summary {0}/trim/Summary/{1}.summary {0}/cut/1/{1}.1.fastq.gz {0}/cut/2/{1}.2.fastq.gz {0}/trim/1/{1}.1.fastq.gz {0}/trim/singleton/{1}.1_unpaired.fq.gz {0}/trim/2/{1}.2.fastq.gz {0}/trim/singleton/{1}.2_unpaired.fq.gz LEADING:10 TRAILING:10 SLIDINGWINDOW:4:15 MINLEN:80'.format(outDir, prefix))

            os.system('rm {0}/cut/1/{1}.1.fastq.gz {0}/cut/2/{1}.2.fastq.gz'.format(outDir, prefix))

    trimReads1 = "{}/trim/1".format(outDir)
    trimReads2 = "{}/trim/2".format(outDir)
    return trimReads1, trimReads2

numRef = 1
refs = snakemake.params["refs"]
out = snakemake.params["folder"]
pair1 = snakemake.params["pair1"]
pair2 = snakemake.params["pair2"]
forward = snakemake.params["forward"]
reverse = snakemake.params["rev"]

refSeqs, refNames = getReference(numRef, refs)

out = out.replace('\n', '')    # remove '\n' only
makeOutDirs(out, refNames);

pairedReadFiles1 = getReads(pair1)
pairedReadFiles2 = getReads(pair2)

trim1, trim2 = trimReads(pair1, pair2, out, pairedReadFiles1, pairedReadFiles2, forward, reverse)
trimReads1 = getReads(trim1)
trimReads2 = getReads(trim2)
print("trim1 " + trim1) # CSP/out/trim/1 add these as parameters/inputs to synchronizeReads
print("trim2 " + trim2) # CSP/out/trim/2
print("trimReads1")
print(trimReads1)
#['BF1.1.fastq.gz', 'BF10.1.fastq.gz', 'BF2.1.fastq.gz', 'BF3.1.fastq.gz', 'BF4.1.fastq.gz', 'BF5.1.fastq.gz', 'BF6.1.fastq.gz', 'BF7.1.fastq.gz', 'BF8.1.fastq.gz', 'BF9.1.fastq.gz']
# this one could just use getReads functions

# ($trim1, $trim2) = trimReads("$pair1", "$pair2", "$out", \@PairedReadfiles1, \@PairedReadfiles2, "$forward", "$reverse");

# @trimReads1 = getReads("$trim1");
# @trimReads2 = getReads("$trim2");
    
# splitReads(\@refSeqs, \@refNames, "$out", \@trimReads1, \@trimReads2, "$trim1", "$trim2");
# ############################################################

# sub getReference
# {
#     my $numRef = shift;
#     my $refPaths = shift;
#     my $i;
#     my @referenceFastas;
#     my @refNames;
#     print "\n$numRef\t$refPaths\n";

#     my @refs = split(',', $refPaths);
#     my $ref;
#     $i = 0;
#     foreach $ref (@refs)
#     {
# 	$referenceFastas[$i] = $ref;
# 	$referenceFastas[$i] =~ s/^\s+|\s+$//g;
# 	unless (-e $referenceFastas[$i])
# 	{die "\n**Reference file does not exist**\n";}
# 	my @refSplit = split( '/', $referenceFastas[$i]);
# 	my $x = @refSplit;
# 	my $nameIndex = ($x - 1);
# 	my @refFasta = split('\.', $refSplit[$nameIndex]);
# 	$refNames[$i] = $refFasta[0];
# 	$i++;
#     }
#     return (\@referenceFastas, \@refNames);
# }
# ############################################################
# sub makeOutDirs
# {
#     my $topOut = shift;
#     my $refs = shift;
#     my @refNames = @{$refs};
#     my $elem;
#     my $i = 0;
#     unless (-d $topOut)
#     {system "mkdir $topOut";}
#     if ( -d $topOut)
#     {
#         unless (-d "$topOut/fastq")
#         {
#             system "mkdir $topOut/fastq";
#             foreach $elem (@refNames)
#             {
#                 system "mkdir $topOut/fastq/$refNames[$i]";
#                 $i++;
#             }
#             print "\tSynchronized paired end fastq files stored in $topOut/fastq\n";
#         }
			
#         unless (-d "$topOut/Results")
#         {system "mkdir $topOut/Results";}
#         print "\n\tLog files stored in $topOut/Results\n";
            
#         unless (-d "$topOut/fastqc_in")
#         {system "mkdir $topOut/fastqc_in";}
#         print "\n\tFastqc .html files of input reads stored in $topOut/fastqc_in\n";
            
#         unless (-d "$topOut/cut")
#         {system "mkdir $topOut/cut";
#         system "mkdir $topOut/cut/1";
#         system "mkdir $topOut/cut/2";}
#         print "\tAdapter cut reads temporarily stored in $topOut/cut\n";

#         unless (-d "$topOut/trim")
#         {system "mkdir $topOut/trim";
#         system "mkdir $topOut/trim/1";
#         system "mkdir $topOut/trim/2";
#         system "mkdir $topOut/trim/singleton";
#         system "mkdir $topOut/trim/Log";
#         system "mkdir $topOut/trim/Summary";
#         system "mkdir $topOut/trim/fastqcTrim";}
#         print "\tTrimmed reads stored in $topOut/trim\n";

#         unless (-d "$topOut/fastqc_trim_split")
#         {system "mkdir $topOut/fastqc_trim_split";}
#         print "\n\tFastqc .html files of trimmed reads stored in $topOut/fastqc_trim_split\n\n";
# 	}
# }
# ############################################################
# sub getReads
# {
#     my $readsDir = shift();
#     my @Reads = ();
#     my $elem;
#     if ( -d $readsDir)
#     {
# 		opendir (READS, "$readsDir");
# 		@Reads = readdir READS;
# 		closedir READS;
# 		splice (@Reads, 0, 2);
#     }
# 	else { die "\n\t**Reads not found**\n"; }

# 	my @sortReads = sort(@Reads);
# 	return @sortReads;
# }
# ############################################################
# sub QCreads
# {
#     my $read1Dir = shift;
#     my $read2Dir = shift;
#     my $outDir = shift;
#     my $pair1Reads = shift;
#     my $pair2Reads = shift;
#     my $format = shift;
#     my @Reads1 = @{$pair1Reads};
#     my @Reads2 = @{$pair2Reads};
#     my $i;
#     my $size = @Reads1;
#     my $size2 = @Reads2;
#     if ($size != $size2) {die "Paired end read files unequal";}
    
#     for ($i = 0; $i < $size; $i++)
#     {
#         system "fastqc -o $outDir -f $format $read1Dir/$Reads1[$i] $read2Dir/$Reads2[$i]";
#     } 
# }
# ############################################################
# sub trimReads
# {
#     my $read1Dir = shift;
#     my $read2Dir = shift;
#     my $outDir = shift;
#     my $pair1Reads = shift;
#     my $pair2Reads = shift;
#     my $forward = shift;
#     my $reverse = shift;
#     my @Reads1 = @{$pair1Reads};
#     my @Reads2 = @{$pair2Reads};
#     my $i;
#     my $size = @Reads1;
#     my $size2 = @Reads2;
#     my @PRE;
#     my $prefix;
#     if ($size != $size2) {die "\n\t***Paired-end read file names unequal***\n";}

#     for ($i = 0; $i < $size; $i++)
#     {
#         @PRE = split('_', $Reads1[$i]);
#         $prefix = $PRE[0];
#         print "\n\tTrimming $prefix reads\n";
#         my @PRE2 = split('_', $Reads2[$i]);
#         my $pre2 = $PRE2[0];
#         if($prefix eq $pre2)
#         {
# 	    system "cutadapt -g file:$forward -G file:$reverse -o $outDir/cut/1/$prefix.1.fastq.gz -p $outDir/cut/2/$prefix.2.fastq.gz $read1Dir/$Reads1[$i] $read2Dir/$Reads2[$i]";

#         system "trimmomatic PE -phred33 -summary $out/trim/Summary/$prefix.summary $outDir/cut/1/$prefix.1.fastq.gz $outDir/cut/2/$prefix.2.fastq.gz $outDir/trim/1/$prefix.1.fastq.gz $outDir/trim/singleton/$prefix.1_unpaired.fq.gz $outDir/trim/2/$prefix.2.fastq.gz $outDir/trim/singleton/$prefix.2_unpaired.fq.gz LEADING:10 TRAILING:10 SLIDINGWINDOW:4:15 MINLEN:80";

# 	    system "rm $outDir/cut/1/$prefix.1.fastq.gz $outDir/cut/2/$prefix.2.fastq.gz";
#         }
#     }

#     my $trimReads1 = "$outDir/trim/1";
#     my $trimReads2 = "$outDir/trim/2";
    
#     return ($trimReads1, $trimReads2);
# }
# ############################################################
# sub splitReads
# {
# 	my $fastaRefs = shift;
# 	my $refs = shift;
# 	my $out = shift;
# 	my $readsFile1 = shift;
# 	my $readsFile2 = shift;
# 	my $read1Dir = shift;
# 	my $read2Dir = shift;
# 	my @refSeqs = @{$fastaRefs};
# 	my @refNames = @{$refs};
# 	my @read1 = @{$readsFile1};
# 	my @read2 = @{$readsFile2};
# 	my $i;
# 	my $size = @read1;
# 	my @sampleName;
# 	my $elem;

# 	my $Refs = join( ',', @refSeqs );

# 	for($i = 0; $i < $size; $i++)
# 	{
# 		my @fileSplit = split(/\./, $read1[$i]);
# 		$sampleName[$i] = $fileSplit[0];
# 		print "\n\tAligning $sampleName[$i] to $Refs\n";
# 		my @file2Split = split(/\./, $read2[$i]);
# 		my $sampleName2 = $file2Split[0];

# 		if ($sampleName[$i] eq $sampleName2)
# 		{
# 			system "bbsplit.sh -Xmx8000m in=$read1Dir/$read1[$i] in2=$read2Dir/$read2[$i] ref=$Refs basename=$sampleName[$i]_%_#.fastq >& $out/Results/$sampleName[$i].txt";
			
# 			foreach $elem (@refNames)
# 			{
# 				system "mv *$elem* $out/fastq/$elem";
# 				system "gzip $out/fastq/$elem/*.fastq";
# 				unless (-d "$out/fastq/$elem/1")
# 				{system "mkdir $out/fastq/$elem/1";}
# 				unless (-d "$out/fastq/$elem/2")
# 				{system "mkdir $out/fastq/$elem/2";}
# 				system "mv $out/fastq/$elem/*_1.fastq.gz $out/fastq/$elem/1";
# 				system "mv $out/fastq/$elem/*_2.fastq.gz $out/fastq/$elem/2";

# 			}
# 		}
# 	}
    
#     print "\nSynchronizing paired end reads...\n\n";
#     foreach $elem (@refNames)
#     {
#         my @unsyncReads1 = getReads("$out/fastq/$elem/1");
#         my @unsyncReads2 = getReads("$out/fastq/$elem/2");
#         syncReads("$out/fastq/$elem/1", "$out/fastq/$elem/2", \@unsyncReads1, \@unsyncReads2);
        
#     }   
# }
# ############################################################
# sub syncReads
# {
#     my $read1Dir = shift;
#     my $read2Dir = shift;
#     my $pair1Reads = shift;
#     my $pair2Reads = shift;
#     my @Reads1 = @{$pair1Reads};
#     my @Reads2 = @{$pair2Reads}; 
#     my $i;
#     my @sampleName;
#     my $size = @Reads1;
#     my $size2 = @Reads2;
#     if ($size != $size2) {die "Paired end read files unequal";}

#     for ($i = 0; $i < $size; $i++)
#     {
#     	my @fileSplit = split(/\./, $Reads1[$i]);
# 	$sampleName[$i] = $fileSplit[0];
# 	print "\n\tSynchronizing paired reads for $sampleName[$i]\n";
# 	my @file2Split = split(/\./, $Reads2[$i]);
# 	my $sampleName2 = $file2Split[0];

# 	system "repair.sh in=$read1Dir/$Reads1[$i] in2=$read2Dir/$Reads2[$i] out=$read1Dir/$sampleName[$i].paired.fastq.gz out2=$read2Dir/$sampleName2.paired.fastq.gz outs=singletons.fq repair";
# 	system "rm singletons.fq $read1Dir/$Reads1[$i] $read2Dir/$Reads2[$i]";
# 	system "mv $read1Dir/$sampleName[$i].paired.fastq.gz $read1Dir/$Reads1[$i]";
# 	system "mv $read2Dir/$sampleName2.paired.fastq.gz $read2Dir/$Reads2[$i]";
#     }
# }
# ############################################################

# shell commands
# make_folder_command = ['mkdir', snakemake.params["refs"]]
# move_folders_command = ['mv', snakemake.params["forward_samples"]]

# subprocess.run(make_folder_command)
# os.system('mkdir {}'.format(snakemake.params["refs"]))
# os.system('mv {0}/*.fastq.gz {1} && mv {2}/*.fastq.gz {1}'.format(snakemake.params["forward_samples"], snakemake.params["out"], snakemake.params["reverse_samples"]))
# os.system('rm -r {0} && rm -r {1}'.format(snakemake.params["forward_samples"], snakemake.params["reverse_samples"]))
# os.system('mv {params.forward_samples}/*.fastq.gz {params.out} && mv {params.reverse_samples}/*.fastq.gz {params.out}"')
